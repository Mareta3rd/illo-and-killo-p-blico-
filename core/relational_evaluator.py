"""Deterministic evaluation primitives for relational invariants."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Literal

RelationalDecision = Literal["pass", "fail", "unknown"]


@dataclass(frozen=True)
class RelationalEvaluation:
    invariant: str
    decision: RelationalDecision
    reason: str


def _read_path(value: Any, path: tuple[str, ...]) -> tuple[bool, Any]:
    current = value
    for key in path:
        if not isinstance(current, dict) or key not in current:
            return False, None
        current = current[key]
    return True, current


def evaluate_relational(
    invariant: str,
    observed: Any,
    *,
    left_path: tuple[str, ...] = (),
    right_path: tuple[str, ...] = (),
) -> RelationalEvaluation:
    """Compare two canonical paths without coercion or inference."""
    if not isinstance(observed, dict):
        return RelationalEvaluation(invariant, "unknown", "observed relation is not a mapping")

    left_found, left = _read_path(observed, left_path)
    right_found, right = _read_path(observed, right_path)

    if not left_found or not right_found:
        missing = []
        if not left_found:
            missing.append(".".join(left_path))
        if not right_found:
            missing.append(".".join(right_path))
        return RelationalEvaluation(
            invariant,
            "unknown",
            f"required relational path is missing: {', '.join(missing)}",
        )

    if type(left) is not type(right):
        return RelationalEvaluation(
            invariant,
            "fail",
            "related values have incompatible types",
        )

    if left == right:
        return RelationalEvaluation(
            invariant,
            "pass",
            "required relation holds",
        )

    return RelationalEvaluation(
        invariant,
        "fail",
        "required relation is violated",
    )
