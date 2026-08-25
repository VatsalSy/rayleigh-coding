#!/usr/bin/env python3
"""Run a repository-aware CodeRabbit review without cross-org fallback."""

from __future__ import annotations

import argparse
import fcntl
import hashlib
import json
import os
from pathlib import Path
import re
import select
import signal
import subprocess
import sys
import tempfile
import threading
import time
from typing import Any, Iterable, Sequence
from urllib.parse import urlparse


RATE_LIMIT_RE = re.compile(
    r"(?:rate[ -]?limit(?:ed| (?:reached|exceeded))|"
    r"fair[ -]?use(?: limit)? (?:reached|exceeded)|"
    r"quota (?:is )?(?:exhausted|exceeded)|usage limit (?:reached|exceeded)|"
    r"too many requests|\b429\b)",
    re.IGNORECASE,
)
PRIVATE_FALLBACK_RE = re.compile(
    r'(?:"orgAttributed"\s*:\s*false|orgAttributed\s*=\s*false)',
    re.IGNORECASE,
)
BLOCKING_SEVERITIES = {"critical", "warning", "high", "major"}


class GuardError(RuntimeError):
    """Expected guard refusal with a stable exit code."""

    def __init__(self, message: str, exit_code: int = 2) -> None:
        super().__init__(message)
        self.exit_code = exit_code


def run_text(command: Sequence[str], cwd: Path, check: bool = True) -> str:
    completed = subprocess.run(
        list(command),
        cwd=cwd,
        check=False,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
    )
    if check and completed.returncode != 0:
        raise GuardError(
            f"command failed ({completed.returncode}): {' '.join(command)}\n{completed.stdout.strip()}",
            3,
        )
    return completed.stdout.strip()


def git(root: Path, *args: str, check: bool = True) -> str:
    return run_text(("git", *args), root, check=check)


def resolve_repo(path: str) -> Path:
    candidate = Path(path).expanduser().resolve()
    output = run_text(("git", "rev-parse", "--show-toplevel"), candidate)
    return Path(output).resolve()


def parse_github_remote(remote: str) -> tuple[str, str] | None:
    value = remote.strip()
    match = re.match(r"^git@github\.com:([^/]+)/(.+?)(?:\.git)?$", value, re.I)
    if match:
        return match.group(1), re.sub(r"\.git$", "", match.group(2), flags=re.I)

    parsed = urlparse(value)
    if parsed.hostname and parsed.hostname.lower() == "github.com":
        path = parsed.path.lstrip("/")
        if "/" not in path:
            return None
        owner, repo = path.split("/", 1)
        return owner, re.sub(r"\.git$", "", repo, flags=re.I)
    return None


def repository_identity(root: Path) -> tuple[str, str, str]:
    candidates: list[tuple[str, str, str, str]] = []
    remote_names = [name.strip() for name in git(root, "remote").splitlines() if name.strip()]
    for remote_name in remote_names:
        remote = git(root, "remote", "get-url", remote_name)
        parsed = parse_github_remote(remote)
        if parsed is not None:
            owner, repo = parsed
            candidates.append((remote_name, owner, repo, remote))
    if not candidates:
        raise GuardError(
            "CODERABBIT_EXEMPT reason=no-github-remote "
            f"remotes={','.join(remote_names)}",
            20,
        )
    if len(candidates) != 1:
        names = ",".join(candidate[0] for candidate in candidates)
        raise GuardError(
            f"CODERABBIT_AMBIGUOUS github_remotes={names}; resolve one GitHub remote before review",
            20,
        )
    _name, owner, repo, remote = candidates[0]
    return owner, repo, remote


def require_explicit_org() -> bool:
    return os.environ.get("CODERABBIT_REQUIRE_ORG", "").strip().lower() in {
        "1",
        "true",
        "yes",
    }


def expected_org(owner: str, *, visibility: str | None = None) -> str | None:
    """Resolve CodeRabbit org from env or the GitHub remote owner.

    Preference order:
    1. ``CODERABBIT_ORG`` environment variable
    2. Remote owner for non-public repositories (when strict mode is off)
    3. ``None`` for public/OSS routes, or when ``CODERABBIT_REQUIRE_ORG=1``
       and no explicit org is set (caller refuses private repos)
    """
    env_org = os.environ.get("CODERABBIT_ORG", "").strip()
    if env_org:
        return env_org
    if require_explicit_org():
        return None
    if visibility is not None and visibility.upper() == "PUBLIC":
        return None
    return owner


