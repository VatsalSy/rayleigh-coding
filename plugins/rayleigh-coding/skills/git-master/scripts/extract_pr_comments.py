#!/usr/bin/env python3
"""Extract all comments from a GitHub PR using the gh CLI.

Usage:
    python extract_pr_comments.py <PR_URL_or_NUMBER> [--repo OWNER/REPO]

Examples:
    python extract_pr_comments.py 42
    python extract_pr_comments.py https://github.com/owner/repo/pull/42
    python extract_pr_comments.py 42 --repo owner/repo
"""

import subprocess
import shutil
import json
import os
import sys
import re
import argparse
from dataclasses import dataclass
from typing import Optional

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


def run_gh_command(args: list[str]) -> dict | list:
    """Run a gh CLI command and return parsed JSON."""
    cmd = [GH_CMD] + args + ["--json"]
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        raise RuntimeError(f"gh command failed: {result.stderr}")
    return json.loads(result.stdout) if result.stdout.strip() else {}


def parse_pr_url(url_or_number: str) -> tuple[Optional[str], int]:
    """Parse PR URL or number, returning (repo, pr_number)."""
    # Direct number
    if url_or_number.isdigit():
        return None, int(url_or_number)
    
    # GitHub URL pattern
    match = re.match(r"https?://github\.com/([^/]+/[^/]+)/pull/(\d+)", url_or_number)
    if match:
        return match.group(1), int(match.group(2))
    
    raise ValueError(f"Invalid PR URL or number: {url_or_number}")


def get_issue_comments(pr_number: int, repo: Optional[str] = None) -> list[Comment]:
    """Get top-level PR comments (issue comments)."""
    cmd = ["api"]
    if repo:
        cmd.extend([f"repos/{repo}/issues/{pr_number}/comments"])
    else:
        cmd.extend([f"repos/{{owner}}/{{repo}}/issues/{pr_number}/comments"])
    
    # Use gh pr view to get issue comments instead
    view_cmd = ["pr", "view", str(pr_number), "--comments"]
    if repo:
        view_cmd.extend(["--repo", repo])
    view_cmd.append("--json")
    view_cmd.append("comments")
    
    result = subprocess.run([GH_CMD] + view_cmd, capture_output=True, text=True)
    if result.returncode != 0:
        return []
    
    data = json.loads(result.stdout) if result.stdout.strip() else {}
    comments = []
    for c in data.get("comments", []):
        comments.append(Comment(
            author=c.get("author", {}).get("login", "unknown"),
            body=c.get("body", ""),
            path=None,
            line=None,
            created_at=c.get("createdAt", ""),
            comment_type="issue",
            url=c.get("url")
        ))
    return comments


def get_review_comments(pr_number: int, repo: Optional[str] = None) -> list[Comment]:
    """Get inline review comments on specific code lines."""
    cmd = ["pr", "view", str(pr_number)]
    if repo:
        cmd.extend(["--repo", repo])
    cmd.extend(["--json", "reviews,reviewRequests"])
    
    result = subprocess.run([GH_CMD] + cmd, capture_output=True, text=True)
    if result.returncode != 0:
        return []

    data = json.loads(result.stdout) if result.stdout.strip() else {}
    comments = []

    # Get review-level comments
    for review in data.get("reviews", []):
        if review.get("body"):
            comments.append(Comment(
                author=review.get("author", {}).get("login", "unknown"),
                body=review.get("body", ""),
                path=None,
                line=None,
                created_at=review.get("submittedAt", ""),
                comment_type="review",
                state=review.get("state"),
                url=review.get("url")
            ))
    
    return comments


