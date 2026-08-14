from pathlib import Path
import unittest

from core.loader import load_repository
from core.structural_constraints import load_structural_constraint
from core.structural_evaluator import evaluate_structural


class StructuralEvaluatorIntegrationTests(unittest.TestCase):
    ROOT = Path(__file__).resolve().parents[1]

    def test_green_scarf_passes_against_real_repository(self):
        result = evaluate_structural(
            "green_scarf",
            {"scarf": {"color": "green"}},
            **self._constraint("characters", "illo", "green_scarf"),
        )
        self.assertEqual(result.decision, "pass")

    def test_green_scarf_mismatch_fails_against_real_repository(self):
        result = evaluate_structural(
            "green_scarf",
            {"scarf": {"color": "red"}},
            **self._constraint("characters", "illo", "green_scarf"),
        )
        self.assertEqual(result.decision, "fail")

    def test_black_hooves_require_all_canonical_parts(self):
        result = evaluate_structural(
            "black_hooves",
            {"feet": {"type": "hoof", "color": "black"}},
            **self._constraint("characters", "illo", "black_hooves"),
        )
        self.assertEqual(result.decision, "pass")

    def test_black_hooves_partial_observation_is_unknown(self):
        result = evaluate_structural(
            "black_hooves",
            {"feet": {"type": "hoof"}},
            **self._constraint("characters", "illo", "black_hooves"),
        )
        self.assertEqual(result.decision, "unknown")

    def test_missing_constraint_is_not_inferred(self):
        self.assertIsNone(
            load_structural_constraint(
                self.ROOT, "characters", "illo", "invented_structure"
            )
        )

    def test_real_repository_catalog_remains_unchanged(self):
        knowledge = load_repository(self.ROOT)
        self.assertEqual(
            knowledge.data["characters"]["illo"]["invariants"][0],
            "green_scarf",
        )

    def _constraint(self, catalog, entry, invariant):
        required_paths, expected = load_structural_constraint(
            self.ROOT, catalog, entry, invariant
        )
        return {"required_paths": required_paths, "expected": expected}


if __name__ == "__main__":
    unittest.main()