def repository_visibility(root: Path, owner: str, repo: str) -> str:
    output = run_text(
        ("gh", "repo", "view", f"{owner}/{repo}", "--json", "visibility", "--jq", ".visibility"),
        root,
    )
    visibility = output.strip().upper()
    if visibility not in {"PUBLIC", "PRIVATE", "INTERNAL"}:
        raise GuardError(f"cannot establish repository visibility: {output!r}", 21)
    return visibility


def parse_json_object(output: str) -> dict[str, Any]:
    for line in reversed(output.splitlines()):
        try:
            value = json.loads(line)
        except json.JSONDecodeError:
            continue
        if isinstance(value, dict):
            return value
    raise GuardError("expected JSON object was not returned", 3)


def auth_status(root: Path, binary: str) -> dict[str, Any]:
    output = run_text((binary, "auth", "status", "--agent"), root)
    status = parse_json_object(output)
    if not status.get("authenticated"):
        raise GuardError("CODERABBIT_AUTH_REQUIRED action='coderabbit auth login'", 22)
    return status


def current_org(status: dict[str, Any]) -> str | None:
    value = status.get("currentOrg")
    if isinstance(value, dict) and isinstance(value.get("name"), str):
        return value["name"]
    return None


def organisation_picker_keys(
    organizations: Sequence[str], current: str, required: str
) -> bytes:
    """Return the ordinary cursor keys needed by CodeRabbit's org picker."""
    try:
        current_index = organizations.index(current)
        required_index = organizations.index(required)
    except ValueError as error:
        raise GuardError(
            "CodeRabbit organisation picker state disagrees with auth status", 22
        ) from error
    delta = required_index - current_index
    arrow = b"\x1b[B" if delta > 0 else b"\x1b[A"
    return arrow * abs(delta) + b"\r"


def run_org_picker(
    root: Path,
    binary: str,
    organizations: Sequence[str],
    current: str,
    required: str,
    timeout_seconds: float = 15.0,
) -> None:
    """Select an organisation through the supported picker in a private PTY."""
    master: int | None = None
    slave: int | None = None
    process: subprocess.Popen[bytes] | None = None
    output = bytearray()
    deadline = time.monotonic() + timeout_seconds
    keys_sent = False
    try:
        master, slave = os.openpty()
        process = subprocess.Popen(
            (binary, "auth", "org"),
            cwd=root,
            stdin=slave,
            stdout=slave,
            stderr=slave,
            close_fds=True,
        )
        os.close(slave)
        slave = None
        while process.poll() is None:
            remaining = deadline - time.monotonic()
            if remaining <= 0:
                process.terminate()
                raise GuardError("CodeRabbit organisation picker timed out", 22)
            readable, _, _ = select.select([master], [], [], min(0.25, remaining))
            if readable:
                try:
                    output.extend(os.read(master, 4096))
                except OSError:
                    break
            if not keys_sent and all(name.encode() in output for name in organizations):
                os.write(
                    master,
                    organisation_picker_keys(organizations, current, required),
                )
                keys_sent = True
        if process.wait() != 0:
            raise GuardError("CodeRabbit's supported organisation picker failed", 22)
        if not keys_sent:
            raise GuardError(
                "CodeRabbit organisation picker did not display the expected choices", 22
            )
    finally:
        if process is not None and process.poll() is None:
            process.terminate()
            try:
                process.wait(timeout=2)
            except subprocess.TimeoutExpired:
                process.kill()
                process.wait()
        if slave is not None:
            os.close(slave)
        if master is not None:
            os.close(master)


