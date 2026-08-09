"""First deterministic vertical slice for SinergYa Core v0.1.

This module joins the validated pipeline, the bounded loop, and the evaluator.
It remains model-agnostic: an external execution layer is injected rather than
called from Core. Each generated candidate is revalidated against repository
knowledge before the evaluator decides whether to continue, accept, or request
human review.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any, Callable

from .canon_guard import ValidationResult, validate_piece
from .evaluator import EvaluationReport, evaluate_candidate
from .loop import Evaluation, LoopResult, run_loop
from .pipeline import PipelineResult, run_pipeline
from .prompt_compiler import CompiledPrompt


Candidate = dict[str, Any]
Executor = Callable[[CompiledPrompt, int, Candidate | None], Candidate]


@dataclass(frozen=True)
class VerticalSliceResult:
    """Auditable result of the first end-to-end Core slice."""

    pipeline: PipelineResult
    loop: LoopResult[Candidate] | None
    stopped: bool
    stop_reason: str | None


def run_vertical_slice(
    idea: str,
    root: str | Path,
    executor: Executor,
    *,
    initial_candidate: Candidate | None = None,
    max_iterations: int = 3,
) -> VerticalSliceResult:
    """Run pipeline -> compiled prompt -> loop -> validation -> evaluator.

    The compiled prompt is created once by the pipeline and passed unchanged
    to every executor iteration. Each candidate is independently validated
    against the immutable repository knowledge before evaluation.
    """
    proposal = initial_candidate or {}
    pipeline = run_pipeline(idea, root, proposal)

    if pipeline.stopped or pipeline.compiled_prompt is None:
        return VerticalSliceResult(
            pipeline=pipeline,
            loop=None,
            stopped=True,
            stop_reason=pipeline.stop_reason or "pipeline_stopped",
        )

    prompt = pipeline.compiled_prompt
    knowledge = pipeline.context.knowledge

    reports: dict[int, EvaluationReport] = {}

    def execute(iteration: int, previous: Candidate | None) -> Candidate:
        candidate = executor(prompt, iteration, previous)
        if not isinstance(candidate, dict):
            raise TypeError("executor must return a candidate dictionary")
        return candidate

    def evaluate(candidate: Candidate, iteration: int) -> Evaluation:
        validation: ValidationResult = validate_piece(candidate, knowledge)
        report = evaluate_candidate(candidate, validation)
        reports[iteration] = report
        return report.evaluation

    loop = run_loop(
        execute,
        evaluate,
        max_iterations=max_iterations,
        initial_candidate=initial_candidate,
    )

    return VerticalSliceResult(
        pipeline=pipeline,
        loop=loop,
        stopped=loop.status == "human_review",
        stop_reason=(
            loop.iterations[-1].evaluation.reason
            if loop.status == "human_review"
            else None
        ),
    )
