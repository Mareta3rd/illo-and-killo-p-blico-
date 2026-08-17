import unittest

from core.evaluator import CandidateCheck, EvaluationReport
from core.loop import Evaluation
from core.semantic_regression import detect_semantic_regressions


class SemanticRegressionDetectorTests(unittest.TestCase):
    def _report(self, checks):
        return EvaluationReport(Evaluation("accept", "test"), tuple(checks))

    def test_passing_check_that_becomes_fail_is_regression(self):
        previous = self._report((CandidateCheck("canon", "pass", "ok"),))
        current = self._report((CandidateCheck("canon", "fail", "broken"),))

        regressions = detect_semantic_regressions(previous, current)

        self.assertEqual(len(regressions), 1)
        self.assertEqual(regressions[0].name, "canon")
        self.assertEqual(regressions[0].current_decision, "fail")

    def test_passing_check_that_becomes_unknown_is_regression(self):
        previous = self._report((CandidateCheck("readable_as_mosquito", "pass", "confirmed"),))
        current = self._report((CandidateCheck("readable_as_mosquito", "unknown", "insufficient"),))

        regressions = detect_semantic_regressions(previous, current)

        self.assertEqual(len(regressions), 1)
        self.assertEqual(regressions[0].current_decision, "unknown")

    def test_removed_passing_check_is_regression(self):
        previous = self._report((CandidateCheck("canon", "pass", "ok"),))
        current = self._report(())

        regressions = detect_semantic_regressions(previous, current)

        self.assertEqual(len(regressions), 1)
        self.assertEqual(regressions[0].current_decision, "missing")

    def test_preserved_or_new_passing_checks_are_not_regressions(self):
        previous = self._report((CandidateCheck("canon", "pass", "ok"),))
        current = self._report(
            (
                CandidateCheck("canon", "pass", "still ok"),
                CandidateCheck("coherence", "pass", "newly checked"),
            )
        )

        self.assertEqual(detect_semantic_regressions(previous, current), ())


if __name__ == "__main__":
    unittest.main()
