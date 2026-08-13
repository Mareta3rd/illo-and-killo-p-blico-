import unittest

from core.invariant_evaluator import evaluate_quantitative


class InvariantEvaluatorTests(unittest.TestCase):
    def test_value_inside_inclusive_range_passes(self):
        result = evaluate_quantitative("count", 4, minimum=2, maximum=8)
        self.assertEqual(result.decision, "pass")

    def test_minimum_boundary_passes(self):
        result = evaluate_quantitative("count", 2, minimum=2, maximum=8)
        self.assertEqual(result.decision, "pass")

    def test_maximum_boundary_passes(self):
        result = evaluate_quantitative("count", 8, minimum=2, maximum=8)
        self.assertEqual(result.decision, "pass")

    def test_value_below_minimum_fails(self):
        result = evaluate_quantitative("count", 1, minimum=2, maximum=8)
        self.assertEqual(result.decision, "fail")

    def test_value_above_maximum_fails(self):
        result = evaluate_quantitative("count", 9, minimum=2, maximum=8)
        self.assertEqual(result.decision, "fail")

    def test_non_numeric_observation_is_unknown(self):
        result = evaluate_quantitative("count", "unknown", minimum=2, maximum=8)
        self.assertEqual(result.decision, "unknown")

    def test_boolean_is_not_accepted_as_number(self):
        result = evaluate_quantitative("count", True, minimum=2, maximum=8)
        self.assertEqual(result.decision, "unknown")

    def test_invalid_bounds_are_unknown(self):
        result = evaluate_quantitative("count", 4, minimum="2", maximum=8)
        self.assertEqual(result.decision, "unknown")

    def test_unbounded_lower_side_is_supported(self):
        result = evaluate_quantitative("count", 4, maximum=8)
        self.assertEqual(result.decision, "pass")

    def test_unbounded_upper_side_is_supported(self):
        result = evaluate_quantitative("count", 4, minimum=2)
        self.assertEqual(result.decision, "pass")


if __name__ == "__main__":
    unittest.main()
