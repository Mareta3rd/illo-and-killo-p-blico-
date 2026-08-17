from pathlib import Path
import unittest

from core.evidence_adapter import DefaultEvidenceAdapter
from core.evidence_adapter_snapshot import build_snapshot_from_adapter
from core.evidence_state import EvidenceState
from core.orchestrator import run_vertical_slice

ROOT = Path(__file__).resolve().parents[1]


class SimulatedProviderEndToEndTests(unittest.TestCase):
    def _run(self, verdict):
        adapter = DefaultEvidenceAdapter()
        snapshot = build_snapshot_from_adapter(
            ROOT,
            adapter,
            {
                "fauna/mosquito_tigre/readable_as_mosquito": {
                    "claim": "fauna/mosquito_tigre/readable_as_mosquito",
                    "verdict": verdict,
                    "source": "simulated-provider",
                }
            },
        )

        calls = []

        def executor(prompt, iteration, previous):
            calls.append(iteration)
            return {
                "name": "simulated-candidate",
                "checks": {
                    "intention": True,
                    "canon": True,
                    "coherence": True,
                    "reuse_intention": True,
                },
            }

        result = run_vertical_slice(
            "Create a mosquito-tigre candidate",
            ROOT,
            executor,
            evidence_claims=snapshot.claims,
            max_iterations=3,
        )
        return result, snapshot, calls

    def test_confirmed_provider_evidence_reaches_accept(self):
        result, snapshot, calls = self._run("confirmed")
        claim = snapshot.claims["fauna/mosquito_tigre/readable_as_mosquito"]
        self.assertEqual(claim.state, EvidenceState.CONFIRMED)
        self.assertIsNone(result.loop)
        self.assertTrue(result.stopped)
        self.assertEqual(result.stop_reason, "router_requires_human_review")
        self.assertIsNotNone(result.execution_audit)
        self.assertEqual(calls, [])

    def test_contradicted_provider_evidence_reaches_continue_gate(self):
        result, snapshot, calls = self._run("contradicted")
        claim = snapshot.claims["fauna/mosquito_tigre/readable_as_mosquito"]
        self.assertEqual(claim.state, EvidenceState.CONTRADICTED)
        self.assertIsNone(result.loop)
        self.assertTrue(result.stopped)
        self.assertEqual(result.stop_reason, "router_requires_human_review")
        self.assertIsNotNone(result.execution_audit)
        self.assertEqual(calls, [])

    def test_unknown_provider_evidence_reaches_human_review_gate(self):
        result, snapshot, calls = self._run("unknown")
        claim = snapshot.claims["fauna/mosquito_tigre/readable_as_mosquito"]
        self.assertEqual(claim.state, EvidenceState.UNKNOWN)
        self.assertIsNone(result.loop)
        self.assertTrue(result.stopped)
        self.assertEqual(result.stop_reason, "router_requires_human_review")
        self.assertIsNotNone(result.execution_audit)
        self.assertEqual(calls, [])

    def test_provider_snapshot_and_candidate_are_independent(self):
        adapter = DefaultEvidenceAdapter()
        observations = {
            "fauna/mosquito_tigre/readable_as_mosquito": {
                "claim": "fauna/mosquito_tigre/readable_as_mosquito",
                "verdict": "confirmed",
                "source": "simulated-provider",
            }
        }
        snapshot = build_snapshot_from_adapter(ROOT, adapter, observations)
        candidate = {
            "checks": {
                "intention": True,
                "canon": True,
                "coherence": True,
                "reuse_intention": True,
            }
        }
        before = dict(candidate["checks"])

        def executor(prompt, iteration, previous):
            return candidate

        result = run_vertical_slice(
            "Create a mosquito-tigre candidate",
            ROOT,
            executor,
            evidence_claims=snapshot.claims,
        )

        self.assertEqual(candidate["checks"], before)
        self.assertEqual(
            snapshot.claims["fauna/mosquito_tigre/readable_as_mosquito"].state,
            EvidenceState.CONFIRMED,
        )
        self.assertIsNone(result.loop)
        self.assertTrue(result.stopped)
        self.assertEqual(result.stop_reason, "router_requires_human_review")


if __name__ == "__main__":
    unittest.main()
