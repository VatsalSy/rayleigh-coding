#!/usr/bin/env python3
"""Read a complete GitHub PR snapshot without mutating remote or local Git state."""

import datetime
import json
import math
import re
import subprocess
import time
from urllib.parse import urlsplit


__all__ = ["SnapshotError", "fetch_discussion", "fetch_snapshot", "parse_pr_url"]

PAGE_SIZE = 100
MAX_PAGES = 100
_REPOSITORY = re.compile(r"([A-Za-z0-9](?:[A-Za-z0-9-]{0,37}[A-Za-z0-9])?)/([A-Za-z0-9_.-]{1,100})\Z")
_SHA = re.compile(r"[0-9a-fA-F]{40}\Z")

_METADATA_QUERY = """
query SnapshotMetadata($owner:String!, $name:String!, $number:Int!) {
  repository(owner:$owner, name:$name) {
    nameWithOwner
    pullRequest(number:$number) {
      number url title headRefOid baseRefName state isDraft
      mergeable mergeStateStatus reviewDecision
    }
  }
}
"""

_CHECKS_QUERY = """
query SnapshotChecks($owner:String!, $name:String!, $number:Int!, $cursor:String) {
  repository(owner:$owner, name:$name) {
    nameWithOwner
    pullRequest(number:$number) {
      number headRefOid
      commits(last:1) {
        nodes {
          commit {
            oid
            statusCheckRollup {
              contexts(first:100, after:$cursor) {
                totalCount pageInfo { hasNextPage endCursor }
                nodes {
                  __typename
                  ... on CheckRun {
                    id name status conclusion title summary text detailsUrl
                    databaseId startedAt completedAt
                    isRequired(pullRequestNumber:$number)
                    checkSuite { id commit { oid } app { id slug } }
                  }
                  ... on StatusContext {
                    id context state description targetUrl createdAt
                    isRequired(pullRequestNumber:$number)
                    commit { oid } creator { login }
                  }
                }
              }
            }
          }
        }
      }
    }
  }
}
"""

_REVIEWS_QUERY = """
query SnapshotReviews($owner:String!, $name:String!, $number:Int!, $cursor:String) {
  repository(owner:$owner, name:$name) {
    nameWithOwner
    pullRequest(number:$number) {
      number headRefOid
      reviews(first:100, after:$cursor) {
        totalCount pageInfo { hasNextPage endCursor }
        nodes { id author { login } state commit { oid } submittedAt body url }
      }
    }
  }
}
"""

_COMMENTS_QUERY = """
query SnapshotComments($owner:String!, $name:String!, $number:Int!, $cursor:String) {
  repository(owner:$owner, name:$name) {
    nameWithOwner
    pullRequest(number:$number) {
      number headRefOid
      comments(first:100, after:$cursor) {
        totalCount pageInfo { hasNextPage endCursor }
        nodes { id author { login } body url createdAt updatedAt }
      }
    }
  }
}
"""

_THREADS_QUERY = """
query SnapshotThreads($owner:String!, $name:String!, $number:Int!, $cursor:String) {
  repository(owner:$owner, name:$name) {
    nameWithOwner
    pullRequest(number:$number) {
      number headRefOid
      reviewThreads(first:100, after:$cursor) {
        totalCount pageInfo { hasNextPage endCursor }
        nodes {
          id isResolved isOutdated path line
          diffSide startLine startDiffSide originalLine originalStartLine
          resolvedBy { login }
          comments(first:100) {
            totalCount pageInfo { hasNextPage endCursor }
            nodes { id author { login } body url createdAt updatedAt commit { oid } }
          }
        }
      }
    }
  }
}
"""

_THREAD_COMMENTS_QUERY = """
query SnapshotThreadComments($owner:String!, $name:String!, $number:Int!, $threadId:ID!, $cursor:String) {
  repository(owner:$owner, name:$name) {
    nameWithOwner
    pullRequest(number:$number) { number headRefOid }
  }
  node(id:$threadId) {
    __typename
    ... on PullRequestReviewThread {
      id
      pullRequest { number headRefOid repository { nameWithOwner } }
      comments(first:100, after:$cursor) {
        totalCount pageInfo { hasNextPage endCursor }
        nodes { id author { login } body url createdAt updatedAt commit { oid } }
      }
    }
  }
}
"""


