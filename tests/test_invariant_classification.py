from pathlib import Path
import unittest

from core.invariant_taxonomy import (
    load_invariant_classification,
    load_invariant_taxonomy,
    validate_invariant_classification,
)


ROOT = Path(__file__).resolve().parents[1]


class InvariantClassificationTests(unittest.TestCase):

    def test_real_classification_loads(self):
        items = load_invariant_classification(ROOT)
        self.assertGreater(len(items), 0)

    def test_every_classification_uses_known_family(self):
        taxonomy = load_invariant_taxonomy(ROOT)
        items = load_invariant_classification(ROOT)
        self.assertTrue(all(item.family in taxonomy.families for item in items))

    def test_family_mechanisms_and_evidence_flags_are_consistent(self):
        taxonomy = load_invariant_taxonomy(ROOT)
        items = load_invariant_classification(ROOT)
        for item in items:
            family = taxonomy.families[item.family]
            mechanism = taxonomy.mechanisms[family.mechanism]
            self.assertEqual(item.mechanism, family.mechanism)
            self.assertEqual(item.evidence_required, mechanism.requires_evidence)

    def test_current_catalog_is_classified_exactly(self):
        errors = validate_invariant_classification(ROOT)
        self.assertEqual(errors, ())

    def test_evidence_bound_families_are_not_deterministic_shortcuts(self):
        taxonomy = load_invariant_taxonomy(ROOT)
        items = load_invariant_classification(ROOT)
        for item in items:
            mechanism = taxonomy.mechanisms[item.mechanism]
            if item.evidence_required:
                self.assertEqual(mechanism.mode, "evidence_boundary")

    def test_no_classification_is_duplicated(self):
        items = load_invariant_classification(ROOT)
        keys = [(item.catalog, item.entry, item.invariant) for item in items]
        self.assertEqual(len(keys), len(set(keys)))


if __name__ == "__main__":
    unittest.main()
