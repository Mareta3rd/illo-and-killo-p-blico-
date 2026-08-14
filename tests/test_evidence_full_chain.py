"""End-to-end semantic evidence chain regression tests."""

from __future__ import annotations

import unittest

from core.evidence_contract_executor import evaluate_evidence_contract
from core.evidence_state import EvidenceState, assess_claim
from core.invariant_dispatcher import dispatch_invariant


class EvidenceFullChainTests(unittest.TestCase):
    ROOT = "."

    def test_perceptual_full_chain(self) -> None:
        route = dispatch_invariant(
            self.ROOT, "fauna", "mosquito_tigre", "readable_as_mosquito"
        )
        self.assertEqual(route.mode, "evidence")
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
        self.assertEqual(result.evaluation.decision, "pass")

    def test_unknown_full_chain_reaches_human_review_state(self) -> None:
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
        self.assertEqual(claim.state, EvidenceState.UNKNOWN)
        self.assertEqual(result.evaluation.decision, "unknown")

    def test_contradiction_full_chain_remains_fail(self) -> None:
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

    def test_deterministic_route_cannot_enter_evidence_chain(self) -> None:
        with self.assertRaises(ValueError):
            evaluate_evidence_contract(
                self.ROOT,
                "characters",
                "killo",
                "clavel",
                assess_claim("wrong deterministic claim", ["source"]),
            )

    def test_unknown_invariant_cannot_enter_evidence_chain(self) -> None:
        with self.assertRaises(KeyError):
            evaluate_evidence_contract(
                self.ROOT,
                "gaviota",
                "missing",
                "invented",
                assess_claim("invented", ["source"]),
            )


if __name__ == "__main__":
    unittest.main()
