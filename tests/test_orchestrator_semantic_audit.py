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
    }
}


class OrchestratorSemanticAuditTests(unittest.TestCase):
    def test_accepted_candidate_produces_audit_record(self):
        result = run_vertical_slice(
            "Crear una escena veraniega",
            ROOT,
            lambda prompt, iteration, previous: dict(BASELINE),
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
        self.assertTrue(record.candidate_fingerprint)

    def test_regression_is_present_in_audit_record(self):
        changed = {
            "checks": {
                "intention": True,
                "canon": True,
                "coherence": True,
                "reuse_intention": False,
            }
        }

        result = run_vertical_slice(
            "Crear una escena veraniega",
            ROOT,
            lambda prompt, iteration, previous: dict(changed),
            evidence_claims=CLAIMS,
            initial_candidate=BASELINE,
            max_iterations=1,
        )

        self.assertEqual(len(result.audit_trail), 1)
        record = result.audit_trail[0]
        self.assertEqual(record.decision, "continue")
        self.assertEqual([r.name for r in record.regressions], ["reuse_intention"])

    def test_audit_trail_matches_loop_order(self):
        candidates = [
            dict(BASELINE),
            {"checks": {"intention": True, "canon": True, "coherence": True, "reuse_intention": False}},
            {"checks": {"intention": True, "canon": True, "coherence": True, "reuse_intention": True}},
        ]

        def executor(prompt, iteration, previous):
            return candidates[iteration - 1]

        result = run_vertical_slice(
            "Crear una escena veraniega",
            ROOT,
            executor,
            evidence_claims=CLAIMS,
            initial_candidate=BASELINE,
            max_iterations=3,
        )

        self.assertEqual([r.iteration for r in result.audit_trail], [1, 2, 3])
        self.assertEqual(
            [r.decision for r in result.audit_trail],
            ["accept", "continue", "accept"],
        )


if __name__ == "__main__":
    unittest.main()
