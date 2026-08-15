from pathlib import Path
import unittest

from core.evidence_contracts import load_evidence_contracts
from core.evidence_snapshot import build_evidence_snapshot
from core.invariant_classification import load_invariant_classification
from core.invariant_dispatcher import dispatch_invariant
from core.invariant_execution import execute_invariant
from core.evidence_state import EvidenceClaim, EvidenceState


ROOT = Path(__file__).resolve().parents[1]


class ArchitectureGovernanceTests(unittest.TestCase):
    def test_known_invariant_has_known_classification(self):
        classification = load_invariant_classification(ROOT)
        self.assertIn("fauna/mosquito_tigre/readable_as_mosquito", classification)
        self.assertTrue(classification["fauna/mosquito_tigre/readable_as_mosquito"].evidence_required)

    def test_evidence_required_invariant_has_matching_contract(self):
        classification = load_invariant_classification(ROOT)
        contracts = load_evidence_contracts(ROOT)
        key = "fauna/mosquito_tigre/readable_as_mosquito"
        classified = classification[key]
        contract = contracts[key]
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