class SnapshotError(Exception):
    """A failed snapshot whose message is safe to include in a watcher receipt."""

    def __init__(self, message, *, code):
        super().__init__(message)
        self.code = code


def _invalid(message):
    raise SnapshotError(message, code="invalid_response")


def _object(value, field):
    if not isinstance(value, dict):
        _invalid("GitHub returned an invalid " + field + ".")
    return value


def _fields(value, fields, field):
    value = _object(value, field)
    if any(key not in value for key in fields):
        _invalid("GitHub omitted fields from its " + field + ".")
    return value


def _string(value, field, *, nullable=False, empty=False):
    if value is None and nullable:
        return None
    if not isinstance(value, str) or (not empty and not value.strip()):
        _invalid("GitHub returned an invalid " + field + ".")
    return value


def _boolean(value, field):
    if type(value) is not bool:
        _invalid("GitHub returned an invalid " + field + ".")
    return value


def _integer(value, field, *, nullable=False, minimum=0):
    if value is None and nullable:
        return None
    if type(value) is not int or value < minimum:
        _invalid("GitHub returned an invalid " + field + ".")
    return value


def _enum(value, field, choices, *, nullable=False):
    value = _string(value, field, nullable=nullable)
    if value is not None and value not in choices:
        _invalid("GitHub returned an unknown " + field + ".")
    return value


def _sha(value, field, *, nullable=False):
    value = _string(value, field, nullable=nullable)
    if value is not None and not _SHA.fullmatch(value):
        _invalid("GitHub returned an invalid " + field + ".")
    return value.lower() if value is not None else None


def _timestamp(value, field, *, nullable=False):
    value = _string(value, field, nullable=nullable)
    if value is not None:
        try:
            parsed = datetime.datetime.fromisoformat(value.replace("Z", "+00:00"))
        except ValueError:
            _invalid("GitHub returned an invalid " + field + ".")
        if parsed.tzinfo is None:
            _invalid("GitHub returned an invalid " + field + ".")
    return value


def _same_head(actual, expected):
    if actual != expected:
        raise SnapshotError("The PR head changed while reading its snapshot.", code="head_changed")


def _request(query, variables, timeout):
    # JSON on stdin keeps all repository names and opaque cursors out of shell
    # syntax and gh's field/file expansion. Only fixed read-only queries run.
    allowed_timeout = timeout() if callable(timeout) else timeout
    try:
        result = subprocess.run(
            ["gh", "api", "graphql", "--hostname", "github.com", "--input", "-"],
            input=json.dumps({"query": query, "variables": variables}),
            capture_output=True,
            text=True,
            shell=False,
            check=False,
            timeout=allowed_timeout,
        )
    except subprocess.TimeoutExpired:
        if callable(timeout):
            timeout()  # Preserve an exhausted whole-snapshot deadline as its own outcome.
        raise SnapshotError("GitHub API request timed out.", code="api_error") from None
    except FileNotFoundError:
        raise SnapshotError("GitHub CLI is unavailable.", code="api_error") from None
    except OSError:
        raise SnapshotError("GitHub CLI request could not run.", code="api_error") from None
    except UnicodeError:
        raise SnapshotError("GitHub API response was not valid UTF-8.", code="invalid_response") from None
    if result.returncode:
        # Classify known failures without reproducing GitHub CLI diagnostics.
        diagnostic = (result.stderr or "").casefold()
        if "rate limit" in diagnostic or "http 429" in diagnostic:
            raise SnapshotError("GitHub API rate limit reached.", code="rate_limited")
        auth_indicators = ("http 401", "bad credentials", "required scopes", "saml enforcement")
        if result.returncode == 4 or any(value in diagnostic for value in auth_indicators):
            raise SnapshotError("GitHub CLI needs authentication.", code="auth_required")
        raise SnapshotError("GitHub API request failed.", code="api_error")
    try:
        response = json.loads(result.stdout)
    except (ValueError, TypeError):
        raise SnapshotError("GitHub API response was not valid JSON.", code="invalid_response") from None
    response = _object(response, "response")
    if "errors" in response:
        if not isinstance(response["errors"], list):
            _invalid("GitHub returned an invalid GraphQL error shape.")
        if response["errors"]:
            raise SnapshotError("GitHub GraphQL response reported errors.", code="api_error")
    return _object(response.get("data"), "response data")


