from pathlib import Path
import unittest

from core.evidence_state import EvidenceClaim, EvidenceState
from core.orchestrator import run_vertical_slice

ROOT = Path(__file__).resolve().parents[1]
CLAIMS = {
    name: EvidenceClaim(name, EvidenceState.CONFIRMED)
    for name in ("intention", "canon", "coherence", "reuse_intention")
}
CANDIDATE = {
    "checks": {
        "intention": True,
        "canon": True,
        "coherence": True,
        "reuse_intention": True,
    }
}


class OrchestratorExecutionAuditIntegrationTests(unittest.TestCase):
    def test_accepted_execution_exposes_reconstructable_audit(self):
        def executor(prompt, iteration, previous):
            return dict(CANDIDATE)

        result = run_vertical_slice(
            "Crear una escena veraniega",
            ROOT,
            executor,
            evidence_claims=CLAIMS,
            max_iterations=1,
        )

        self.assertIsNotNone(result.execution_audit)
        audit = result.execution_audit
        self.assertEqual(audit.idea, "Crear una escena veraniega")
        self.assertEqual(audit.final_status, "accepted")
        self.assertIsNone(audit.stop_reason)
        self.assertEqual(len(audit.iterations), 1)
        self.assertEqual(audit.iterations[0], result.audit_trail[0])
        self.assertIsNotNone(audit.evidence_digest)

    def test_pipeline_stop_also_produces_audit(self):
        result = run_vertical_slice(
            "idea ambigua sin clasificación suficiente",
            ROOT,
            lambda prompt, iteration, previous: dict(CANDIDATE),
            evidence_claims=CLAIMS,
            max_iterations=1,
        )

        self.assertIsNotNone(result.execution_audit)
        self.assertIsNone(result.loop)
        self.assertTrue(result.stopped)
        self.assertEqual(result.execution_audit.final_status, "pipeline_stopped")
        self.assertEqual(result.execution_audit.stop_reason, result.stop_reason)
        self.assertEqual(result.execution_audit.iterations, ())


if __name__ == "__main__":
    unittest.main()
