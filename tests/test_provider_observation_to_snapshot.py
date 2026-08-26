"""Tests for the provider observation -> Core snapshot boundary."""

from __future__ import annotations

from pathlib import Path
import unittest

from core.evidence_state import EvidenceState
from core.evidence_snapshot import EvidenceSnapshot
from core.external_evidence_adapter import ExternalEvidenceRecord
from core.provider_evidence_observation import (
    ProviderEvidenceObservation,
    collect_provider_observation,
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

    def test_multiple_canonical_records_share_the_same_snapshot_boundary(self):
        second = ExternalEvidenceRecord(
            claim_key="gag/001/composition/ham_primary",
            statement="The ham is the central object of Illo's boxing action.",
            state=EvidenceState.UNKNOWN,
            supporting_sources=(),
            contradicting_sources=(),
        )
        observation = freeze_provider_observation("gemini", "run-006", (self.record(), second))
        snapshot = snapshot_from_provider_observation(self.ROOT, observation)
        self.assertEqual(set(snapshot.claims), {self.KEY, "gag/001/composition/ham_primary"})
        self.assertEqual(snapshot.get("gag/001/composition/ham_primary").state, EvidenceState.UNKNOWN)

    def test_provider_collection_creates_observation_and_snapshot(self):
        class Provider:
            def collect(self, requested_keys):
                return (self_record,)

        self_record = self.record()
        observation, snapshot = collect_provider_observation(
            self.ROOT,
            Provider(),
            "gemini",
            "run-007",
            (self.KEY,),
        )

        self.assertEqual(observation.provider, "gemini")
        self.assertEqual(observation.run_id, "run-007")
        self.assertEqual(snapshot.get(self.KEY).state, EvidenceState.CONFIRMED)

    def test_collection_passes_requested_keys_without_mutation(self):
        requested = [self.KEY]
        seen = []

        class Provider:
            def collect(self, requested_keys):
                seen.append(requested_keys)
                return (self_record,)

        self_record = self.record()
        collect_provider_observation(self.ROOT, Provider(), "gemini", "run-008", requested)

        self.assertIs(seen[0], requested)
        self.assertEqual(requested, [self.KEY])

    def test_provider_error_does_not_create_snapshot(self):
        class Provider:
            def collect(self, requested_keys):
                raise RuntimeError("provider unavailable")

        with self.assertRaisesRegex(RuntimeError, "provider unavailable"):
            collect_provider_observation(self.ROOT, Provider(), "gemini", "run-009", (self.KEY,))

    def test_collection_preserves_all_evidence_states(self):
        for state in EvidenceState:
            with self.subTest(state=state):
                observation, snapshot = collect_provider_observation(
                    self.ROOT,
                    type("Provider", (), {"collect": lambda _self, _keys: (self.record(state),)})(),
                    "gemini",
                    f"run-{state.value}",
                    (self.KEY,),
                )
                self.assertEqual(observation.records[0].state, state)
                self.assertEqual(snapshot.get(self.KEY).state, state)

    def test_gag_claim_is_preserved_without_contract_evaluation(self):
        observation, snapshot = collect_provider_observation(
            self.ROOT,
            type("Provider", (), {"collect": lambda _self, _keys: (self.record(),)})(),
            "gemini",
            "run-010",
            (self.KEY,),
        )

        self.assertEqual(tuple(snapshot.claims), (self.KEY,))
        self.assertEqual(snapshot.canonical_evaluations, ())
        self.assertEqual(observation.records[0].claim_key, self.KEY)

    def test_three_segment_invariant_keeps_contract_evaluation(self):
        key = "fauna/mosquito_tigre/readable_as_mosquito"
        record = ExternalEvidenceRecord(
            key,
            "candidate is visually readable as mosquito",
            EvidenceState.CONFIRMED,
            supporting_sources=("gemini",),
        )

        _, snapshot = collect_provider_observation(
            str(Path(__file__).resolve().parents[1]),
            type("Provider", (), {"collect": lambda _self, _keys: (record,)})(),
            "gemini",
            "run-011",
            (key,),
        )

        self.assertEqual(snapshot.get(key).state, EvidenceState.CONFIRMED)
        self.assertEqual(len(snapshot.canonical_evaluations), 1)
        self.assertEqual(snapshot.canonical_evaluations[0].evaluation.decision, "pass")


if __name__ == "__main__":
    unittest.main()
