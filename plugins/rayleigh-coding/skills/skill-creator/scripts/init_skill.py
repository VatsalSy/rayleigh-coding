#!/usr/bin/env python3
"""
Initialize a new OpenClaw/AgentSkills skill scaffold.

Usage:
    init_skill.py <skill-name> [--path <skills-root>] [--resources scripts,references,assets] [--examples]

Defaults:
    --path resolves to the parent skills folder of this script.
    If this script lives at <skills>/skill-creator/scripts/init_skill.py,
    default output is <skills>/.
"""

from __future__ import annotations

import argparse
import re
from pathlib import Path


SKILL_TEMPLATE = """---
name: {skill_name}
description: [TODO: describe what this skill does AND when to use it. Include trigger examples.]
---

# {skill_title}

## Overview

[TODO: one short paragraph]

## Workflow

[TODO: step-by-step instructions]

## Optional resources

- `scripts/` for deterministic helpers
- `references/` for detailed docs loaded as needed
- `assets/` for templates/static files used in outputs
"""

EXAMPLE_SCRIPT = '''#!/usr/bin/env python3
"""Example helper script for {skill_name}. Replace or delete."""


def main() -> None:
    print("example helper for {skill_name}")


if __name__ == "__main__":
    main()
'''

EXAMPLE_REFERENCE = """# Reference Notes

Put detailed material here (schemas, API notes, long examples).
Keep SKILL.md concise and load references only when needed.
"""

VALID_RESOURCES = ("scripts", "references", "assets")


def title_case_skill_name(skill_name: str) -> str:
    return " ".join(part.capitalize() for part in skill_name.split("-"))


def validate_skill_name(skill_name: str) -> None:
    if not re.fullmatch(r"[a-z0-9-]{1,64}", skill_name):
        raise ValueError("Skill name must be 1-64 chars of lowercase letters, digits, and hyphens")
    if skill_name.startswith("-") or skill_name.endswith("-") or "--" in skill_name:
        raise ValueError("Skill name cannot start/end with hyphen or contain consecutive hyphens")


def default_skills_root() -> Path:
    # .../<skills>/skill-creator/scripts/init_skill.py -> .../<skills>
    return Path(__file__).resolve().parents[2]


def parse_resources(raw: str | None) -> list[str]:
    if not raw:
        return ["scripts", "references", "assets"]
    parsed = [item.strip() for item in raw.split(",") if item.strip()]
    unknown = [item for item in parsed if item not in VALID_RESOURCES]
    if unknown:
        raise ValueError(f"Unknown resource directories: {', '.join(unknown)}")
    # keep order stable, remove duplicates
    deduped: list[str] = []
    for item in parsed:
        if item not in deduped:
            deduped.append(item)
    return deduped


def init_skill(skill_name: str, skills_root: Path, resources: list[str], with_examples: bool) -> Path:
    validate_skill_name(skill_name)

    skill_dir = skills_root.resolve() / skill_name
    if skill_dir.exists():
        raise FileExistsError(f"Directory already exists: {skill_dir}")

    skill_dir.mkdir(parents=True, exist_ok=False)

    # SKILL.md
    skill_md = skill_dir / "SKILL.md"
    skill_md.write_text(
        SKILL_TEMPLATE.format(skill_name=skill_name, skill_title=title_case_skill_name(skill_name))
    )

    # Optional resources
    for resource in resources:
        resource_dir = skill_dir / resource
        resource_dir.mkdir(parents=True, exist_ok=True)

        if with_examples and resource == "scripts":
            example = resource_dir / "example.py"
            example.write_text(EXAMPLE_SCRIPT.format(skill_name=skill_name))
            example.chmod(0o755)
        elif with_examples and resource == "references":
            (resource_dir / "reference.md").write_text(EXAMPLE_REFERENCE)

    return skill_dir


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Initialize an OpenClaw skill scaffold")
    parser.add_argument("skill_name", help="hyphen-case skill name (e.g., paper-triage)")
    parser.add_argument(
        "--path",
        default=str(default_skills_root()),
        help="skills root directory (default: sibling skills folder)",
    )
    parser.add_argument(
        "--resources",
        default=",".join(VALID_RESOURCES),
        help="comma-separated subset of scripts,references,assets",
    )
    parser.add_argument("--examples", action="store_true", help="create example files in resource directories")
    return parser


def main() -> None:
    parser = build_parser()
    args = parser.parse_args()

    skills_root = Path(args.path).expanduser()
    resources = parse_resources(args.resources)

    print(f"🚀 Initializing skill: {args.skill_name}")
    print(f"   Skills root: {skills_root}")
    print(f"   Resources: {', '.join(resources)}")
    print(f"   Examples: {'yes' if args.examples else 'no'}\n")

    try:
        skill_dir = init_skill(args.skill_name, skills_root, resources, args.examples)
    except Exception as exc:
        print(f"❌ {exc}")
        raise SystemExit(1)

    print(f"✅ Created: {skill_dir}")
    print("\nNext steps:")
    print("1) Fill in SKILL.md (tight, trigger-rich description)")
    print("2) Add scripts/references/assets only if they materially help")
    print("3) Validate/package with scripts/package_skill.py if needed")


if __name__ == "__main__":
    main()
