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

# TRUNCATED_FOR_SIZE_TEST - will replace with full
print('partial')
