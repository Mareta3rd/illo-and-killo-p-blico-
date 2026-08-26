import unittest

from core.evidence_state import EvidenceState
from core.external_evidence_adapter import ExternalEvidenceRecord
from core.provider_evidence_observation import ProviderEvidenceObservation, freeze_provider_observation


class ProviderEvidenceObservationTests(unittest.TestCase):
    KEY = "gag/001/composition/illo_primary"

    def _record(self, state=EvidenceState.CONFIRMED, source="image"):
        return ExternalEvidenceRecord(
            claim_key=self.KEY,
            statement="Illo is the primary visual and narrative subject of the gag.",
            state=state,
            supporting_sources=(source,) if state is EvidenceState.CONFIRMED else (),
            contradicting_sources=(source,) if state is EvidenceState.CONTRADICTED else (),
        )

    def test_freezes_records_without_merging_states(self):
        first = self._record(EvidenceState.CONFIRMED, "image")
        second = self._record(EvidenceState.UNKNOWN, "gemini")
        observation_a = freeze_provider_observation("gemini", "run-1", (first,))
        observation_b = freeze_provider_observation("gemini", "run-2", (second,))

        self.assertEqual(observation_a.records[0].state, EvidenceState.CONFIRMED)
        self.assertEqual(observation_b.records[0].state, EvidenceState.UNKNOWN)
        self.assertNotEqual(observation_a, observation_b)

    def test_provider_and_run_identity_are_preserved(self):
        observation = freeze_provider_observation("gemini", "run-42", (self._record(),))

        self.assertEqual(observation.provider, "gemini")
        self.assertEqual(observation.run_id, "run-42")

    def test_records_are_immutable(self):
        observation = freeze_provider_observation("gemini", "run-1", (self._record(),))

        with self.assertRaises(AttributeError):
            observation.provider = "openai"

    def test_each_provider_observation_rejects_duplicate_claims(self):
        record = self._record()

        with self.assertRaises(ValueError):
            freeze_provider_observation("gemini", "run-1", (record, record))

    def test_unknown_remains_unknown_without_sources(self):
        observation = freeze_provider_observation(
            "gemini",
            "run-3",
            (self._record(EvidenceState.UNKNOWN, "image"),),
        )

        self.assertEqual(observation.records[0].state, EvidenceState.UNKNOWN)
        self.assertEqual(observation.records[0].supporting_sources, ())
        self.assertEqual(observation.records[0].contradicting_sources, ())

    def test_observation_requires_provider_and_run_identity(self):
        record = self._record()

        with self.assertRaises(ValueError):
            ProviderEvidenceObservation("", "run-1", (record,))
        with self.assertRaises(ValueError):
            ProviderEvidenceObservation("gemini", "", (record,))


if __name__ == "__main__":
    unittest.main()
