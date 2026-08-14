"""Integration tests for taxonomy -> contract -> evidence execution."""

from __future__ import annotations

import unittest

from core.evidence_contract_executor import evaluate_evidence_contract
from core.evidence_state import EvidenceClaim, EvidenceState, assess_claim


class EvidenceContractIntegrationTests(unittest.TestCase):
    ROOT = "."

    def test_perceptual_contract_accepts_confirmed_claim(self) -> None:
        claim = assess_claim(
            "candidate is visually readable as mosquito",
            ["visual-review-1"],
        )
        result = evaluate_evidence_contract(
            self.ROOT,
            "fauna",
            "mosquito_tigre",
            "readable_as_mosquito",
            claim,
        )
        self.assertEqual(result.family, "perceptual_semantic")
        self.assertEqual(result.mechanism, "evidence_perceptual")
        self.assertEqual(result.evaluation.decision, "pass")

    def test_context_contract_preserves_unknown(self) -> None:
        claim = assess_claim(
            "summer context activates the mosquito-tigre appearance rule"
        )
        result = evaluate_evidence_contract(
            self.ROOT,
            "fauna",
            "mosquito_tigre",
            "summer_context",
            claim,
        )
        self.assertEqual(result.family, "contextual_conditional")
        self.assertEqual(result.mechanism, "evidence_context")
        self.assertEqual(result.evaluation.decision, "unknown")

    def test_contradicted_claim_becomes_fail(self) -> None:
        claim = assess_claim(
            "candidate is visually readable as seagull",
            contradicting_sources=["visual-review-2"],
        )
        result = evaluate_evidence_contract(
            self.ROOT,
            "fauna",
            "gaviota",
            "readable_as_seagull",
            claim,
        )
        self.assertEqual(result.evaluation.decision, "fail")

    def test_deterministic_invariant_cannot_use_evidence_contract(self) -> None:
        claim = EvidenceClaim(
            claim="wrong deterministic claim",
            state=EvidenceState.CONFIRMED,
            supporting_sources=("source",),
        )
        with self.assertRaises(ValueError):
            evaluate_evidence_contract(
                self.ROOT,
                "characters",
                "killo",
                "clavel",
                claim,
            )

    def test_unknown_invariant_cannot_use_evidence_contract(self) -> None:
        claim = EvidenceClaim(
            claim="invented",
            state=EvidenceState.CONFIRMED,
            supporting_sources=("source",),
        )
        with self.assertRaises(KeyError):
            evaluate_evidence_contract(
                self.ROOT,
                "fauna",
                "gaviota",
                "invented_invariant",
                claim,
            )

    def test_claim_without_sources_is_rejected_by_explicit_support_policy(self) -> None:
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


if __name__ == "__main__":
    unittest.main()
