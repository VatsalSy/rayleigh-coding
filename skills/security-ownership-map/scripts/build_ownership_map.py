#!/usr/bin/env python3
"""Build a security ownership map from git history."""

from __future__ import annotations

import argparse
import csv
import datetime as dt
import fnmatch
import json
import math
import os
import re
import subprocess
import sys
from collections import defaultdict
from pathlib import Path
from typing import Iterable

DEFAULT_SENSITIVE_RULES: list[tuple[str, str, float]] = [
    ("**/auth/**", "auth", 1.0),
    ("**/oauth/**", "auth", 1.0),
    ("**/rbac/**", "auth", 1.0),
    ("**/session/**", "auth", 1.0),
    ("**/token/**", "auth", 1.0),
    ("**/crypto/**", "crypto", 1.0),
    ("**/tls/**", "crypto", 1.0),
    ("**/ssl/**", "crypto", 1.0),
    ("**/secrets/**", "secrets", 1.0),
    ("**/keys/**", "secrets", 1.0),
    ("**/*.pem", "secrets", 1.0),
    ("**/*.key", "secrets", 1.0),
    ("**/*.p12", "secrets", 1.0),
    ("**/*.pfx", "secrets", 1.0),
    ("**/iam/**", "auth", 1.0),
    ("**/sso/**", "auth", 1.0),
]

DEFAULT_AUTHOR_EXCLUDE_REGEXES = [
    "dependabot",
]

DEFAULT_COCHANGE_EXCLUDES = [
    "**/Cargo.lock",
    "**/Cargo.toml",
    "**/package-lock.json",
    "**/yarn.lock",
    "**/pnpm-lock.yaml",
    "**/go.sum",
    "**/go.mod",
    "**/Gemfile.lock",
    "**/Pipfile.lock",
    "**/poetry.lock",
    "**/composer.lock",
    "**/.github/**",
    "**/.gitignore",
    "**/.gitattributes",
    "**/.gitmodules",
    "**/.editorconfig",
    "**/.vscode/**",
    "**/.idea/**",
]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Build ownership graphs and security ownership summaries from git history."
    )
    parser.add_argument("--repo", default=".", help="Path to the git repo (default: .)")
    parser.add_argument(
        "--out",
        default="ownership-map-out",
        help="Output directory for graph artifacts",
    )
    parser.add_argument("--since", default=None, help="Limit git log to commits since date")
    parser.add_argument("--until", default=None, help="Limit git log to commits until date")
    parser.add_argument(
        "--identity",
        choices=("author", "committer"),
        default="author",
        help="Identity to attribute touches to",
    )
    parser.add_argument(
        "--date-field",
        choices=("author", "committer"),
        default="author",
        help="Date field to use for recency and bucketing",
    )
    parser.add_argument(
        "--include-merges",
        action="store_true",
        help="Include merge commits (excluded by default)",
    )
    parser.add_argument(
        "--half-life-days",
        type=float,
        default=180.0,
        help="Half life for recency weighting",
    )
    parser.add_argument(
        "--sensitive-config",
        default=None,
        help="CSV file with pattern,tag,weight for sensitive paths",
    )
    parser.add_argument(
        "--owner-threshold",
        type=float,
        default=0.5,
        help="Share threshold for hidden owner detection",
    )
    parser.add_argument(
        "--bus-factor-threshold",
        type=int,
        default=1,
        help="Bus factor threshold for hotspots",
    )
    parser.add_argument(
        "--stale-days",
        type=int,
        default=365,
        help="Days since last touch to consider stale",
    )
    parser.add_argument(
        "--min-touches",
        type=int,
        default=1,
        help="Minimum touches to keep an edge",
    )
    parser.add_argument(
        "--emit-commits",
        action="store_true",
        help="Write commit list to commits.jsonl",
    )
    parser.add_argument(
        "--author-exclude-regex",
        action="append",
        default=[],
        help="Regex for author name/email to exclude (repeatable)",
    )
    parser.add_argument(
        "--no-default-author-excludes",
        action="store_true",
        help="Disable default author excludes (dependabot)",
    )
    parser.add_argument(
        "--no-cochange",
        action="store_true",
        help="Disable co-change graph output",
    )
    parser.add_argument(
        "--cochange-max-files",
        type=int,
        default=50,
        help="Ignore commits touching more than this many files for co-change graph",
    )
    parser.add_argument(
        "--cochange-min-count",
        type=int,
        default=2,
        help="Minimum co-change count to keep file-file edge",
    )
    parser.add_argument(
        "--cochange-min-jaccard",
        type=float,
        default=0.05,
        help="Minimum Jaccard similarity to keep file-file edge",
    )
    parser.add_argument(
        "--cochange-exclude",
        action="append",
        default=[],
        help="Glob to exclude from co-change graph (repeatable)",
    )
    parser.add_argument(
        "--no-default-cochange-excludes",
        action="store_true",
        help="Disable default co-change excludes (lockfiles, .github, editor config)",
    )
    parser.add_argument(
        "--no-communities",
        dest="communities",
        action="store_false",
        help="Disable community detection (enabled by default, requires networkx)",
    )
    parser.add_argument(
        "--graphml",
        action="store_true",
        help="Emit ownership.graphml (requires networkx)",
    )
    parser.add_argument(
        "--max-community-files",
        type=int,
        default=50,
        help="Max files listed per community",
    )
    parser.add_argument(
        "--community-top-owners",
        type=int,
        default=5,
        help="Top maintainers saved per community",
    )
    parser.set_defaults(communities=True)
    return parser.parse_args()