def ensure_org(root: Path, binary: str, required: str, allow_switch: bool) -> str:
    status = auth_status(root, binary)
    current = current_org(status)
    available = {
        item.get("name")
        for item in status.get("organizations", [])
        if isinstance(item, dict)
    }
    if required not in available:
        raise GuardError(
            f"CODERABBIT_ORG_UNAVAILABLE expected={required} available={sorted(available)!r}",
            22,
        )
    if current == required:
        return current
    if not allow_switch:
        raise GuardError(
            f"CODERABBIT_ORG_MISMATCH expected={required} current={current or 'none'} "
            "action='rerun this guard with --switch-org in a PTY'",
            22,
        )
    print(f"CODERABBIT_ORG_SWITCH expected={required} current={current or 'none'}", flush=True)
    organizations = [
        item["name"]
        for item in status.get("organizations", [])
        if isinstance(item, dict) and isinstance(item.get("name"), str)
    ]
    if current is None:
        raise GuardError("CodeRabbit reports no current organisation to switch from", 22)
    run_org_picker(root, binary, organizations, current, required)
    verified = current_org(auth_status(root, binary))
    if verified != required:
        raise GuardError(
            f"CODERABBIT_ORG_MISMATCH expected={required} current={verified or 'none'}",
            22,
        )
    return verified


def acquire_lock(timeout_seconds: int):
    lock_dir = Path.home() / ".cache" / "coderabbit-review-guard"
    lock_dir.mkdir(mode=0o700, parents=True, exist_ok=True)
    directory_stat = lock_dir.lstat()
    if lock_dir.is_symlink() or directory_stat.st_uid != os.getuid():
        raise GuardError(f"unsafe CodeRabbit lock directory: {lock_dir}", 23)
    os.chmod(lock_dir, 0o700)

    path = lock_dir / "review.lock"
    flags = os.O_RDWR | os.O_CREAT | os.O_NOFOLLOW | getattr(os, "O_CLOEXEC", 0)
    try:
        descriptor = os.open(path, flags | os.O_EXCL, 0o600)
    except FileExistsError:
        try:
            descriptor = os.open(path, flags, 0o600)
        except OSError as error:
            raise GuardError(f"unsafe CodeRabbit lock file: {path}", 23) from error
    os.fchmod(descriptor, 0o600)
    handle = os.fdopen(descriptor, "r+", encoding="utf-8")
    deadline = time.monotonic() + timeout_seconds
    while True:
        try:
            fcntl.flock(handle.fileno(), fcntl.LOCK_EX | fcntl.LOCK_NB)
            break
        except BlockingIOError as error:
            if time.monotonic() >= deadline:
                handle.close()
                raise GuardError(
                    "CODERABBIT_LOCK_TIMEOUT another guarded review is active", 23
                ) from error
            time.sleep(0.25)
    handle.seek(0)
    handle.truncate()
    handle.write(f"pid={os.getpid()}\n")
    handle.flush()
    return handle


def review_scope(args: Sequence[str]) -> dict[str, Any]:
    scope: dict[str, Any] = {
        "mode": "tracked",
        "base": None,
        "base_commit": None,
        "dir": None,
        "include_untracked": False,
        "config_files": [],
    }
    index = 0
    while index < len(args):
        arg = args[index]
        option, separator, inline_value = arg.partition("=")
        if separator and option in {"--api-key", "--region"}:
            raise GuardError(f"{option} is not allowed by the repository guard")
        if separator and option in {"--base", "--base-commit", "--dir"}:
            if not inline_value:
                raise GuardError(f"missing value for {option}")
            scope[option[2:].replace("-", "_")] = inline_value
            index += 1
            continue
        if separator and option == "--config":
            if not inline_value:
                raise GuardError(f"missing value for {option}")
            scope["config_files"].append(inline_value)
            index += 1
            continue
        if arg == "--uncommitted":
            scope["mode"] = "uncommitted"
        elif arg == "--committed":
            scope["mode"] = "committed"
        elif arg == "--include-untracked":
            scope["include_untracked"] = True
        elif arg in {"--base", "--base-commit", "--dir"}:
            if index + 1 >= len(args):
                raise GuardError(f"missing value for {arg}")
            key = arg[2:].replace("-", "_")
            scope[key] = args[index + 1]
            index += 1
        elif arg in {"-c", "--config"}:
            if index + 1 >= len(args) or args[index + 1].startswith("-"):
                raise GuardError(f