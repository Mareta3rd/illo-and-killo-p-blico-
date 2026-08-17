"""First deterministic vertical slice for SinergYa Core v0.1.

This module joins the validated pipeline, the bounded loop, the evidence-aware
evaluator, the compiled prompt, semantic-regression protection, and immutable
semantic/execution audit trails. It remains model-agnostic: an external
execution layer is injected rather than called from Core.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any, Callable, Mapping

from .canon_guard import ValidationResult, validate_piece
from .context import CoreContext, build_context
from .evidence_evaluator import evaluate_candidate_with_evidence
from .evidence_snapshot import EvidenceSnapshot
from .evidence_state import EvidenceClaim
from .evaluator import EvaluationReport
from .execution_audit import ExecutionAudit, build_execution_audit
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
    execution_audit: ExecutionAudit | None = None


def run_vertical_slice(
    idea: str,
    root: str | Path,
    executor: Executor,
    *,
    evidence_claims: Mapping[str, EvidenceClaim],
    initial_candidate: Candidate | None = None,
    max_iterations: int = 3,
) -> VerticalSliceResult:
    """Run the Evidence-aware pipeline -> loop -> validation -> evaluator."""
    proposal = initial_candidate or {}
    pipeline = run_pipeline(
        idea,
        root,
        proposal,
        evidence_claims=evidence_claims,
    )

    if pipeline.stopped or pipeline.compiled_prompt is None:
        context = build_context(idea, root)
        execution_audit = build_execution_audit(
            context,
            pipeline.evidence_snapshot,
            (),
            final_status="stopped",
            stop_reason=pipeline.stop_reason or "pipeline_stopped",
        )
        return VerticalSliceResult(
            pipeline=pipeline,
            loop=None,
            stopped=True,
            stop_reason=pipeline.stop_reason or "pipeline_stopped",
            execution_audit=execution_audit,
        )

    prompt = pipeline.compiled_prompt
    knowledge = pipeline.context.knowledge
    snapshot: EvidenceSnapshot | None = pipeline.evidence_snapshot
    if snapshot is None:
        execution_audit = build_execution_audit(
            pipeline.context,
            None,
            (),
            final_status="stopped",
            stop_reason="missing_evidence_snapshot",
        )
        return VerticalSliceResult(
            pipeline=pipeline,
            loop=None,
            stopped=True,
            stop_reason="missing_evidence_snapshot",
            execution_audit=execution_audit,
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

    final_status = loop.status
    stop_reason = (
        loop.iterations[-1].evaluation.reason
        if loop.status == "human_review"
        else None
    )
    execution_audit = build_execution_audit(
        pipeline.context,
        snapshot,
        audit_trail,
        final_status=final_status,
        stop_reason=stop_reason,
    )

    return VerticalSliceResult(
        pipeline=pipeline,
        loop=loop,
        stopped=loop.status == "human_review",
        stop_reason=stop_reason,
        audit_trail=tuple(audit_trail),
        execution_audit=execution_audit,
    )
