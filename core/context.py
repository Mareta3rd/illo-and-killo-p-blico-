"""Build the first SinergYa Core execution context.

This layer connects repository knowledge with deterministic routing. It does not
create content, modify canon, call external models, or execute loops.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from .loader import RepositoryKnowledge, load_repository
from .router import Route, route_idea


@dataclass(frozen=True)
class CoreContext:
    """Immutable context passed to later Core stages."""

    idea: str
    route: Route
    confidence: float
    requires_human_review: bool
    reason: str
    knowledge: RepositoryKnowledge


def build_context(idea: str, root: str | Path) -> CoreContext:
    """Load repository knowledge and route *idea* without generating content."""

    knowledge = load_repository(root)
    decision = route_idea(idea)

    return CoreContext(
        idea=idea,
        route=decision.route,
        confidence=decision.confidence,
        requires_human_review=decision.requires_human_review,
        reason=decision.reason,
        knowledge=knowledge,
    )
