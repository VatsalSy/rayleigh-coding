"""GitHub snapshot regressions using a paginated fake gh GraphQL endpoint."""

import copy
import importlib.util
import json
from pathlib import Path
import runpy
import subprocess
import unittest
from unittest import mock


_SPEC = importlib.util.spec_from_file_location(
    "github_snapshot", Path(__file__).resolve().parents[1] / "scripts" / "github_snapshot.py"
)
snapshot = importlib.util.module_from_spec(_SPEC)
_SPEC.loader.exec_module(snapshot)

REPO = "BaseOwner/widget"
NUMBER = 17
HEAD = "a" * 40
OTHER_HEAD = "b" * 40
WHEN = "2026-10-07T12:00:00Z"


def metadata():
    return {
        "number": NUMBER,
        "title": "Portable change",
        "url": "https://github.com/" + REPO + "/pull/" + str(NUMBER),
        "headRefOid": HEAD,
        "baseRefName": "release/next",
        "state": "OPEN",
        "isDraft": False,
        "mergeable": "MERGEABLE",
        "mergeStateStatus": "CLEAN",
        "reviewDecision": "APPROVED",
    }


def check(index):
    return {
        "__typename": "CheckRun", "id": "check-" + str(index),
        "name": "validate-" + str(index), "status": "COMPLETED", "conclusion": "SUCCESS",
        "title": "Validation complete", "summary": "All assertions passed", "text": None,
        "detailsUrl": "https://github.com/" + REPO + "/actions/runs/1",
        "databaseId": index + 1, "startedAt": WHEN, "completedAt": WHEN,
        "isRequired": index % 2 == 0,
        "checkSuite": {"id": "suite-1", "commit": {"oid": HEAD}, "app": {"id": "app-1", "slug": "github-actions"}},
    }


def status(index=0):
    return {
        "__typename": "StatusContext", "id": "status-" + str(index),
        "context": "CodeRabbit", "state": "SUCCESS", "description": "Review rate limited",
        "targetUrl": "https://example.org/review", "createdAt": WHEN, "isRequired": False,
        "commit": {"oid": HEAD}, "creator": {"login": "coderabbitai"},
    }


def review(index):
    return {
        "id": "review-" + str(index), "author": {"login": "reviewer-" + str(index)},
        "state": "COMMENTED", "commit": {"oid": HEAD}, "submittedAt": WHEN,
        "body": "Guidance outside the diff: preserve the existing contract.",
        "url": "https://github.com/" + REPO + "/pull/17#pullrequestreview-" + str(index),
    }


def thread(index):
    return {
        "id": "thread-" + str(index), "isResolved": False, "isOutdated": index % 2 == 0,
        "path": "src/example.py", "line": index + 1,
        "comments": {"totalCount": 0, "nodes": [], "pageInfo": {"hasNextPage": False, "endCursor": None}},
    }


def comment(index):
    return {
        "id": "comment-" + str(index), "author": {"login": "reader-" + str(index)},
        "body": "A question in the PR conversation.",
        "url": "https://github.com/" + REPO + "/pull/17#issuecomment-" + str(index),
        "createdAt": WHEN, "updatedAt": WHEN,
    }


def reply(index):
    node = comment(index)
    node.update(id="reply-" + str(index), commit={"oid": HEAD})
    return node


