import unittest

from core.evidence_state import (
    EvidenceClaim,
    EvidenceConflictError,
    EvidenceState,
    assess_claim,
)


class EvidenceStateTests(unittest.TestCase):

    def test_supporting_evidence_confirms_claim(self):
        result = assess_claim(
            "jamón is historically present",
            supporting_sources=("gags/001_jamon.md",),
        )

        self.assertIsInstance(result, EvidenceClaim)
        self.assertEqual(result.state, EvidenceState.CONFIRMED)

    def test_contradicting_evidence_contradicts_claim(self):
        result = assess_claim(
            "mosquito is canonically required",
            contradicting_sources=("data/objects.yaml",),
        )

        self.assertEqual(result.state, EvidenceState.CONTRADICTED)

    def test_missing_evidence_is_unknown(self):
        result = assess_claim("mosquito was used in a gag")

        self.assertEqual(result.state, EvidenceState.UNKNOWN)

    def test_conflicting_evidence_is_not_resolved_silently(self):
        with self.assertRaises(EvidenceConflictError):
            assess_claim(
                "claim",
                supporting_sources=("source/a",),
                contradicting_sources=("source/b",),
            )

    def test_sources_are_preserved(self):
        result = assess_claim(
            "claim",
            supporting_sources=("source/a", "source/b"),
        )

        self.assertEqual(result.supporting_sources, ("source/a", "source/b"))
        self.assertEqual(result.contradicting_sources, ())


if __name__ == "__main__":
    unittest.main()
