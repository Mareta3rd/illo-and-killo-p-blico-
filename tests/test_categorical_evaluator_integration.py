import unittest
from pathlib import Path

import yaml

from core.categorical_evaluator import evaluate_categorical


class CategoricalEvaluatorIntegrationTests(unittest.TestCase):
    ROOT = Path(__file__).resolve().parents[1]

    def _load_fauna(self):
        with (self.ROOT / "data" / "fauna.yaml").open("r", encoding="utf-8") as handle:
            return yaml.safe_load(handle)

    def _load_constraints(self):
        with (self.ROOT / "data" / "invariant_constraints.yaml").open("r", encoding="utf-8") as handle:
            return yaml.safe_load(handle)

    def test_very_small_constraint_is_read_from_real_repository(self):
        fauna = self._load_fauna()
        constraints = self._load_constraints()
        invariant = fauna["mosquito_tigre"]["invariants"][0]
        expected = constraints["categorical"]["fauna"]["mosquito_tigre"][invariant]["expected"]

        result = evaluate_categorical(invariant, True, expected)

        self.assertEqual(result.status, "pass")
        self.assertEqual(result.invariant, "very_small")

    def test_very_small_false_value_fails_against_real_constraint(self):
        constraints = self._load_constraints()
        expected = constraints["categorical"]["fauna"]["mosquito_tigre"]["very_small"]["expected"]

        result = evaluate_categorical("very_small", False, expected)

        self.assertEqual(result.status, "fail")

    def test_missing_observation_remains_unknown_against_real_constraint(self):
        constraints = self._load_constraints()
        expected = constraints["categorical"]["fauna"]["mosquito_tigre"]["very_small"]["expected"]

        result = evaluate_categorical("very_small", None, expected)

        self.assertEqual(result.status, "unknown")

    def test_missing_constraint_is_not_inferred(self):
        fauna = self._load_fauna()
        constraints = self._load_constraints()
        self.assertIn("very_small", fauna["mosquito_tigre"]["invariants"])
        self.assertNotIn("readable_as_mosquito", constraints["categorical"].get("fauna", {}).get("mosquito_tigre", {}))


if __name__ == "__main__":
    unittest.main()
