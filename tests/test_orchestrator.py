from pathlib import Path
import unittest

from core.evidence_state import EvidenceClaim, EvidenceState
from core.orchestrator import run_vertical_slice


ROOT = Path(__file__).resolve().parents[1]


INITIAL = {
    "characters": ["illo", "killo"],
    "elements": [
        {"id": "clavel", "intention": "character_identity"},
        {"id": "black_spots", "count": 2, "intention": "character_identity"},
    ],
}

COMPLETE_EVIDENCE = {
    "intention": EvidenceClaim("intention", EvidenceState.CONFIRMED),
    "canon": EvidenceClaim("canon", EvidenceState.CONFIRMED),
    "coherence": EvidenceClaim("coherence", EvidenceState.CONFIRMED),
    "reuse_intention": EvidenceClaim("reuse", EvidenceState.CONFIRMED),
}


class OrchestratorTests(unittest.TestCase):

    def test_vertical_slice_accepts_candidate(self):
        prompts = []

        def executor(prompt, iteration, previous):
            prompts.append(prompt)
            return {**INITIAL}

        result = run_vertical_slice(
            "Crear un gag nuevo de Illo y Killo",
            ROOT,
            executor,
            evidence_claims=COMPLETE_EVIDENCE,
            initial_candidate=INITIAL,
        )

        self.assertFalse(result.stopped)
        self.assertEqual(result.loop.status, "accepted")
        self.assertEqual(len(result.loop.iterations), 1)
        self.assertEqual(prompts[0], result.pipeline.compiled_prompt)

    def test_compiled_prompt_is_stable_across_iterations(self):
        prompts = []

        def executor(prompt, iteration, previous):
            prompts.append(prompt)
            candidate = {**INITIAL}
            return candidate

        result = run_vertical_slice(
            "Crear un gag nuevo de Illo y Killo",
            ROOT,
            executor,
            evidence_claims=COMPLETE_EVIDENCE,
            initial_candidate=INITIAL,
            max_iterations=3,
        )

        self.assertEqual(result.loop.status, "accepted")
        self.assertEqual(len(result.loop.iterations), 1)
        self.assertIs(prompts[0], result.pipeline.compiled_prompt)
        self.assertEqual(prompts[0].render(), prompts[0].render())

    def test_failed_candidate_continues_and_passes_previous_candidate(self):
        previous_values = []

        def executor(prompt, iteration, previous):
            previous_values.append(previous)
            if iteration == 1:
                return {
                    **INITIAL,
                    "checks": {"coherence": False},
                }
            return {
                **INITIAL,
            }

        result = run_vertical_slice(
            "Crear un gag nuevo de Illo y Killo",
            ROOT,
            executor,
            evidence_claims=COMPLETE_EVIDENCE,
            initial_candidate=INITIAL,
            max_iterations=3,
        )

        self.assertEqual(result.loop.status, "accepted")
        self.assertEqual(len(result.loop.iterations), 2)
        self.assertEqual(previous_values[0], INITIAL)
        self.assertEqual(previous_values[1]["checks"]["coherence"], False)

    def test_missing_quality_check_requests_human_review(self):
        evidence = dict(COMPLETE_EVIDENCE)
        evidence.pop("reuse_intention")

        def executor(prompt, iteration, previous):
            return {**INITIAL}

        result = run_vertical_slice(
            "Crear un gag nuevo de Illo y Killo",
            ROOT,
            executor,
            evidence_claims=evidence,
            initial_candidate=INITIAL,
        )

        self.assertTrue(result.stopped)
        self.assertIsNotNone(result.loop)
        self.assertEqual(result.loop.status, "human_review")
        self.assertIn("missing checks", result.stop_reason)

    def test_unknown_evidence_blocks_before_loop(self):
        evidence = dict(COMPLETE_EVIDENCE)
        evidence["coherence"] = EvidenceClaim(
            "coherence",
            EvidenceState.UNKNOWN,
        )

        def executor(prompt, iteration, previous):
            raise AssertionError("executor must not run when Evidence requires review")

        result = run_vertical_slice(
            "Crear un gag nuevo de Illo y Killo",
            ROOT,
            executor,
            evidence_claims=evidence,
            initial_candidate=INITIAL,
        )

        self.assertTrue(result.stopped)
        self.assertIsNone(result.loop)
        self.assertEqual(result.stop_reason, "evaluation_requires_human_review")


if __name__ == "__main__":
    unittest.main()
