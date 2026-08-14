import unittest

from core.evidence_boundary import evaluate_evidence_claim
from core.evidence_state import EvidenceClaim, EvidenceState


class EvidenceBoundaryIntegrationTests(unittest.TestCase):
    def test_confirmed_claim_becomes_passing_evaluation(self):
        claim = EvidenceClaim("readable_as_mosquito", EvidenceState.CONFIRMED)

        result = evaluate_evidence_claim(claim)

        self.assertEqual(result.invariant, "readable_as_mosquito")
        self.assertEqual(result.decision, "pass")

    def test_contradicted_claim_becomes_failing_evaluation(self):
        claim = EvidenceClaim("readable_as_mosquito", EvidenceState.CONTRADICTED)

        result = evaluate_evidence_claim(claim)

        self.assertEqual(result.decision, "fail")

    def test_unknown_claim_remains_unknown(self):
        claim = EvidenceClaim("readable_as_mosquito", EvidenceState.UNKNOWN)

        result = evaluate_evidence_claim(claim)

        self.assertEqual(result.decision, "unknown")

    def test_claim_sources_are_not_needed_for_decision(self):
        claim = EvidenceClaim(
            "readable_as_mosquito",
            EvidenceState.CONFIRMED,
            supporting_sources=("evidence://1",),
        )

        result = evaluate_evidence_claim(claim)

        self.assertEqual(result.decision, "pass")

    def test_claim_type_is_required(self):
        with self.assertRaises(TypeError):
            evaluate_evidence_claim("readable_as_mosquito")


if __name__ == "__main__":
    unittest.main()
