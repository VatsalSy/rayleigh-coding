#!/usr/bin/env python3
"""Reject direct CodeRabbit review commands outside the guarded entry point."""

from __future__ import annotations

import argparse
from pathlib import Path
import re
import sys


COMMAND_RE = re.compile(
    r"(?:^\s*(?:(?:[-*+]|\d+\.)\s+)?|&&|\|\||[;|])\s*(?:\$\s*)?"
    r"(?:cr(?:\s+review)?|coderabbit\s+review)(?:\s|$)",
    re.I,
)
INLINE_RE = re.compile(r"`(?:cr(?:\s+review)?|coderabbit\s+review)(?:\s|`)", re.I)
FORBIDDEN_BOT_RE = re.compile(r"@coderabbitai\s+(?:rate\s+limit|review)", re.I)


def violations(root: Path) -> list[str]:
    found: list[str] = []
    for path in sorted(root.rglob("*.md")):
        relative = path.relative_to(root)
        for number, line in enumerate(
            path.read_text(encoding="utf-8", errors="replace").splitlines(), 1
        ):
            if COMMAND_RE.search(line) or INLINE_RE.search(line) or FORBIDDEN_BOT_RE.search(line):
                found.append(f"{relative}:{number}:{line.strip()}")
    return found


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("root", nargs="?", default=Path(__file__).resolve().parents[2])
    args = parser.parse_args()
    root = Path(args.root).resolve()
    if not root.is_dir():
        print(f"CodeRabbit policy scan root is not a directory: {root}", file=sys.stderr)
        return 2
    found = violations(root)
    if found:
        print("Direct CodeRabbit review or bot-control invocation found:", file=sys.stderr)
        print("\n".join(found), file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
