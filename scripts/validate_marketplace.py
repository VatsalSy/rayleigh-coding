#!/usr/bin/env python3
"""Validate marketplace manifests and manifest membership."""
from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PLUGIN = ROOT / "plugins" / "rayleigh-coding"
MANIFEST = PLUGIN / "skills.manifest"
SKILLS = PLUGIN / "skills"


def load_manifest() -> set[str]:
    names: set[str] = set()
    for line in MANIFEST.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        names.add(line)
    return names


def main() -> int:
    market = json.loads((ROOT / ".cursor-plugin" / "marketplace.json").read_text())
    assert market["name"] == "rayleigh-coding"
    plugins = market["plugins"]
    assert any(p.get("name") == "rayleigh-coding" for p in plugins)
    for p in plugins:
        src = ROOT / p["source"]
        assert src.is_dir(), src
        assert (src / ".cursor-plugin" / "plugin.json").is_file(), src

    plugin = json.loads((PLUGIN / ".cursor-plugin" / "plugin.json").read_text())
    assert plugin["name"] == "rayleigh-coding"

    allow = load_manifest()
    present = {p.name for p in SKILLS.iterdir() if p.is_dir()}
    extra = present - allow
    missing = allow - present
    if extra or missing:
        print(f"manifest mismatch extra={sorted(extra)} missing={sorted(missing)}", file=sys.stderr)
        return 1

    print(f"marketplace ok; skills={len(present)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
