"""Shared result contract for deterministic invariant evaluation."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Literal


InvariantDecision = Literal["pass", "fail", "unknown"]


@dataclass(frozen=True)
class InvariantEvaluation:
    """Immutable, auditable result shared by deterministic evaluators."""

    invariant: str
    decision: InvariantDecision
    reason: str
