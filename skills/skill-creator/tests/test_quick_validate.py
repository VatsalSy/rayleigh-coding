from __future__ import annotations

import importlib.util
import sys
import tempfile
import unittest
from pathlib import Path


SCRIPT = Path(__file__).parents[1] / "scripts" / "quick_validate.py"
SPEC = importlib.util.spec_from_file_location("quick_validate_under_test", SCRIPT)
assert SPEC is not None and SPEC.loader is not None
quick_validate = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = quick_validate
SPEC.loader.exec_module(quick_validate)


class DescriptionLengthTests(unittest.TestCase):
    def write_skill(self, root: Path, description: str) -> Path:
        skill = root / "example"
        skill.mkdir()
        (skill / "SKILL.md").write_text(
            f"---\nname: example\ndescription: {description}\n---\n\n# Example\n",
            encoding="utf-8",
        )
        return skill

    def test_accepts_sixty_word_trigger_description(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            skill = self.write_skill(Path(temporary), " ".join(["trigger"] * 60))
            valid, message = quick_validate.validate_skill(skill)

        self.assertTrue(valid, message)

    def test_rejects_sixty_one_word_description(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            skill = self.write_skill(Path(temporary), " ".join(["trigger"] * 61))
            valid, message = quick_validate.validate_skill(skill)

        self.assertFalse(valid)
        self.assertIn("61 words", message)
        self.assertIn("trigger conditions only", message)

    def test_rejects_folder_name_mismatch(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            skill = self.write_skill(Path(temporary), "Use when asked for an example.")
            (skill / "SKILL.md").write_text(
                "---\nname: different\ndescription: Use when asked for an example.\n---\n",
                encoding="utf-8",
            )
            valid, message = quick_validate.validate_skill(skill)

        self.assertFalse(valid)
        self.assertIn("must match frontmatter name", message)


if __name__ == "__main__":
    unittest.main()
