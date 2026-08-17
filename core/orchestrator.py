"""First deterministic vertical slice for SinergYa Core v0.1.

This module joins the validated pipeline, the bounded loop, the evidence-aware
evaluator, the compiled prompt, semantic-regression protection, and an
immutable semantic audit trail. It remains model-agnostic: an external
execution layer is injected rather than called from Core.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any, Callable, Mapping

from .canon_guard import ValidationResult, validate_piece
from .evidence_evaluator import evaluate_candidate_with_evidence
from .evidence_snapshot import EvidenceSnapshot
from .evidence_state import EvidenceClaim
from .evaluator import EvaluationReport
from .loop import Evaluation, LoopResult, run_loop
from .pipeline import PipelineResult, run_pipeline
from .prompt_compiler import CompiledPrompt
from .semantic_audit import SemanticAuditRecord, build_semantic_audit_record
from .semantic_regression import SemanticRegression, detect_semantic_regressions


Candidate = dict[str, Any]
Executor = Callable[[CompiledPrompt, int, Candidate | None], Candidate]


@dataclass(frozen=True)
class VerticalSliceResult:
    """Auditable result of the first end-to-end Core slice."""

    pipeline: PipelineResult
    loop: LoopResult[Candidate] | None
    stopped: bool
    stop_reason: str | None
    audit_trail: tuple[SemanticAuditRecord, ...] = ()


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

    Evidence is validated once by the pipeline and then reused through its
    immutable snapshot for every loop candidate. The loop cannot reinterpret,
    replace, or silently bypass the execution-boundary Evidence.

    When an initial candidate already has a passing evaluation, subsequent
    candidates are checked for semantic regressions against the latest
    accepted baseline. Each evaluated candidate also receives an immutable
    audit record with a deterministic fingerprint.
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
    snapshot: EvidenceSnapshot | None = pipeline.evidence_snapshot
    if snapshot is None:
        return VerticalSliceResult(
            pipeline=pipeline,
            loop=None,
            stopped=True,
            stop_reason="missing_evidence_snapshot",
        )

    baseline_report: EvaluationReport | None = pipeline.evaluation
    audit_trail: list[SemanticAuditRecord] = []

    def execute(iteration: int, previous: Candidate | None) -> Candidate:
        candidate = executor(prompt, iteration, previous)
        if not isinstance(candidate, dict):
            raise TypeError("executor must return a candidate dictionary")
        return candidate

    def evaluate(candidate: Candidate, iteration: int) -> Evaluation:
        nonlocal baseline_report

        validation: ValidationResult = validate_piece(candidate, knowledge)
        report: EvaluationReport = evaluate_candidate_with_evidence(
            candidate,
            validation,
            snapshot.claims,
        )

        regressions: tuple[SemanticRegression, ...] = ()
        decision = report.evaluation

        if baseline_report is not None:
            regressions = detect_semantic_regressions(baseline_report, report)
            if regressions and decision.decision != "human_review":
                decision = Evaluation(
                    "continue",
                    "semantic regressions detected: "
                    + ", ".join(regression.name for regression in regressions),
                )

        if decision.decision == "accept":
            baseline_report = report

        audit_trail.append(
            build_semantic_audit_record(
                iteration,
                candidate,
                EvaluationReport(decision, report.checks),
                regressions,
            )
        )
        return decision

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
        audit_trail=tuple(audit_trail),
    )
