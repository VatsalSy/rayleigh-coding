#!/usr/bin/env python3
"""Thin CodeRabbit CLI wrapper for rayleigh-coding.

Organisation hint:
  export CODERABBIT_ORG=<org>
  export CODERABBIT_REQUIRE_ORG=1  # refuse when unset

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

_CRED_FLAGS = {
    "--token",
    "--api-key",
    "--apikey",
    "--password",
    "--secret",
    "-t",
}


def parse_github_remote(raw: str) -> tuple[str, str] | None:
    raw = raw.strip()
    if not raw:
        return None
    if raw.startswith("git@"):
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


def _reject_credential_args(argv: list[str]) -> None:
    joined = " ".join(argv)
    if re.search(r"(api[_-]?key|token|password|secret)=", joined, re.I):
        print("Refusing credential-like name=value arguments.", file=sys.stderr)
        raise SystemExit(30)
    i = 0
    while i < len(argv):
        arg = argv[i]
        key = arg.split("=", 1)[0].lower() if arg.startswith("-") else arg.lower()
        if key in _CRED_FLAGS or key.lstrip("-") in {
            "token",
            "api-key",
            "apikey",
            "password",
            "secret",
        }:
            print("Refusing credential-like CLI arguments.", file=sys.stderr)
            raise SystemExit(30)
        i += 1


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Thin CodeRabbit review wrapper"
    )
    parser.add_argument("--uncommitted", action="store_true")
    parser.add_argument(
        "--switch-org",
        action="store_true",
        help="Accepted for compatibility; org comes from env/remote",
    )
    parser.add_argument("--base", default="main")
    parser.add_argument(
        "--light",
        action="store_true",
        help="Accepted for compatibility; forwarded when supported by the CLI",
    )
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
        # Make the resolved hint visible to the child process.
        os.environ["CODERABBIT_ORG"] = org
        print(f"Using CodeRabbit organisation hint: {org}")

    cmd = ["coderabbit", "review", "--plain", "--base", args.base]
    if args.light:
        cmd.append("--light")
    cmd += passthrough

    _reject_credential_args(cmd)

    print("Running:", " ".join(cmd))
    try:
        return subprocess.call(cmd)
    except OSError as exc:
        print(f"Failed to run coderabbit: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
