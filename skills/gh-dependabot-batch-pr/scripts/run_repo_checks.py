#!/usr/bin/env python3
"""
Run a standard Node repository quality gate based on available package.json scripts.

Default execution order:
lint -> lint:ci -> typecheck -> test -> test:ci -> test:unit -> test:integration -> build -> check -> verify
"""

from __future__ import annotations

import argparse
import json
import shlex
import subprocess
import sys
import time
from pathlib import Path


DEFAULT_ORDER = [
    "lint",
    "lint:ci",
    "typecheck",
    "test",
    "test:ci",
    "test:unit",
    "test:integration",
    "build",
    "check",
    "verify",
]

MANAGER_CANDIDATES = [
    ("pnpm-lock.yaml", "pnpm"),
    ("yarn.lock", "yarn"),
    ("bun.lockb", "bun"),
    ("bun.lock", "bun"),
    ("package-lock.json", "npm"),
]


def detect_manager(repo: Path, requested: str) -> str:
    if requested != "auto":
        return requested
    for lock_file, manager in MANAGER_CANDIDATES:
        if (repo / lock_file).exists():
            return manager
    return "npm"


def manager_command(manager: str, script_name: str) -> list[str]:
    if manager == "npm":
        return ["npm", "run", script_name]
    if manager == "pnpm":
        return ["pnpm", "run", script_name]
    if manager == "yarn":
        return ["yarn", script_name]
    if manager == "bun":
        return ["bun", "run", script_name]
    raise ValueError(f"Unsupported manager: {manager}")


def parse_list(values: list[str]) -> list[str]:
    items: list[str] = []
    for value in values:
        for token in value.split(","):
            token = token.strip()
            if token:
                items.append(token)
    return items


def load_scripts(repo: Path) -> dict[str, str]:
    package_json = repo / "package.json"
    if not package_json.exists():
        raise FileNotFoundError(f"package.json not found at {package_json}")
    data = json.loads(package_json.read_text())
    scripts = data.get("scripts")
    if not isinstance(scripts, dict):
        return {}
    return {str(name): str(cmd) for name, cmd in scripts.items()}


def select_scripts(
    available: dict[str, str],
    explicit_only: list[str],
    extra: list[str],
    skip: set[str],
) -> list[str]:
    if explicit_only:
        selected = explicit_only
    else:
        selected = DEFAULT_ORDER + extra

    ordered: list[str] = []
    seen = set()
    for item in selected:
        if item in seen:
            continue
        seen.add(item)
        if item in skip:
            continue
        if item not in available:
            continue
        ordered.append(item)
    return ordered


def run_checks(repo: Path, manager: str, scripts: list[str], continue_on_error: bool) -> int:
    failures = 0
    for script_name in scripts:
        cmd = manager_command(manager, script_name)
        started = time.time()
        print(f"\n==> {shlex.join(cmd)}")
        result = subprocess.run(cmd, cwd=repo, check=False)
        duration = time.time() - started
        if result.returncode == 0:
            print(f"[PASS] {script_name} ({duration:.1f}s)")
            continue

        failures += 1
        print(f"[FAIL] {script_name} ({duration:.1f}s) code={result.returncode}", file=sys.stderr)
        if not continue_on_error:
            return failures
    return failures


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Run a standard Node quality gate.")
    parser.add_argument(
        "--repo",
        type=Path,
        default=Path.cwd(),
        help="Repository path (default: current directory).",
    )
    parser.add_argument(
        "--manager",
        choices=["auto", "npm", "pnpm", "yarn", "bun"],
        default="auto",
        help="Package manager (default: auto).",
    )
    parser.add_argument(
        "--only",
        action="append",
        default=[],
        help="Comma-separated script names to run instead of defaults.",
    )
    parser.add_argument(
        "--extra",
        action="append",
        default=[],
        help="Comma-separated extra script names to append after defaults.",
    )
    parser.add_argument(
        "--skip",
        action="append",
        default=[],
        help="Comma-separated script names to skip.",
    )
    parser.add_argument(
        "--list",
        action="store_true",
        help="List resolved scripts and exit.",
    )
    parser.add_argument(
        "--continue-on-error",
        action="store_true",
        help="Run all selected checks even if one fails.",
    )
    parser.add_argument(
        "--require-scripts",
        action="store_true",
        help="Fail when no matching scripts are found.",
    )
    return parser


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()
    repo = args.repo.resolve()

    scripts = load_scripts(repo)
    manager = detect_manager(repo, args.manager)

    only = parse_list(args.only)
    extra = parse_list(args.extra)
    skip = set(parse_list(args.skip))

    selected = select_scripts(
        available=scripts,
        explicit_only=only,
        extra=extra,
        skip=skip,
    )

    if args.list:
        print(f"manager={manager}")
        if not selected:
            print("scripts=<none>")
            return 0
        for item in selected:
            print(item)
        return 0

    if not selected:
        message = "No matching package.json scripts found for requested quality gate."
        if args.require_scripts:
            print(message, file=sys.stderr)
            return 2
        print(message)
        return 0

    print(f"Detected manager: {manager}")
    print(f"Scripts to run: {', '.join(selected)}")
    failures = run_checks(
        repo=repo,
        manager=manager,
        scripts=selected,
        continue_on_error=args.continue_on_error,
    )
    if failures:
        print(f"\nQuality gate failed ({failures} failing step(s)).", file=sys.stderr)
        return 1

    print("\nQuality gate passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
