from pathlib import Path
import tempfile
import unittest
from dataclasses import FrozenInstanceError

from core.application import ApplicationRequest, ApplicationResult, run_application
from core.evidence_snapshot import EvidenceSnapshot
from core.evidence_state import EvidenceClaim, EvidenceState
from core.execution_artifact import read_execution_artifact
from core.external_evidence_adapter import ExternalEvidenceRecord
from core.provider_evidence_observation import ProviderEvidenceObservation


ROOT = Path(__file__).resolve().parents[1]
INVARIANT = "fauna/mosquito_tigre/readable_as_mosquito"
CANONICAL = "gag/001/composition/illo_primary"
PROPOSAL = {
    "characters": ["illo", "killo"],
    "elements": [
        {"id": "clavel", "intention": "character_identity"},
        {"id": "black_spots", "count": 2, "intention": "character_identity"},
    ],
    "checks": {
        "intention": True,
        "canon": True,
        "coherence": True,
        "reuse_intention": True,
    },
}


class FakeProvider:
    def __init__(self, state=EvidenceState.CONFIRMED, key=INVARIANT):
        self.state = state
        self.key = key
        self.calls = 0
        self.requested = None

    def collect(self, requested_keys):
        self.calls += 1
        self.requested = requested_keys
        return (ExternalEvidenceRecord(
            self.key,
            f"observation for {self.key}",
            self.state,
            supporting_sources=("image",) if self.state is EvidenceState.CONFIRMED else (),
            contradicting_sources=("image",) if self.state is EvidenceState.CONTRADICTED else (),
        ),)


class FailingProvider:
    def collect(self, requested_keys):
        raise RuntimeError("provider unavailable")


class ApplicationTests(unittest.TestCase):
    def request(self, provider, *, claims=(INVARIANT,), artifact_path=None, executor=None):
        executor = executor or (lambda prompt, iteration, previous: dict(PROPOSAL))
        return ApplicationRequest(
            idea="Crear un gag nuevo de Illo y Killo",
            root=ROOT,
            provider=provider,
            provider_name="fake-provider",
            run_id="application-run-001",
            requested_claims=claims,
            proposal=PROPOSAL,
            executor=executor,
            model="fake-model",
            image="gags/images/001_jamon.png",
            artifact_path=artifact_path,
        )

    def test_valid_request_runs_provider_and_core_once(self):
        provider = FakeProvider()
        executions = []
        result = run_application(self.request(provider, executor=lambda prompt, iteration, previous: executions.append(iteration) or dict(PROPOSAL)))

        self.assertEqual(provider.calls, 1)
        self.assertEqual(result.run_id, "application-run-001")
        self.assertEqual(executions, [1])
        self.assertIsInstance(result.observation, ProviderEvidenceObservation)
        self.assertIsInstance(result.snapshot, EvidenceSnapshot)
        self.assertIsNotNone(result.core)
        self.assertEqual(result.core.pipeline.evaluation.evaluation.decision, "accept")
        self.assertFalse(result.stopped)

    def test_requested_claims_and_metadata_remain_separate(self):
        provider = FakeProvider()
        result = run_application(self.request(provider, claims=(INVARIANT,)))
        self.assertEqual(provider.requested, (INVARIANT,))
        self.assertEqual(result.observation.provider, "fake-provider")
        self.assertEqual(result.observation.run_id, "application-run-001")
        self.assertNotIn("fake-provider", result.snapshot.claims)
        self.assertNotIn("application-run-001", result.snapshot.claims)

    def test_unknown_and_contradicted_states_reach_core_unchanged(self):
        for state, decision in ((EvidenceState.UNKNOWN, "human_review"), (EvidenceState.CONTRADICTED, "continue")):
            with self.subTest(state=state):
                result = run_application(self.request(FakeProvider(state)))
                self.assertEqual(result.observation.records[0].state, state)
                self.assertEqual(result.snapshot.get(INVARIANT).state, state)
                self.assertEqual(result.core.pipeline.evaluation.evaluation.decision, decision)

    def test_four_segment_claim_is_preserved_without_contract_evaluation(self):
        result = run_application(self.request(FakeProvider(EvidenceState.UNKNOWN, CANONICAL), claims=(CANONICAL,)))
        self.assertIn(CANONICAL, result.snapshot.claims)
        self.assertEqual(result.snapshot.canonical_evaluations, ())

    def test_provider_failure_stops_before_snapshot(self):
        result = run_application(self.request(FailingProvider()))
        self.assertEqual(result.run_id, "application-run-001")
        self.assertIsNone(result.observation)
        self.assertIsNone(result.snapshot)
        self.assertIsNone(result.core)
        self.assertIsNone(result.artifact)
        self.assertTrue(result.stopped)
        self.assertIn("external_evidence_provider_failed", result.stop_reason)

    def test_artifact_failure_preserves_execution_and_core_decision(self):
        executions = []
        request = self.request(
            FakeProvider(),
            artifact_path=ROOT / "missing" / "application.json",
            executor=lambda prompt, iteration, previous: executions.append(iteration) or dict(PROPOSAL),
        )
        result = run_application(request)

        self.assertEqual(result.run_id, request.run_id)
        self.assertIsNotNone(result.observation)
        self.assertIsNotNone(result.snapshot)
        self.assertIsNotNone(result.core)
        self.assertIsNone(result.artifact)
        self.assertIsNotNone(result.artifact_error)
        self.assertEqual(result.core.pipeline.evaluation.evaluation.decision, "accept")
        self.assertEqual(executions, [1])

    def test_core_stop_preserves_existing_result(self):
        result = run_application(self.request(FakeProvider(EvidenceState.UNKNOWN)))
        self.assertTrue(result.stopped)
        self.assertEqual(result.stop_reason, result.core.stop_reason)
        self.assertEqual(result.core.pipeline.evaluation.evaluation.decision, "human_review")

    def test_artifact_is_optional_and_contains_existing_result(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "application.json"
            provider = FakeProvider()
            result = run_application(self.request(provider, artifact_path=path))
            artifact = read_execution_artifact(path)
            self.assertEqual(result.artifact, artifact)
            self.assertEqual(artifact.run_id, "application-run-001")
            self.assertEqual(artifact.provider, "fake-provider")
            self.assertEqual(artifact.model, "fake-model")
            self.assertEqual(artifact.claims[0].state, EvidenceState.CONFIRMED)
            self.assertEqual(artifact.core_decision, "accept")
            self.assertEqual(provider.calls, 1)

    def test_without_artifact_path_writes_nothing(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "missing.json"
            result = run_application(self.request(FakeProvider()))
            self.assertIsNone(result.artifact)
            self.assertFalse(path.exists())

    def test_application_result_is_immutable(self):
        result = run_application(self.request(FakeProvider()))
        with self.assertRaises(FrozenInstanceError):
            result.stopped = True


if __name__ == "__main__":
    unittest.main()