class FakeGitHub:
    """Read-only fake with separate cursor namespaces and variable page sizes."""

    def __init__(self, checks=(), reviews=(), threads=(), *, comments=(), replies=None, page_sizes=None, mutate=None, rollup=True, cursor_factory=None):
        self.items = {"checks": list(checks), "reviews": list(reviews), "reviewThreads": list(threads), "comments": list(comments)}
        self.replies = dict(replies or {})
        self.page_sizes = dict(page_sizes or {})
        self.mutate = mutate
        self.rollup = rollup
        self.cursor_factory = cursor_factory
        self.calls = []
        self.offsets = {}
        self.metadata_reads = 0

    def page(self, namespace, items, cursor):
        offset = 0 if cursor is None else self.offsets[(namespace, cursor)]
        size = self.page_sizes.get(namespace, 100)
        nodes = copy.deepcopy(items[offset:offset + size])
        end_offset = offset + len(nodes)
        end_cursor = None
        if nodes:
            end_cursor = self.cursor_factory(namespace, end_offset) if self.cursor_factory else namespace + "-" + str(end_offset)
            self.offsets[(namespace, end_cursor)] = end_offset
        return {
            "totalCount": len(items), "nodes": nodes,
            "pageInfo": {"hasNextPage": end_offset < len(items), "endCursor": end_cursor},
        }

    def __call__(self, argv, **kwargs):
        if argv != ["gh", "api", "graphql", "--hostname", "github.com", "--input", "-"]:
            raise AssertionError("Only the fixed GitHub GraphQL argv is allowed")
        if kwargs.get("shell") is not False or kwargs.get("check") is not False:
            raise AssertionError("The transport must disable shell and implicit subprocess errors")
        if kwargs.get("capture_output") is not True or kwargs.get("text") is not True:
            raise AssertionError("The transport must capture JSON separately from CLI diagnostics")
        request = json.loads(kwargs["input"])
        query = request["query"]
        if "mutation" in query:
            raise AssertionError("No GitHub mutations are allowed")
        variables = request["variables"]
        if (variables["owner"], variables["name"], variables["number"]) != (*REPO.split("/"), NUMBER):
            raise AssertionError("Queries must stay bound to the explicit base repo and PR")
        if "SnapshotMetadata" in query:
            key = "metadata"
            self.metadata_reads += 1
            pr = metadata()
        else:
            key = "checks" if "SnapshotChecks" in query else "reviews" if "SnapshotReviews" in query else "threadComments" if "SnapshotThreadComments" in query else "comments" if "SnapshotComments" in query else "reviewThreads"
            pr = {"number": NUMBER, "headRefOid": HEAD}
            if key == "threadComments":
                identity = variables["threadId"]
                page = self.page(key + ":" + identity, self.replies[identity], variables["cursor"])
            else:
                page = self.page(key, self.items[key], variables["cursor"])
                if key == "checks":
                    pr["commits"] = {"nodes": [{"commit": {"oid": HEAD, "statusCheckRollup": {"contexts": page} if self.rollup else None}}]}
                else:
                    if key == "reviewThreads":
                        for node in page["nodes"]:
                            if node["id"] in self.replies:
                                node["comments"] = self.page("threadComments:" + node["id"], self.replies[node["id"]], None)
                    pr[key] = page
        result = {"data": {"repository": {"nameWithOwner": REPO, "pullRequest": pr}}}
        if key == "threadComments":
            result["data"]["node"] = {
                "__typename": "PullRequestReviewThread", "id": variables["threadId"],
                "pullRequest": dict(pr, repository={"nameWithOwner": REPO}), "comments": page,
            }
        self.calls.append((key, copy.deepcopy(variables), kwargs["timeout"]))
        if self.mutate:
            self.mutate(key, variables, result, self)
        return subprocess.CompletedProcess(argv, 0, stdout=json.dumps(result), stderr="")


def connection(response, key):
    if key == "threadComments":
        return response["data"]["node"]["comments"]
    pr = response["data"]["repository"]["pullRequest"]
    if key == "checks":
        return pr["commits"]["nodes"][0]["commit"]["statusCheckRollup"]["contexts"]
    return pr[key]