def _pull_request(data, repo, number, expected_head=None):
    repository = _object(data.get("repository"), "repository")
    name = _string(repository.get("nameWithOwner"), "repository identity")
    if name.lower() != repo.lower():
        _invalid("GitHub returned a different base repository.")
    pr = _object(repository.get("pullRequest"), "pull request")
    if _integer(pr.get("number"), "PR number", minimum=1) != number:
        _invalid("GitHub returned a different pull request.")
    head = _sha(pr.get("headRefOid"), "PR head")
    if expected_head is not None:
        _same_head(head, expected_head)
    return pr


def _metadata(pr, repo, number):
    _fields(pr, ("url", "baseRefName", "state", "isDraft", "mergeable", "mergeStateStatus", "reviewDecision"), "PR metadata")
    url = _string(pr.get("url"), "PR URL")
    try:
        parsed_url = urlsplit(url)
    except ValueError:
        _invalid("GitHub returned an invalid PR URL.")
    if (
        parsed_url.scheme != "https"
        or parsed_url.netloc.lower() != "github.com"
        or parsed_url.path.lower() != "/" + repo.lower() + "/pull/" + str(number)
        or parsed_url.query
        or parsed_url.fragment
    ):
        _invalid("GitHub returned a different PR URL.")
    return {
        "repository": repo,
        "number": number,
        "url": url,
        "head": _sha(pr.get("headRefOid"), "PR head"),
        "base": _string(pr.get("baseRefName"), "base branch"),
        "state": _enum(pr.get("state"), "PR state", {"OPEN", "MERGED", "CLOSED"}),
        "is_draft": _boolean(pr.get("isDraft"), "draft state"),
        "mergeable": _enum(pr.get("mergeable"), "mergeability", {"MERGEABLE", "CONFLICTING", "UNKNOWN"}),
        "merge_state_status": _enum(
            pr.get("mergeStateStatus"),
            "merge status",
            {"BEHIND", "BLOCKED", "CLEAN", "DIRTY", "DRAFT", "HAS_HOOKS", "UNKNOWN", "UNSTABLE"},
        ),
        "review_decision": _enum(
            pr.get("reviewDecision"), "review decision", {"APPROVED", "CHANGES_REQUESTED", "REVIEW_REQUIRED"}, nullable=True
        ),
    }


def _checks_connection(pr, head):
    commits = _object(pr.get("commits"), "PR commits").get("nodes")
    if not isinstance(commits, list) or len(commits) != 1:
        _invalid("GitHub did not return the current PR commit.")
    commit = _object(_object(commits[0], "PR commit node").get("commit"), "PR commit")
    _same_head(_sha(commit.get("oid"), "commit head"), head)
    if "statusCheckRollup" not in commit:
        _invalid("GitHub omitted the check rollup.")
    if commit["statusCheckRollup"] is None:
        return None
    return _object(_object(commit["statusCheckRollup"], "check rollup").get("contexts"), "check contexts")


def _collect_pages(connection, key, next_page):
    """Validate and collect one connection, including an embedded first page."""
    items = []
    ids = set()
    cursors = set()
    total = None
    for _page in range(MAX_PAGES):
        connection = _object(connection, key + " connection")
        page_total = _integer(connection.get("totalCount"), key + " total count")
        if total is None:
            total = page_total
        elif total != page_total:
            _invalid("GitHub evidence changed during pagination.")
        nodes = connection.get("nodes")
        if not isinstance(nodes, list) or len(nodes) > PAGE_SIZE:
            _invalid("GitHub returned invalid connection nodes.")
        page_info = _object(connection.get("pageInfo"), "page information")
        has_next = _boolean(page_info.get("hasNextPage"), "pagination state")
        if "endCursor" not in page_info:
            _invalid("GitHub omitted a pagination cursor.")
        end_cursor = _string(page_info["endCursor"], "pagination cursor", nullable=True)
        if nodes or has_next:
            if end_cursor is None or end_cursor in cursors:
                _invalid("GitHub returned a missing or repeated pagination cursor.")
            cursors.add(end_cursor)
        if has_next and not nodes:
            _invalid("GitHub returned an empty incomplete page.")
        for node in nodes:
            node = _object(node, key + " node")
            identity = _string(node.get("id"), key + " ID")
            if identity in ids:
                _invalid("GitHub repeated an evidence ID during pagination.")
            ids.add(identity)
            items.append(node)
        if len(items) > total or (has_next and len(items) >= total):
            _invalid("GitHub pagination disagrees with its total count.")
        if not has_next:
            if len(items) != total:
                _invalid("GitHub returned incomplete evidence.")
            return items
        if _page + 1 < MAX_PAGES:
            connection = next_page(end_cursor)
    _invalid("GitHub pagination exceeded the safety limit.")


