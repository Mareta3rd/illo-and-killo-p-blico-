import unittest

from core.structural_evaluator import evaluate_structural


class StructuralEvaluatorTests(unittest.TestCase):
    def test_required_path_present_passes(self):
        observed = {"scarf": {"color": "green"}}
        result = evaluate_structural("green_scarf", observed, required_paths=(("scarf", "color"),))
        self.assertEqual(result.decision, "pass")

    def test_missing_required_path_is_unknown(self):
        observed = {"scarf": {}}
        result = evaluate_structural("green_scarf", observed, required_paths=(("scarf", "color"),))
        self.assertEqual(result.decision, "unknown")

    def test_non_mapping_is_unknown(self):
        result = evaluate_structural("green_scarf", None, required_paths=(("scarf",),))
        self.assertEqual(result.decision, "unknown")

    def test_expected_structure_matches_passes(self):
        observed = {"tail": {"type": "flame", "length": "short"}}
        result = evaluate_structural(
            "short_flame_tail",
            observed,
            expected=((("tail", "type"), "flame"), (("tail", "length"), "short")),
        )
        self.assertEqual(result.decision, "pass")

    def test_expected_structure_mismatch_fails(self):
        observed = {"tail": {"type": "simple", "length": "short"}}
        result = evaluate_structural(
            "short_flame_tail",
            observed,
            expected=((("tail", "type"), "flame"), (("tail", "length"), "short")),
        )
        self.assertEqual(result.decision, "fail")

    def test_expected_structure_missing_is_unknown(self):
        observed = {"tail": {"type": "flame"}}
        result = evaluate_structural(
            "short_flame_tail",
            observed,
            expected=((("tail", "type"), "flame"), (("tail", "length"), "short")),
        )
        self.assertEqual(result.decision, "unknown")

    def test_type_mismatch_fails_without_coercion(self):
        observed = {"legs": {"count": "4"}}
        result = evaluate_structural(
            "four_legs",
            observed,
            expected=((("legs", "count"), 4),),
        )
        self.assertEqual(result.decision, "fail")

    def test_evaluator_does_not_mutate_observed(self):
        observed = {"scarf": {"color": "green"}}
        before = {"scarf": {"color": "green"}}
        evaluate_structural("green_scarf", observed, required_paths=(("scarf", "color"),))
        self.assertEqual(observed, before)


if __name__ == "__main__":
    unittest.main()
