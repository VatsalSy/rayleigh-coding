#!/usr/bin/env python3
"""Build a lightweight ownership map from git history.

Public simplified entrypoint. For Neo4j export and advanced graphs, extend
locally. This script prints path -> likely authors from `git shortlog`.
"""
from __future__ import annotations

import argparse
import subprocess
from collections import defaultdict
from pathlib import Path


def shortlog(path: Path) -> dict[str, list[tuple[int, str]]]:
    out = subprocess.check_output(
        ["git", "-C", str(path), "shortlog", "-sn", "--all"], text=True
    )
    authors = []
    for line in out.splitlines():
        line = line.strip()
        if not line:
            continue
        count, name = line.split("	", 1) if "	" in line else line.split(None, 1)
        authors.append((int(count), name))
    return {"repo": authors}


def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument("--repo", type=Path, default=Path("."))
    args = p.parse_args()
    data = shortlog(args.repo.resolve())
    for count, name in data["repo"][:30]:
        print(f"{count:6d}  {name}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
