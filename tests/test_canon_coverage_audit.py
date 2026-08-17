from pathlib import Path
import unittest

from core.evidence_contracts import load_evidence_contracts
from core.invariant_taxonomy import load_invariant_classification, load_invariant_taxonomy, validate_invariant_classification

ROOT = Path(__file__).resolve().parents[1]


class CanonCoverageAuditTests(unittest.TestCase):
    def test_current_canon_classification_is_complete(self):
        self.assertEqual(validate_invariant_classification(ROOT), ())

    def test_every_classified_family_uses_declared_taxonomy_mechanism(self):
        taxonomy = load_invariant_taxonomy(ROOT)
        for item in load_invariant_classification(ROOT):
            self.assertIn(item.family, taxonomy.families)
            self.assertIn(item.mechanism, taxonomy.mechanisms)
            self.assertEqual(item.mechanism, taxonomy.families[item.family].mechanism)
            self.assertEqual(
                item.evidence_required,
                taxonomy.mechanisms[item.mechanism].requires_evidence,
            )

    def test_every_evidence_required_invariant_has_a_contract(self):
        classification = load_invariant_classification(ROOT)
        contracts = {
            (item.catalog, item.entry, item.invariant): item
            for item in load_evidence_contracts(ROOT)
        }
        required = [
            item for item in classification
            if item.evidence_required
        ]
        self.assertTrue(required)
        for item in required:
            self.assertIn((item.catalog, item.entry, item.invariant), contracts)

    def test_unpopulated_taxonomy_families_are_explicitly_known(self):
        taxonomy = load_invariant_taxonomy(ROOT)
        classified_families = {
            item.family for item in load_invariant_classification(ROOT)
        }
        unpopulated = set(taxonomy.families) - classified_families
        self.assertEqual(unpopulated, {"quantitative", "relational"})


if __name__ == "__main__":
    unittest.main()
