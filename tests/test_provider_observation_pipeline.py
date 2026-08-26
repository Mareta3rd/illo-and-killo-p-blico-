from __future__ import annotations

from pathlib import Path
import unittest

from core.evidence_state import EvidenceState
from core.external_evidence_adapter import ExternalEvidenceRecord
from core.provider_evidence_observation import (
    ProviderEvidencePipelineResult,
    run_provider_evidence_pipeline,
)


ROOT = Path(__file__).resolve().parents[1]
KEY = "fauna/mosquito_tigre/readable_as_mosquito"
GAG_KEY = "gag/001/composition/illo_primary"

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


class StaticProvider:
    def __init__(self, records):
        self.records = tuple(records)
        self.requested_keys = None

    def collect(self, requested_keys):
        self.requested_keys = requested_keys
        return self.records


class FailingProvider:
    def collect(self, requested_keys):
        raise RuntimeError("provider unavailable")


def record(key=KEY, state=EvidenceState.CONFIRMED):
    return ExternalEvidenceRecord(
        key,
        f"observation for {key}",
        state,
        supporting_sources=("image",) if state is EvidenceState.CONFIRMED else (),
        contradicting_sources=("image",) if state is EvidenceState.CONTRADICTED else (),
    )


class ProviderObservationPipelineTests(unittest.TestCase):
    def run_flow(self, state=EvidenceState.CONFIRMED, *, proposal=None, key=KEY):
        provider = StaticProvider((record(key, state),))
        result = run_provider_evidence_pipeline(
            "Crear un gag nuevo de Illo y Killo",
            ROOT,
            provider,
            "test-provider",
            "run-test",
            [key],
            proposal=proposal or PROPOSAL,
        )
        return provider, result

    def test_provider_observation_snapshot_and_pipeline_are_composed(self):
        provider, result = self.run_flow()

        self.assertIsInstance(result, ProviderEvidencePipelineResult)
        self.assertFalse(result.stopped)
        self.assertIsNotNone(result.observation)
        self.assertIsNotNone(result.snapshot)
        self.assertIsNotNone(result.pipeline)
        self.assertFalse(result.pipeline.stopped)
        self.assertEqual(provider.requested_keys, [KEY])
        self.assertEqual(result.pipeline.evidence_snapshot.claims, result.snapshot.claims)

    def test_confirmed_evidence_reaches_core_and_can_complete_pipeline(self):
        _, result = self.run_flow(EvidenceState.CONFIRMED)

        self.assertEqual(result.pipeline.evaluation.evaluation.decision, "accept")

    def test_contradicted_evidence_makes_core_continue(self):
        _, result = self.run_flow(EvidenceState.CONTRADICTED)

        self.assertTrue(result.stopped)
        self.assertEqual(result.stop_reason, "evaluation_requires_continuation")
        self.assertEqual(result.pipeline.evaluation.evaluation.decision, "continue")

    def test_unknown_evidence_makes_core_request_human_review(self):
        _, result = self.run_flow(EvidenceState.UNKNOWN)

        self.assertTrue(result.stopped)
        self.assertEqual(result.stop_reason, "evaluation_requires_human_review")
        self.assertEqual(result.pipeline.evaluation.evaluation.decision, "human_review")

    def test_provider_and_run_id_stay_outside_snapshot_claims(self):
        _, result = self.run_flow()

        self.assertEqual(result.observation.provider, "test-provider")
        self.assertEqual(result.observation.run_id, "run-test")
        self.assertNotIn("provider", result.snapshot.claims)
        self.assertNotIn("run_id", result.snapshot.claims)

    def test_claim_key_remains_literal(self):
        _, result = self.run_flow(key=GAG_KEY)

        self.assertIn(GAG_KEY, result.snapshot.claims)
        self.assertEqual(result.observation.records[0].claim_key, GAG_KEY)
        self.assertEqual(result.snapshot.canonical_evaluations, ())

    def test_provider_failure_stops_without_snapshot_or_acceptance(self):
        result = run_provider_evidence_pipeline(
            "Crear un gag nuevo de Illo y Killo",
            ROOT,
            FailingProvider(),
            "test-provider",
            "run-failure",
            [KEY],
            proposal=PROPOSAL,
        )

        self.assertTrue(result.stopped)
        self.assertIsNone(result.observation)
        self.assertIsNone(result.snapshot)
        self.assertIsNone(result.pipeline)
        self.assertIn("external_evidence_provider_failed", result.stop_reason)

    def test_conflicting_candidate_and_evidence_checks_request_review(self):
        proposal = {**PROPOSAL, "checks": {KEY: False}}
        _, result = self.run_flow(proposal=proposal)

        self.assertTrue(result.stopped)
        self.assertEqual(result.stop_reason, "evaluation_requires_human_review")
        self.assertEqual(result.pipeline.evaluation.evaluation.decision, "human_review")

    def test_three_segment_invariant_keeps_contract_evaluation(self):
        _, result = self.run_flow()

        evaluation = result.snapshot.canonical_evaluations[0]
        self.assertEqual(evaluation.invariant, "readable_as_mosquito")
        self.assertEqual(evaluation.evaluation.decision, "pass")


if __name__ == "__main__":
    unittest.main()