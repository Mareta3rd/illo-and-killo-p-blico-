"""Deterministic evaluation primitives for classified invariants."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Literal


InvariantDecision = Literal["pass", "fail", "unknown"]


@dataclass(frozen=True)
class InvariantEvaluation:
    invariant: str
    decision: InvariantDecision
    reason: str


def evaluate_quantitative(
    invariant: str,
    observed: Any,
    *,
    minimum: int | float | None = None,
    maximum: int | float | None = None,
) -> InvariantEvaluation:
    """Evaluate a numeric invariant against optional inclusive bounds."""

    if not isinstance(observed, (int, float)) or isinstance(observed, bool):
        return InvariantEvaluation(
            invariant,
            "unknown",
            "observed value is not a numeric scalar",
        )

    if minimum is not None and not isinstance(minimum, (int, float)):
        return InvariantEvaluation(invariant, "unknown", "minimum bound is invalid")
    if maximum is not None and not isinstance(maximum, (int, float)):
        return InvariantEvaluation(invariant, "unknown", "maximum bound is invalid")

    if minimum is not None and observed < minimum:
        return InvariantEvaluation(
            invariant,
            "fail",
            f"observed value {observed} is below minimum {minimum}",
        )

    if maximum is not None and observed > maximum:
        return InvariantEvaluation(
            invariant,
            "fail",
            f"observed value {observed} is above maximum {maximum}",
        )

    return InvariantEvaluation(invariant, "pass", "observed value is within canonical bounds")