def _read_connection(query, key, variables, repo, number, head, timeout):
    """Page one PR connection with its own independent cursor and head guard."""
    def page(cursor):
        data = _request(query, dict(variables, cursor=cursor), timeout)
        pr = _pull_request(data, repo, number, head)
        return _checks_connection(pr, head) if key == "checks" else pr.get(key)

    first_page = page(None)
    if first_page is None and key == "checks":
        return [], False
    return _collect_pages(first_page, key, page), True


def _read_thread_comments(thread, variables, repo, number, head, timeout):
    """Finish a thread's embedded comment page without re-reading other threads."""
    identity = _string(thread.get("id"), "thread ID")

    def page(cursor):
        data = _request(_THREAD_COMMENTS_QUERY, dict(variables, threadId=identity, cursor=cursor), timeout)
        _pull_request(data, repo, number, head)
        node = _object(data.get("node"), "review thread node")
        if node.get("__typename") != "PullRequestReviewThread" or node.get("id") != identity:
            _invalid("GitHub returned a different review thread.")
        bound_pr = _object(node.get("pullRequest"), "thread pull request")
        bound_repo = _object(bound_pr.get("repository"), "thread repository")
        _pull_request({"repository": dict(bound_repo, pullRequest=bound_pr)}, repo, number, head)
        return node.get("comments")

    return _collect_pages(thread.get("comments"), "thread replies", page)


def _actor(value, field):
    if value is None:
        return None
    return _string(_object(value, field).get("login"), field + " login")


def _normalize_check(node, head):
    kind = _enum(node.get("__typename"), "check kind", {"CheckRun", "StatusContext"})
    common = {
        "id": _string(node.get("id"), "check ID"),
        "kind": kind,
        "head": head,
        "is_required": _boolean(node.get("isRequired"), "required-check state"),
    }
    if kind == "CheckRun":
        _fields(node, ("conclusion", "title", "summary", "text", "detailsUrl", "databaseId", "startedAt", "completedAt"), "check run")
        suite = _fields(node.get("checkSuite"), ("id", "commit", "app"), "check suite")
        commit = _object(suite.get("commit"), "check commit")
        _same_head(_sha(commit.get("oid"), "check head"), head)
        app = suite.get("app")
        if app is not None:
            app = _object(app, "check provider")
        title = _string(node.get("title"), "check title", nullable=True, empty=True)
        summary = _string(node.get("summary"), "check summary", nullable=True, empty=True)
        body = _string(node.get("text"), "check text", nullable=True, empty=True)
        common.update(
            name=_string(node.get("name"), "check name"),
            status=_enum(node.get("status"), "check status", {"QUEUED", "IN_PROGRESS", "COMPLETED", "WAITING", "PENDING", "REQUESTED"}),
            conclusion=_enum(
                node.get("conclusion"), "check conclusion",
                {"ACTION_REQUIRED", "CANCELLED", "FAILURE", "NEUTRAL", "SKIPPED", "STALE", "STARTUP_FAILURE", "SUCCESS", "TIMED_OUT"},
                nullable=True,
            ),
            description="\n\n".join(part for part in (title, summary, body) if part),
            details_url=_string(node.get("detailsUrl"), "check details URL", nullable=True, empty=True),
            provider=_string(app.get("slug"), "provider slug") if app is not None else None,
            provider_id=_string(app.get("id"), "provider ID") if app is not None else None,
            check_suite_id=_string(suite.get("id"), "check suite ID"),
            database_id=_integer(node.get("databaseId"), "check database ID", nullable=True, minimum=1),
            started_at=_timestamp(node.get("startedAt"), "check start", nullable=True),
            completed_at=_timestamp(node.get("completedAt"), "check completion", nullable=True),
            title=title,
            summary=summary,
            text=body,
        )
    else:
        _fields(node, ("description", "targetUrl", "createdAt", "creator"), "status context")
        commit = _object(node.get("commit"), "status commit")
        _same_head(_sha(commit.get("oid"), "status head"), head)
        state = _enum(node.get("state"), "status state", {"ERROR", "EXPECTED", "FAILURE", "PENDING", "SUCCESS"})
        terminal = state in {"ERROR", "FAILURE", "SUCCESS"}
        common.update(
            name=_string(node.get("context"), "status name"),
            status="COMPLETED" if terminal else "PENDING",
            conclusion=state if terminal else None,
            state=state,
            description=_string(node.get("description"), "status description", nullable=True, empty=True) or "",
            details_url=_string(node.get("targetUrl"), "status details URL", nullable=True, empty=True),
            provider=_actor(node.get("creator"), "status creator"),
            provider_id=None,
            check_suite_id=None,
            database_id=None,
            created_at=_timestamp(node.get("createdAt"), "status creation"),
        )
    return common


