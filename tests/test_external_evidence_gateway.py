from pathlib import Path
import unittest

from core.evidence_state import EvidenceState
from core.external_evidence_adapter import ExternalEvidenceRecord
from core.external_evidence_gateway import collect_external_evidence
from core.simulated_evidence_provider import build_simulated_provider

ROOT = Path(__file__).resolve().parents[1]


class FailingProvider:
    def collect(self, requested_keys):
        raise RuntimeError("provider offline")


class ExternalEvidenceGatewayTests(unittest.TestCase):
    KEY = "fauna/mosquito_tigre/readable_as_mosquito"

    def record(self, state):
        return ExternalEvidenceRecord(
            self.KEY,
            "candidate is visually readable as mosquito",
            state,
            supporting_sources=("provider",) if state is EvidenceState.CONFIRMED else (),
            contradicting_sources=("provider",) if state is EvidenceState.CONTRADICTED else (),
        )

    def test_confirmed_provider_result_is_frozen(self):
        provider = build_simulated_provider((self.record(EvidenceState.CONFIRMED),))
        result = collect_external_evidence(ROOT, provider, (self.KEY,))

        self.assertFalse(result.stopped)
        self.assertEqual(result.missing_keys, ())
        self.assertIsNotNone(result.snapshot)
        self.assertEqual(result.claims[self.KEY].state, EvidenceState.CONFIRMED)
        self.assertEqual(result.snapshot.get(self.KEY).state, EvidenceState.CONFIRMED)

    def test_missing_requested_key_is_visible_and_not_invented(self):
        provider = build_simulated_provider(())
        result = collect_external_evidence(ROOT, provider, (self.KEY,))

        self.assertTrue(result.stopped)
        self.assertEqual(result.stop_reason, "external_evidence_missing_requested_keys")
        self.assertEqual(result.missing_keys, (self.KEY,))
        self.assertEqual(result.claims, {})

    def test_provider_failure_is_visible(self):
        result = collect_external_evidence(ROOT, FailingProvider(), (self.KEY,))

        self.assertTrue(result.stopped)
        self.assertIn("external_evidence_provider_failed", result.stop_reason)
        self.assertEqual(result.missing_keys, (self.KEY,))
        self.assertIsNone(result.snapshot)

    def test_requested_key_order_is_deterministic_and_duplicate_free(self):
        second = "fauna/mosquito_tigre/summer_context"
        provider = build_simulated_provider(
            (
                ExternalEvidenceRecord(second, "summer context", EvidenceState.UNKNOWN),
                self.record(EvidenceState.CONFIRMED),
            )
        )
        result = collect_external_evidence(
            ROOT,
            provider,
            (self.KEY, self.KEY, second),
        )

        self.assertFalse(result.stopped)
        self.assertEqual(tuple(result.claims), (self.KEY, second))
        self.assertEqual(result.missing_keys, ())

    def test_all_provider_states_survive_normalization(self):
        for state in EvidenceState:
            with self.subTest(state=state):
                provider = build_simulated_provider((self.record(state),))
                result = collect_external_evidence(ROOT, provider, (self.KEY,))
                self.assertFalse(result.stopped)
                self.assertEqual(result.snapshot.get(self.KEY).state, state)


if __name__ == "__main__":
    unittest.main()