class SnapshotTests(unittest.TestCase):
    def fetch(self, api, **kwargs):
        with mock.patch.object(snapshot.subprocess, "run", side_effect=api):
            return snapshot.fetch_snapshot(REPO, NUMBER, **kwargs)

    def failure(self, api, code="invalid_response"):
        with self.assertRaises(snapshot.SnapshotError) as raised:
            self.fetch(api)
        self.assertEqual(raised.exception.code, code)
        return raised.exception

    def test_whole_snapshot_deadline_bounds_all_pages(self):
        api = FakeGitHub()
        with mock.patch.object(snapshot.time, "monotonic", side_effect=[0, 4, 11]):
            with self.assertRaises(snapshot.SnapshotError) as raised:
                self.fetch(api, request_timeout=30, overall_timeout=10)
        self.assertEqual(raised.exception.code, "snapshot_deadline")
        self.assertEqual(len(api.calls), 1)
        self.assertEqual(api.calls[0][2], 6)

    def test_invalid_overall_deadline_never_calls_github(self):
        for value in (True, 0, -1, float("nan"), float("inf"), 10 ** 400):
            with self.subTest(value=value), mock.patch.object(snapshot.subprocess, "run") as run:
                with self.assertRaises(ValueError):
                    snapshot.fetch_snapshot(REPO, NUMBER, overall_timeout=value)
                run.assert_not_called()

    def test_all_connections_exceed_100_and_finish_at_different_pages(self):
        api = FakeGitHub(
            [check(i) for i in range(201)], [review(i) for i in range(151)], [thread(i) for i in range(108)],
            page_sizes={"checks": 100, "reviews": 60, "reviewThreads": 99},
        )
        result = self.fetch(api, request_timeout=2.5)
        self.assertEqual([item["id"] for item in result["checks"]], ["check-" + str(i) for i in range(201)])
        self.assertEqual([item["id"] for item in result["reviews"]], ["review-" + str(i) for i in range(151)])
        self.assertEqual([item["id"] for item in result["threads"]], ["thread-" + str(i) for i in range(108)])
        self.assertEqual([call[0] for call in api.calls], ["metadata", "checks", "checks", "checks", "reviews", "reviews", "reviews", "comments", "reviewThreads", "reviewThreads", "metadata"])
        self.assertEqual([call[1].get("cursor") for call in api.calls if call[0] == "checks"], [None, "checks-100", "checks-200"])
        self.assertEqual([call[1].get("cursor") for call in api.calls if call[0] == "reviews"], [None, "reviews-60", "reviews-120"])
        self.assertEqual([call[1].get("cursor") for call in api.calls if call[0] == "reviewThreads"], [None, "reviewThreads-99"])
        self.assertTrue(all(call[2] == 2.5 for call in api.calls))
        self.assertTrue(result["checks_available"])
        self.assertEqual(result["head"], HEAD)
        self.assertTrue(result["observed_at"].endswith("Z"))

    def test_fork_pr_is_queried_by_explicit_base_repo(self):
        def add_fork(_key, _variables, response, _api):
            response["data"]["repository"]["pullRequest"]["headRepository"] = {"nameWithOwner": "Contributor/fork"}
        api = FakeGitHub(mutate=add_fork)
        result = self.fetch(api)
        self.assertEqual(result["repository"], REPO)
        self.assertEqual(result["base"], "release/next")
        self.assertTrue(all(call[1]["owner"] == "BaseOwner" for call in api.calls))

    def test_discussion_paginates_without_loading_checks(self):
        api = FakeGitHub([], [review(i) for i in range(102)], [thread(0)])
        with mock.patch.object(snapshot.subprocess, "run", side_effect=api):
            result = snapshot.fetch_discussion(REPO, NUMBER)
        self.assertEqual(snapshot.parse_pr_url(result["pull_request"]["url"]), (REPO, NUMBER))
        self.assertEqual(result["pull_request"]["head"], HEAD)
        self.assertEqual(result["pull_request"]["baseRefName"], "release/next")
        self.assertEqual(result["pull_request"]["title"], "Portable change")
        self.assertEqual(len(result["reviews"]), 102)
        self.assertEqual(len(result["review_threads"]), 1)
        self.assertEqual([key for key, _, _ in api.calls],
                         ["metadata", "reviews", "reviews", "comments", "reviewThreads", "metadata"])

    def test_known_cli_failures_keep_diagnostics_private(self):
        cases = (
            (4, "", "auth_required"),
            (1, "HTTP 401: Bad credentials", "auth_required"),
            (1, "The token is missing required scopes", "auth_required"),
            (1, "Protected by organisation SAML enforcement", "auth_required"),
            (1, "API rate limit exceeded", "rate_limited"),
            (1, "HTTP 429", "rate_limited"),
        )
        for exit_code, diagnostic, error_code in cases:
            with self.subTest(error_code=error_code, diagnostic=diagnostic):
                private_diagnostic = diagnostic + " unused fixture text"
                response = subprocess.CompletedProcess([], exit_code, stdout="", stderr=private_diagnostic)
                with mock.patch.object(snapshot.subprocess, "run", return_value=response):
                    with self.assertRaises(snapshot.SnapshotError) as raised:
                        snapshot.fetch_discussion(REPO, NUMBER)
                self.assertEqual(raised.exception.code, error_code)
                self.assertNotIn(private_diagnostic, str(raised.exception))

    def test_discussion_rejects_malformed_thread_resolution(self):
        for value in ("false", None, 0):
            with self.subTest(value=value):
                item = dict(thread(0), isResolved=value)
                api = FakeGitHub([], [], [item])
                with mock.patch.object(snapshot.subprocess, "run", side_effect=api):
                    with self.assertRaises(snapshot.SnapshotError):
                        snapshot.fetch_discussion(REPO, NUMBER)

    def test_triage_distinguishes_resolved_threads_and_failed_reads(self):
        script = Path(__file__).resolve().parents[2] / "gh-pr-triage/scripts/extract_pr_comments.py"
        triage = runpy.run_path(str(script))
        open_thread = thread(0)
        resolved_thread = dict(thread(1), isResolved=True)
        for index, item in enumerate((open_thread, resolved_thread)):
            item["comments"] = {"nodes": [comment(index)]}
        discussion = {
            "conversation_comments": [], "reviews": [],
            "review_threads": [open_thread, resolved_thread],
        }
        self.assertEqual([item.state for item in triage["collect_comments"](discussion)], ["OPEN"])
        self.assertEqual([item.state for item in triage["collect_comments"](discussion, True)],
                         ["OPEN", "RESOLVED"])

        def failed_read(*_args, **_kwargs):
            raise triage["SnapshotError"]("incomplete read", code="invalid_response")

        main = triage["main"]
        with mock.patch.dict(main.__globals__, {
            "get_pr_info": lambda *_: metadata(), "fetch_discussion": failed_read,
        }), mock.patch("sys.argv", [str(script), metadata()["url"]]), mock.patch("sys.stderr") as stderr:
            with self.assertRaises(SystemExit) as stopped:
                main()
        self.assertEqual(stopped.exception.code, 1)
        self.assertIn("incomplete read", "".join(str(call) for call in stderr.write.call_args_list))

    def test_check_provider_head_description_and_required_state_are_retained(self):
        item = check(0)
        item.update(title="Review complete", summary="Review rate limited", text="Try again later")
        result = self.fetch(FakeGitHub([item, status()]))
        action, bot = result["checks"]
        self.assertEqual((action["provider"], action["provider_id"], action["check_suite_id"], action["head"]), ("github-actions", "app-1", "suite-1", HEAD))
        self.assertTrue(action["is_required"])
        self.assertEqual(action["description"], "Review complete\n\nReview rate limited\n\nTry again later")
        self.assertEqual((bot["provider"], bot["kind"], bot["status"], bot["conclusion"]), ("coderabbitai", "StatusContext", "COMPLETED", "SUCCESS"))
        self.assertEqual(bot["description"], "Review rate limited")
        self.assertFalse(bot["is_required"])

    def test_distinct_attempts_and_same_name_different_providers_are_not_collapsed(self):
        attempts = [check(i) for i in range(3)]
        for item in attempts:
            item["name"] = "validate"
        attempts[1]["checkSuite"]["id"] = "suite-2"
        attempts[2]["checkSuite"]["app"] = {"id": "app-2", "slug": "another-provider"}
        result = self.fetch(FakeGitHub(attempts))
        self.assertEqual([item["database_id"] for item in result["checks"]], [1, 2, 3])
        self.assertEqual([item["id"] for item in result["checks"]], ["check-0", "check-1", "check-2"])

    def test_pending_statuses_and_missing_provider_do_not_become_success(self):
        for state in ("PENDING", "EXPECTED"):
            with self.subTest(state=state):
                item = status()
                item.update(state=state, creator=None, description=None, targetUrl=None)
                result = self.fetch(FakeGitHub([item]))["checks"][0]
                self.assertEqual(result["status"], "PENDING")
                self.assertIsNone(result["conclusion"])
                self.assertIsNone(result["provider"])
                self.assertEqual(result["description"], "")

    def test_null_rollup_differs_from_a_complete_empty_rollup(self):
        unavailable = self.fetch(FakeGitHub(reviews=[review(0)], threads=[thread(0)], rollup=False))
        empty = self.fetch(FakeGitHub())
        self.assertEqual(unavailable["checks"], [])
        self.assertFalse(unavailable["checks_available"])
        self.assertEqual(len(unavailable["reviews"]), 1)
        self.assertEqual(len(unavailable["threads"]), 1)
        self.assertEqual(empty["checks"], [])
        self.assertTrue(empty["checks_available"])

    def test_review_body_edits_and_outdated_unresolved_threads_are_retained(self):
        body = review(0)
        original = self.fetch(FakeGitHub(reviews=[body], threads=[thread(0)]))
        body["body"] = "Edited instructions in the same review."
        edited = self.fetch(FakeGitHub(reviews=[body]))
        self.assertEqual(original["reviews"][0]["id"], edited["reviews"][0]["id"])
        self.assertNotEqual(original["reviews"][0]["body"], edited["reviews"][0]["body"])
        self.assertEqual(edited["reviews"][0]["body"], body["body"])
        self.assertEqual((original["threads"][0]["is_resolved"], original["threads"][0]["is_outdated"]), (False, True))

    def test_deleted_review_author_pending_commit_and_outdated_line_can_be_null(self):
        pending = review(0)
        pending.update(author=None, commit=None, submittedAt=None, state="PENDING")
        outdated = thread(0)
        outdated["line"] = None
        result = self.fetch(FakeGitHub(reviews=[pending], threads=[outdated]))
        self.assertIsNone(result["reviews"][0]["author"])
        self.assertIsNone(result["reviews"][0]["head"])
        self.assertIsNone(result["reviews"][0]["submitted_at"])
        self.assertIsNone(result["threads"][0]["line"])

    def test_final_metadata_is_used_when_head_stays_the_same(self):
        def close(key, _variables, response, api):
            if key == "metadata" and api.metadata_reads == 2:
                pr = response["data"]["repository"]["pullRequest"]
                pr.update(state="MERGED", mergeStateStatus="UNKNOWN", reviewDecision=None)
        result = self.fetch(FakeGitHub(mutate=close))
        self.assertEqual((result["state"], result["merge_state_status"], result["review_decision"]), ("MERGED", "UNKNOWN", None))

    def test_head_change_on_each_collection_and_final_metadata_is_rejected(self):
        for target in ("checks", "reviews", "reviewThreads", "metadata"):
            with self.subTest(target=target):
                def move(key, variables, response, api):
                    if key == target and (api.metadata_reads == 2 if target == "metadata" else variables["cursor"] is not None):
                        response["data"]["repository"]["pullRequest"]["headRefOid"] = OTHER_HEAD
                self.failure(FakeGitHub([check(i) for i in range(101)], [review(i) for i in range(101)], [thread(i) for i in range(101)], mutate=move), "head_changed")

    def test_first_evidence_page_is_bound_to_the_baseline_head(self):
        def move(key, _variables, response, _api):
            if key == "checks":
                response["data"]["repository"]["pullRequest"]["headRefOid"] = OTHER_HEAD
        self.failure(FakeGitHub(mutate=move), "head_changed")

    def test_commit_and_check_evidence_must_match_the_current_pr_head(self):
        def move_commit(key, _variables, response, _api):
            if key == "checks":
                response["data"]["repository"]["pullRequest"]["commits"]["nodes"][0]["commit"]["oid"] = OTHER_HEAD
        self.failure(FakeGitHub(mutate=move_commit), "head_changed")
        item = check(0)
        item["checkSuite"]["commit"]["oid"] = OTHER_HEAD
        self.failure(FakeGitHub([item]), "head_changed")
        item = status()
        item["commit"]["oid"] = OTHER_HEAD
        self.failure(FakeGitHub([item]), "head_changed")

    def test_partial_graphql_errors_discard_all_response_data(self):
        def error(key, _variables, response, _api):
            if key == "reviews":
                response["errors"] = [{"message": "Private token and repository details"}]
        raised = self.failure(FakeGitHub(reviews=[review(0)], mutate=error), "api_error")
        self.assertNotIn("Private", str(raised))

    def test_cli_failures_and_timeouts_never_leak_diagnostics(self):
        failures = [
            subprocess.CompletedProcess([], 1, stdout="private response", stderr="Authorization: Bearer secret-value"),
            subprocess.TimeoutExpired(["gh"], 30, output="private response", stderr="secret-value"),
            FileNotFoundError("private executable path"),
            PermissionError("private executable path"),
        ]
        for failure in failures:
            with self.subTest(failure=type(failure).__name__):
                with mock.patch.object(snapshot.subprocess, "run", side_effect=failure if isinstance(failure, Exception) else None, return_value=failure):
                    with self.assertRaises(snapshot.SnapshotError) as raised:
                        snapshot.fetch_snapshot(REPO, NUMBER)
                self.assertEqual(raised.exception.code, "api_error")
                self.assertNotIn("private", str(raised.exception))
                self.assertNotIn("secret-value", str(raised.exception))

    def test_malformed_json_and_non_object_response_fail_closed(self):
        for stdout in ("not-json", "[]", "null", '{"data":null}', '{"errors":null,"data":{}}'):
            with self.subTest(stdout=stdout):
                with mock.patch.object(snapshot.subprocess, "run", return_value=subprocess.CompletedProcess([], 0, stdout=stdout, stderr="")):
                    with self.assertRaises(snapshot.SnapshotError) as raised:
                        snapshot.fetch_snapshot(REPO, NUMBER)
                self.assertEqual(raised.exception.code, "invalid_response")

    def test_null_or_missing_authority_shapes_fail_closed(self):
        for field in ("repository", "pullRequest", "headRefOid", "number", "url", "reviewDecision"):
            with self.subTest(field=field):
                def corrupt(key, _variables, response, _api):
                    if key != "metadata":
                        return
                    repository = response["data"]["repository"]
                    if field == "repository":
                        response["data"]["repository"] = None
                    elif field == "pullRequest":
                        repository["pullRequest"] = None
                    else:
                        repository["pullRequest"].pop(field)
                self.failure(FakeGitHub(mutate=corrupt))

    def test_null_or_missing_connections_are_not_empty_evidence(self):
        for key in ("checks", "reviews", "reviewThreads"):
            with self.subTest(key=key):
                def corrupt(actual, _variables, response, _api):
                    if actual != key:
                        return
                    pr = response["data"]["repository"]["pullRequest"]
                    if key == "checks":
                        pr["commits"]["nodes"][0]["commit"]["statusCheckRollup"]["contexts"] = None
                    else:
                        pr[key] = None
                self.failure(FakeGitHub(mutate=corrupt))

    def test_missing_rollup_and_missing_current_commit_are_rejected(self):
        for mode in ("rollup", "commit"):
            def corrupt(key, _variables, response, _api):
                if key == "checks":
                    commits = response["data"]["repository"]["pullRequest"]["commits"]["nodes"]
                    if mode == "rollup":
                        commits[0]["commit"].pop("statusCheckRollup")
                    else:
                        commits.clear()
            with self.subTest(mode=mode):
                self.failure(FakeGitHub(mutate=corrupt))

    def test_rollup_cannot_disappear_halfway_through_pagination(self):
        def disappear(key, variables, response, _api):
            if key == "checks" and variables["cursor"]:
                response["data"]["repository"]["pullRequest"]["commits"]["nodes"][0]["commit"]["statusCheckRollup"] = None
        self.failure(FakeGitHub([check(i) for i in range(101)], mutate=disappear))

    def test_missing_cursor_repeated_cursor_and_duplicate_ids_are_rejected(self):
        for mode in ("missing", "null", "cycle", "duplicate"):
            with self.subTest(mode=mode):
                def corrupt(key, variables, response, _api):
                    if key != "reviews":
                        return
                    page = connection(response, key)
                    if mode == "missing":
                        page["pageInfo"].pop("endCursor")
                    elif mode == "null":
                        page["pageInfo"]["endCursor"] = None
                    elif variables["cursor"]:
                        if mode == "cycle":
                            page["pageInfo"]["endCursor"] = "reviews-100"
                        else:
                            page["nodes"][0]["id"] = "review-0"
                self.failure(FakeGitHub(reviews=[review(i) for i in range(101)], mutate=corrupt))

    def test_incomplete_counts_empty_pages_and_total_changes_are_rejected(self):
        for mode in ("short", "empty", "changed", "overflow"):
            with self.subTest(mode=mode):
                def corrupt(key, variables, response, _api):
                    if key != "reviews":
                        return
                    page = connection(response, key)
                    if mode == "short":
                        page["pageInfo"]["hasNextPage"] = False
                    elif mode == "empty":
                        page["nodes"] = []
                    elif mode == "overflow":
                        page["totalCount"] = 1
                    elif variables["cursor"]:
                        page["totalCount"] += 1
                self.failure(FakeGitHub(reviews=[review(i) for i in range(101)], mutate=corrupt))

    def test_pagination_safety_limit_fails_without_returning_a_partial_snapshot(self):
        api = FakeGitHub(reviews=[review(i) for i in range(201)])
        with mock.patch.object(snapshot, "MAX_PAGES", 2):
            raised = self.failure(api)
        self.assertIn("safety limit", str(raised))
        self.assertEqual(len([call for call in api.calls if call[0] == "reviews"]), 2)
        self.assertEqual(api.metadata_reads, 1)

    def test_malformed_evidence_primitives_and_omitted_nullable_fields_fail(self):
        for kind, field, value in (
            ("checks", "isRequired", "false"), ("checks", "status", True),
            ("checks", "conclusion", []), ("checks", "summary", {}),
            ("checks", "startedAt", "yesterday"), ("checks", "databaseId", True),
            ("reviews", "body", []), ("reviews", "author", "reviewer"),
            ("reviews", "submittedAt", "2026-10-07T12:00:00"),
            ("reviewThreads", "isResolved", "true"), ("reviewThreads", "line", True),
            ("reviewThreads", "path", []),
        ):
            with self.subTest(kind=kind, field=field):
                node = check(0) if kind == "checks" else review(0) if kind == "reviews" else thread(0)
                node[field] = value
                self.failure(FakeGitHub(**{kind if kind != "reviewThreads" else "threads": [node]}))
        for kind, field in (("checks", "title"), ("checks", "conclusion"), ("reviews", "commit"), ("reviewThreads", "line")):
            with self.subTest(kind=kind, omitted=field):
                node = check(0) if kind == "checks" else review(0) if kind == "reviews" else thread(0)
                node.pop(field)
                self.failure(FakeGitHub(**{kind if kind != "reviewThreads" else "threads": [node]}))

    def test_different_base_repo_pr_number_or_url_is_rejected(self):
        for mode in ("repository", "number", "url", "malformed_url"):
            with self.subTest(mode=mode):
                def corrupt(key, _variables, response, _api):
                    if key == "metadata":
                        repo = response["data"]["repository"]
                        if mode == "repository":
                            repo["nameWithOwner"] = "Contributor/fork"
                        elif mode == "number":
                            repo["pullRequest"]["number"] = NUMBER + 1
                        else:
                            repo["pullRequest"]["url"] = "https://[" if mode == "malformed_url" else "https://github.com/Contributor/fork/pull/17"
                self.failure(FakeGitHub(mutate=corrupt))

    def test_opaque_cursor_is_passed_only_in_json_stdin(self):
        attack = 'cursor; $(touch /tmp/should-never-run) `echo secret`'
        api = FakeGitHub(reviews=[review(i) for i in range(101)], cursor_factory=lambda key, end: attack if key == "reviews" and end == 100 else key + "-" + str(end))
        self.fetch(api)
        self.assertEqual([call[1]["cursor"] for call in api.calls if call[0] == "reviews"], [None, attack])

    def test_page_101_conversation_and_replies_are_complete_with_independent_cursors(self):
        resolved = thread(0)
        resolved["isResolved"] = True
        api = FakeGitHub(
            threads=[resolved, thread(1), thread(2)], comments=[comment(i) for i in range(101)],
            replies={"thread-0": [reply(i) for i in range(201)], "thread-1": [reply(i + 201) for i in range(101)], "thread-2": [reply(302)]},
        )
        result = self.fetch(api)
        self.assertEqual([item["id"] for item in result["comments"]], ["comment-" + str(i) for i in range(101)])
        self.assertEqual([item["id"] for item in result["threads"][0]["comments"]], ["reply-" + str(i) for i in range(201)])
        self.assertEqual([item["id"] for item in result["threads"][1]["comments"]], ["reply-" + str(i) for i in range(201, 302)])
        self.assertEqual([item["id"] for item in result["threads"][2]["comments"]], ["reply-302"])
        self.assertTrue(result["threads"][0]["is_resolved"])
        self.assertEqual(
            [(call[1]["threadId"], call[1]["cursor"]) for call in api.calls if call[0] == "threadComments"],
            [("thread-0", "threadComments:thread-0-100"), ("thread-0", "threadComments:thread-0-200"), ("thread-1", "threadComments:thread-1-100")],
        )
        self.assertEqual([call[1]["cursor"] for call in api.calls if call[0] == "comments"], [None, "comments-100"])

    def test_comment_and_reply_body_edits_null_authors_and_commit_bindings_are_retained(self):
        conversation = comment(0)
        conversation.update(author=None, commit={"oid": HEAD})
        old_reply = reply(0)
        old_reply.update(author=None, commit={"oid": OTHER_HEAD})
        unbound_reply = reply(1)
        unbound_reply.update(commit=None, body="")
        before = self.fetch(FakeGitHub(threads=[thread(0)], comments=[conversation], replies={"thread-0": [old_reply, unbound_reply]}))
        conversation.update(body="Edited human conversation feedback", updatedAt="2026-10-07T12:01:00Z")
        old_reply.update(body="Edited reply on the old commit", updatedAt="2026-10-07T12:02:00Z")
        after = self.fetch(FakeGitHub(threads=[thread(0)], comments=[conversation], replies={"thread-0": [old_reply, unbound_reply]}))
        self.assertIsNone(after["comments"][0]["head"])
        self.assertIsNone(after["comments"][0]["author"])
        self.assertNotEqual(before["comments"][0]["body"], after["comments"][0]["body"])
        self.assertEqual(after["comments"][0]["updated_at"], "2026-10-07T12:01:00Z")
        self.assertEqual(after["threads"][0]["comments"][0]["head"], OTHER_HEAD)
        self.assertIsNone(after["threads"][0]["comments"][0]["author"])
        self.assertNotEqual(before["threads"][0]["comments"][0]["body"], after["threads"][0]["comments"][0]["body"])
        self.assertIsNone(after["threads"][0]["comments"][1]["head"])
        self.assertEqual(after["threads"][0]["comments"][1]["body"], "")

    def test_issue_comments_and_reply_text_never_submit_approval_reviews(self):
        conversation = comment(0)
        conversation.update(author={"login": "review-bot"}, body="APPROVED", state="APPROVED", commit={"oid": HEAD})
        body_reply = reply(0)
        body_reply.update(author={"login": "review-bot"}, body="APPROVED", state="APPROVED")
        def no_decision(key, _variables, response, _api):
            if key == "metadata":
                response["data"]["repository"]["pullRequest"]["reviewDecision"] = None
        result = self.fetch(FakeGitHub(comments=[conversation], threads=[thread(0)], replies={"thread-0": [body_reply]}, mutate=no_decision))
        self.assertEqual(result["reviews"], [])
        self.assertIsNone(result["review_decision"])
        self.assertIsNone(result["comments"][0]["head"])
        self.assertNotIn("state", result["comments"][0])
        self.assertNotIn("state", result["threads"][0]["comments"][0])

    def test_conversation_page_101_must_match_the_baseline_head(self):
        def drift(key, variables, response, _api):
            if key == "comments" and variables["cursor"]:
                response["data"]["repository"]["pullRequest"]["headRefOid"] = OTHER_HEAD
        self.failure(FakeGitHub(comments=[comment(i) for i in range(101)], mutate=drift), "head_changed")

    def test_nested_reply_page_guards_both_requested_pr_and_thread_pr_heads(self):
        for mode in ("requested_pr", "thread_pr"):
            with self.subTest(mode=mode):
                def drift(key, _variables, response, _api):
                    if key == "threadComments":
                        pr = response["data"]["repository"]["pullRequest"] if mode == "requested_pr" else response["data"]["node"]["pullRequest"]
                        pr["headRefOid"] = OTHER_HEAD
                self.failure(FakeGitHub(threads=[thread(0)], replies={"thread-0": [reply(i) for i in range(101)]}, mutate=drift), "head_changed")

    def test_nested_reply_node_identity_type_and_parent_binding_are_checked(self):
        for mode in ("null", "identity", "type", "repo", "number"):
            with self.subTest(mode=mode):
                def corrupt(key, _variables, response, _api):
                    if key != "threadComments":
                        return
                    node = response["data"]["node"]
                    if mode == "null":
                        response["data"]["node"] = None
                    elif mode == "identity":
                        node["id"] = "thread-99"
                    elif mode == "type":
                        node["__typename"] = "IssueComment"
                    elif mode == "repo":
                        node["pullRequest"]["repository"]["nameWithOwner"] = "Contributor/fork"
                    else:
                        node["pullRequest"]["number"] = NUMBER + 1
                self.failure(FakeGitHub(threads=[thread(0)], replies={"thread-0": [reply(i) for i in range(101)]}, mutate=corrupt))

    def test_nested_and_conversation_pagination_fail_closed_on_broken_evidence(self):
        for target in ("comments", "threadComments"):
            for mode in ("missing", "cycle", "duplicate", "count_drift", "null", "short"):
                with self.subTest(target=target, mode=mode):
                    def corrupt(key, _variables, response, _api):
                        if key != target:
                            return
                        page = connection(response, key)
                        if mode == "missing":
                            page["pageInfo"].pop("endCursor")
                        elif mode == "cycle":
                            page["pageInfo"]["endCursor"] = "comments-100" if target == "comments" else "threadComments:thread-0-100"
                        elif mode == "duplicate":
                            page["nodes"][0]["id"] = "comment-0" if target == "comments" else "reply-0"
                        elif mode == "count_drift":
                            page["totalCount"] += 1
                        elif mode == "null":
                            page["nodes"] = None
                        else:
                            page["nodes"] = []
                    def after_first(key, variables, response, api):
                        if variables.get("cursor"):
                            corrupt(key, variables, response, api)
                    self.failure(FakeGitHub(
                        comments=[comment(i) for i in range(101)], threads=[thread(0)],
                        replies={"thread-0": [reply(i) for i in range(101)]}, mutate=after_first,
                    ))

    def test_embedded_thread_reply_page_is_validated_even_without_extra_requests(self):
        for mode in ("missing", "null", "duplicate", "missing_cursor", "incomplete"):
            with self.subTest(mode=mode):
                def corrupt(key, _variables, response, _api):
                    if key != "reviewThreads":
                        return
                    node = connection(response, key)["nodes"][0]
                    if mode == "missing":
                        node.pop("comments")
                    elif mode == "null":
                        node["comments"] = None
                    elif mode == "duplicate":
                        node["comments"]["nodes"][1]["id"] = "reply-0"
                    elif mode == "missing_cursor":
                        node["comments"]["pageInfo"].pop("endCursor")
                    else:
                        node["comments"]["totalCount"] += 1
                api = FakeGitHub(threads=[thread(0)], replies={"thread-0": [reply(0), reply(1)]}, mutate=corrupt)
                self.failure(api)
                self.assertFalse(any(call[0] == "threadComments" for call in api.calls))

    def test_nested_partial_graphql_error_discards_discussion_snapshot(self):
        def error(key, _variables, response, _api):
            if key == "threadComments":
                response["errors"] = [{"message": "private reply details"}]
        raised = self.failure(FakeGitHub(threads=[thread(0)], replies={"thread-0": [reply(i) for i in range(101)]}, mutate=error), "api_error")
        self.assertNotIn("private reply", str(raised))

    def test_nested_reply_pagination_safety_limit_is_enforced(self):
        api = FakeGitHub(threads=[thread(0)], replies={"thread-0": [reply(i) for i in range(201)]})
        with mock.patch.object(snapshot, "MAX_PAGES", 2):
            raised = self.failure(api)
        self.assertIn("safety limit", str(raised))
        self.assertEqual(len([call for call in api.calls if call[0] == "threadComments"]), 1)

    def test_comment_and_reply_malformed_primitives_and_omitted_commit_fail(self):
        for nested in (False, True):
            for field, value in (("body", []), ("author", {}), ("createdAt", "yesterday"), ("updatedAt", None), ("url", [])):
                with self.subTest(nested=nested, field=field):
                    node = reply(0) if nested else comment(0)
                    node[field] = value
                    api = FakeGitHub(threads=[thread(0)], replies={"thread-0": [node]}) if nested else FakeGitHub(comments=[node])
                    self.failure(api)
        node = reply(0)
        node.pop("commit")
        self.failure(FakeGitHub(threads=[thread(0)], replies={"thread-0": [node]}))

    def test_invalid_bindings_and_timeouts_fail_before_any_cli_call(self):
        bad_repos = (None, "widget", "https://github.com/owner/widget", "owner/widget/extra", "-owner/widget", "owner/widget;echo", "owner/..", "owner/.", " owner/widget")
        bad_numbers = (0, -1, True, "17", 2147483648)
        bad_timeouts = (0, -1, True, "30", float("nan"), float("inf"), 10 ** 400)
        with mock.patch.object(snapshot.subprocess, "run") as run:
            for repo in bad_repos:
                with self.subTest(repo=repo), self.assertRaises(ValueError):
                    snapshot.fetch_snapshot(repo, NUMBER)
            for number in bad_numbers:
                with self.subTest(number=number), self.assertRaises(ValueError):
                    snapshot.fetch_snapshot(REPO, number)
            for timeout in bad_timeouts:
                with self.subTest(timeout=timeout), self.assertRaises(ValueError):
                    snapshot.fetch_snapshot(REPO, NUMBER, timeout)
        run.assert_not_called()


if __name__ == "__main__":
    unittest.main()