def _normalize_review(node):
    _fields(node, ("author", "commit", "submittedAt", "body", "url"), "review")
    commit = node.get("commit")
    return {
        "id": _string(node.get("id"), "review ID"),
        "author": _actor(node.get("author"), "review author"),
        "state": _enum(node.get("state"), "review state", {"PENDING", "COMMENTED", "APPROVED", "CHANGES_REQUESTED", "DISMISSED"}),
        "head": _sha(_object(commit, "review commit").get("oid"), "review head") if commit is not None else None,
        "submitted_at": _timestamp(node.get("submittedAt"), "review submission", nullable=True),
        "body": _string(node.get("body"), "review body", empty=True),
        "url": _string(node.get("url"), "review URL"),
    }


def _normalize_comment(node, *, head_bound):
    _fields(node, ("author", "body", "url", "createdAt", "updatedAt"), "comment")
    head = None
    if head_bound:
        _fields(node, ("commit",), "review reply")
        commit = node.get("commit")
        if commit is not None:
            head = _sha(_object(commit, "reply commit").get("oid"), "reply head")
    # Conversation comments and review replies do not submit a review. In
    # particular, body text saying APPROVED never creates approval evidence.
    return {
        "id": _string(node.get("id"), "comment ID"),
        "author": _actor(node.get("author"), "comment author"),
        "body": _string(node.get("body"), "comment body", empty=True),
        "url": _string(node.get("url"), "comment URL"),
        "created_at": _timestamp(node.get("createdAt"), "comment creation"),
        "updated_at": _timestamp(node.get("updatedAt"), "comment update"),
        "head": head,
    }


def _normalize_thread(node):
    _fields(node, ("line",), "review thread")
    return {
        "id": _string(node.get("id"), "thread ID"),
        "is_resolved": _boolean(node.get("isResolved"), "thread resolution"),
        "is_outdated": _boolean(node.get("isOutdated"), "thread age"),
        "path": _string(node.get("path"), "thread path"),
        "line": _integer(node.get("line"), "thread line", nullable=True, minimum=1),
    }


