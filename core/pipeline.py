"""Deterministic v0.1 pipeline joining loader, router, guard, evaluator and compiler."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any, Mapping

from core.canon_guard import ValidationResult, validate_piece
from core.context import CoreContext, build_context
from core.evidence_evaluator import evaluate_candidate_with_evidence
from core.evidence_snapshot import EvidenceSnapshot, build_evidence_snapshot
from core.evidence_state import EvidenceClaim
from core.evaluator import EvaluationReport
from core.loop import Evaluation
from core.prompt_compiler import CompiledPrompt, compile_prompt


@dataclass(frozen=True)
class PipelineResult:
    context: CoreContext
    validation: ValidationResult
    stopped: bool
    stop_reason: str | None
    compiled_prompt: CompiledPrompt | None = None
    evaluation: EvaluationReport | None = None
    evidence_snapshot: EvidenceSnapshot | None = None


def run_pipeline(
    idea: str,
    root: str | Path,
    proposal: dict[str, Any] | None = None,
    evidence_claims: Mapping[str, EvidenceClaim] | None = None,
) -> PipelineResult:
    """Run the deterministic Core v0.1 pipeline through evaluation and compilation.

    Evidence claims are validated once and frozen into an EvidenceSnapshot
    before evaluator/compiler decisions. Legacy claim names remain supported.
    """
    context = build_context(idea, root)
    proposal = proposal or {}
    snapshot: EvidenceSnapshot | None = None

    if not idea.strip():
        validation = validate_piece(proposal, context.knowledge)
        return PipelineResult(context, validation, True, "missing_idea")

    if context.requires_human_review:
        validation = validate_piece(proposal, context.knowledge)
        return PipelineResult(context, validation, True, "router_requires_human_review")

    validation = validate_piece(proposal, context.knowledge)
    if validation.requires_human_review:
        return PipelineResult(context, validation, True, "canon_requires_human_review")

    evaluation: EvaluationReport | None = None
    if evidence_claims is not None:
        try:
            snapshot = build_evidence_snapshot(str(root), evidence_claims)
        except (TypeError, ValueError, KeyError) as exc:
            return PipelineResult(
                context,
                validation,
                True,
                "evidence_contract_requires_human_review",
                evaluation=EvaluationReport(
                    Evaluation("human_review", f"invalid canonical evidence claims: {exc}"),
                    (),
                ),
            )

        evaluation = evaluate_candidate_with_evidence(proposal, validation, snapshot.claims)

        if evaluation.evaluation.decision == "human_review":
            return PipelineResult(
                context,
                validation,
                True,
                "evaluation_requires_human_review",
                evaluation=evaluation,
                evidence_snapshot=snapshot,
            )
        if evaluation.evaluation.decision == "continue":
            return PipelineResult(
                context,
                validation,
                True,
                "evaluation_requires_continuation",
                evaluation=evaluation,
                evidence_snapshot=snapshot,
            )

    result = PipelineResult(
        context,
        validation,
        False,
        None,
        evaluation=evaluation,
        evidence_snapshot=snapshot,
    )
    return PipelineResult(
        context=result.context,
        validation=result.validation,
        stopped=result.stopped,
        stop_reason=result.stop_reason,
        compiled_prompt=compile_prompt(result),
        evaluation=result.evaluation,
        evidence_snapshot=result.evidence_snapshot,
    )
