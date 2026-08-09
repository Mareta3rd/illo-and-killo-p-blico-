import tempfile
import unittest
from pathlib import Path

from core.context import build_context


ROOT = Path(__file__).resolve().parents[1]


class ContextTests(unittest.TestCase):

    def test_gag_context_contains_loaded_knowledge(self):
        context = build_context("Crear un gag nuevo de Illo y Killo", ROOT)
        self.assertEqual(context.route, "gag")
        self.assertFalse(context.requires_human_review)
        self.assertIn("characters", context.knowledge.data)
        self.assertIn("decisions", context.knowledge.data)

    def test_parody_context_routes_to_parody(self):
        context = build_context(
            "Illo y Killo en una parodia de Peaky Blinders", ROOT
        )
        self.assertEqual(context.route, "parody")

    def test_ambiguous_idea_requires_human_review(self):
        context = build_context("", ROOT)
        self.assertTrue(context.requires_human_review)
        self.assertEqual(context.route, "general")

    def test_source_files_remain_unchanged(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_root = Path(temp_dir)
            (temp_root / "data").mkdir()
            (temp_root / "docs").mkdir()
            (temp_root / "data" / "characters.yaml").write_text(
                "characters:\n  - name: Illo\n", encoding="utf-8"
            )
            (temp_root / "docs" / "RULES.md").write_text(
                "# Rules\n", encoding="utf-8"
            )

            before_data = (temp_root / "data" / "characters.yaml").read_text(
                encoding="utf-8"
            )
            before_docs = (temp_root / "docs" / "RULES.md").read_text(
                encoding="utf-8"
            )

            build_context("Crear un gag", temp_root)

            self.assertEqual(
                before_data,
                (temp_root / "data" / "characters.yaml").read_text(
                    encoding="utf-8"
                ),
            )
            self.assertEqual(
                before_docs,
                (temp_root / "docs" / "RULES.md").read_text(encoding="utf-8"),
            )


if __name__ == "__main__":
    unittest.main()
