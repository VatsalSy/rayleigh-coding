"""Exercise the privacy gate in disposable repositories."""

import os
from pathlib import Path
import shutil
import subprocess
import tempfile
import unittest


SCRIPTS = Path(__file__).resolve().parents[1]
MARKER = "SYNTHETIC-LOCAL-IDENTIFIER"


class PrivacyGateTests(unittest.TestCase):
    def setUp(self):
        directory = tempfile.TemporaryDirectory()
        self.addCleanup(directory.cleanup)
        self.root = Path(directory.name)
        (self.root / "scripts").mkdir()
        for name in ("check_no_private_leakage.sh", "privacy-patterns.pcre"):
            shutil.copyfile(SCRIPTS / name, self.root / "scripts" / name)
        self.git("init", "-q")
        self.git("add", "scripts")
        self.git("commit", "-qm", "Initial fixture")
        self.git("update-ref", "refs/remotes/origin/main", "HEAD")

    def git(self, *args):
        subprocess.run(
            ["git", "-c", "user.name=Test Author", "-c", "user.email=test@example.com", *args],
            cwd=self.root, check=True, capture_output=True,
        )

    def scan(self, pattern=MARKER, **settings):
        env = dict(os.environ, PRIVACY_EXTRA_PATTERN=pattern, HISTORY_HYGIENE_BASE="origin/main")
        env.update(settings)
        return subprocess.run(
            ["bash", "scripts/check_no_private_leakage.sh"], cwd=self.root,
            env=env, capture_output=True, text=True, check=False,
        )

    def test_clean_repository(self):
        self.assertEqual(self.scan().returncode, 0)

    def test_extra_pattern_fails_without_repeating_matched_value(self):
        (self.root / MARKER).write_text(MARKER + "\n", encoding="utf-8")
        result = self.scan()
        self.assertEqual(result.returncode, 1)
        self.assertNotIn(MARKER, result.stdout + result.stderr)
        self.assertIn("publishable paths", result.stderr)
        self.assertIn("publishable file contents", result.stderr)

    def test_default_patterns_work_without_ci_secret(self):
        value = "/" + "Users/synthetic-account/settings"
        (self.root / "note.txt").write_text(value + "\n", encoding="utf-8")
        result = self.scan(pattern="")
        self.assertEqual(result.returncode, 1)
        self.assertNotIn(value, result.stdout + result.stderr)

    def test_scans_new_commit_messages(self):
        self.git("commit", "--allow-empty", "-qm", MARKER)
        result = self.scan()
        self.assertEqual(result.returncode, 1)
        self.assertIn("new commit metadata", result.stderr)
        self.assertNotIn(MARKER, result.stdout + result.stderr)

    def test_bad_regex_or_base_fails_closed(self):
        self.assertEqual(self.scan(pattern="[").returncode, 2)
        self.assertEqual(self.scan(HISTORY_HYGIENE_BASE="missing").returncode, 2)
