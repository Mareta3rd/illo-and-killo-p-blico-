import unittest
from pathlib import Path

from core.evidence import build_evidence


ROOT = Path(__file__).resolve().parents[1]


class EvidenceTests(unittest.TestCase):

    def test_detects_clavel_as_canonical_invariant(self):
        evidence = build_evidence(ROOT)

        self.assertIn("clavel", evidence.canonical_invariants["killo"])

    def test_detects_existing_gag_history(self):
        evidence = build_evidence(ROOT)

        self.assertIn("001_jamon.md", evidence.gag_history)
        self.assertIn("002_pesca.md", evidence.gag_history)

    def test_detects_historical_asset_from_gag_text(self):
        evidence = build_evidence(ROOT)

        self.assertIn("jamón", evidence.historical_assets)
        self.assertIn("chorizo", evidence.historical_assets)

    def test_unknown_asset_is_not_invented_as_historical(self):
        evidence = build_evidence(ROOT)

        self.assertNotIn("mosquito_tigre", evidence.historical_assets)

    def test_evidence_does_not_modify_repository(self):
        before = (ROOT / "data" / "characters.yaml").read_text(
            encoding="utf-8"
        )

        build_evidence(ROOT)

        after = (ROOT / "data" / "characters.yaml").read_text(
            encoding="utf-8"
        )

        self.assertEqual(before, after)


if __name__ == "__main__":
    unittest.main()
