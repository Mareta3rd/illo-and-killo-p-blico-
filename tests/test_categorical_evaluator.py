import unittest

from core.categorical_evaluator import evaluate_categorical


class CategoricalEvaluatorTests(unittest.TestCase):
    def test_equal_value_passes(self):
        result = evaluate_categorical("color", "black", expected="black")
        self.assertEqual(result.decision, "pass")

    def test_different_value_fails(self):
        result = evaluate_categorical("color", "red", expected="black")
        self.assertEqual(result.decision, "fail")

    def test_missing_observed_value_is_unknown(self):
        result = evaluate_categorical("color", None, expected="black")
        self.assertEqual(result.decision, "unknown")

    def test_missing_expected_value_is_unknown(self):
        result = evaluate_categorical("color", "black", expected=None)
        self.assertEqual(result.decision, "unknown")

    def test_different_types_are_unknown(self):
        result = evaluate_categorical("very_small", True, expected="true")
        self.assertEqual(result.decision, "unknown")

    def test_boolean_values_compare_strictly(self):
        result = evaluate_categorical("very_small", True, expected=True)
        self.assertEqual(result.decision, "pass")

    def test_numeric_values_compare_strictly(self):
        result = evaluate_categorical("level", 2, expected=2)
        self.assertEqual(result.decision, "pass")

    def test_numeric_mismatch_fails(self):
        result = evaluate_categorical("level", 2, expected=3)
        self.assertEqual(result.decision, "fail")

    def test_invariant_name_is_preserved(self):
        result = evaluate_categorical("very_small", True, expected=True)
        self.assertEqual(result.invariant, "very_small")

    def test_evaluator_does_not_mutate_values(self):
        observed = {"value": "black"}
        expected = {"value": "black"}
        evaluate_categorical("marker", observed, expected=expected)
        self.assertEqual(observed, {"value": "black"})
        self.assertEqual(expected, {"value": "black"})


if __name__ == "__main__":
    unittest.main()
