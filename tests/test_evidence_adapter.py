import unittest

from core.canon_guard import ValidationResult
from core.evidence_adapter import claims_to_checks
from core.evidence_state import EvidenceClaim, EvidenceState
from core.evaluator import evaluate_candidate


class EvidenceAdapterTests(unittest.TestCase):

    def test_confirmed_claim_becomes_passing_check(self):
        claim = EvidenceClaim(
            claim="mosquito is a main gag",
            state=EvidenceState.CONFIRMED,
            supporting_sources=("gags/001.md",),
        )

        checks = claims_to_checks({"reuse_intention": claim})

        self.assertEqual(checks["reuse_intention"]["decision"], "pass")
        self.assertEqual(checks["reuse_intention"]["claim"], claim.claim)
        self.assertEqual(checks["reuse_intention"]["supporting_sources"], claim.supporting_sources)

    def test_contradicted_claim_becomes_failing_check(self):
        claim = EvidenceClaim(
            claim="mosquito is a main gag",
            state=EvidenceState.CONTRADICTED,
            contradicting_sources=("canon/characters.md",),
        )

        checks = claims_to_checks({"reuse_intention": claim})

        self.assertEqual(checks["reuse_intention"]["decision"], "fail")
        self.assertEqual(
            checks["reuse_intention"]["contradicting_sources"],
            claim.contradicting_sources,
        )

    def test_unknown_claim_remains_unknown(self):
        claim = EvidenceClaim(
            claim="mosquito is a main gag",
            state=EvidenceState.UNKNOWN,
        )

        checks = claims_to_checks({"reuse_intention": claim})

        self.assertEqual(checks["reuse_intention"]["decision"], "unknown")

    def test_adapter_output_is_consumable_by_evaluator(self):
        claims = {
            "intention": EvidenceClaim(
                claim="the asset has an explicit intention",
                state=EvidenceState.CONFIRMED,
            ),
            "canon": EvidenceClaim(
                claim="the asset is canon-compatible",
                state=EvidenceState.CONFIRMED,
            ),
            "coherence": EvidenceClaim(
                claim="the candidate is coherent",
                state=EvidenceState.CONFIRMED,
            ),
            "reuse_intention": EvidenceClaim(
                claim="reuse has an explicit intention",
                state=EvidenceState.CONFIRMED,
            ),
        }

        candidate = {"checks": claims_to_checks(claims)}
        report = evaluate_candidate(candidate, ValidationResult(True, False, ()))

        self.assertEqual(report.evaluation.decision, "accept")

    def test_unknown_evidence_reaches_human_review(self):
        claims = {
            "intention": EvidenceClaim("intention", EvidenceState.CONFIRMED),
            "canon": EvidenceClaim("canon", EvidenceState.CONFIRMED),
            "coherence": EvidenceClaim("coherence", EvidenceState.UNKNOWN),
            "reuse_intention": EvidenceClaim("reuse", EvidenceState.CONFIRMED),
        }

        candidate = {"checks": claims_to_checks(claims)}
        report = evaluate_candidate(candidate, ValidationResult(True, False, ()))

        self.assertEqual(report.evaluation.decision, "human_review")
        self.assertIn("coherence", report.evaluation.reason)

    def test_invalid_claim_type_is_rejected(self):
        with self.assertRaises(TypeError):
            claims_to_checks({"reuse_intention": object()})


if __name__ == "__main__":
    unittest.main()
