import unittest

from core.evidence_claim_router import EvidenceClaimKey, evaluate_canonical_evidence_claims
from core.evidence_state import assess_claim


class EvidenceClaimRouterTests(unittest.TestCase):
    ROOT = "."

    def test_canonical_key_parses(self):
        key = EvidenceClaimKey.parse("fauna/mosquito_tigre/readable_as_mosquito")
        self.assertEqual(key.catalog, "fauna")
        self.assertEqual(key.entry, "mosquito_tigre")
        self.assertEqual(key.invariant, "readable_as_mosquito")

    def test_malformed_key_is_rejected(self):
        with self.assertRaises(ValueError):
            EvidenceClaimKey.parse("fauna/mosquito_tigre")

    def test_confirmed_claim_uses_real_contract(self):
        claim = assess_claim(
            "candidate is visually readable as mosquito",
            supporting_sources=["visual-review-1"],
        )
        results = evaluate_canonical_evidence_claims(
            self.ROOT,
            {"fauna/mosquito_tigre/readable_as_mosquito": claim},
        )
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0].evaluation.decision, "pass")
        self.assertEqual(results[0].mechanism, "evidence_perceptual")

    def test_deterministic_invariant_is_rejected_by_route(self):
        claim = assess_claim("not applicable", supporting_sources=["source"])
        with self.assertRaises(ValueError):
            evaluate_canonical_evidence_claims(
                self.ROOT,
                {"characters/killo/clavel": claim},
            )

    def test_unknown_invariant_is_not_invented(self):
        claim = assess_claim("invented", supporting_sources=["source"])
        with self.assertRaises(KeyError):
            evaluate_canonical_evidence_claims(
                self.ROOT,
                {"fauna/gaviota/invented": claim},
            )

    def test_multiple_claims_are_evaluated_independently(self):
        claims = {
            "fauna/mosquito_tigre/readable_as_mosquito": assess_claim(
                "candidate is visually readable as mosquito",
                supporting_sources=["visual-review-1"],
            ),
            "fauna/gaviota/readable_as_seagull": assess_claim(
                "candidate is visually readable as seagull",
                contradicting_sources=["visual-review-2"],
            ),
        }
        results = evaluate_canonical_evidence_claims(self.ROOT, claims)
        self.assertEqual([item.evaluation.decision for item in results], ["pass", "fail"])


if __name__ == "__main__":
    unittest.main()
