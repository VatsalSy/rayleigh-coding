#!/usr/bin/env python3
"""
Package an OpenClaw/AgentSkills skill into a .skill archive.

Usage:
    package_skill.py <path/to/skill-folder> [output-directory]
"""

from __future__ import annotations

import sys
import zipfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from quick_validate import validate_skill  # noqa: E402


def package_skill(skill_path: str | Path, output_dir: str | Path | None = None) -> Path | None:
    skill_path = Path(skill_path).expanduser().resolve()

    if not skill_path.exists() or not skill_path.is_dir():
        print(f"❌ Skill folder not found: {skill_path}")
        return None

    skill_md = skill_path / "SKILL.md"
    if not skill_md.exists():
        print(f"❌ SKILL.md not found in {skill_path}")
        return None

    print("🔍 Validating skill...")
    valid, message = validate_skill(skill_path)
    if not valid:
        print(f"❌ Validation failed: {message}")
        return None
    print(f"✅ {message}\n")

    output_path = Path(output_dir).expanduser().resolve() if output_dir else Path.cwd()
    output_path.mkdir(parents=True, exist_ok=True)
    package_path = output_path / f"{skill_path.name}.skill"

    try:
        with zipfile.ZipFile(package_path, "w", zipfile.ZIP_DEFLATED) as zf:
            for file_path in skill_path.rglob("*"):
                if not file_path.is_file():
                    continue
                if "__pycache__" in str(file_path) or file_path.suffix in {".pyc"}:
                    continue
                if file_path.name in {".DS_Store"}:
                    continue
                arcname = file_path.relative_to(skill_path.parent)
                zf.write(file_path, arcname)
                print(f"  Added: {arcname}")

        print(f"\n✅ Packaged: {package_path}")
        return package_path
    except Exception as exc:
        print(f"❌ Packaging error: {exc}")
        return None


def main() -> None:
    if len(sys.argv) < 2:
        print("Usage: package_skill.py <path/to/skill-folder> [output-directory]")
        raise SystemExit(1)

    skill_path = sys.argv[1]
    output_dir = sys.argv[2] if len(sys.argv) > 2 else None

    print(f"📦 Packaging skill: {skill_path}")
    if output_dir:
        print(f"   Output dir: {output_dir}")
    print()

    result = package_skill(skill_path, output_dir)
    raise SystemExit(0 if result else 1)


if __name__ == "__main__":
    main()
