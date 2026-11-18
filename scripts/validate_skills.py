#!/usr/bin/env python3
"""Validate required SKILL.md frontmatter for every shipped skill."""
from __future__ import annotations

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SKILLS = ROOT / "plugins" / "rayleigh-coding" / "skills"
SHIPPED_PATH = re.compile(r"<skills-dir>/([a-z][a-z0-9-]+/(?:scripts|references|docs)/[a-zA-Z0-9._/-]+)")
RELATIVE_LINK = re.compile(r"\]\((\.{1,2}/[^\s)#]+)(?:#[^)]*)?\)")
FENCE = re.compile(r"^\s*(`{3,}|~{3,})")
FM_RE = re.compile(r"^---\n(.*?)\n---\n", re.S)


def dependency_errors(path: Path) -> list[str]:
    errors = []
    fence = None
    for number, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
        marker = FENCE.match(line)
        if marker is not None:
            token = marker[1]
            if fence is None:
                fence = token
            elif token[0] == fence[0] and len(token) >= len(fence):
                fence = None
        targets = [(SKILLS / ref, ref) for ref in SHIPPED_PATH.findall(line)]
        if fence is None:
            targets.extend((path.parent / ref, ref) for ref in RELATIVE_LINK.findall(line))
        for target, label in targets:
            if not target.resolve().is_relative_to(SKILLS.parent) or not target.exists():
                errors.append(f"{path.relative_to(ROOT)}:{number}: missing bundled target {label}")
    return errors


def main() -> int:
    errors: list[str] = []
    for skill_dir in sorted(p for p in SKILLS.iterdir() if p.is_dir()):
        path = skill_dir / "SKILL.md"
        if not path.is_file():
            errors.append(f"{skill_dir.name}: missing SKILL.md")
            continue
        text = path.read_text(encoding="utf-8")
        m = FM_RE.match(text)
        if not m:
            errors.append(f"{skill_dir.name}: missing YAML frontmatter")
            continue
        fm = m.group(1)
        if not re.search(r"(?m)^name:\s*\S+", fm):
            errors.append(f"{skill_dir.name}: missing name")
        if not re.search(r"(?m)^description:\s*\S+", fm) and "description: >" not in fm and 'description: "' not in fm and "description: |" not in fm:
            # folded descriptions
            if "description:" not in fm:
                errors.append(f"{skill_dir.name}: missing description")
        name_m = re.search(r"(?m)^name:\s*[\"']?([^\"'\n]+)", fm)
        if name_m and name_m.group(1).strip() != skill_dir.name:
            errors.append(
                f"{skill_dir.name}: name {name_m.group(1).strip()!r} != directory"
            )
    for path in SKILLS.parent.rglob("*.md"):
        errors.extend(dependency_errors(path))
    if errors:
        print("\n".join(errors), file=sys.stderr)
        return 1
    print(f"skill frontmatter ok; count={sum(1 for p in SKILLS.iterdir() if p.is_dir())}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