def get_review_threads(pr_number: int, repo: Optional[str] = None) -> list[Comment]:
    """Get review thread comments using GraphQL API."""
    repo_arg = f"-R {repo}" if repo else ""
    
    # GraphQL query to get review threads with comments
    query = """
    query($owner: String!, $repo: String!, $pr: Int!) {
      repository(owner: $owner, name: $repo) {
        pullRequest(number: $pr) {
          reviewThreads(first: 100) {
            nodes {
              isResolved
              path
              line
              comments(first: 100) {
                nodes {
                  author { login }
                  body
                  createdAt
                  url
                }
              }
            }
          }
        }
      }
    }
    """
    
    # Get repo info if not provided
    if not repo:
        result = subprocess.run(
            [GH_CMD, "repo", "view", "--json", "owner,name"],
            capture_output=True, text=True
        )
        if result.returncode != 0:
            return []
        repo_info = json.loads(result.stdout)
        owner = repo_info["owner"]["login"]
        name = repo_info["name"]
    else:
        owner, name = repo.split("/")
    
    cmd = [
        GH_CMD, "api", "graphql",
        "-f", f"query={query}",
        "-F", f"owner={owner}",
        "-F", f"repo={name}",
        "-F", f"pr={pr_number}"
    ]
    
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        return []
    
    data = json.loads(result.stdout)
    comments = []
    
    threads = (data.get("data", {})
               .get("repository", {})
               .get("pullRequest", {})
               .get("reviewThreads", {})
               .get("nodes", []))
    
    for thread in threads:
        is_resolved = thread.get("isResolved", False)
        path = thread.get("path")
        line = thread.get("line")
        
        for c in thread.get("comments", {}).get("nodes", []):
            comments.append(Comment(
                author=c.get("author", {}).get("login", "unknown"),
                body=c.get("body", ""),
                path=path,
                line=line,
                created_at=c.get("createdAt", ""),
                comment_type="review_thread",
                state="RESOLVED" if is_resolved else "OPEN",
                url=c.get("url")
            ))
    
    return comments


def get_pr_info(pr_number: int, repo: Optional[str] = None) -> dict:
    """Get basic PR information."""
    cmd = ["pr", "view", str(pr_number)]
    if repo:
        cmd.extend(["--repo", repo])
    cmd.extend(["--json", "title,author,url,state,baseRefName,headRefName,files"])
    
    result = subprocess.run([GH_CMD] + cmd, capture_output=True, text=True)
    if result.returncode != 0:
        raise RuntimeError(f"Failed to get PR info: {result.stderr}")
    
    return json.loads(result.stdout)


def format_output(pr_info: dict, comments: list[Comment]) -> str:
    """Format PR info and comments as structured markdown."""
    lines = []
    
    # PR Header
    lines.append(f"# PR #{pr_info.get('number', 'N/A')}: {pr_info.get('title', 'Unknown')}")
    lines.append(f"**Author:** {pr_info.get('author', {}).get('login', 'unknown')}")
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
    
    # Filter out empty comments and resolved threads (optionally)
    active_comments = [c for c in comments if c.body.strip()]
    
    if not active_comments:
        lines.append("## Comments")
        lines.append("*No comments found.*")
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
            state_emoji = {"APPROVED": "✅", "CHANGES_REQUESTED": "❌", "COMMENTED": "💬"}.get(c.state, "")
            lines.append(f"### {state_emoji} @{c.author} — {c.state}")
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
                status = "🔴" if c.state == "OPEN" else "✅"
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
    args = parser.parse_args()
    
    try:
        repo, pr_number = parse_pr_url(args.pr)
        repo = args.repo or repo
        
        # Gather all data
        pr_info = get_pr_info(pr_number, repo)
        pr_info["number"] = pr_number
        
        all_comments = []
        all_comments.extend(get_issue_comments(pr_number, repo))
        all_comments.extend(get_review_comments(pr_number, repo))
        all_comments.extend(get_review_threads(pr_number, repo))
        
        # Sort by date
        all_comments.sort(key=lambda c: c.created_at)
        
        output = format_output(pr_info, all_comments)
        
        if args.output:
            with open(args.output, "w") as f:
                f.write(output)
            print(f"Output written to {args.output}", file=sys.stderr)
        else:
            print(output)
            
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
