#!/usr/bin/env python3
"""
Collect and normalize Dependabot update proposals from:
- Open GitHub PRs (`gh pr list`)
- Pasted text files or stdin

Outputs either:
- JSON update payload for automation
- Human-readable table
- Batched npm install commands
"""

from __future__ import annotations

import argparse
import json
import os
import re
import subprocess
import shutil
import sys
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Iterable


TITLE_PATTERN = re.compile(
    r"\bbump\s+(?P<package>[^\s]+)\s+from\s+(?P<from>[^\s]+)\s+to\s+(?P<to>[^\s]+)",
    flags=re.IGNORECASE,
)

GH_CMD = "gh"


@dataclass
class Update:
    package: str
    from_version: str
    to_version: str
    scope: str  # dev | prod | unknown
    source_title: str
    pr_number: int | None = None
    pr_url: str | None = None


def infer_scope(raw_title: str) -> str:
    title = raw_title.lower()
    if "deps-dev" in title or "dev-dependencies" in title or "dev dependency" in title:
        return "dev"
    if "deps" in title:
        return "prod"
    return "unknown"


def normalize_version_key(version: str) -> tuple:
    raw = version.lstrip("vV")
    parts = re.split(r"[.\-+_]", raw)
    key: list[tuple[int, object]] = []
    for part in parts:
        if not part:
            continue
        if part.isdigit():
            key.append((0, int(part)))
        else:
            key.append((1, part.lower()))
    return tuple(key)


def parse_title(title: str, pr_number: int | None = None, pr_url: str | None = None) -> Update | None:
    match = TITLE_PATTERN.search(title)
    if not match:
        return None
    return Update(
        package=match.group("package").strip(),
        from_version=match.group("from").strip(),
        to_version=match.group("to").strip(),
        scope=infer_scope(title),
        source_title=title.strip(),
        pr_number=pr_number,
        pr_url=pr_url,
    )


def dedupe_updates(updates: Iterable[Update]) -> list[Update]:
    deduped: dict[str, Update] = {}
    for update in updates:
        current = deduped.get(update.package)
        if current is None:
            deduped[update.package] = update
            continue
        if normalize_version_key(update.to_version) > normalize_version_key(current.to_version):
            deduped[update.package] = update
    return sorted(deduped.values(), key=lambda item: item.package.lower())


def fetch_from_gh(limit: int) -> list[Update]:
    cmd = [
        GH_CMD,
        "pr",
        "list",
        "--state",
        "open",
        "--limit",
        str(limit),
        "--search",
        "author:app/dependabot",
        "--json",
        "number,title,url,author",
    ]
    result = subprocess.run(cmd, capture_output=True, text=True, check=False)
    if result.returncode != 0:
        raise RuntimeError(
            "Failed to query GitHub PRs with gh. "
            f"stderr: {result.stderr.strip() or '<empty>'}"
        )

    rows = json.loads(result.stdout or "[]")
    updates: list[Update] = []
    for row in rows:
        author = (row.get("author") or {}).get("login", "")
        title = row.get("title", "")
        if "dependabot" not in author and "bump " not in title.lower():
            continue
        parsed = parse_title(
            title=title,
            pr_number=row.get("number"),
            pr_url=row.get("url"),
        )
        if parsed is not None:
            updates.append(parsed)
    return updates


def parse_from_text_blob(text: str) -> list[Update]:
    updates: list[Update] = []
    for raw_line in text.splitlines():
        line = raw_line.strip()
        if not line:
            continue
        parsed = parse_title(line)
        if parsed is not None:
            updates.append(parsed)
    return updates


def make_npm_commands(updates: list[Update]) -> list[str]:
    prod = sorted(f"{item.package}@{item.to_version}" for item in updates if item.scope == "prod")
    dev = sorted(f"{item.package}@{item.to_version}" for item in updates if item.scope == "dev")
    unknown = sorted(f"{item.package}@{item.to_version}" for item in updates if item.scope == "unknown")

    commands: list[str] = []
    if prod:
        commands.append("npm install --save " + " ".join(prod))
    if dev:
        commands.append("npm install --save-dev " + " ".join(dev))
    if unknown:
        commands.append(
            "# Scope unknown for: " + ", ".join(item.split("@", 1)[0] for item in unknown)
        )
        commands.append("npm install " + " ".join(unknown))
    return commands


def render_table(updates: list[Update]) -> str:
    headers = ["package", "from", "to", "scope", "pr"]
    rows = []
    for item in updates:
        pr_ref = str(item.pr_number) if item.pr_number is not None else "-"
        rows.append([item.package, item.from_version, item.to_version, item.scope, pr_ref])

    widths = [len(h) for h in headers]
    for row in rows:
        for idx, cell in enumerate(row):
            widths[idx] = max(widths[idx], len(str(cell)))

    def fmt(row: list[str]) -> str:
        return "  ".join(str(cell).ljust(widths[idx]) for idx, cell in enumerate(row))

    output = [fmt(headers), fmt(["-" * width for width in widths])]
    output.extend(fmt([str(cell) for cell in row]) for row in rows)
    return "\n".join(output)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Collect Dependabot updates and prepare batched install commands."
    )
    source = parser.add_mutually_exclusive_group()
    source.add_argument(
        "--from-gh",
        action="store_true",
        help="Read open Dependabot PRs from the current repo via gh CLI.",
    )
    source.add_argument(
        "--input-file",
        type=Path,
        help="Read raw text (for example pasted PR titles) from file.",
    )
    source.add_argument(
        "--text",
        help="Read raw text directly from this argument.",
    )

    parser.add_argument(
        "--limit",
        type=int,
        default=100,
        help="Maximum PR count when using --from-gh (default: 100).",
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="Print normalized update list as JSON.",
    )
    parser.add_argument(
        "--npm-install",
        action="store_true",
        help="Print grouped npm install command(s).",
    )
    parser.add_argument(
        "--write-json",
        type=Path,
        help="Write normalized update list JSON to this path.",
    )
    return parser


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()

    if args.from_gh:
        updates = fetch_from_gh(limit=args.limit)
    elif args.input_file:
        updates = parse_from_text_blob(args.input_file.read_text())
    elif args.text:
        updates = parse_from_text_blob(args.text)
    else:
        if sys.stdin.isatty():
            parser.error("Provide one source: --from-gh, --input-file, --text, or stdin.")
        updates = parse_from_text_blob(sys.stdin.read())

    updates = dedupe_updates(updates)
    if not updates:
        print("No Dependabot bump lines found.", file=sys.stderr)
        return 2

    payload = [asdict(item) for item in updates]
    if args.write_json:
        args.write_json.parent.mkdir(parents=True, exist_ok=True)
        args.write_json.write_text(json.dumps(payload, indent=2) + "\n")

    if args.npm_install:
        commands = make_npm_commands(updates)
        if not commands:
            print("No npm commands generated.", file=sys.stderr)
            return 3
        print("\n".join(commands))
        return 0

    if args.json:
        print(json.dumps(payload, indent=2))
        return 0

    print(render_table(updates))
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except RuntimeError as exc:
        print(str(exc), file=sys.stderr)
        raise SystemExit(1)
