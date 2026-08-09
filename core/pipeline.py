"""Deterministic v0.1 pipeline joining loader, router, context and guard."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Callable

from core.canon_guard import ValidationResult, validate_piece
from core.context import CoreContext
from core.router import RouteDecision, route_idea


@dataclass(frozen=True)
class PipelineResult:
    context: CoreContext
    validation: ValidationResult
    stopped: bool
    stop_reason: str | None


def run_pipeline(
    idea: str,
    knowledge: dict[str, Any],
    *,
    loader: Callable[[dict[str, Any]], dict[str, Any]] | None = None,
) -> PipelineResult:
    """Run the non-generative Core v0.1 pipeline.

    The supplied knowledge is treated as read-only. ``loader`` may be used
    to provide a repository loader; when omitted, the knowledge object is
    used directly. The pipeline stops on missing input or human-review
    validation conditions and never generates or rewrites creative content.
    """
    if not idea.strip():
        decision = route_idea(idea)
        context = CoreContext(
            idea=idea,
            route=decision.route,
            confidence=decision.confidence,
            requires_human_review=decision.requires_human_review,
            reason=decision.reason,
            knowledge=knowledge,
        )
        validation = validate_piece({}, knowledge)
        return PipelineResult(
            context=context,
            validation=validation,
            stopped=True,
            stop_reason="missing_idea",
        )

    loaded = loader(knowledge) if loader else knowledge
    decision: RouteDecision = route_idea(idea)

    context = CoreContext(
        idea=idea,
        route=decision.route,
        confidence=decision.confidence,
        requires_human_review=decision.requires_human_review,
        reason=decision.reason,
        knowledge=loaded,
    )

    validation = validate_piece(
        {"elements": []},
        loaded,
    )

    if decision.requires_human_review:
        return PipelineResult(
            context=context,
            validation=validation,
            stopped=True,
            stop_reason="router_requires_human_review",
        )

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
