import unittest

from core.evaluator import CandidateCheck, EvaluationReport
from core.loop import Evaluation
from core.semantic_audit import build_semantic_audit_record, fingerprint_candidate
from core.semantic_regression import SemanticRegression


class SemanticAuditTests(unittest.TestCase):
    def test_fingerprint_is_deterministic_for_mapping_order(self):
        a = {"b": 2, "a": {"y": True, "x": 1}}
        b = {"a": {"x": 1, "y": True}, "b": 2}
        self.assertEqual(fingerprint_candidate(a), fingerprint_candidate(b))

    def test_audit_record_preserves_decision_reason_and_regressions(self):
        report = EvaluationReport(
            Evaluation("continue", "semantic regressions detected: visual_readability"),
            (CandidateCheck("visual_readability", "fail", "lost readability"),),
        )
        regression = SemanticRegression(
            "visual_readability", "pass", "fail", "lost readability"
        )

        record = build_semantic_audit_record(2, {"x": 1}, report, (regression,))

        self.assertEqual(record.iteration, 2)
        self.assertEqual(record.decision, "continue")
        self.assertEqual(record.reason, "semantic regressions detected: visual_readability")
        self.assertEqual(record.regressions, (regression,))

    def test_building_record_does_not_mutate_candidate(self):
        candidate = {"checks": {"visual_readability": True}}
        before = {"checks": {"visual_readability": True}}
        report = EvaluationReport(
            Evaluation("accept", "all required quality checks passed"),
            (),
        )

        build_semantic_audit_record(1, candidate, report)

        self.assertEqual(candidate, before)


if __name__ == "__main__":
    unittest.main()
