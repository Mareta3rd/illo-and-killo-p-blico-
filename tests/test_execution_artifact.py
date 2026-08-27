import json
import tempfile
import unittest
from pathlib import Path

from core.evidence_snapshot import build_evidence_snapshot
from core.evidence_state import EvidenceClaim, EvidenceState
from core.execution_artifact import (
    ExecutionArtifact,
    build_execution_artifact,
    deserialize_execution_artifact,
    read_execution_artifact,
    serialize_execution_artifact,
    write_execution_artifact,
)
from core.external_evidence_adapter import ExternalEvidenceRecord
from core.provider_evidence_observation import freeze_provider_observation


ROOT = Path(__file__).resolve().parents[1]
CANONICAL_KEY = "gag/001/composition/illo_primary"
INVARIANT_KEY = "fauna/mosquito_tigre/readable_as_mosquito"


class ExecutionArtifactTests(unittest.TestCase):
    def artifact(self):
        records = (
            ExternalEvidenceRecord(
                CANONICAL_KEY,
                "Illo is the primary visual and narrative subject of the gag.",
                EvidenceState.UNKNOWN,
            ),
            ExternalEvidenceRecord(
                INVARIANT_KEY,
                "The image is readable as a mosquito.",
                EvidenceState.CONFIRMED,
                supporting_sources=("image",),
            ),
        )
        observation = freeze_provider_observation("gemini", "run-001", records)
        snapshot = build_evidence_snapshot(
            str(ROOT),
            {
                CANONICAL_KEY: EvidenceClaim(
                    records[0].statement, records[0].state
                ),
                INVARIANT_KEY: EvidenceClaim(
                    records[1].statement,
                    records[1].state,
                    supporting_sources=("image",),
                ),
            },
        )
        return build_execution_artifact(
            observation,
            snapshot,
            model="gemini-3.6-flash",
            image="gags/images/001_jamon.png",
            core_decision="accept",
        )

    def test_serialization_is_stable_and_sorted(self):
        payload = serialize_execution_artifact(self.artifact())
        self.assertEqual(payload, serialize_execution_artifact(self.artifact()))
        self.assertLess(payload.index('"canonical_evaluations"'), payload.index('"claims"'))
        self.assertTrue(payload.endswith("\n"))

    def test_deserialization_and_round_trip_are_identical(self):
        artifact = self.artifact()
        loaded = deserialize_execution_artifact(serialize_execution_artifact(artifact))
        self.assertEqual(loaded, artifact)
        self.assertEqual(serialize_execution_artifact(loaded), serialize_execution_artifact(artifact))

    def test_file_persistence_uses_utf8_and_preserves_run_id(self):
        artifact = self.artifact()
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "run.json"
            write_execution_artifact(path, artifact)
            self.assertEqual(read_execution_artifact(path).run_id, "run-001")
            self.assertEqual(path.read_text(encoding="utf-8"), serialize_execution_artifact(artifact))

    def test_metadata_stays_outside_claims_and_states_sources_are_preserved(self):
        artifact = self.artifact()
        self.assertEqual(
            [claim.claim_key for claim in artifact.claims],
            [INVARIANT_KEY, CANONICAL_KEY],
        )
        self.assertEqual(artifact.provider, "gemini")
        self.assertEqual(artifact.model, "gemini-3.6-flash")
        self.assertEqual(artifact.claims[0].state, EvidenceState.CONFIRMED)
        self.assertEqual(artifact.claims[1].state, EvidenceState.UNKNOWN)
        self.assertEqual(artifact.claims[0].supporting_sources, ("image",))
        self.assertEqual(artifact.canonical_evaluations[0].decision, "pass")
        self.assertEqual(artifact.core_decision, "accept")

    def test_four_segment_canonical_claim_has_no_contract_evaluation(self):
        artifact = self.artifact()
        self.assertEqual(
            [evaluation.invariant for evaluation in artifact.canonical_evaluations],
            ["readable_as_mosquito"],
        )
        self.assertIn(CANONICAL_KEY, [claim.claim_key for claim in artifact.claims])

    def test_all_states_and_core_decisions_are_data_only(self):
        for state in EvidenceState:
            record = ExternalEvidenceRecord("claim/key", "statement", state)
            observation = freeze_provider_observation("provider", "run", (record,))
            snapshot = build_evidence_snapshot(
                str(ROOT), {"claim/key": EvidenceClaim("statement", state)}
            )
            artifact = build_execution_artifact(
                observation, snapshot, model="model", image="image.png", core_decision=None
            )
            loaded = deserialize_execution_artifact(serialize_execution_artifact(artifact))
            self.assertEqual(loaded.claims[0].state, state)
            self.assertIsNone(loaded.core_decision)

    def test_secret_fields_and_invalid_payloads_are_rejected(self):
        payload = self.artifact().to_dict()
        payload["api_key"] = "secret"
        with self.assertRaises(ValueError):
            deserialize_execution_artifact(json.dumps(payload))
        invalid = self.artifact().to_dict()
        invalid["claims"][0]["state"] = "accept"
        with self.assertRaises(ValueError):
            deserialize_execution_artifact(json.dumps(invalid))

    def test_unknown_schema_version_is_rejected(self):
        payload = self.artifact().to_dict()
        payload["schema_version"] = 2
        with self.assertRaises(ValueError):
            deserialize_execution_artifact(json.dumps(payload))

    def test_artifact_does_not_create_a_new_core_decision(self):
        loaded = deserialize_execution_artifact(serialize_execution_artifact(self.artifact()))
        self.assertEqual(loaded.core_decision, "accept")
        self.assertFalse(hasattr(loaded, "evaluate"))
        self.assertFalse(hasattr(loaded, "run_pipeline"))


if __name__ == "__main__":
    unittest.main()