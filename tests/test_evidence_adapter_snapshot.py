from pathlib import Path
import unittest

from core.evidence_adapter import EvidenceAdapter
from core.evidence_adapter_snapshot import build_snapshot_from_adapter
from core.evidence_state import EvidenceState

ROOT = Path(__file__).resolve().parents[1]


class EvidenceAdapterSnapshotTests(unittest.TestCase):
    def test_confirmed_observation_is_frozen_in_snapshot(self):
        adapter = EvidenceAdapter()
        snapshot = build_snapshot_from_adapter(
            ROOT,
            adapter,
            {"fauna/mosquito_tigre/readable_as_mosquito": "CONFIRMED"},
        )
        claim = snapshot.claims["fauna/mosquito_tigre/readable_as_mosquito"]
        self.assertEqual(claim.state, EvidenceState.CONFIRMED)
        with self.assertRaises(TypeError):
            snapshot.claims["new"] = claim

    def test_contradicted_observation_preserves_state_and_source(self):
        adapter = EvidenceAdapter()
        snapshot = build_snapshot_from_adapter(
            ROOT,
            adapter,
            {
                "fauna/mosquito_tigre/readable_as_mosquito": {
                    "state": "CONTRADICTED",
                    "source": "external-review",
                }
            },
        )
        claim = snapshot.claims["fauna/mosquito_tigre/readable_as_mosquito"]
        self.assertEqual(claim.state, EvidenceState.CONTRADICTED)
        self.assertIn("external-review", claim.contradicting_sources)

    def test_unknown_observation_remains_unknown(self):
        adapter = EvidenceAdapter()
        snapshot = build_snapshot_from_adapter(
            ROOT,
            adapter,
            {"fauna/mosquito_tigre/readable_as_mosquito": "UNKNOWN"},
        )
        self.assertEqual(
            snapshot.claims["fauna/mosquito_tigre/readable_as_mosquito"].state,
            EvidenceState.UNKNOWN,
        )

    def test_multiple_claims_are_kept_distinct(self):
        adapter = EvidenceAdapter()
        snapshot = build_snapshot_from_adapter(
            ROOT,
            adapter,
            {
                "fauna/mosquito_tigre/readable_as_mosquito": "CONFIRMED",
                "fauna/mosquito_tigre/summer_context": "UNKNOWN",
            },
        )
        self.assertEqual(len(snapshot.claims), 2)
        self.assertEqual(
            snapshot.claims["fauna/mosquito_tigre/readable_as_mosquito"].state,
            EvidenceState.CONFIRMED,
        )
        self.assertEqual(
            snapshot.claims["fauna/mosquito_tigre/summer_context"].state,
            EvidenceState.UNKNOWN,
        )

    def test_adapter_failure_becomes_unknown_without_bypassing_snapshot(self):
        adapter = EvidenceAdapter()
        snapshot = build_snapshot_from_adapter(
            ROOT,
            adapter,
            {"fauna/mosquito_tigre/readable_as_mosquito": {"error": "timeout"}},
        )
        self.assertEqual(
            snapshot.claims["fauna/mosquito_tigre/readable_as_mosquito"].state,
            EvidenceState.UNKNOWN,
        )


if __name__ == "__main__":
    unittest.main()