def load_sensitive_rules(path: str | None) -> list[tuple[str, str, float]]:
    if not path:
        return list(DEFAULT_SENSITIVE_RULES)
    rules: list[tuple[str, str, float]] = []
    with open(path, "r", encoding="utf-8") as handle:
        for raw in handle:
            line = raw.strip()
            if not line or line.startswith("#"):
                continue
            parts = [part.strip() for part in line.split(",")]
            if not parts:
                continue
            pattern = parts[0]
            tag = parts[1] if len(parts) > 1 and parts[1] else "sensitive"
            weight = float(parts[2]) if len(parts) > 2 and parts[2] else 1.0
            rules.append((pattern, tag, weight))
    return rules


def parse_date(value: str) -> dt.datetime:
    parsed = dt.datetime.fromisoformat(value)
    if parsed.tzinfo is None:
        parsed = parsed.replace(tzinfo=dt.timezone.utc)
    return parsed


def offset_minutes(timestamp: dt.datetime) -> int | None:
    offset = timestamp.utcoffset()
    if offset is None:
        return None
    return int(offset.total_seconds() / 60)


def format_offset(minutes: int) -> str:
    sign = "+" if minutes >= 0 else "-"
    minutes = abs(minutes)
    return f"{sign}{minutes // 60:02d}:{minutes % 60:02d}"


def recency_weighted(now: dt.datetime, when: dt.datetime, half_life_days: float) -> float:
    if half_life_days <= 0:
        return 1.0
    age_days = max(0.0, (now - when).total_seconds() / 86400.0)
    return math.exp(-math.log(2) * age_days / half_life_days)


def match_sensitive(path: str, rules: Iterable[tuple[str, str, float]]) -> dict[str, float]:
    tags: dict[str, float] = defaultdict(float)
    posix = path.replace("\\", "/")
    for pattern, tag, weight in rules:
        patterns = [pattern]
        if pattern.startswith("**/"):
            patterns.append(pattern[3:])
        for candidate in patterns:
            if fnmatch.fnmatchcase(posix, candidate):
                tags[tag] += weight
                break
    return tags


def matches_glob(path: str, pattern: str) -> bool:
    posix = path.replace("\\", "/")
    patterns = [pattern]
    if pattern.startswith("**/"):
        patterns.append(pattern[3:])
    return any(fnmatch.fnmatchcase(posix, candidate) for candidate in patterns)


def is_excluded(path: str, patterns: Iterable[str]) -> bool:
    return any(matches_glob(path, pattern) for pattern in patterns)


def author_excluded(name: str, email: str, patterns: Iterable[re.Pattern[str]]) -> bool:
    if not patterns:
        return False
    haystack = f"{name} {email}".strip()
    return any(pattern.search(haystack) for pattern in patterns)


def compute_community_owners(
    community_files: Iterable[str],
    people: dict[str, dict[str, object]],
    file_people_touches: dict[str, dict[str, int]],
    file_people_recency: dict[str, dict[str, float]],
    file_people_sensitive: dict[str, dict[str, float]],
    top_n: int,
) -> dict[str, object]:
    touches_by_person: dict[str, int] = defaultdict(int)
    recency_by_person: dict[str, float] = defaultdict(float)
    sensitive_by_person: dict[str, float] = defaultdict(float)

    for path in community_files:
        for person, touches in file_people_touches.get(path, {}).items():
            touches_by_person[person] += touches
        for person, recency in file_people_recency.get(path, {}).items():
            recency_by_person[person] += recency
        for person, weight in file_people_sensitive.get(path, {}).items():
            sensitive_by_person[person] += weight

    total_touches = sum(touches_by_person.values())
    total_recency = sum(recency_by_person.values())
    total_sensitive = sum(sensitive_by_person.values())

    ranked = sorted(touches_by_person.items(), key=lambda item: item[1], reverse=True)
    owners = []
    for person_id, touches in ranked[:top_n]:
        recency = recency_by_person.get(person_id, 0.0)
        sensitive = sensitive_by_person.get(person_id, 0.0)
        owners.append(
            {
                "person_id": person_id,
                "name": people.get(person_id, {}).get("name", person_id),
                "touches": touches,
                "touch_share": round(touches / total_touches, 4) if total_touches else 0.0,
                "recency_share": round(recency / total_recency, 4) if total_recency else 0.0,
