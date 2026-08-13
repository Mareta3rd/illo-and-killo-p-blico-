import unittest
from pathlib import Path

from core.invariant_evaluator import evaluate_quantitative
from core.loader import load_repository


ROOT = Path(__file__).resolve().parents[1]


class InvariantEvaluatorIntegrationTests(unittest.TestCase):
    def test_killo_canonical_count_is_consumed_as_numeric_bounds(self):
        knowledge = load_repository(ROOT)
        rule = knowledge.data["characters"]["killo"]["body"]["spots"]["count"]

        result = evaluate_quantitative(
            "count",
            4,
            minimum=rule["min"],
            maximum=rule["max"],
        )

        self.assertEqual(result.decision, "pass")

    def test_killo_canonical_lower_violation_is_rejected(self):
        knowledge = load_repository(ROOT)
        rule = knowledge.data["characters"]["killo"]["body"]["spots"]["count"]

        result = evaluate_quantitative(
            "count",
            1,
            minimum=rule["min"],
            maximum=rule["max"],
        )

        self.assertEqual(result.decision, "fail")

    def test_killo_canonical_upper_violation_is_rejected(self):
        knowledge = load_repository(ROOT)
        rule = knowledge.data["characters"]["killo"]["body"]["spots"]["count"]

        result = evaluate_quantitative(
            "count",
            9,
            minimum=rule["min"],
            maximum=rule["max"],
        )

        self.assertEqual(result.decision, "fail")

    def test_missing_observation_remains_unknown(self):
        knowledge = load_repository(ROOT)
        rule = knowledge.data["characters"]["killo"]["body"]["spots"]["count"]

        result = evaluate_quantitative(
            "count",
            None,
            minimum=rule["min"],
            maximum=rule["max"],
        )

        self.assertEqual(result.decision, "unknown")


if __name__ == "__main__":
    unittest.main()
