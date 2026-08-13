from pathlib import Path
import copy
import unittest

import yaml

from core.invariant_taxonomy import load_invariant_taxonomy


ROOT = Path(__file__).resolve().parents[1]


class InvariantTaxonomyTests(unittest.TestCase):
    def test_real_taxonomy_loads(self):
        taxonomy = load_invariant_taxonomy(ROOT)
        self.assertEqual(taxonomy.version, "0.1")
        self.assertGreaterEqual(len(taxonomy.families), 6)
        self.assertGreaterEqual(len(taxonomy.mechanisms), 7)

    def test_every_family_points_to_known_mechanism(self):
        taxonomy = load_invariant_taxonomy(ROOT)
        for family in taxonomy.families.values():
            self.assertIn(family.mechanism, taxonomy.mechanisms)

    def test_evidence_families_require_evidence(self):
        taxonomy = load_invariant_taxonomy(ROOT)
        for name in (
            "perceptual_semantic",
            "stylistic_interpretive",
            "contextual_conditional",
        ):
            family = taxonomy.families[name]
            mechanism = taxonomy.mechanisms[family.mechanism]
            self.assertTrue(mechanism.requires_evidence)
            self.assertEqual(mechanism.unknown_action, "human_review")

    def test_deterministic_families_are_not_evidence_shortcuts(self):
        taxonomy = load_invariant_taxonomy(ROOT)
        for name in (
            "quantitative",
            "categorical",
            "structural",
            "relational",
        ):
            family = taxonomy.families[name]
            mechanism = taxonomy.mechanisms[family.mechanism]
            self.assertFalse(mechanism.requires_evidence)
            self.assertEqual(mechanism.unknown_action, "human_review")

    def test_taxonomy_file_has_no_duplicate_family_names(self):
        path = ROOT / "data" / "invariant_taxonomy.yaml"
        raw = yaml.safe_load(path.read_text(encoding="utf-8"))
        names = list(raw["families"].keys())
        self.assertEqual(len(names), len(set(names)))

    def test_loader_does_not_mutate_source_mapping(self):
        path = ROOT / "data" / "invariant_taxonomy.yaml"
        before = yaml.safe_load(path.read_text(encoding="utf-8"))
        snapshot = copy.deepcopy(before)
        load_invariant_taxonomy(ROOT)
        self.assertEqual(before, snapshot)


if __name__ == "__main__":
    unittest.main()
