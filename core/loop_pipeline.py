"""Connect a compiled prompt to the bounded Core loop.

This adapter deliberately keeps prompt compilation, execution, and evaluation
separate. It renders an already validated CompiledPrompt once and gives that
stable execution context to each bounded loop iteration. No model provider is
selected here and no creative decision is made by the adapter itself.
"""

from __future__ import annotations

from typing import Any, Callable, TypeVar

from core.loop import Evaluation, LoopResult, run_loop
from core.prompt_compiler import CompiledPrompt


CandidateT = TypeVar("CandidateT")

CompiledExecutor = Callable[[str, int, CandidateT | None], CandidateT]
LoopEvaluator = Callable[[CandidateT, int], Evaluation]


def run_compiled_loop(
    compiled_prompt: CompiledPrompt,
    executor: CompiledExecutor[CandidateT],
    evaluator: LoopEvaluator[CandidateT],
    *,
    max_iterations: int = 3,
    initial_candidate: CandidateT | None = None,
) -> LoopResult[CandidateT]:
    """Execute a compiled prompt through the bounded loop engine.

    The rendered prompt is captured once and passed unchanged to every
    iteration. The loop engine remains responsible for iteration limits and
    terminal states; the evaluator remains responsible for accept/continue/
    human-review decisions.
    """
    rendered_prompt = compiled_prompt.render()

    def bound_executor(iteration: int, previous: CandidateT | None) -> CandidateT:
        return executor(rendered_prompt, iteration, previous)

    return run_loop(
        bound_executor,
        evaluator,
        max_iterations=max_iterations,
        initial_candidate=initial_candidate,
    )
