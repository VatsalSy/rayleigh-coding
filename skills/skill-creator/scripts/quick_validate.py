#!/usr/bin/env python3
"""Quick validation script for jarvis skill folders."""

from __future__ import annotations

import re
import sys
from pathlib import Path

try:
    import yaml
except ModuleNotFoundError as exc:
    if exc.name == "yaml":
        print(
            "Missing dependency: PyYAML (module 'yaml').\n"
            "Install with:\n"
            "  python3 -m pip install -r skill-creator/requirements-dev.txt",
            file=sys.stderr,
        )
        sys.exit(2)
    raise


ALLOWED_FRONTMATTER_KEYS = {
    "name",
    "description",
    "metadata",
    "homepage",
    "user-invocable",
    "disable-model-invocation",
    "command-dispatch",
    "command-tool",
    "command-arg-mode",
    "license",
    "allowed-tools",
}
DESCRIPTION_RUNTIME_MAX_CHARS = 1024
DESCRIPTION_HOUSE_MAX_WORDS = 60


def validate_skill(skill_path: str | Path) -> tuple[bool, str]:
    """Basic validation of a skill folder."""
    skill_path = Path(skill_path)
    skill_md = skill_path / "SKILL.md"

    if not skill_md.exists():
        return False, "SKILL.md not found"

    content = skill_md.read_text()
    if not content.startswith("---"):
        return False, "No YAML frontmatter found"

    match = re.match(r"^---\n(.*?)\n---", content, re.DOTALL)
    if not match:
        return False, "Invalid frontmatter format"

    frontmatter_text = match.group(1)

    try:
        frontmatter = yaml.safe_load(frontmatter_text)
        if not isinstance(frontmatter, dict):
            return False, "Frontmatter must be a YAML dictionary"
    except yaml.YAMLError as e:
        return False, f"Invalid YAML in frontmatter: {e}"

    unexpected = set(frontmatter.keys()) - ALLOWED_FRONTMATTER_KEYS
    if unexpected:
        return (
            False,
            f"Unexpected frontmatter key(s): {', '.join(sorted(unexpected))}. "
            f"Allowed: {', '.join(sorted(ALLOWED_FRONTMATTER_KEYS))}",
        )

    if "name" not in frontmatter:
        return False, "Missing 'name' in frontmatter"
    if "description" not in frontmatter:
        return False, "Missing 'description' in frontmatter"

    name = frontmatter.get("name", "")
    if not isinstance(name, str):
        return False, f"Name must be a string, got {type(name).__name__}"
    name = name.strip()
    if not name:
        return False, "'name' cannot be empty"
    if not re.fullmatch(r"[a-z0-9-]{1,64}", name):
        return False, "'name' must be 1-64 chars, lowercase letters/digits/hyphens only"
    if name.startswith("-") or name.endswith("-") or "--" in name:
        return False, "'name' cannot start/end with hyphen or contain consecutive hyphens"
    if skill_path.name != name:
        return False, f"Skill folder {skill_path.name!r} must match frontmatter name {name!r}"

    description = frontmatter.get("description", "")
    if not isinstance(description, str):
        return False, f"Description must be a string, got {type(description).__name__}"
    description = description.strip()
    if not description:
        return False, "'description' cannot be empty"
    if len(description) > DESCRIPTION_RUNTIME_MAX_CHARS:
        return (
            False,
            f"Description too long ({len(description)} chars). Max 1024 — the runtime "
            "rejects skills with descriptions over this cap (InputValidationError on load).",
        )
    word_count = len(description.split())
    if word_count > DESCRIPTION_HOUSE_MAX_WORDS:
        return (
            False,
            f"Description too long ({word_count} words). Jarvis descriptions must stay at "
            f"or below {DESCRIPTION_HOUSE_MAX_WORDS} words and contain trigger conditions only.",
        )

    return True, "Skill is valid!"


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: quick_validate.py <skill_directory>")
        raise SystemExit(1)

    ok, msg = validate_skill(sys.argv[1])
    print(msg)
    raise SystemExit(0 if ok else 1)
