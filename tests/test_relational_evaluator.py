import copy
import unittest

from core.relational_evaluator import evaluate_relational


class RelationalEvaluatorTests(unittest.TestCase):
    def test_equal_related_values_pass(self):
        result = evaluate_relational(
            "same_color",
            {"left": {"color": "green"}, "right": {"color": "green"}},
            left_path=("left", "color"),
            right_path=("right", "color"),
        )
        self.assertEqual(result.decision, "pass")

    def test_different_related_values_fail(self):
        result = evaluate_relational(
            "same_color",
            {"left": {"color": "green"}, "right": {"color": "red"}},
            left_path=("left", "color"),
            right_path=("right", "color"),
        )
        self.assertEqual(result.decision, "fail")

    def test_missing_left_path_is_unknown(self):
        result = evaluate_relational(
            "same_color",
            {"right": {"color": "green"}},
            left_path=("left", "color"),
            right_path=("right", "color"),
        )
        self.assertEqual(result.decision, "unknown")

    def test_missing_right_path_is_unknown(self):
        result = evaluate_relational(
            "same_color",
            {"left": {"color": "green"}},
            left_path=("left", "color"),
            right_path=("right", "color"),
        )
        self.assertEqual(result.decision, "unknown")

    def test_non_mapping_observation_is_unknown(self):
        result = evaluate_relational(
            "same_color",
            "green",
            left_path=("left",),
            right_path=("right",),
        )
        self.assertEqual(result.decision, "unknown")

    def test_different_types_fail_without_coercion(self):
        result = evaluate_relational(
            "same_value",
            {"left": 1, "right": "1"},
            left_path=("left",),
            right_path=("right",),
        )
        self.assertEqual(result.decision, "fail")

    def test_evaluator_does_not_mutate_observed(self):
        observed = {"left": {"color": "green"}, "right": {"color": "green"}}
        before = copy.deepcopy(observed)
        evaluate_relational(
            "same_color",
            observed,
            left_path=("left", "color"),
            right_path=("right", "color"),
        )
        self.assertEqual(observed, before)

    def test_invariant_name_is_preserved(self):
        result = evaluate_relational(
            "same_color",
            {"left": "green", "right": "green"},
            left_path=("left",),
            right_path=("right",),
        )
        self.assertEqual(result.invariant, "same_color")


if __name__ == "__main__":
    unittest.main()
