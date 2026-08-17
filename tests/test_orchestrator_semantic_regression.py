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


class OrchestratorSemanticRegressionTests(unittest.TestCase):
    def test_accepted_baseline_regression_forces_continuation(self):
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

        self.assertIsNotNone(result.loop)
        self.assertEqual(result.loop.status, "max_iterations")
        self.assertEqual(
            result.loop.iterations[0].evaluation.decision,
            "continue",
        )
        self.assertIn(
            "visual_readability",
            result.loop.iterations[0].evaluation.reason,
        )

    def test_preserving_baseline_allows_normal_acceptance(self):
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

        self.assertIsNotNone(result.loop)
        self.assertEqual(result.loop.status, "accepted")
        self.assertEqual(
            result.loop.iterations[0].evaluation.decision,
            "accept",
        )

    def test_human_review_remains_stronger_than_regression_continuation(self):
        def executor(prompt, iteration, previous):
            return {
                "checks": {
                    "intention": True,
                    "canon": True,
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

        self.assertIsNotNone(result.loop)
        self.assertEqual(result.loop.status, "human_review")
        self.assertEqual(
            result.loop.iterations[0].evaluation.decision,
            "human_review",
        )


if __name__ == "__main__":
    unittest.main()
