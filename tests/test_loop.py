import unittest

from core.loop import Evaluation, run_loop


class LoopTests(unittest.TestCase):

    def test_accepts_and_records_single_iteration(self):
        calls = []

        def executor(iteration, previous):
            calls.append((iteration, previous))
            return "candidate-1"

        def evaluator(candidate, iteration):
            return Evaluation("accept", "meets all checks")

        result = run_loop(executor, evaluator, max_iterations=3)

        self.assertEqual(result.status, "accepted")
        self.assertEqual(result.candidate, "candidate-1")
        self.assertEqual(len(result.iterations), 1)
        self.assertEqual(calls, [(1, None)])

    def test_continues_with_previous_candidate_and_then_accepts(self):
        def executor(iteration, previous):
            return f"candidate-{iteration}:{previous or 'start'}"

        def evaluator(candidate, iteration):
            if iteration == 1:
                return Evaluation("continue", "needs refinement")
            return Evaluation("accept", "passes evaluation")

        result = run_loop(executor, evaluator, max_iterations=3)

        self.assertEqual(result.status, "accepted")
        self.assertEqual(result.candidate, "candidate-2:candidate-1:start")
        self.assertEqual(len(result.iterations), 2)
        self.assertEqual(result.iterations[0].evaluation.decision, "continue")
        self.assertEqual(result.iterations[1].evaluation.decision, "accept")

    def test_human_review_stops_without_further_iterations(self):
        calls = []

        def executor(iteration, previous):
            calls.append(iteration)
            return f"candidate-{iteration}"

        def evaluator(candidate, iteration):
            return Evaluation("human_review", "ambiguous canon decision")

        result = run_loop(executor, evaluator, max_iterations=3)

        self.assertEqual(result.status, "human_review")
        self.assertEqual(len(result.iterations), 1)
        self.assertEqual(calls, [1])

    def test_max_iterations_is_hard_stop(self):
        def executor(iteration, previous):
            return iteration

        def evaluator(candidate, iteration):
            return Evaluation("continue", "not ready")

        result = run_loop(executor, evaluator, max_iterations=2)

        self.assertEqual(result.status, "max_iterations")
        self.assertEqual(result.candidate, 2)
        self.assertEqual(len(result.iterations), 2)

    def test_invalid_iteration_limit_is_rejected(self):
        with self.assertRaises(ValueError):
            run_loop(
                lambda iteration, previous: iteration,
                lambda candidate, iteration: Evaluation("accept", "ok"),
                max_iterations=0,
            )


if __name__ == "__main__":
    unittest.main()
