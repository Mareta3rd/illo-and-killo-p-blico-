import unittest
from pathlib import Path

from core.loader import load_repository


class LoaderTests(unittest.TestCase):
    def test_loads_core_repository_knowledge(self):
        root = Path(__file__).resolve().parents[1]
        knowledge = load_repository(root)

        self.assertIn("characters", knowledge.data)
        self.assertIn("decisions", knowledge.data)
        self.assertIn("objects", knowledge.data)
        self.assertIn("fauna", knowledge.data)
        self.assertIn("heritage", knowledge.data)
        self.assertIn("metrics", knowledge.data)
        self.assertIn("gag_001_claims", knowledge.data)
        self.assertIn("CORE_SPEC.md", knowledge.markdown)
        self.assertIn("PRINCIPLES.md", knowledge.markdown)

    def test_loader_does_not_mutate_source_files(self):
        root = Path(__file__).resolve().parents[1]
        before = (root / "data" / "characters.yaml").read_text(encoding="utf-8")

        load_repository(root)

        after = (root / "data" / "characters.yaml").read_text(encoding="utf-8")
        self.assertEqual(before, after)

    def test_loader_reads_gag_claims_as_mapping(self):
        root = Path(__file__).resolve().parents[1]
        knowledge = load_repository(root)

        claims = knowledge.data["gag_001_claims"]

        self.assertIn("gag/001/composition/ham_primary", claims)
        self.assertEqual(claims["gag/001/composition/arsa_primary"]["narrative_role"], "primary")


if __name__ == "__main__":
    unittest.main()
