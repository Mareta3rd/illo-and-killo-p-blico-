"""Deterministic v0.1 pipeline joining loader, router, context and guard."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any

from core.canon_guard import ValidationResult, validate_piece
from core.context import CoreContext, build_context


@dataclass(frozen=True)
class PipelineResult:
    context: CoreContext
    validation: ValidationResult
    stopped: bool
    stop_reason: str | None


def run_pipeline(
    idea: str,
    root: str | Path,
    proposal: dict[str, Any] | None = None,
) -> PipelineResult:
    """Run the non-generative Core v0.1 pipeline.

    The repository is loaded through the canonical loader and passed into the
    immutable CoreContext. The optional structured proposal is then checked
    by the Canon Guard. The pipeline never generates, rewrites, or mutates
    creative content or repository knowledge.
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

    return PipelineResult(
        context=context,
        validation=validation,
        stopped=False,
        stop_reason=None,
    )
