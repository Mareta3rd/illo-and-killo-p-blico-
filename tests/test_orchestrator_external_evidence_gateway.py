from pathlib import Path
import unittest

from core.external_evidence_adapter import ExternalEvidenceRecord
from core.external_evidence_gateway import ExternalEvidenceGateway
from core.evidence_state import EvidenceState
from core.orchestrator import run_vertical_slice

ROOT = Path(__file__).resolve().parents[1]
KEY = "fauna/mosquito_tigre/readable_as_mosquito"


class StaticProvider:
    def __init__(self, records):
        self.records = tuple(records)

    def collect(self, requested_keys):
        return tuple(
            record
            for key in requested_keys
            for record in self.records
            if record.claim_key == key
        )


class FailingProvider:
    def collect(self, requested_keys):
        raise RuntimeError("provider unavailable")


class OrchestratorExternalEvidenceGatewayTests(unittest.TestCase):
    def _record(self, state):
        return ExternalEvidenceRecord(
            KEY,
            "candidate is visually readable as mosquito",
            state,
            supporting_sources=("simulated-provider",)
            if state is EvidenceState.CONFIRMED
            else (),
            contradicting_sources=("simulated-provider",)
            if state is EvidenceState.CONTRADICTED
            else (),
        )

    def _executor(self, prompt, iteration, previous):
        return {
            "name": "gateway-candidate",
            "checks": {
                "intention": True,
                "canon": True,
                "coherence": True,
                "reuse_intention": True,
            },
        }

    def test_confirmed_gateway_evidence_reaches_pipeline_boundary(self):
        gateway = ExternalEvidenceGateway(ROOT)
        result = gateway.collect(
            StaticProvider((self._record(EvidenceState.CONFIRMED),)),
            (KEY,),
        )
        self.assertEqual(result.claims[KEY].state, EvidenceState.CONFIRMED)

    def test_contradicted_gateway_evidence_preserves_contradiction(self):
        gateway = ExternalEvidenceGateway(ROOT)
        result = gateway.collect(
            StaticProvider((self._record(EvidenceState.CONTRADICTED),)),
            (KEY,),
        )
        self.assertEqual(result.claims[KEY].state, EvidenceState.CONTRADICTED)
        self.assertIn(
            "simulated-provider",
            result.claims[KEY].contradicting_sources,
        )

    def test_missing_gateway_evidence_is_explicit(self):
        gateway = ExternalEvidenceGateway(ROOT)
        result = gateway.collect(StaticProvider(()), (KEY,))
        self.assertEqual(result.missing_keys, (KEY,))
        self.assertIsNotNone(result.snapshot) if result.claims else self.assertIsNone(result.snapshot)
        self.assertTrue(result.stopped)

    def test_provider_failure_is_explicit(self):
        gateway = ExternalEvidenceGateway(ROOT)
        result = gateway.collect(FailingProvider(), (KEY,))
        self.assertTrue(result.stopped)
        self.assertTrue(result.stop_reason.startswith("external_evidence_provider_failed:"))
        self.assertIsNone(result.snapshot)

    def test_gateway_snapshot_can_feed_real_orchestrator_without_direct_provider_access(self):
        gateway = ExternalEvidenceGateway(ROOT)
        collection = gateway.collect(
            StaticProvider((self._record(EvidenceState.CONFIRMED),)),
            (KEY,),
        )
        self.assertIsNotNone(collection.snapshot)
        result = run_vertical_slice(
            "Create a mosquito-tigre candidate",
            ROOT,
            self._executor,
            evidence_claims=collection.snapshot.claims,
        )
        self.assertIsNotNone(result)
        self.assertIsNotNone(result.execution_audit)


if __name__ == "__main__":
    unittest.main()
