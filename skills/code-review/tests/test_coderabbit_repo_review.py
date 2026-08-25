from __future__ import annotations

import importlib.util
import os
from pathlib import Path
import subprocess
import tempfile
import unittest


SCRIPT = Path(__file__).resolve().parents[1] / "scripts" / "coderabbit_repo_review.py"
SPEC = importlib.util.spec_from_file_location("coderabbit_repo_review", SCRIPT)
MODULE = importlib.util.module_from_spec(SPEC)
assert SPEC.loader is not None
SPEC.loader.exec_module(MODULE)


class RemoteParsingTests(unittest.TestCase):
    def test_parses_ssh_remote(self):
        self.assertEqual(
            MODULE.parse_github_remote("git@github.com:acme/example-repo.git"),
            ("acme", "example-repo"),
        )

    def test_parses_https_remote(self):
        self.assertEqual(
            MODULE.parse_github_remote("https://github.com/example-org/example.git"),
            ("example-org", "example"),
        )

    def test_parses_ssh_url_remote(self):
        self.assertEqual(
            MODULE.parse_github_remote("ssh://git@github.com/acme/private.git"),
            ("acme", "private"),
        )

    def test_rejects_non_github_remote(self):
        self.assertIsNone(
            MODULE.parse_github_remote("ssh://git@gitlab.example.com/acme/example.git")
        )
        self.assertIsNone(
            MODULE.parse_github_remote("https://bitbucket.org/acme/example.git")
        )

    def test_identity_selects_github_remote_by_host(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            subprocess.run(
                ["git", "-c", "init.templateDir=", "init", "-b", "main"],
                cwd=root,
                check=True,
                stdout=subprocess.DEVNULL,
            )
            subprocess.run(
                ["git", "remote", "add", "origin", "https://git.example.com/acme/example-repo.git"],
                cwd=root,
                check=True,
            )
            subprocess.run(
                ["git", "remote", "add", "github", "git@github.com:acme/example-repo.git"],
                cwd=root,
                check=True,
            )
            owner, repo, remote = MODULE.repository_identity(root)
            self.assertEqual((owner, repo), ("acme", "example-repo"))
            self.assertIn("github.com", remote.lower())
            self.assertIn("example-repo", remote)

    def test_identity_rejects_multiple_github_remotes(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            subprocess.run(
                ["git", "-c", "init.templateDir=", "init", "-b", "main"],
                cwd=root,
                check=True,
                stdout=subprocess.DEVNULL,
            )
            subprocess.run(
                ["git", "remote", "add", "github", "git@github.com:acme/example-repo.git"],
                cwd=root,
                check=True,
            )
            subprocess.run(
                ["git", "remote", "add", "backup", "https://github.com/acme/example-repo.git"],
                cwd=root,
                check=True,
            )
            with self.assertRaisesRegex(MODULE.GuardError, "CODERABBIT_AMBIGUOUS"):
                MODULE.repository_identity(root)

    def test_expected_org_prefers_env_then_owner(self):
        previous_org = os.environ.pop("CODERABBIT_ORG", None)
        previous_require = os.environ.pop("CODERABBIT_REQUIRE_ORG", None)
        try:
            self.assertEqual(MODULE.expected_org("acme"), "acme")
            self.assertIsNone(MODULE.expected_org("acme", visibility="PUBLIC"))
            os.environ["CODERABBIT_ORG"] = "paid-team"
            self.assertEqual(MODULE.expected_org("acme", visibility="PUBLIC"), "paid-team")
            del os.environ["CODERABBIT_ORG"]
            os.environ["CODERABBIT_REQUIRE_ORG"] = "1"
            self.assertIsNone(MODULE.expected_org("acme", visibility="PRIVATE"))
        finally:
            if previous_org is None:
                os.environ.pop("CODERABBIT_ORG", None)
            else:
                os.environ["CODERABBIT_ORG"] = previous_org
            if previous_require is None:
                os.environ.pop("CODERABBIT_REQUIRE_ORG", None)
            else:
                os.environ["CODERABBIT_REQUIRE_ORG"] = previous_require

    def test_org_picker_keys_follow_structured_order(self):
        organizations = ["acme", "example-org"]
        self.assertEqual(
            MODULE.organisation_picker_keys(organizations, "example-org", "acme"),
            b"\x1b[A\r",
        )
        self.assertEqual(
            MODULE.organisation_picker_keys(organizations, "acme", "example-org"),
            b"\x1b[B\r",
        )
        self.assertEqual(
            MODULE.organisation_picker_keys(organizations, "acme", "acme"),
            b"\r",
        )

    def test_org_picker_keys_reject_unknown_state(self):
        with self.assertRaises(MODULE.GuardError):
            MODULE.organisation_picker_keys(organizations, "missing", "acme")


class ReceiptTests(unittest.TestCase):
    def test_review_scope_requires_one_exact_mode(self):
        with self.assertRaises(MODULE.GuardError):
            MODULE.review_scope(["--agent"])
        with self.assertRaises(MODULE.GuardError):
            MODULE.review_scope(["--uncommitted", "--base", "main", "--agent"])

    def test_blocking_severities_are_counted_from_structured_output(self):
        output = '\n'.join(
            [
                '{"type":"finding","severity":"Critical"}',
                '{"finding":{"level":"warning"}}',
                '{"type":"finding","severity":"major"}',
                '{"type":"status","level":"info"}',
            ]
        )
        counts = MODULE.severity_counts(output)
        self.assertEqual(counts["critical"], 1)
        self.assertEqual(counts["warning"], 1)
        self.assertEqual(counts["major"], 1)

    def test_base_scope_receipt_includes_tracked_worktree(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            subprocess.run(
                ["git", "-c", "init.templateDir=", "init", "-b", "main"],
                cwd=root,
                check=True,
                stdout=subprocess.DEVNULL,
            )
            subprocess.run(["git", "config", "user.email", "test@example.invalid"], cwd=root, check=True)
            subprocess.run(["git", "config", "user.name", "Test"], cwd=root, check=True)
            subprocess.run(["git", "config", "commit.gpgsign", "false"], cwd=root, check=True)
            subprocess.run(["git", "config", "core.hooksPath", "/dev/null"], cwd=root, check=True)
            (root / "sample.txt").write_text("base\n")
            subprocess.run(["git", "add", "sample.txt"], cwd=root, check=True)
            subprocess.run(["git", "commit", "-m", "Base"], cwd=root, check=True, stdout=subprocess.DEVNULL)
            (root / "sample.txt").write_text("working\n")
            scope = MODULE.review_scope(["--base", "main", "--agent"])
            diff, _, _ = MODULE.diff_bytes(root, scope)
            self.assertIn(b"TRACKED_WORKTREE", diff)
            self.assertIn(b"+working", diff)

    def test_rate_limit_and_private_fallback_detection(self):
        self.assertRegex("Fair use rate limit reached", MODULE.RATE_LIMIT_RE)
        self.assertTrue(
            MODULE.rate_limited_detected(
                '{"type":"error","message":"Review rate limited by fair use"}', 0
            )
        )
        self.assertFalse(
            MODULE.rate_limited_detected(
                '{"type":"finding","message":"rate limit exceeded in application code"}',
                0,
            )
        )
        self.assertTrue(MODULE.private_fallback_detected('{"orgAttributed":false}'))
        self.assertTrue(
            MODULE.private_fallback_detected(
                "warning: orgAttributed=false, using free capacity"
            )
        )
        self.assertTrue(
            MODULE.rate_limited_detected("Review rate limited by fair use", 1)
        )
        self.assertFalse(
            MODULE.private_fallback_detected(
                '{"type":"finding","message":"check orgAttributed: false text"}'
            )
        )

    def test_review_scope_rejects_config_without_value(self):
        with self.assertRaises(MODULE.GuardError):
            MODULE.review_scope(["--uncommitted", "--config"])

    def test_review_scope_handles_equals_forms_and_blocks_credentials(self):
        scope = MODULE.review_scope(["--base=main", "--config=rules.md"])
        self.assertEqual(scope["base"], "main")
        self.assertEqual(scope["config_files"], ["rules.md"])
        with self.assertRaises(MODULE.GuardError):
            MODULE.review_scope(["--uncommitted", "--api-key=secret"])
        with self.assertRaises(MODULE.GuardError):
            MODULE.review_scope(["--uncommitted", "--region=eu"])

    def test_untracked_review_requires_exact_allowlist(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            subprocess.run(
                ["git", "-c", "init.templateDir=", "init", "-b", "main"],
                cwd=root,
                check=True,
                stdout=subprocess.DEVNULL,
            )
            (root / "new.txt").write_text("new\n")
            scope = MODULE.review_scope(["--uncommitted", "--include-untracked"])
            with self.assertRaises(MODULE.GuardError):
                MODULE.validate_untracked_allowlist(root, scope, [])
            self.assertEqual(
                MODULE.validate_untracked_allowlist(root, scope, ["new.txt"]),
                ["new.txt"],
            )

    def test_invalid_initial_counter_fails_closed(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "cadence.json"
            MODULE.atomic_json_write(
                path,
                {
                    "schema": "coderabbit-review-cadence-v1",
                    "series": {
                        "series": {
                            "initial_attempts": 1,
                            "follow_up_attempts": 0,
                            "attempts": [],
                        }
                    },
                },
            )
            with self.assertRaises(MODULE.GuardError):
                MODULE.reserve_cadence_attempt(
                    path,
                    "series",
                    follow_up=False,
                    extra_follow_up=False,
                    reason=None,
                    diff_sha256="new",
                )

    def test_nested_severity_container_is_counted(self):
        counts = MODULE.severity_counts(
            '{"level":{"items":[{"severity":"critical"}]}}'
        )
        self.assertEqual(counts["critical"], 1)

    def test_aborted_initial_allows_changed_retry(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "cadence.json"
            ledger, index = MODULE.reserve_cadence_attempt(
                path,
                "series",
                follow_up=False,
                extra_follow_up=False,
                reason=None,
                diff_sha256="first",
            )
            MODULE.finish_cadence_attempt(path, ledger, "series", index, "aborted")
            MODULE.reserve_cadence_attempt(
                path,
                "series",
                follow_up=False,
                extra_follow_up=False,
                reason=None,
                diff_sha256="second",
            )

    def test_atomic_receipt_write(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "receipt.json"
            MODULE.atomic_json_write(path, {"quality_gate": "pass"})
            self.assertEqual(path.read_text(), '{\n  "quality_gate": "pass"\n}\n')

    def test_cadence_allows_one_initial_and_one_normal_follow_up(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "cadence.json"
            ledger, index = MODULE.reserve_cadence_attempt(
                path,
                "series",
                follow_up=False,
                extra_follow_up=False,
                reason=None,
                diff_sha256="first",
            )
            MODULE.finish_cadence_attempt(path, ledger, "series", index, "pass")
            ledger, index = MODULE.reserve_cadence_attempt(
                path,
                "series",
                follow_up=True,
                extra_follow_up=False,
                reason=None,
                diff_sha256="second",
            )
            MODULE.finish_cadence_attempt(path, ledger, "series", index, "pass")
            with self.assertRaises(MODULE.GuardError):
                MODULE.reserve_cadence_attempt(
                    path,
                    "series",
                    follow_up=True,
                    extra_follow_up=False,
                    reason=None,
                    diff_sha256="third",
                )

    def test_extra_follow_up_requires_reason(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "cadence.json"
            ledger, index = MODULE.reserve_cadence_attempt(
                path,
                "series",
                follow_up=False,
                extra_follow_up=False,
                reason=None,
                diff_sha256="first",
            )
            MODULE.finish_cadence_attempt(path, ledger, "series", index, "pass")
            with self.assertRaises(MODULE.GuardError):
                MODULE.reserve_cadence_attempt(
                    path,
                    "series",
                    follow_up=True,
                    extra_follow_up=True,
                    reason=None,
                    diff_sha256="second",
                )

    def test_extra_follow_up_requires_prior_findings_and_changed_diff(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "cadence.json"
            ledger, index = MODULE.reserve_cadence_attempt(
                path,
                "series",
                follow_up=False,
                extra_follow_up=False,
                reason=None,
                diff_sha256="first",
            )
            MODULE.finish_cadence_attempt(path, ledger, "series", index, "findings")
            ledger, index = MODULE.reserve_cadence_attempt(
                path,
                "series",
                follow_up=True,
                extra_follow_up=False,
                reason=None,
                diff_sha256="second",
            )
            MODULE.finish_cadence_attempt(path, ledger, "series", index, "findings")
            with self.assertRaises(MODULE.GuardError):
                MODULE.reserve_cadence_attempt(
                    path,
                    "series",
                    follow_up=True,
                    extra_follow_up=True,
                    reason="verified warning",
                    diff_sha256="second",
                )
            ledger, index = MODULE.reserve_cadence_attempt(
                path,
                "series",
                follow_up=True,
                extra_follow_up=True,
                reason="verified warning",
                diff_sha256="third",
            )
            MODULE.finish_cadence_attempt(path, ledger, "series", index, "findings")
            with self.assertRaises(MODULE.GuardError):
                MODULE.reserve_cadence_attempt(
                    path,
                    "series",
                    follow_up=True,
                    extra_follow_up=True,
                    reason="another verified warning",
                    diff_sha256="fourth",
                )


if __name__ == "__main__":
    unittest.main()
