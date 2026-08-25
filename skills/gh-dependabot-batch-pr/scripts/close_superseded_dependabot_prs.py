#!/usr/bin/env python3
"""
Close superseded Dependabot PRs after creating a combined batch PR.

Input is the normalized JSON produced by collect_dependabot_updates.py.
"""

from __future__ import annotations

import argparse
import json
import os
import shlex
import subprocess
import shutil
import sys
from collections import defaultdict
from pathlib import Path

GH_CMD = "gh"


def build_gh_base(repo: str | None) -> list[str]:
    base = [GH_CMD]
    if repo:
        base.extend(["-R", repo])
    return base


def run_gh(cmd: list[str]) -> subprocess.CompletedProcess[str]:
    return subprocess.run(cmd, capture_output=True, text=True, check=False)


def load_pr_map(updates_json: Path) -> dict[int, list[str]]:
    data = json.loads(updates_json.read_text())
    if not isinstance(data, list):
        raise ValueError("updates JSON must be a list of update objects.")

    pr_to_packages: dict[int, list[str]] = defaultdict(list)
    for row in data:
        if not isinstance(row, dict):
            continue
        pr_number = row.get("pr_number")
        package = str(row.get("package", "")).strip()
        if isinstance(pr_number, int) and pr_number > 0:
            if package:
                pr_to_packages[pr_number].append(package)
            else:
                pr_to_packages[pr_number].append("<unknown>")
    return dict(pr_to_packages)


def dedupe_preserve_order(values: list[str]) -> list[str]:
    seen = set()
    result: list[str] = []
    for value in values:
        if value in seen:
            continue
        seen.add(value)
        result.append(value)
    return result


def default_comment(batch_pr_url: str) -> str:
    return (
        "Superseded by batched dependency update PR: "
        f"{batch_pr_url}. Closing this individual Dependabot PR."
    )


def close_pr(
    pr_number: int,
    gh_base: list[str],
    comment: str,
    dry_run: bool,
    no_state_check: bool,
) -> tuple[bool, str]:
    close_cmd = gh_base + ["pr", "close", str(pr_number), "--comment", comment]

    if dry_run:
        return True, f"[dry-run] {shlex.join(close_cmd)}"

    if not no_state_check:
        view_cmd = gh_base + ["pr", "view", str(pr_number), "--json", "state,url,title"]
        view = run_gh(view_cmd)
        if view.returncode != 0:
            return False, (
                f"PR #{pr_number}: failed to inspect state: "
                f"{view.stderr.strip() or '<empty>'}"
            )
        payload = json.loads(view.stdout or "{}")
        state = str(payload.get("state", "")).upper()
        if state != "OPEN":
            return True, f"PR #{pr_number}: skipped (state={state or 'UNKNOWN'})"

    result = run_gh(close_cmd)
    if result.returncode != 0:
        return False, f"PR #{pr_number}: close failed: {result.stderr.strip() or '<empty>'}"
    return True, f"PR #{pr_number}: closed"


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Close superseded Dependabot PRs from a normalized updates JSON file."
    )
    parser.add_argument(
        "--updates-json",
        type=Path,
        required=True,
        help="Path to JSON produced by collect_dependabot_updates.py --write-json.",
    )
    parser.add_argument(
        "--batch-pr-url",
        help="URL of the new aggregate PR; used in default close comment.",
    )
    parser.add_argument(
        "--comment",
        help="Custom close comment. Overrides --batch-pr-url template.",
    )
    parser.add_argument(
        "--repo",
        help="Optional owner/repo for gh -R, for example OWNER/jarvis.",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Print planned close commands without changing PR state.",
    )
    parser.add_argument(
        "--no-state-check",
        action="store_true",
        help="Skip gh pr view state check before close.",
    )
    return parser


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()

    if not args.comment and not args.batch_pr_url:
        parser.error("Provide --batch-pr-url or --comment.")

    updates_json = args.updates_json.resolve()
    if not updates_json.exists():
        print(f"updates JSON not found: {updates_json}", file=sys.stderr)
        return 2

    pr_to_packages = load_pr_map(updates_json)
    if not pr_to_packages:
        print(
            "No PR numbers found in updates JSON. "
            "Re-collect with --from-gh so pr_number fields are populated.",
            file=sys.stderr,
        )
        return 3

    comment = args.comment or default_comment(args.batch_pr_url)
    gh_base = build_gh_base(args.repo)

    print(f"Found {len(pr_to_packages)} superseded Dependabot PR(s).")
    for pr, packages in sorted(pr_to_packages.items()):
        labels = ", ".join(dedupe_preserve_order(packages))
        print(f"- #{pr}: {labels}")

    failures = 0
    for pr in sorted(pr_to_packages.keys()):
        ok, message = close_pr(
            pr_number=pr,
            gh_base=gh_base,
            comment=comment,
            dry_run=args.dry_run,
            no_state_check=args.no_state_check,
        )
        print(message)
        if not ok:
            failures += 1

    if failures:
        print(f"Completed with {failures} failure(s).", file=sys.stderr)
        return 1

    print("Done.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
