"""Deterministic v0.1 pipeline joining loader, router, guard, evaluator and compiler."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any, Mapping

from core.canon_guard import ValidationResult, validate_piece
from core.context import CoreContext, build_context
from core.evidence_claim_router import evaluate_canonical_evidence_claims
from core.evidence_evaluator import evaluate_candidate_with_evidence
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


def _validate_canonical_claims(
    root: str | Path,
    claims: Mapping[str, EvidenceClaim],
) -> None:
    """Validate any canonical claims while preserving legacy claim names."""
    canonical_keys = [key for key in claims if "/" in str(key)]
    if canonical_keys:
        evaluate_canonical_evidence_claims(str(root), {
            key: claims[key] for key in canonical_keys
        })


def run_pipeline(
    idea: str,
    root: str | Path,
    proposal: dict[str, Any] | None = None,
    evidence_claims: Mapping[str, EvidenceClaim] | None = None,
) -> PipelineResult:
    """Run the deterministic Core v0.1 pipeline through evaluation and compilation.

    Repository knowledge remains read-only. Canon validation happens first;
    when explicit Evidence claims are supplied, they are translated into
    evaluator checks without mutating the proposal. Canonical Evidence keys
    (``catalog/entry/invariant``) are validated against the taxonomy and its
    Evidence contracts before evaluator execution. Legacy claim names remain
    supported, and canonical claims may coexist with those existing checks.
    """
    context = build_context(idea, root)
    proposal = proposal or {}

    if not idea.strip():
        validation = validate_piece(proposal, context.knowledge)
        return PipelineResult(
            context=context,
            validation=validation,
            stopped=True,
            stop_reason="missing_idea",
        )

    if context.requires_human_review:
        validation = validate_piece(proposal, context.knowledge)
        return PipelineResult(
            context=context,
            validation=validation,
            stopped=True,
            stop_reason="router_requires_human_review",
        )

    validation = validate_piece(proposal, context.knowledge)

    if validation.requires_human_review:
        return PipelineResult(
            context=context,
            validation=validation,
            stopped=True,
            stop_reason="canon_requires_human_review",
        )

    evaluation: EvaluationReport | None = None
    if evidence_claims is not None:
        try:
            _validate_canonical_claims(root, evidence_claims)
        except (KeyError, TypeError, ValueError) as exc:
            return PipelineResult(
                context=context,
                validation=validation,
                stopped=True,
                stop_reason="evidence_contract_requires_human_review",
                evaluation=EvaluationReport(
                    Evaluation("human_review", f"invalid canonical evidence claims: {exc}"),
                    (),
                ),
            )

        evaluation = evaluate_candidate_with_evidence(
            proposal,
            validation,
            evidence_claims,
        )

        if evaluation.evaluation.decision == "human_review":
            return PipelineResult(
                context=context,
                validation=validation,
                stopped=True,
                stop_reason="evaluation_requires_human_review",
                evaluation=evaluation,
            )

        if evaluation.evaluation.decision == "continue":
            return PipelineResult(
                context=context,
                validation=validation,
                stopped=True,
                stop_reason="evaluation_requires_continuation",
                evaluation=evaluation,
            )

    result = PipelineResult(
        context=context,
        validation=validation,
        stopped=False,
        stop_reason=None,
        evaluation=evaluation,
    )

    return PipelineResult(
        context=result.context,
        validation=result.validation,
        stopped=result.stopped,
        stop_reason=result.stop_reason,
        compiled_prompt=compile_prompt(result),
        evaluation=result.evaluation,
    )
