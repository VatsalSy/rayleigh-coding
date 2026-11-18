#!/usr/bin/env python3
"""Run the shared PR triage extractor from the Git entry point."""

from pathlib import Path
from runpy import run_path


if __name__ == "__main__":
    run_path(str(Path(__file__).resolve().parents[2] / "gh-pr-triage" / "scripts" / "extract_pr_comments.py"),
             run_name="__main__")
