"""Deterministic evaluation primitives for structural invariants."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Literal


StructuralDecision = Literal["pass", "fail", "unknown"]


@dataclass(frozen=True)
class StructuralEvaluation:
    invariant: str
    decision: StructuralDecision
    reason: str


def _read_path(value: Any, path: tuple[str, ...]) -> tuple[bool, Any]:
    current = value
    for key in path:
        if not isinstance(current, dict) or key not in current:
            return False, None
        current = current[key]
    return True, current


def evaluate_structural(
    invariant: str,
    observed: Any,
    *,
    required_paths: tuple[tuple[str, ...], ...] = (),
    expected: tuple[tuple[tuple[str, ...], Any], ...] = (),
) -> StructuralEvaluation:
    """Evaluate required structure without inferring absent structure."""
    if not isinstance(observed, dict):
        return StructuralEvaluation(invariant, "unknown", "observed structure is not a mapping")

    for path in required_paths:
        found, _ = _read_path(observed, path)
        if not found:
            return StructuralEvaluation(
                invariant,
                "unknown",
                f"required structural path is missing: {'.'.join(path)}",
            )

    for path, expected_value in expected:
        found, actual = _read_path(observed, path)
        if not found:
            return StructuralEvaluation(
                invariant,
                "unknown",
                f"required structural path is missing: {'.'.join(path)}",
            )
        if type(actual) is not type(expected_value) or actual != expected_value:
            return StructuralEvaluation(
                invariant,
                "fail",
                f"structural value at {'.'.join(path)} does not match canonical value",
            )

    return StructuralEvaluation(invariant, "pass", "required structure is present and canonically coherent")
