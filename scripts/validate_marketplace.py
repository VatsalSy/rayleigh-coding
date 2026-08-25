#!/usr/bin/env python3
"""Validate marketplace manifests and skills.manifest membership."""
from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PLUGIN = ROOT / "plugins" / "rayleigh-coding"
MANIFEST = PLUGIN / "skills.manifest"
SKILLS = PLUGIN / "skills"
EXPECTED_SOURCE = "plugins/rayleigh-coding"


def fail(message: str) -> int:
    print(message, file=sys.stderr)
    return 1


def load_manifest() -> list[str] | int:
    names: list[str] = []
    for line in MANIFEST.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        names.append(line)
    dupes = sorted({n for n in names if names.count(n) > 1})
    if dupes:
        return fail(f"duplicate skills.manifest entries: {dupes}")
    return names


def main() -> int:
    try:
        market = json.loads((ROOT / ".cursor-plugin" / "marketplace.json").read_text())
    except (OSError, json.JSONDecodeError) as exc:
        return fail(f"marketplace.json unreadable: {exc}")

    if market.get("name") != "rayleigh-coding":
        return fail(f"unexpected marketplace name: {market.get('name')!r}")

    plugins = market.get("plugins")
    if not isinstance(plugins, list) or len(plugins) != 1:
        return fail("marketplace must declare exactly one plugin")
    entry = plugins[0]
    if entry.get("name") != "rayleigh-coding":
        return fail(f"unexpected plugin name: {entry.get('name')!r}")
    source = str(entry.get("source") or "").lstrip("./")
    if source != EXPECTED_SOURCE:
        return fail(f"unexpected plugin source: {entry.get('source')!r}")

    src = ROOT / source
    if not src.is_dir():
        return fail(f"plugin source missing: {src}")
    plugin_json = src / ".cursor-plugin" / "plugin.json"
    if not plugin_json.is_file():
        return fail(f"missing {plugin_json}")

    try:
        plugin = json.loads(plugin_json.read_text())
    except (OSError, json.JSONDecodeError) as exc:
        return fail(f"plugin.json unreadable: {exc}")
    if plugin.get("name") != "rayleigh-coding":
        return fail(f"unexpected plugin.json name: {plugin.get('name')!r}")

    loaded = load_manifest()
    if isinstance(loaded, int):
        return loaded
    allow = set(loaded)
    present = {p.name for p in SKILLS.iterdir() if p.is_dir()}
    extra = present - allow
    missing = allow - present
    if extra or missing:
        return fail(f"skills.manifest mismatch extra={sorted(extra)} missing={sorted(missing)}")

    print(f"marketplace ok; skills={len(present)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
