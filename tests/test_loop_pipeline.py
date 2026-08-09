import unittest

from core.loop import Evaluation
from core.loop_pipeline import run_compiled_loop
from core.prompt_compiler import CompiledPrompt


class LoopPipelineTests(unittest.TestCase):

    def make_prompt(self):
        return CompiledPrompt(
            route="gag",
            task="Develop the requested gag.",
            constraints=("Preserve canon.",),
            checks=("Confirm intention.",),
            context_summary=("idea=test gag",),
        )

    def test_compiled_prompt_is_stable_across_iterations(self):
        prompts = []

        def executor(prompt, iteration, previous):
            prompts.append(prompt)
            return f"candidate-{iteration}"

        def evaluator(candidate, iteration):
            if iteration == 1:
                return Evaluation("continue", "refine")
            return Evaluation("accept", "passes")

        result = run_compiled_loop(self.make_prompt(), executor, evaluator)

        self.assertEqual(result.status, "accepted")
        self.assertEqual(len(prompts), 2)
        self.assertEqual(prompts[0], prompts[1])
        self.assertIn("ROUTE: gag", prompts[0])
        self.assertIn("TASK:", prompts[0])

    def test_loop_terminal_state_is_preserved(self):
        def executor(prompt, iteration, previous):
            return iteration

        def evaluator(candidate, iteration):
            return Evaluation("human_review", "ambiguous intention")

        result = run_compiled_loop(
            self.make_prompt(),
            executor,
            evaluator,
            max_iterations=3,
        )

        self.assertEqual(result.status, "human_review")
        self.assertEqual(len(result.iterations), 1)
        self.assertEqual(result.iterations[0].evaluation.reason, "ambiguous intention")

    def test_initial_candidate_reaches_first_executor_iteration(self):
        received = []

        def executor(prompt, iteration, previous):
            received.append(previous)
            return "accepted"

        def evaluator(candidate, iteration):
            return Evaluation("accept", "ok")

        result = run_compiled_loop(
            self.make_prompt(),
            executor,
            evaluator,
            initial_candidate="seed",
        )

        self.assertEqual(result.candidate, "accepted")
        self.assertEqual(received, ["seed"])


if __name__ == "__main__":
    unittest.main()
