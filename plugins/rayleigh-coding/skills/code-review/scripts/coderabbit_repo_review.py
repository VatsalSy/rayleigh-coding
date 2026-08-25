#!/usr/bin/env python3
"""Thin public CodeRabbit CLI wrapper for rayleigh-coding.

This is intentionally small. It does not implement private org-routing
receipts, cadence locks, or secret-diff redaction. Those belong in a private
guard if needed.

Organisation hint:
  export CODERABBIT_ORG=<org>
  export CODERABBIT_REQUIRE_ORG=1  # refuse when unset on private repos

Examples:
  python3 coderabbit_repo_review.py -- --base main
  python3 coderabbit_repo_review.py --uncommitted -- --base HEAD
"""
from __future__ import annotations

import argparse
import os
import re
import shutil
import subprocess
import sys
from urllib.parse import urlparse


def parse_github_remote(raw: str) -> tuple[str, str] | None:
    raw = raw.strip()
    if not raw:
        return None
    if raw.startswith("git@"):
        # git@github.com:owner/repo.git
        if "github.com:" not in raw:
            return None
        path = raw.split(":", 1)[1]
        parts = path.split("/")
        if len(parts) < 2:
            return None
        owner, repo = parts[0], parts[1]
        return owner, repo[:-4] if repo.endswith(".git") else repo
    parsed = urlparse(raw)
    host = (parsed.hostname or "").lower()
    if host not in {"github.com", "www.github.com"}:
        return None
    parts = [p for p in parsed.path.split("/") if p]
    if len(parts) < 2:
        return None
    owner, repo = parts[0], parts[1]
    return owner, repo[:-4] if repo.endswith(".git") else repo


def remote_owner() -> str | None:
    try:
        raw = subprocess.check_output(
            ["git", "remote", "get-url", "origin"], text=True
        ).strip()
    except (subprocess.CalledProcessError, FileNotFoundError):
        return None
    parsed = parse_github_remote(raw)
    return parsed[0] if parsed else None


def resolve_org() -> str | None:
    env = os.environ.get("CODERABBIT_ORG")
    if env:
        return env
    owner = remote_owner()
    if os.environ.get("CODERABBIT_REQUIRE_ORG") == "1" and not env:
        print(
            "CODERABBIT_REQUIRE_ORG=1 but CODERABBIT_ORG is unset.",
            file=sys.stderr,
        )
        sys.exit(20)
    return owner


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Thin CodeRabbit review wrapper (public)"
    )
    parser.add_argument("--uncommitted", action="store_true")
    parser.add_argument(
        "--switch-org",
        action="store_true",
        help="Accepted for compatibility; org comes from env/remote",
    )
    parser.add_argument("--base", default="main")
    parser.add_argument("--light", action="store_true")
    parser.add_argument("--follow-up", action="store_true")
    args, passthrough = parser.parse_known_args(argv)

    if passthrough and passthrough[0] == "--":
        passthrough = passthrough[1:]

    if shutil.which("coderabbit") is None:
        print(
            "coderabbit CLI not found. Install from https://www.coderabbit.ai/cli",
            file=sys.stderr,
        )
        return 127

    org = resolve_org()
    if org:
        print(f"Using CodeRabbit organisation hint: {org}")

    cmd = ["coderabbit", "review", "--plain"]
    if args.uncommitted:
        cmd += ["--base", args.base]
    else:
        cmd += ["--base", args.base]
    if args.light:
        # Best-effort; older CLIs may ignore unknown flags after --plain path.
        pass
    cmd += passthrough

    # Refuse obviously secret-looking CLI args.
    joined = " ".join(cmd)
    if re.search(r"(api[_-]?key|token|password|secret)=", joined, re.I):
        print("Refusing to invoke CodeRabbit with credential-like arguments.", file=sys.stderr)
        return 30

    print("Running:", " ".join(cmd))
    try:
        return subprocess.call(cmd)
    except OSError as exc:
        print(f"Failed to run coderabbit: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
