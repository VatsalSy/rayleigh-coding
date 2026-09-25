from __future__ import annotations

import importlib.util
import json
import unittest
from pathlib import Path

SCRIPT = Path(__file__).resolve().parents[1] / "scripts" / "pick_models.py"
SPEC = importlib.util.spec_from_file_location("pick_models", SCRIPT)
MODULE = importlib.util.module_from_spec(SPEC)
assert SPEC.loader is not None
SPEC.loader.exec_module(MODULE)

SESSION_SLUGS = [
    "inherit",
    "claude-fable-5-1-thinking-high",
    "claude-opus-5-5-high",
    "claude-opus-5-thinking-high",
    "composer-2.5-fast",
    "grok-4.7-xhigh-fast",
    "gpt-5.6-sol-medium",
    "muse-spark-1.3-high",
]


class PickModelsTests(unittest.TestCase):
    def test_session_enum_maps_to_allowlisted_ensemble(self):
        mapping = MODULE.pick_mapping(SESSION_SLUGS)
        self.assertEqual(
            mapping,
            {
                "default": "grok-4.7-xhigh-fast",
                "executor": "composer-2.5-fast",
                "wise-owl": "claude-opus-5-5-high",
            },
        )

    def test_never_assigns_disallowed_families(self):
        mapping = MODULE.pick_mapping(
            [
                "claude-fable-5-1-thinking-high",
                "gpt-5.6-sol-medium",
                "muse-spark-1.3-high",
                "claude-sonnet-5-thinking-high",
            ]
        )
        self.assertEqual(mapping, MODULE.auto_mapping())

    def test_opus_max_and_xhigh_are_not_wise_owl(self):
        mapping = MODULE.pick_mapping(
            [
                "claude-opus-5-5-max",
                "claude-opus-5-5-xhigh",
                "grok-4.7-high",
                "composer-2.5",
            ]
        )
        self.assertEqual(mapping["wise-owl"], "auto")
        self.assertEqual(mapping["default"], "grok-4.7-high")
        self.assertEqual(mapping["executor"], "composer-2.5")

    def test_prefers_newer_opus_high(self):
        mapping = MODULE.pick_mapping(
            [
                "claude-opus-5-thinking-high",
                "claude-opus-5-5-high",
                "claude-opus-5-5-high-fast",
                "grok-4.7-high",
                "composer-2.5",
            ]
        )
        self.assertEqual(mapping["wise-owl"], "claude-opus-5-5-high")

    def test_prefers_newer_grok_and_higher_effort(self):
        mapping = MODULE.pick_mapping(
            [
                "cursor-grok-4.6-high",
                "cursor-grok-4.6-medium",
                "grok-4.7-medium",
                "grok-4.7-xhigh-fast",
                "cursor-grok-4.6-xhigh-fast",
            ]
        )
        self.assertEqual(mapping["default"], "grok-4.7-xhigh-fast")
        self.assertEqual(MODULE.effort_rank(mapping["default"]), 3)

    def test_prefers_non_fast_composer_when_both_exist(self):
        mapping = MODULE.pick_mapping(["composer-2.5-fast", "composer-2.5"])
        self.assertEqual(mapping["executor"], "composer-2.5")

    def test_accepts_unprefixed_grok_slug_as_default_family(self):
        mapping = MODULE.pick_mapping(["grok-4.7-xhigh-fast", "composer-2.5-fast"])
        self.assertEqual(mapping["default"], "grok-4.7-xhigh-fast")
        self.assertEqual(mapping["executor"], "composer-2.5-fast")

    def test_accepts_cursor_prefixed_grok_slug_as_default_family(self):
        mapping = MODULE.pick_mapping(["cursor-grok-4.7-xhigh-fast", "composer-2.5-fast"])
        self.assertEqual(mapping["default"], "cursor-grok-4.7-xhigh-fast")
        self.assertEqual(mapping["executor"], "composer-2.5-fast")

    def test_empty_detections_are_all_auto(self):
        self.assertEqual(MODULE.pick_mapping([]), MODULE.auto_mapping())

    def test_policy_auto_ignores_detected_slugs(self):
        from io import StringIO
        from unittest import mock

        buf = StringIO()
        with mock.patch("sys.stdout", buf):
            result = MODULE.main(
                ["--policy", "auto", "--format", "json", *SESSION_SLUGS]
            )
        self.assertEqual(result, 0)
        self.assertEqual(json.loads(buf.getvalue()), MODULE.auto_mapping())

    def test_cli_rule_format_contains_three_categories(self):
        from io import StringIO
        from unittest import mock

        buf = StringIO()
        with mock.patch("sys.stdout", buf):
            code = MODULE.main([*SESSION_SLUGS, "--format", "rule"])
        self.assertEqual(code, 0)
        text = buf.getvalue()
        self.assertIn("alwaysApply: true", text)
        self.assertIn("default: grok-4.7-xhigh-fast", text)
        self.assertIn("executor: composer-2.5-fast", text)
        self.assertIn("wise-owl: claude-opus-5-5-high", text)
        self.assertNotIn("code:", text)
        self.assertNotIn("judgment:", text)

    def test_cli_json_round_trip(self):
        from io import StringIO
        from unittest import mock

        buf = StringIO()
        with mock.patch("sys.stdout", buf):
            MODULE.main([*SESSION_SLUGS, "--format", "json"])
        data = json.loads(buf.getvalue())
        self.assertEqual(set(data), {"default", "executor", "wise-owl"})


if __name__ == "__main__":
    unittest.main()
