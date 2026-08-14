import unittest

from core.evidence_contract_executor import evaluate_evidence_contract
from core.evidence_state import EvidenceClaim, EvidenceState


class EvidenceContractExecutorTests(unittest.TestCase):
    ROOT = "."

    def test_perceptual_contract_routes_through_evidence(self):
        claim = EvidenceClaim(
            claim="candidate is visually readable as mosquito",
            state=EvidenceState.CONFIRMED,
            supporting_sources=("review/visual-001",),
        )
        result = evaluate_evidence_contract(
            self.ROOT,
            "fauna",
            "mosquito_tigre",
            "readable_as_mosquito",
            claim,
        )
        self.assertEqual(result.mechanism, "evidence_perceptual")
        self.assertEqual(result.evaluation.decision, "pass")

    def test_contradicted_claim_remains_fail(self):
        claim = EvidenceClaim(
            claim="candidate is visually readable as mosquito",
            state=EvidenceState.CONTRADICTED,
            contradicting_sources=("review/visual-002",),
        )
        result = evaluate_evidence_contract(
            self.ROOT,
            "fauna",
            "mosquito_tigre",
            "readable_as_mosquito",
            claim,
        )
        self.assertEqual(result.evaluation.decision, "fail")

    def test_unknown_claim_remains_unknown(self):
        claim = EvidenceClaim(
            claim="candidate is visually readable as mosquito",
            state=EvidenceState.UNKNOWN,
            supporting_sources=("review/uncertain-001",),
        )
        result = evaluate_evidence_contract(
            self.ROOT,
            "fauna",
            "mosquito_tigre",
            "readable_as_mosquito",
            claim,
        )
        self.assertEqual(result.evaluation.decision, "unknown")

    def test_missing_sources_are_rejected_by_explicit_support_policy(self):
        claim = EvidenceClaim(
            claim="candidate is visually readable as mosquito",
            state=EvidenceState.CONFIRMED,
        )
        with self.assertRaises(ValueError):
            evaluate_evidence_contract(
                self.ROOT,
                "fauna",
                "mosquito_tigre",
                "readable_as_mosquito",
                claim,
            )

    def test_deterministic_invariant_cannot_use_evidence_contract(self):
        claim = EvidenceClaim(
            claim="canonical value matches",
            state=EvidenceState.CONFIRMED,
            supporting_sources=("review/value-001",),
        )
        with self.assertRaises(ValueError):
            evaluate_evidence_contract(
                self.ROOT,
                "fauna",
                "mosquito_tigre",
                "very_small",
                claim,
            )

    def test_unknown_invariant_is_not_invented(self):
        claim = EvidenceClaim(
            claim="invented claim",
            state=EvidenceState.CONFIRMED,
            supporting_sources=("review/invented-001",),
        )
        with self.assertRaises(KeyError):
            evaluate_evidence_contract(
                self.ROOT,
                "fauna",
                "mosquito_tigre",
                "invented_invariant",
                claim,
            )


if __name__ == "__main__":
    unittest.main()
