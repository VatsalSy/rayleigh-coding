#!/usr/bin/env python3
"""Public thin CodeRabbit CLI entrypoint for rayleigh-coding.

Prefer this over a heavy private org-routing guard. Organisation selection:

  export CODERABBIT_ORG=<org>
  # or let the remote owner decide for private repos
  export CODERABBIT_REQUIRE_ORG=1  # refuse private repos without CODERABBIT_ORG

Examples:
  python3 coderabbit_repo_review.py -- --base main
  python3 coderabbit_repo_review.py --uncommitted -- --base HEAD
"""
from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
from pathlib import Path
from urllib.parse import urlparse


def remote_owner() -> str | None:
    try:
        raw = subprocess.check_output(
            ["git", "remote", "get-url", "origin"], text=True
        ).strip()
    except subprocess.CalledProcessError:
        return None
    if raw.startswith("git@"):
        # git@github.com:owner/repo.git
        path = raw.split(":", 1)[-1]
        return path.split("/")[0]
    try:
        p = urlparse(raw)
        parts = [x for x in p.path.split("/") if x]
        return parts[0] if parts else None
    except Exception:
        return None


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
    parser = argparse.ArgumentParser(description="Thin CodeRabbit review wrapper")
    parser.add_argument("--uncommitted", action="store_true")
    parser.add_argument("--switch-org", action="store_true",
                        help="Accepted for compatibility; org comes from env/remote")
    parser.add_argument("--base", default="main")
    parser.add_argument("--light", action="store_true")
    parser.add_argument("--follow-up", action="store_true")
    args, passthrough = parser.parse_known_args(argv)

    if passthrough and passthrough[0] == "--":
        passthrough = passthrough[1:]

    org = resolve_org()
    if org:
        print(f"Using CodeRabbit organisation hint: {org}")

    cmd = ["coderabbit", "review", "--plain"]
    if args.uncommitted:
        # review working tree via base comparison still preferred
        cmd += ["--base", args.base]
    else:
        cmd += ["--base", args.base]
    if args.light:
        cmd += ["--light"]
    cmd += passthrough

    try:
        proc = subprocess.run(cmd, check=False)
    except FileNotFoundError:
        print(
            "coderabbit CLI not found. Install from https://www.coderabbit.ai/cli",
            file=sys.stderr,
        )
        return 3
    return proc.returncode


if __name__ == "__main__":
    raise SystemExit(main())
