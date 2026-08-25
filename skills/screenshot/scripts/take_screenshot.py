#!/usr/bin/env python3
"""Cross-platform screenshot helper for Codex skills."""

from __future__ import annotations

import argparse
import datetime as dt
import json
import os
import platform
import shutil
import subprocess
import tempfile
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
MAC_PERM_SCRIPT = SCRIPT_DIR / "macos_permissions.swift"
MAC_PERM_HELPER = SCRIPT_DIR / "ensure_macos_permissions.sh"
MAC_WINDOW_SCRIPT = SCRIPT_DIR / "macos_window_info.swift"
MAC_DISPLAY_SCRIPT = SCRIPT_DIR / "macos_display_info.swift"
TEST_MODE_ENV = "CODEX_SCREENSHOT_TEST_MODE"
TEST_PLATFORM_ENV = "CODEX_SCREENSHOT_TEST_PLATFORM"
TEST_WINDOWS_ENV = "CODEX_SCREENSHOT_TEST_WINDOWS"
TEST_DISPLAYS_ENV = "CODEX_SCREENSHOT_TEST_DISPLAYS"
TEST_PNG = (
    b"\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x01\x00\x00\x00\x01"
    b"\x08\x06\x00\x00\x00\x1f\x15\xc4\x89\x00\x00\x00\x0cIDAT\x08\xd7c"
    b"\xf8\xff\xff?\x00\x05\xfe\x02\xfeA\xad\x1c\x1c\x00\x00\x00\x00IEND"
    b"\xaeB`\x82"
)

def parse_region(value: str) -> tuple[int, int, int, int]:
    parts = [p.strip() for p in value.split(",")]
    if len(parts) != 4:
        raise argparse.ArgumentTypeError("region must be x,y,w,h")
    try:
        x, y, w, h = (int(p) for p in parts)
    except ValueError as exc:
        raise argparse.ArgumentTypeError("region values must be integers") from exc
    if w <= 0 or h <= 0:
        raise argparse.ArgumentTypeError("region width and height must be positive")
    return x, y, w, h

def test_mode_enabled() -> bool:
    value = os.environ.get(TEST_MODE_ENV, "")
    return value.lower() in {"1", "true", "yes", "on"}

def normalize_platform(value: str) -> str:
    lowered = value.strip().lower()
    if lowered in {"darwin", "mac", "macos", "osx"}:
        return "Darwin"
    if lowered in {"linux", "ubuntu"}:
        return "Linux"
    if lowered in {"windows", "win"}:
        return "Windows"
    return value

def test_platform_override() -> str | None:
    value = os.environ.get(TEST_PLATFORM_ENV)
    if value:
        return normalize_platform(value)
    return None

def parse_int_list(value: str) -> list[int]:
    results: list[int] = []
    for part in value.split(","):
        part = part.strip()
        if not part:
            continue
        try:
            results.append(int(part))
        except ValueError:
            continue
    return results

def test_window_ids() -> list[int]:
    value = os.environ.get(TEST_WINDOWS_ENV, "101,102")
    ids = parse_int_list(value)
    return ids or [101]

def test_display_ids() -> list[int]:
    value = os.environ.get(TEST_DISPLAYS_ENV, "1,2")
    ids = parse_int_list(value)
    return ids or [1]

def write_test_png(path: Path) -> None:
    ensure_parent(path)
    path.write_bytes(TEST_PNG)

def timestamp() -> str:
    return dt.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")

def default_filename(fmt: str, prefix: str = "screenshot") -> str:
    return f"{prefix}-{timestamp()}.{fmt}"

def mac_default_dir() -> Path:
    desktop = Path.home() / "Desktop"
    try:
        proc = subprocess.run(
            ["defaults", "read", "com.apple.screencapture", "location"],
            check=False,
            capture_output=True,
            text=True,
        )
        location = proc.stdout.strip()
        if location:
            return Path(location).expanduser()
    except OSError:
        pass
    return desktop

def default_dir(system: str) -> Path:
    home = Path.home()
    if system == "Darwin":
        return mac_default_dir()
    if system == "Windows":
        pictures = home / "Pictures"
        screenshots = pictures / "Screenshots"
        if screenshots.exists():
            return screenshots
        if pictures.exists():
            return pictures
        return home
    pictures = home / "Pictures"
    screenshots = pictures / "Screenshots"
    if screenshots.exists():
        return screenshots
    if pictures.exists():
        return pictures
    return home

def ensure_parent(path: Path) -> None:
    try:
        path.parent.mkdir(parents=True, exist_ok=True)
    except OSError:
        # Fall back to letting the capture command report a clearer error.
        pass

def resolve_output_path(
    requested_path: str | None, mode: str, fmt: str, system: str
) -> Path:
    if requested_path:
        path = Path(requested_path).expanduser()
        if path.exists() and path.is_dir():
            path = path / default_filename(fmt)
        elif requested_path.endswith(("/", "\\")) and not path.exists():
            path.mkdir(parents=True, exist_ok=True)
            path = path / default_filename(fmt)
        elif path.suffix == "":
            path = path.with_suffix(f".{fmt}")
        ensure_parent(path)
        return path

    if mode == "temp":
        tmp_dir = Path(tempfile.gettempdir())
        tmp_path = tmp_dir / default_filename(fmt, prefix="codex-shot")
        ensure_parent(tmp_path)
        return tmp_path

    dest_dir = default_dir(system)
    dest_path = dest_dir / default_filename(fmt)
    ensure_parent(dest_path)
    return dest_path

def multi_output_paths(base: Path, suffixes: list[str]) -> list[Path]:
    if len(suffixes) <= 1:
        return [base]
    paths: list[Path] = []
    for suffix in suffixes:
        candidate = base.with_name(f"{base.stem}-{suffix}{base.suffix}")
        ensure_parent(candidate)
        paths.append(candidate)
    return paths

def run(cmd: list[str]) -> None:
    try:
        subprocess.run(cmd, check=True)
    except FileNotFoundError as exc:
        raise SystemExit(f"required command not found: {cmd[0]}") from exc
    except subprocess.CalledProcessError as exc:
        raise SystemExit(f"command failed ({exc.returncode}): {' '.join(cmd)}") from exc

def swift_json(script: Path, extra_args: list[str] | None = None) -> dict:
    module_cache = Path(tempfile.gettempdir()) / "codex-swift-module-cache"
    module_cache.mkdir(parents=True, exist_ok=True)
    cmd = ["swift", "-module-cache-path", str(module_cache), str(script)]
    if extra_args:
        cmd.extend(extra_args)
    try:
        proc = subprocess.run(cmd, check=True, capture_output=True, text=True)
    except FileNotFoundError as exc:
        raise SystemExit("swift not found; install Xcode command line tools") from exc
    except subprocess.CalledProcessError as exc:
        stderr = (exc.stderr or "").strip()
        if "ModuleCache" in stderr and "Operation not permitted" in stderr:
            raise SystemExit(
                "swift needs module-cache access; rerun with escalated permissions"
            ) from exc
        msg = stderr or (exc.stdout or "").strip() or "swift helper failed"
        raise SystemExit(msg) from exc
    try:
        return json.loads(proc.stdout)
    except json.JSONDecodeError as e