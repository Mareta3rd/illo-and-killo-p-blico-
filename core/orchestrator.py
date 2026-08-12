"""First deterministic vertical slice for SinergYa Core v0.1.

This module joins the validated pipeline, the bounded loop, the evidence-aware
evaluator, and the compiled prompt. It remains model-agnostic: an external
execution layer is injected rather than called from Core. Every candidate is
revalidated against repository knowledge and explicit Evidence before the
evaluator decides whether to continue, accept, or request human review.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any, Callable, Mapping

from .canon_guard import ValidationResult, validate_piece
from .evidence_evaluator import evaluate_candidate_with_evidence
from .evidence_state import EvidenceClaim
from .evaluator import EvaluationReport
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
    evidence_claims: Mapping[str, EvidenceClaim],
    initial_candidate: Candidate | None = None,
    max_iterations: int = 3,
) -> VerticalSliceResult:
    """Run the Evidence-aware pipeline -> loop -> validation -> evaluator.

    Explicit Evidence claims are required at the end-to-end boundary. The
    compiled prompt is created only after pipeline validation and evaluation,
    and the same Evidence claims are applied again to every loop candidate.
    This prevents the loop from bypassing the semantic decision boundary.
    """
    proposal = initial_candidate or {}
    pipeline = run_pipeline(
        idea,
        root,
        proposal,
        evidence_claims=evidence_claims,
    )

    if pipeline.stopped or pipeline.compiled_prompt is None:
        return VerticalSliceResult(
            pipeline=pipeline,
            loop=None,
            stopped=True,
            stop_reason=pipeline.stop_reason or "pipeline_stopped",
        )

    prompt = pipeline.compiled_prompt
    knowledge = pipeline.context.knowledge

    def execute(iteration: int, previous: Candidate | None) -> Candidate:
        candidate = executor(prompt, iteration, previous)
        if not isinstance(candidate, dict):
            raise TypeError("executor must return a candidate dictionary")
        return candidate

    def evaluate(candidate: Candidate, iteration: int) -> Evaluation:
        validation: ValidationResult = validate_piece(candidate, knowledge)
        report: EvaluationReport = evaluate_candidate_with_evidence(
            candidate,
            validation,
            evidence_claims,
        )
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
