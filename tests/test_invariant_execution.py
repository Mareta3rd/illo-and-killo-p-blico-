import unittest
from pathlib import Path

from core.invariant_execution import evaluate_classified_evidence


ROOT = Path(__file__).resolve().parents[1]


class InvariantExecutionTests(unittest.TestCase):
    def test_perceptual_invariant_uses_evidence_boundary(self):
        route, result = evaluate_classified_evidence(
            str(ROOT), "fauna", "mosquito_tigre", "readable_as_mosquito", "pass"
        )
        self.assertEqual(route.mode, "evidence")
        self.assertEqual(route.mechanism, "evidence_perceptual")
        self.assertEqual(result.decision, "pass")

    def test_contextual_invariant_uses_evidence_boundary(self):
        route, result = evaluate_classified_evidence(
            str(ROOT), "fauna", "mosquito_tigre", "summer_context", "unknown"
        )
        self.assertEqual(route.mode, "evidence")
        self.assertEqual(route.mechanism, "evidence_context")
        self.assertEqual(result.decision, "unknown")

    def test_deterministic_invariant_cannot_enter_evidence_boundary(self):
        with self.assertRaises(ValueError):
            evaluate_classified_evidence(
                str(ROOT), "characters", "killo", "clavel", "pass"
            )

    def test_contradicted_evidence_stays_contradicted(self):
        route, result = evaluate_classified_evidence(
            str(ROOT), "fauna", "mosquito_tigre", "readable_as_mosquito", "fail"
        )
        self.assertEqual(route.mode, "evidence")
        self.assertEqual(result.decision, "fail")

    def test_unknown_invariant_is_not_inferred(self):
        with self.assertRaises(KeyError):
            evaluate_classified_evidence(
                str(ROOT), "fauna", "mosquito_tigre", "invented", "pass"
            )


if __name__ == "__main__":
    unittest.main()
