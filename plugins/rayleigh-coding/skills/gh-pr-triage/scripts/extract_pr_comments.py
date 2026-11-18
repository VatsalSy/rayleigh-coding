#!/usr/bin/env python3
"""Extract all comments from a GitHub PR using the gh CLI.

Usage:
    python extract_pr_comments.py <PR_URL_or_NUMBER> [--repo OWNER/REPO]

Examples:
    python extract_pr_comments.py 42
    python extract_pr_comments.py https://github.com/owner/repo/pull/42
    python extract_pr_comments.py 42 --repo owner/repo
"""

import argparse
import json
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Optional

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "gh-babysit-pr" / "scripts"))
from github_snapshot import SnapshotError, fetch_discussion, parse_pr_url

GH_CMD = "gh"


@dataclass
class Comment:
    author: str
    body: str
    path: Optional[str]  # File path for review comments
    line: Optional[int]  # Line number for review comments
    created_at: str
    comment_type: str  # 'issue', 'review', or 'review_thread'
    state: Optional[str] = None  # For reviews: APPROVED, CHANGES_REQUESTED, COMMENTED
    url: Optional[str] = None


def author(node: dict) -> str:
    return (node.get("author") or {}).get("login") or "unknown"


def collect_comments(discussion: dict, include_resolved: bool = False) -> list[Comment]:
    comments = [
        Comment(author(node), node["body"], None, None, node["createdAt"], "issue", url=node["url"])
        for node in discussion["conversation_comments"]
    ]
    comments.extend(
        Comment(author(node), node["body"], None, None, node["submittedAt"] or "", "review",
                state=node["state"], url=node["url"])
        for node in discussion["reviews"]
    )
    for thread in discussion["review_threads"]:
        resolved = thread["isResolved"]
        if resolved and not include_resolved:
            continue
        comments.extend(
            Comment(author(node), node["body"], thread["path"], thread["line"], node["createdAt"],
                    "review_thread", state="RESOLVED" if resolved else "OPEN", url=node["url"])
            for node in thread["comments"]["nodes"]
        )
    return sorted(comments, key=lambda comment: comment.created_at)


def get_pr_info(pr_number: int, repo: Optional[str] = None) -> dict:
    """Get basic PR information."""
    cmd = ["pr", "view", str(pr_number)]
    if repo:
        cmd.extend(["--repo", repo])
    cmd.extend(["--json", "title,author,url,state,baseRefName,headRefName,headRefOid,files"])

    result = subprocess.run([GH_CMD] + cmd, capture_output=True, text=True, timeout=30)
    if result.returncode != 0:
        raise RuntimeError(f"Failed to get PR info: {result.stderr}")

    return json.loads(result.stdout)


def format_output(pr_info: dict, comments: list[Comment]) -> str:
    """Format PR info and comments as structured markdown."""
    lines = []

    # PR Header
    lines.append(f"# PR #{pr_info.get('number', 'N/A')}: {pr_info.get('title', 'Unknown')}")
    lines.append(f"**Author:** {author(pr_info)}")
    lines.append(f"**Branch:** {pr_info.get('headRefName', '?')} → {pr_info.get('baseRefName', '?')}")
    lines.append(f"**URL:** {pr_info.get('url', '')}")
    lines.append("")

    # Changed files
    files = pr_info.get("files", [])
    if files:
        lines.append("## Changed Files")
        for f in files:
            lines.append(f"- `{f.get('path', '')}` (+{f.get('additions', 0)}/-{f.get('deletions', 0)})")
        lines.append("")

    # Filter empty bodies after applying the thread visibility option.
    active_comments = [c for c in comments if c.body.strip()]

    if not active_comments:
        lines.append("## Comments")
        lines.append("*No comments matched the selected scope.*")
        return "\n".join(lines)

    # Group by type
    issue_comments = [c for c in active_comments if c.comment_type == "issue"]
    review_comments = [c for c in active_comments if c.comment_type == "review"]
    thread_comments = [c for c in active_comments if c.comment_type == "review_thread"]

    # Issue comments (general discussion)
    if issue_comments:
        lines.append("## General Comments")
        for c in issue_comments:
            lines.append(f"### @{c.author} ({c.created_at[:10]})")
            lines.append(c.body)
            if c.url:
                lines.append(f"[Link]({c.url})")
            lines.append("")

    # Review comments (approvals, change requests)
    if review_comments:
        lines.append("## Review Summaries")
        for c in review_comments:
            lines.append(f"### @{c.author} — {c.state}")
            lines.append(c.body)
            lines.append("")

    # Inline thread comments (code-specific)
    if thread_comments:
        lines.append("## Inline Code Comments")

        # Group by file
        by_file: dict[str, list[Comment]] = {}
        for c in thread_comments:
            key = c.path or "general"
            by_file.setdefault(key, []).append(c)

        for path, file_comments in sorted(by_file.items()):
            lines.append(f"### `{path}`")
            for c in sorted(file_comments, key=lambda x: x.line or 0):
                status = "OPEN" if c.state == "OPEN" else "RESOLVED"
                line_info = f"L{c.line}" if c.line else ""
                lines.append(f"#### {status} {line_info} @{c.author}")
                lines.append(c.body)
                if c.url:
                    lines.append(f"[Link]({c.url})")
                lines.append("")

    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(description="Extract PR comments using gh CLI")
    parser.add_argument("pr", help="PR number or URL")
    parser.add_argument("--repo", "-R", help="Repository in OWNER/REPO format")
    parser.add_argument("--output", "-o", help="Output file (default: stdout)")
    parser.add_argument("--include-resolved", action="store_true", help="Include resolved review threads")
    args = parser.parse_args()

    try:
        if args.pr.isdecimal():
            repo, pr_number = None, int(args.pr)
        else:
            repo, pr_number = parse_pr_url(args.pr)
        if repo and args.repo and repo.casefold() != args.repo.casefold():
            raise ValueError("PR URL and --repo identify different repositories.")
        pr_info = get_pr_info(pr_number, args.repo or repo)
        canonical_repo, canonical_number = parse_pr_url(pr_info["url"])
        if canonical_number != pr_number:
            raise RuntimeError("GitHub returned a different pull request.")
        discussion = fetch_discussion(canonical_repo, canonical_number)
        if discussion["pull_request"]["head"] != pr_info["headRefOid"]:
            raise RuntimeError("PR head changed during triage. Re-run against the current head.")
        pr_info["number"] = canonical_number
        output = format_output(pr_info, collect_comments(discussion, args.include_resolved))
        if args.output:
            with open(args.output, "w") as f:
                f.write(output)
            print(f"Output written to {args.output}", file=sys.stderr)
        else:
            print(output)

    except (OSError, RuntimeError, SnapshotError, subprocess.SubprocessError, ValueError, KeyError) as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
