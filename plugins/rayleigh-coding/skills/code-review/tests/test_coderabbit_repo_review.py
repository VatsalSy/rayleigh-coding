from __future__ import annotations

import importlib.util
import unittest
from pathlib import Path


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

    def test_rejects_empty(self):
        self.assertIsNone(MODULE.parse_github_remote(""))


class ResolveOrgTests(unittest.TestCase):
    def test_env_wins(self):
        import os

        old = os.environ.get("CODERABBIT_ORG")
        os.environ["CODERABBIT_ORG"] = "from-env"
        try:
            self.assertEqual(MODULE.resolve_org(), "from-env")
        finally:
            if old is None:
                os.environ.pop("CODERABBIT_ORG", None)
            else:
                os.environ["CODERABBIT_ORG"] = old

    def test_rejects_separated_token_flag(self):
        with self.assertRaises(SystemExit) as ctx:
            MODULE._reject_credential_args(["coderabbit", "review", "--token", "secret"])
        self.assertEqual(ctx.exception.code, 30)


if __name__ == "__main__":
    unittest.main()
