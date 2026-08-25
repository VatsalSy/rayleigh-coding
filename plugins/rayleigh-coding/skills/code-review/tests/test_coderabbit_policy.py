from __future__ import annotations

import importlib.util
import io
from pathlib import Path
import tempfile
import unittest
from unittest import mock


SCRIPT = Path(__file__).resolve().parents[1] / "scripts" / "validate_coderabbit_policy.py"
SPEC = importlib.util.spec_from_file_location("validate_coderabbit_policy", SCRIPT)
MODULE = importlib.util.module_from_spec(SPEC)
assert SPEC.loader is not None
SPEC.loader.exec_module(MODULE)


class PolicyValidationTests(unittest.TestCase):
    def test_flags_direct_review_commands(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / "SKILL.md").write_text("```bash\ncr --base main\n```\n")
            self.assertEqual(len(MODULE.violations(root)), 1)

    def test_flags_mid_line_and_bot_control_commands(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / "SKILL.md").write_text(
                "git status && cr --base main\n- cr --base main\n@coderabbitai review\n"
            )
            self.assertEqual(len(MODULE.violations(root)), 3)

    def test_tolerates_non_utf8_markdown(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / "SKILL.md").write_bytes(b"\xff\ncr --base main\n")
            self.assertEqual(len(MODULE.violations(root)), 1)

    def test_main_rejects_missing_scan_root(self):
        with tempfile.TemporaryDirectory() as directory:
            missing = Path(directory) / "missing"
            with mock.patch("sys.argv", ["validate", str(missing)]), mock.patch(
                "sys.stderr", new_callable=io.StringIO
            ) as stderr:
                self.assertEqual(MODULE.main(), 2)
                self.assertIn(str(missing), stderr.getvalue())

    def test_accepts_guarded_entry_point(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / "SKILL.md").write_text(
                "python3 <skills-dir>/code-review/scripts/coderabbit_repo_review.py -- --base main\n"
            )
            self.assertEqual(MODULE.violations(root), [])


if __name__ == "__main__":
    unittest.main()
