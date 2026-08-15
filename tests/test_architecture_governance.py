from pathlib import Path
import unittest

from core.evidence_contracts import load_evidence_contracts
from core.evidence_snapshot import build_evidence_snapshot
from core.invariant_taxonomy import (
    load_invariant_classification,
    load_invariant_taxonomy,
    validate_invariant_classification,
)
from core.invariant_dispatcher import dispatch_invariant
from core.invariant_execution import execute_invariant
from core.evidence_state import EvidenceClaim, EvidenceState

ROOT = Path(__file__).resolve().parents[1]


class ArchitectureGovernanceTests(unittest.TestCase):
    def test_known_invariant_has_known_classification(self):
        classification = load_invariant_classification(ROOT)
        found = [
            item for item in classification
            if item.catalog == "fauna"
            and item.entry == "mosquito_tigre"
            and item.invariant == "readable_as_mosquito"
        ]
        self.assertEqual(len(found), 1)
        self.assertTrue(found[0].evidence_required)

    def test_classification_matrix_is_structurally_consistent(self):
        self.assertEqual(validate_invariant_classification(ROOT), ())

    def test_evidence_required_invariant_has_matching_contract(self):
        contracts = load_evidence_contracts(ROOT)
        classified = next(
            item for item in load_invariant_classification(ROOT)
            if (item.catalog, item.entry, item.invariant)
            == ("fauna", "mosquito_tigre", "readable_as_mosquito")
        )
        contract = contracts["fauna/mosquito_tigre/readable_as_mosquito"]
        self.assertTrue(classified.evidence_required)
        self.assertEqual(classified.mechanism, contract.mechanism)

    def test_evidence_execution_cannot_bypass_contract(self):
        with self.assertRaises((KeyError, ValueError)):
            execute_invariant(
                str(ROOT),
                "fauna/mosquito_tigre/readable_as_mosquito",
                {"claim": "missing sources"},
            )

    def test_deterministic_invariant_cannot_cross_evidence_boundary(self):
        decision = dispatch_invariant(str(ROOT), "characters/killo/clavel")
        self.assertFalse(decision.evidence_required)
        with self.assertRaises((ValueError, KeyError)):
            execute_invariant(
                str(ROOT),
                "characters/killo/clavel",
                {"claim": "should not route through evidence"},
            )

    def test_canonical_evidence_is_frozen_before_execution(self):
        claims = {
            "fauna/mosquito_tigre/readable_as_mosquito": EvidenceClaim(
                "candidate is visually readable as mosquito",
                EvidenceState.CONFIRMED,
                supporting_sources=("visual-review-1",),
            )
        }
        snapshot = build_evidence_snapshot(str(ROOT), claims)
        self.assertEqual(len(snapshot), 1)
        with self.assertRaises(TypeError):
            snapshot.claims["new"] = claims[next(iter(claims))]


if __name__ == "__main__":
    unittest.main()
