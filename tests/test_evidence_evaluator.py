import unittest

from core.canon_guard import ValidationResult
from core.evidence_evaluator import evaluate_candidate_with_evidence
from core.evidence_state import EvidenceClaim, EvidenceState


class EvidenceEvaluatorTests(unittest.TestCase):

    def valid_validation(self):
        return ValidationResult(True, False, ())

    def complete_claims(self):
        return {
            "intention": EvidenceClaim("intention", EvidenceState.CONFIRMED),
            "canon": EvidenceClaim("canon", EvidenceState.CONFIRMED),
            "coherence": EvidenceClaim("coherence", EvidenceState.CONFIRMED),
            "reuse_intention": EvidenceClaim("reuse", EvidenceState.CONFIRMED),
        }

    def test_confirmed_evidence_can_complete_required_checks(self):
        candidate = {"name": "candidate"}
        report = evaluate_candidate_with_evidence(
            candidate,
            self.valid_validation(),
            self.complete_claims(),
        )

        self.assertEqual(report.evaluation.decision, "accept")
        self.assertEqual(len(report.checks), 4)

    def test_unknown_evidence_requests_human_review(self):
        claims = self.complete_claims()
        claims["coherence"] = EvidenceClaim("coherence", EvidenceState.UNKNOWN)

        report = evaluate_candidate_with_evidence(
            {"name": "candidate"},
            self.valid_validation(),
            claims,
        )

        self.assertEqual(report.evaluation.decision, "human_review")
        self.assertIn("coherence", report.evaluation.reason)

    def test_contradicted_evidence_requests_continuation(self):
        claims = self.complete_claims()
        claims["reuse_intention"] = EvidenceClaim(
            "reuse",
            EvidenceState.CONTRADICTED,
            contradicting_sources=("canon/example.md",),
        )

        report = evaluate_candidate_with_evidence(
            {"name": "candidate"},
            self.valid_validation(),
            claims,
        )

        self.assertEqual(report.evaluation.decision, "continue")
        self.assertIn("reuse_intention", report.evaluation.reason)

    def test_evidence_does_not_mutate_candidate(self):
        candidate = {
            "name": "candidate",
            "checks": {"intention": True},
        }
        before = {"name": "candidate", "checks": {"intention": True}}

        evaluate_candidate_with_evidence(
            candidate,
            self.valid_validation(),
            self.complete_claims(),
        )

        self.assertEqual(candidate, before)

    def test_conflicting_candidate_and_evidence_requests_human_review(self):
        candidate = {
            "checks": {
                "intention": False,
            }
        }

        report = evaluate_candidate_with_evidence(
            candidate,
            self.valid_validation(),
            self.complete_claims(),
        )

        self.assertEqual(report.evaluation.decision, "human_review")
        self.assertIn("intention", report.evaluation.reason)
        self.assertEqual(candidate["checks"]["intention"], False)


if __name__ == "__main__":
    unittest.main()
