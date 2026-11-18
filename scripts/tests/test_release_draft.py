"""Check release mutations with a fake GitHub CLI and no network."""

import os
from pathlib import Path
import subprocess
import tempfile
import unittest


SCRIPT = Path(__file__).resolve().parents[2] / (
    "plugins/rayleigh-coding/skills/gh-release-notes-writer/scripts/create_release.sh"
)
COMMIT = "a" * 40
GITHUB = """#!/usr/bin/env bash
case "$1 $2" in
  'api graphql')
    printf '%s\n' "$@" > "$FAKE_GH_QUERY"
    printf '%s\n' "$TAG_COMMIT"
    ;;
  'release create') printf '%s\n' "$@" > "$FAKE_GH_ARGS" ;;
  'release view') printf '%s\n' "$DRAFT_READBACK" ;;
  *) exit 3 ;;
esac
"""


class ReleaseDraftTests(unittest.TestCase):
    def setUp(self):
        directory = tempfile.TemporaryDirectory()
        self.addCleanup(directory.cleanup)
        self.root = Path(directory.name)
        self.log = self.root / "argv"
        self.notes = self.root / "release notes.md"
        self.notes.write_text("Release notes\n")
        gh = self.root / "gh"
        gh.write_text(GITHUB)
        gh.chmod(0o700)

    def run_release(self, **overrides):
        env = dict(os.environ, PATH=f"{self.root}:{os.environ['PATH']}",
                   FAKE_GH_ARGS=str(self.log), FAKE_GH_QUERY=str(self.root / "query"),
                   TAG_COMMIT=COMMIT, GH_HOST="github.enterprise.example",
                   DRAFT_READBACK="v1.4.2\thttps://github.com/example/project/releases/tag/v1.4.2")
        repo = overrides.pop("repo", "example/project")
        env.update(overrides)
        return subprocess.run(
            ["bash", str(SCRIPT), repo, "v1.4.2", str(self.notes), COMMIT],
            env=env, capture_output=True, text=True, check=False,
        )

    def test_create_draft_on_an_explicit_verified_tag(self):
        result = self.run_release()
        self.assertEqual(result.returncode, 0, result.stderr)
        arguments = self.log.read_text().splitlines()
        self.assertIn("--draft", arguments)
        self.assertIn("--verify-tag", arguments)
        self.assertIn("--notes-file=" + str(self.notes), arguments)
        self.assertEqual(arguments[arguments.index("--repo") + 1], "github.com/example/project")
        self.assertIn("Verified draft", result.stdout)

    def test_numeric_repository_name_is_sent_as_a_string(self):
        result = self.run_release(repo="example/123")
        self.assertEqual(result.returncode, 0, result.stderr)
        query = (self.root / "query").read_text()
        self.assertIn("-f\nname=123\n", query)
        self.assertNotIn("-F\nname=123\n", query)

    def test_reject_missing_or_moved_tag_before_mutation(self):
        for target in ("", "b" * 40):
            with self.subTest(target=target):
                self.assertNotEqual(self.run_release(TAG_COMMIT=target).returncode, 0)
                self.assertFalse(self.log.exists())

    def test_mismatched_readback_cannot_report_success(self):
        result = self.run_release(DRAFT_READBACK="wrong\thttps://github.com/example/project")
        self.assertEqual(result.returncode, 1)
        self.assertNotIn("Verified draft", result.stdout)
