from pathlib import Path
import unittest

from core.evidence_state import EvidenceClaim, EvidenceState
from core.orchestrator import run_vertical_slice

ROOT = Path(__file__).resolve().parents[1]
CLAIMS = {
    name: EvidenceClaim(name, EvidenceState.CONFIRMED)
    for name in ("intention", "canon", "coherence", "reuse_intention")
}
BASELINE = {
    "checks": {
        "intention": True,
        "canon": True,
        "coherence": True,
        "reuse_intention": True,
        "visual_readability": True,
    }
}


class OrchestratorSemanticAuditTests(unittest.TestCase):
    def test_accepted_candidate_records_audit(self):
        def executor(prompt, iteration, previous):
            return dict(BASELINE)

        result = run_vertical_slice(
            "Crear una escena veraniega",
            ROOT,
            executor,
            evidence_claims=CLAIMS,
            initial_candidate=BASELINE,
            max_iterations=1,
        )

        self.assertEqual(result.loop.status, "accepted")
        self.assertEqual(len(result.audit_trail), 1)
        record = result.audit_trail[0]
        self.assertEqual(record.iteration, 1)
        self.assertEqual(record.decision, "accept")
        self.assertEqual(record.regressions, ())

    def test_regression_is_recorded_on_iteration(self):
        def executor(prompt, iteration, previous):
            return {
                "checks": {
                    "intention": True,
                    "canon": True,
                    "coherence": True,
                    "reuse_intention": True,
                    "visual_readability": False,
                }
            }

        result = run_vertical_slice(
            "Crear una escena veraniega",
            ROOT,
            executor,
            evidence_claims=CLAIMS,
            initial_candidate=BASELINE,
            max_iterations=1,
        )

        self.assertEqual(result.loop.status, "max_iterations")
        self.assertEqual(len(result.audit_trail), 1)
        self.assertEqual(result.audit_trail[0].decision, "continue")
        self.assertEqual(result.audit_trail[0].regressions[0].name, "visual_readability")

    def test_audit_trail_preserves_iteration_order(self):
        def executor(prompt, iteration, previous):
            if iteration == 1:
                return {
                    "checks": {
                        "intention": True,
                        "canon": True,
                        "coherence": True,
                        "reuse_intention": True,
                    }
                }
            return dict(BASELINE)

        result = run_vertical_slice(
            "Crear una escena veraniega",
            ROOT,
            executor,
            evidence_claims=CLAIMS,
            initial_candidate=None,
            max_iterations=2,
        )

        self.assertEqual(len(result.audit_trail), 2)
        self.assertEqual([record.iteration for record in result.audit_trail], [1, 2])
        self.assertEqual([record.decision for record in result.audit_trail], ["human_review", "accept"])


if __name__ == "__main__":
    unittest.main()
