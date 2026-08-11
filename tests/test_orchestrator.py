from pathlib import Path
import unittest

from core.orchestrator import run_vertical_slice


ROOT = Path(__file__).resolve().parents[1]


INITIAL = {
    "characters": ["illo", "killo"],
    "elements": [
        {"id": "clavel", "intention": "character_identity"},
        {"id": "black_spots", "count": 2, "intention": "character_identity"},
    ],
}

CHECKS = {
    "intention": True,
    "canon": True,
    "coherence": True,
    "reuse_intention": True,
}


class OrchestratorTests(unittest.TestCase):

    def test_vertical_slice_accepts_candidate(self):
        prompts = []

        def executor(prompt, iteration, previous):
            prompts.append(prompt)
            return {
                **INITIAL,
                "checks": CHECKS,
            }

        result = run_vertical_slice(
            "Crear un gag nuevo de Illo y Killo",
            ROOT,
            executor,
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
            candidate = {
                **INITIAL,
                "checks": {
                    **CHECKS,
                    "coherence": iteration >= 2,
                },
            }
            return candidate

        result = run_vertical_slice(
            "Crear un gag nuevo de Illo y Killo",
            ROOT,
            executor,
            initial_candidate=INITIAL,
            max_iterations=3,
        )

        self.assertEqual(result.loop.status, "accepted")
        self.assertEqual(len(result.loop.iterations), 2)
        self.assertIs(prompts[0], prompts[1])
        self.assertEqual(prompts[0].render(), prompts[1].render())

    def test_failed_candidate_continues_and_passes_previous_candidate(self):
        previous_values = []

        def executor(prompt, iteration, previous):
            previous_values.append(previous)
            if iteration == 1:
                return {
                    **INITIAL,
                    "checks": {**CHECKS, "coherence": False},
                }
            return {
                **INITIAL,
                "checks": CHECKS,
            }

        result = run_vertical_slice(
            "Crear un gag nuevo de Illo y Killo",
            ROOT,
            executor,
            initial_candidate=INITIAL,
            max_iterations=3,
        )

        self.assertEqual(result.loop.status, "accepted")
        self.assertEqual(len(result.loop.iterations), 2)
        self.assertEqual(previous_values[0], INITIAL)
        self.assertEqual(previous_values[1]["checks"]["coherence"], False)

    def test_missing_quality_check_requests_human_review(self):
        def executor(prompt, iteration, previous):
            return {
                **INITIAL,
                "checks": {
                    "intention": True,
                    "canon": True,
                    "coherence": True,
                },
            }

        result = run_vertical_slice(
            "Crear un gag nuevo de Illo y Killo",
            ROOT,
            executor,
            initial_candidate=INITIAL,
        )

        self.assertTrue(result.stopped)
        self.assertEqual(result.loop.status, "human_review")
        self.assertIn("reuse_intention", result.stop_reason)


if __name__ == "__main__":
    unittest.main()
