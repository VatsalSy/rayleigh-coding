#!/usr/bin/env python3
"""Read the current GitHub PR's full discussion as JSON."""

import json
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "gh-babysit-pr" / "scripts"))
from github_snapshot import SnapshotError, fetch_discussion, parse_pr_url


def main():
    try:
        result = subprocess.run(
            ["gh", "pr", "view", "--json", "url"], capture_output=True, text=True, check=True, timeout=30,
        )
        repo, number = parse_pr_url(json.loads(result.stdout)["url"])
        print(json.dumps(fetch_discussion(repo, number), indent=2))
    except subprocess.CalledProcessError:
        raise SystemExit("Could not identify the current PR. Check gh authentication and the current branch.") from None
    except (OSError, subprocess.SubprocessError, SnapshotError, ValueError, KeyError) as error:
        raise SystemExit(f"Could not read current PR: {error}") from None


if __name__ == "__main__":
    main()
