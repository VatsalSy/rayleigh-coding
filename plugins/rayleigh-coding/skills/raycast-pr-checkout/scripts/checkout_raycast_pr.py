#!/usr/bin/env python3
"""Checkout a Raycast extension PR for local review without running npm."""

from __future__ import annotations

import argparse
import json
import re
import shutil
import subprocess
import sys
from pathlib import Path

RAYCAST_REPO = "raycast/extensions"
DEFAULT_FORK_URL = os.environ.get('RAYCAST_FORK_URL', 'git@github.com:OWNER/raycast-extensions.git')
DEFAULT_UPSTREAM_URL = "https://github.com/raycast/extensions.git"

def run_cmd(cmd: list[str], cwd: Path | None = None, capture: bool = False) -> str:
    result = subprocess.run(
        cmd,
        cwd=str(cwd) if cwd else None,
        text=True,
        capture_output=capture,
        check=False,
    )
    if result.returncode != 0:
        stderr = (result.stderr or "").strip()
        stdout = (result.stdout or "").strip()
        details = stderr or stdout or f"Command failed: {' '.join(cmd)}"
        raise RuntimeError(details)
    return (result.stdout or "").strip() if capture else ""

def require_bin(binary: str) -> None:
    if shutil.which(binary) is None:
        raise RuntimeError(f"Missing required binary: {binary}")

def parse_pr_number(value: str) -> int:
    text = value.strip()
    if text.isdigit():
        return int(text)
    match = re.search(r"github\.com/raycast/extensions/pull/(\d+)", text)
    if not match:
        raise RuntimeError(
            "Provide a Raycast PR URL like "
            "https://github.com/raycast/extensions/pull/25509 or a PR number."
        )
    return int(match.group(1))

def get_pr_data(pr_number: int) -> dict:
    output = run_cmd(
        [
            "gh",
            "pr",
            "view",
            str(pr_number),
            "--repo",
            RAYCAST_REPO,
            "--json",
            "number,headRefName,url,files",
        ],
        capture=True,
    )
    try:
        return json.loads(output)
    except json.JSONDecodeError as exc:
        raise RuntimeError(f"Failed to parse gh JSON output: {exc}") from exc

def detect_extension(pr_data: dict, override_name: str | None) -> str:
    if override_name:
        return override_name
    files = pr_data.get("files", [])
    names: set[str] = set()
    for file_entry in files:
        path = file_entry.get("path", "")
        match = re.match(r"extensions/([^/]+)/", path)
        if match:
            names.add(match.group(1))
    if not names:
        raise RuntimeError(
            "No changed file under extensions/<name>/ was found. "
            "Use --extension-name to set it manually."
        )
    if len(names) > 1:
        joined = ", ".join(sorted(names))
        raise RuntimeError(
            f"PR touches multiple extensions ({joined}). "
            "Use --extension-name to select one."
        )
    return next(iter(names))

def resolve_dest_dir(dest_dir: str | None, pr_number: int) -> Path:
    if dest_dir:
        return Path(dest_dir).expanduser().resolve()
    return Path.cwd() / f"raycast-extensions-pr-{pr_number}"

def checkout_pr(
    pr_number: int,
    extension_name: str,
    fork_url: str,
    upstream_url: str,
    dest_dir: Path,
    local_branch: str,
    dry_run: bool,
) -> Path:
    commands = [
        ["git", "clone", "-n", "--depth=1", "--filter=tree:0", fork_url, str(dest_dir)],
        ["git", "remote", "add", "upstream", upstream_url],
        ["git", "fetch", "--depth=1", "upstream", f"pull/{pr_number}/head:{local_branch}"],
        ["git", "sparse-checkout", "init", "--no-cone"],
        ["git", "sparse-checkout", "set", f"extensions/{extension_name}"],
        ["git", "checkout", local_branch],
    ]

    if dry_run:
        print("Dry run; commands to execute:")
        print()
        for command in commands:
            print(" ".join(command))
        return dest_dir / "extensions" / extension_name

    if dest_dir.exists() and any(dest_dir.iterdir()):
        raise RuntimeError(
            f"Destination exists and is not empty: {dest_dir}. "
            "Use --dest-dir with a new/empty directory."
        )
    dest_dir.parent.mkdir(parents=True, exist_ok=True)

    run_cmd(commands[0])
    repo_dir = dest_dir
    for command in commands[1:]:
        run_cmd(command, cwd=repo_dir)

    return repo_dir / "extensions" / extension_name

def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Checkout a Raycast extension PR for review with sparse checkout.",
    )
    parser.add_argument("pr", help="Raycast PR URL or PR number")
    parser.add_argument(
        "--fork-url",
        default=DEFAULT_FORK_URL,
        help=f"Fork clone URL (default: {DEFAULT_FORK_URL})",
    )
    parser.add_argument(
        "--upstream-url",
        default=DEFAULT_UPSTREAM_URL,
        help=f"Upstream URL for PR fetch (default: {DEFAULT_UPSTREAM_URL})",
    )
    parser.add_argument(
        "--dest-dir",
        help="Directory to clone into (default: ./raycast-extensions-pr-<PR>)",
    )
    parser.add_argument(
        "--local-branch",
        help="Local branch name for fetched PR (default: pr-<PR>)",
    )
    parser.add_argument(
        "--extension-name",
        help="Override extension name if detection from changed files is ambiguous",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Print git commands without executing",
    )
    return parser

def main() -> int:
    parser = build_parser()
    args = parser.parse_args()

    try:
        require_bin("git")
        require_bin("gh")
        pr_number = parse_pr_number(args.pr)
        pr_data = get_pr_data(pr_number)
        extension_name = detect_extension(pr_data, args.extension_name)
        local_branch = args.local_branch or f"pr-{pr_number}"
        dest_dir = resolve_dest_dir(args.dest_dir, pr_number)

        extension_dir = checkout_pr(
            pr_number=pr_number,
            extension_name=extension_name,
            fork_url=args.fork_url,
            upstream_url=args.upstream_url,
            dest_dir=dest_dir,
            local_branch=local_branch,
            dry_run=args.dry_run,
        )

        print()
        print(f"PR: {pr_data.get('url', f'https://github.com/raycast/extensions/pull/{pr_number}')}")
        print(f"Local branch: {local_branch}")
        print(f"Extension: {extension_name}")
        print(f"Extension path: {extension_dir}")
        print()
        print("Checkout complete.")
        print("You can now run:")
        print(f'cd "{extension_dir}"')
        print("npm install && npm run dev")
        return 0
    except RuntimeError as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 1

if __name__ == "__main__":
    raise SystemExit(main())