def _fetch(repo, number, request_timeout, overall_timeout, *, discussion_only):
    """Fetch checks, reviews and full discussion for an explicit base repo and PR.

    Every page and the final metadata read must refer to the baseline head.
    Distinct check IDs retain provider, suite and attempt evidence; readiness
    and latest-attempt policy belong to the caller. A null check rollup is
    unavailable evidence, represented by ``checks_available=False``. PR
    conversation comments are explicitly head-unbound; only submitted reviews
    can supply reviewer approval evidence. Thread replies retain their own
    nullable commit binding, including replies on outdated or resolved threads.
    The overall monotonic deadline includes every page and nested reply read.
    """
    if not isinstance(repo, str) or not _REPOSITORY.fullmatch(repo) or repo.split("/")[-1] in {".", ".."}:
        raise ValueError("Repository must be an explicit GitHub owner/repo.")
    if type(number) is not int or number <= 0 or number > 2147483647:
        raise ValueError("PR number must be a positive GraphQL integer.")
    try:
        valid_timeout = (
            not isinstance(request_timeout, bool)
            and isinstance(request_timeout, (int, float))
            and math.isfinite(request_timeout)
            and request_timeout > 0
        )
    except OverflowError:
        valid_timeout = False
    if not valid_timeout:
        raise ValueError("Request timeout must be a positive finite number.")
    try:
        valid_overall = type(overall_timeout) in (int, float) and math.isfinite(overall_timeout) and overall_timeout > 0
    except OverflowError:
        valid_overall = False
    if not valid_overall:
        raise ValueError("Overall timeout must be a positive finite number.")
    deadline = time.monotonic() + overall_timeout
    per_request_limit = request_timeout

    def remaining_timeout():
        remaining = deadline - time.monotonic()
        if remaining <= 0:
            raise SnapshotError("GitHub snapshot deadline expired.", code="snapshot_deadline")
        return min(per_request_limit, remaining)

    request_timeout = remaining_timeout
    owner, name = repo.split("/")
    variables = {"owner": owner, "name": name, "number": number}
    pr = _pull_request(_request(_METADATA_QUERY, variables, request_timeout), repo, number)
    baseline = _metadata(pr, repo, number)
    head = baseline["head"]
    if not discussion_only:
        checks, checks_available = _read_connection(
            _CHECKS_QUERY, "checks", variables, repo, number, head, request_timeout,
        )
    reviews, _ = _read_connection(_REVIEWS_QUERY, "reviews", variables, repo, number, head, request_timeout)
    comments, _ = _read_connection(_COMMENTS_QUERY, "comments", variables, repo, number, head, request_timeout)
    threads, _ = _read_connection(_THREADS_QUERY, "reviewThreads", variables, repo, number, head, request_timeout)
    for thread in threads:
        replies = _read_thread_comments(thread, variables, repo, number, head, request_timeout)
        thread["comments"] = {"nodes": replies}
    final_pr = _pull_request(_request(_METADATA_QUERY, variables, request_timeout), repo, number, head)
    snapshot = _metadata(final_pr, repo, number)
    normalized_reviews = [_normalize_review(node) for node in reviews]
    normalized_comments = [_normalize_comment(node, head_bound=False) for node in comments]
    normalized_threads = []
    for node in threads:
        normalized = _normalize_thread(node)
        normalized["comments"] = [
            _normalize_comment(reply, head_bound=True) for reply in node["comments"]["nodes"]
        ]
        normalized_threads.append(normalized)

    if discussion_only:
        return {
            "pull_request": {
                "number": number, "url": snapshot["url"],
                "title": _string(final_pr.get("title"), "PR title", empty=True),
                "state": snapshot["state"], "owner": owner, "repo": name,
                "head": head, "baseRefName": snapshot["base"],
            },
            "conversation_comments": comments,
            "reviews": reviews,
            "review_threads": threads,
        }
    normalized_checks = [_normalize_check(node, head) for node in checks]
    snapshot.update(
        checks=normalized_checks,
        checks_available=checks_available,
        reviews=normalized_reviews,
        comments=normalized_comments,
        threads=normalized_threads,
        observed_at=datetime.datetime.now(datetime.timezone.utc).isoformat(timespec="seconds").replace("+00:00", "Z"),
    )
    return snapshot


def parse_pr_url(url):
    """Return the base repository and PR number from a canonical GitHub URL."""
    match = re.fullmatch(r"https://github\.com/([^/]+/[^/]+)/pull/(\d+)(?:[/?#].*)?", url)
    if not match:
        raise ValueError("Expected a GitHub pull request URL.")
    repo, number = match.groups()
    return repo, int(number)


def fetch_snapshot(repo, number, request_timeout=30, *, overall_timeout=120):
    """Return validated checks, reviews and discussion bound to the observed PR head."""
    return _fetch(repo, number, request_timeout, overall_timeout, discussion_only=False)


def fetch_discussion(repo, number, request_timeout=30, *, overall_timeout=120):
    """Return all discussion in GitHub field format without requiring check access."""
    return _fetch(repo, number, request_timeout, overall_timeout, discussion_only=True)


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("pr_url", help="Canonical GitHub pull request URL")
    args = parser.parse_args()
    try:
        repo, number = parse_pr_url(args.pr_url)
        print(json.dumps(fetch_snapshot(repo, number), indent=2))
    except (SnapshotError, ValueError) as error:
        parser.exit(1, f"GitHub snapshot unavailable: {error}\n")
