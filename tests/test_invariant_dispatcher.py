import unittest
from pathlib import Path

from core.invariant_dispatcher import dispatch_invariant


ROOT = Path(__file__).resolve().parents[1]


class InvariantDispatcherTests(unittest.TestCase):
    def test_deterministic_invariant_routes_to_deterministic_boundary(self):
        route = dispatch_invariant(ROOT, "characters", "illo", "green_scarf")
        self.assertEqual(route.family, "structural")
        self.assertEqual(route.mechanism, "deterministic_structure")
        self.assertEqual(route.mode, "deterministic")
        self.assertFalse(route.evidence_required)

    def test_evidence_invariant_routes_to_evidence_boundary(self):
        route = dispatch_invariant(ROOT, "fauna", "mosquito_tigre", "readable_as_mosquito")
        self.assertEqual(route.family, "perceptual_semantic")
        self.assertEqual(route.mechanism, "evidence_perceptual")
        self.assertEqual(route.mode, "evidence")
        self.assertTrue(route.evidence_required)

    def test_contextual_evidence_invariant_routes_to_evidence_boundary(self):
        route = dispatch_invariant(ROOT, "fauna", "mosquito_tigre", "summer_context")
        self.assertEqual(route.mechanism, "evidence_context")
        self.assertEqual(route.mode, "evidence")

    def test_unknown_invariant_is_not_inferred(self):
        with self.assertRaises(KeyError):
            dispatch_invariant(ROOT, "fauna", "mosquito_tigre", "invented_invariant")

    def test_route_preserves_canonical_identity(self):
        route = dispatch_invariant(ROOT, "characters", "killo", "black_hooves")
        self.assertEqual(
            (route.catalog, route.entry, route.invariant),
            ("characters", "killo", "black_hooves"),
        )


if __name__ == "__main__":
    unittest.main()
