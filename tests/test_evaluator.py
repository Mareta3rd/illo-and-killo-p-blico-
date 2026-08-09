import unittest

from core.canon_guard import ValidationResult
from core.evaluator import evaluate_candidate


class EvaluatorTests(unittest.TestCase):

    def valid_validation(self):
        return ValidationResult(True, False, ())

    def test_accepts_when_all_required_checks_pass(self):
        candidate = {
            "checks": {
                "intention": True,
                "canon": True,
                "coherence": True,
                "reuse_intention": True,
            }
        }
        report = evaluate_candidate(candidate, self.valid_validation())
        self.assertEqual(report.evaluation.decision, "accept")
        self.assertEqual(len(report.checks), 4)

    def test_missing_required_check_requests_human_review(self):
        candidate = {"checks": {"intention": True, "canon": True}}
        report = evaluate_candidate(candidate, self.valid_validation())
        self.assertEqual(report.evaluation.decision, "human_review")
        self.assertIn("coherence", report.evaluation.reason)

    def test_failed_check_requests_another_iteration(self):
        candidate = {
            "checks": {
                "intention": True,
                "canon": True,
                "coherence": False,
                "reuse_intention": True,
            }
        }
        report = evaluate_candidate(candidate, self.valid_validation())
        self.assertEqual(report.evaluation.decision, "continue")
        self.assertIn("coherence", report.evaluation.reason)

    def test_unknown_check_requests_human_review(self):
        candidate = {
            "checks": {
                "intention": True,
                "canon": True,
                "coherence": {"decision": "unknown", "reason": "ambiguous"},
                "reuse_intention": True,
            }
        }
        report = evaluate_candidate(candidate, self.valid_validation())
        self.assertEqual(report.evaluation.decision, "human_review")

    def test_canon_review_overrides_quality_checks(self):
        candidate = {
            "checks": {
                "intention": True,
                "canon": True,
                "coherence": True,
                "reuse_intention": True,
            }
        }
        validation = ValidationResult(False, True, ())
        report = evaluate_candidate(candidate, validation)
        self.assertEqual(report.evaluation.decision, "human_review")

    def test_non_review_validation_failure_allows_continuation(self):
        candidate = {"checks": {}}
        validation = ValidationResult(False, False, ())
        report = evaluate_candidate(candidate, validation)
        self.assertEqual(report.evaluation.decision, "continue")


if __name__ == "__main__":
    unittest.main()
