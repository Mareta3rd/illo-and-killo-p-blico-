"""Tests for the real provider-observation -> Core snapshot boundary."""

from __future__ import annotations

import unittest

from core.evidence_state import EvidenceClaim, EvidenceState
from core.evidence_snapshot import EvidenceSnapshot
from core.external_evidence_adapter import ExternalEvidenceRecord
from core.provider_evidence_observation import (
    ProviderEvidenceObservation,
    freeze_provider_observation,
    snapshot_from_provider_observation,
)


class ProviderObservationToSnapshotTests(unittest.TestCase):
    ROOT = "gags"
    KEY = "gag/001/composition/illo_primary"

    def record(self, state=EvidenceState.CONFIRMED):
        return ExternalEvidenceRecord(
            claim_key=self.KEY,
            statement="Illo is the primary visual and narrative subject of the gag.",
            state=state,
            supporting_sources=("image",) if state is EvidenceState.CONFIRMED else (),
            contradicting_sources=("image",) if state is EvidenceState.CONTRADICTED else (),
        )

    def test_real_provider_observation_becomes_frozen_snapshot(self):
        observation = freeze_provider_observation("gemini", "run-001", (self.record(),))
        snapshot = snapshot_from_provider_observation(self.ROOT, observation)
        self.assertIsInstance(snapshot, EvidenceSnapshot)
        self.assertEqual(snapshot.get(self.KEY).state, EvidenceState.CONFIRMED)

    def test_unknown_crosses_boundary_unchanged(self):
        observation = freeze_provider_observation("gemini", "run-002", (self.record(EvidenceState.UNKNOWN),))
        snapshot = snapshot_from_provider_observation(self.ROOT, observation)
        self.assertEqual(snapshot.get(self.KEY).state, EvidenceState.UNKNOWN)
        self.assertEqual(snapshot.get(self.KEY).supporting_sources, ())
        self.assertEqual(snapshot.get(self.KEY).contradicting_sources, ())

    def test_contradicted_crosses_boundary_unchanged(self):
        observation = freeze_provider_observation("gemini", "run-003", (self.record(EvidenceState.CONTRADICTED),))
        snapshot = snapshot_from_provider_observation(self.ROOT, observation)
        self.assertEqual(snapshot.get(self.KEY).state, EvidenceState.CONTRADICTED)
        self.assertEqual(snapshot.get(self.KEY).contradicting_sources, ("image",))

    def test_provider_metadata_does_not_become_a_core_claim(self):
        observation = freeze_provider_observation("gemini", "run-004", (self.record(),))
        snapshot = snapshot_from_provider_observation(self.ROOT, observation)
        self.assertNotIn("provider", snapshot.claims)
        self.assertNotIn("run_id", snapshot.claims)

    def test_snapshot_is_independent_of_observation_tuple(self):
        records = (self.record(),)
        observation = ProviderEvidenceObservation("gemini", "run-005", records)
        snapshot = snapshot_from_provider_observation(self.ROOT, observation)
        self.assertEqual(tuple(snapshot.claims), (self.KEY,))
        self.assertEqual(observation.records[0], records[0])

    def test_non_canonical_records_remain_available_without_evaluation(self):
        record = ExternalEvidenceRecord(
            claim_key="external/source/item",
            statement="External source observation.",
            state=EvidenceState.UNKNOWN,
        )
        observation = freeze_provider_observation("gemini", "run-006", (record,))
        snapshot = snapshot_from_provider_observation(self.ROOT, observation)
        self.assertEqual(snapshot.get("external/source/item").state, EvidenceState.UNKNOWN)


if __name__ == "__main__":
    unittest.main()
