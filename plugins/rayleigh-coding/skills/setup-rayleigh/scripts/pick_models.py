#!/usr/bin/env python3
"""Map detected Cursor Task slugs to rayleigh-coding categories.

Categories stay stable. Concrete slugs are the current Cursor mapping:

- default: latest Cursor Grok family
- executor: latest Composer family
- wise-owl: latest Opus family at *high* only (not max, not extra-high)

Aliases ``auto`` and ``inherit-parent`` mean: omit Task ``model``.
Unknown or disallowed families are never assigned.
"""
from __future__ import annotations

import argparse
import json
import re
import sys

CATEGORIES = ("default", "executor", "wise-owl")
ALIASES = frozenset({"auto", "inherit-parent", "inherit"})
FORBIDDEN = re.compile(
    r"(?i)(?:^|-)(?:fable|sonnet|sol|luna|terra|muse|gemini|gpt)(?:-|$)"
)
GROK = re.compile(r"(?i)(?:^|-)(?:cursor-)?grok-")
COMPOSER = re.compile(r"(?i)(?:^|-)composer-")
OPUS = re.compile(r"(?i)(?:^|-)(?:claude-)?opus-")

RULE_HEADER = """---
description: rayleigh-coding model choices (category mapping; overrides skill defaults)
alwaysApply: true
---
# Categories stay stable. Slugs are the current Cursor mapping.
# `auto` / `inherit-parent`: omit Task `model` (child follows the parent chat).
"""


def _tokens(slug: str) -> str:
    return f"-{slug.lower().strip()}-"


def is_alias(slug: str) -> bool:
    return slug.strip().lower() in ALIASES


def is_fast(slug: str) -> bool:
    return bool(re.search(r"(?i)(?:^|-)fast(?:-|$)", slug))


def version_tuple(slug: str) -> tuple[int, ...]:
    nums = tuple(int(part) for part in re.findall(r"\d+", slug))
    return nums or (0,)


def version_sort_key(slug: str) -> tuple[int, ...]:
    nums = version_tuple(slug)
    padded = nums + (0, 0, 0, 0)
    return tuple(-part for part in padded[:4])


def effort_rank(slug: str) -> int:
    padded = _tokens(slug)
    if "-xhigh-" in padded or "-extra-high-" in padded or "-extrahigh-" in padded:
        return 3
    if "-max-" in padded:
        return 4
    if "-high-" in padded:
        return 2
    if "-medium-" in padded or "-mid-" in padded:
        return 1
    if "-low-" in padded or "-light-" in padded:
        return 0
    return -1


def family_of(slug: str) -> str | None:
    if is_alias(slug) or FORBIDDEN.search(_tokens(slug)):
        return None
    if GROK.search(slug):
        return "default"
    if COMPOSER.search(slug):
        return "executor"
    if OPUS.search(slug):
        return "wise-owl"
    return None


def wise_owl_eligible(slug: str) -> bool:
    return family_of(slug) == "wise-owl" and effort_rank(slug) == 2


def _pick_one(slugs: list[str], key) -> str | None:
    if not slugs:
        return None
    return sorted(slugs, key=key)[0]


def pick_mapping(detected: list[str]) -> dict[str, str]:
    real = [slug.strip() for slug in detected if slug.strip() and not is_alias(slug)]
    grok = [slug for slug in real if family_of(slug) == "default"]
    composer = [slug for slug in real if family_of(slug) == "executor"]
    opus = [slug for slug in real if wise_owl_eligible(slug)]
    return {
        "default": _pick_one(
            grok,
            key=lambda slug: (version_sort_key(slug), -effort_rank(slug), is_fast(slug), slug),
        )
        or "auto",
        "executor": _pick_one(
            composer,
            key=lambda slug: (version_sort_key(slug), is_fast(slug), slug),
        )
        or "auto",
        "wise-owl": _pick_one(
            opus,
            key=lambda slug: (
                version_sort_key(slug),
                0 if "thinking" in slug.lower() else 1,
                is_fast(slug),
                slug,
            ),
        )
        or "auto",
    }


def auto_mapping() -> dict[str, str]:
    return {name: "auto" for name in CATEGORIES}


def format_lines(mapping: dict[str, str]) -> str:
    return "".join(f"{name}: {mapping[name]}\n" for name in CATEGORIES)


def format_rule(mapping: dict[str, str]) -> str:
    return RULE_HEADER + format_lines(mapping)


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Pick default / executor / wise-owl slugs from Task detections."
    )
    parser.add_argument(
        "slugs",
        nargs="*",
        help="Model slugs the Task tool accepts in this session",
    )
    parser.add_argument(
        "--policy",
        choices=("ensemble", "auto"),
        default="ensemble",
        help="ensemble picks allowlisted slugs; auto writes inherit-parent aliases",
    )
    parser.add_argument(
        "--format",
        choices=("lines", "rule", "json"),
        default="lines",
        help="lines (default), full rule file, or JSON",
    )
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    mapping = auto_mapping() if args.policy == "auto" else pick_mapping(args.slugs)
    if args.format == "json":
        sys.stdout.write(json.dumps(mapping, indent=2) + "\n")
    elif args.format == "rule":
        sys.stdout.write(format_rule(mapping))
    else:
        sys.stdout.write(format_lines(mapping))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
