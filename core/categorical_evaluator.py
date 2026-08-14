"""Deterministic evaluation primitives for categorical invariants."""

from __future__ import annotations

from typing import Any

from .invariant_result import InvariantDecision, InvariantEvaluation

CategoricalDecision = InvariantDecision
CategoricalEvaluation = InvariantEvaluation


def evaluate_categorical(
    invariant: str,
    observed: Any,
    *,
    expected: Any,
) -> CategoricalEvaluation:
    """Evaluate an observed categorical value against its canonical value.

    Comparison is deliberately strict: values are never coerced between types,
    and missing observed or canonical values produce ``unknown``.
    """

    if expected is None:
        return CategoricalEvaluation(
            invariant,
            "unknown",
            "canonical categorical value is missing",
        )

    if observed is None:
        return CategoricalEvaluation(
            invariant,
            "unknown",
            "observed categorical value is missing",
        )

    if type(observed) is not type(expected):
        return CategoricalEvaluation(
            invariant,
            "unknown",
            "observed and canonical categorical values have different types",
        )

    if observed == expected:
        return CategoricalEvaluation(
            invariant,
            "pass",
            "observed value matches canonical categorical value",
        )

    return CategoricalEvaluation(
        invariant,
        "fail",
        f"observed value {observed!r} does not match canonical value {expected!r}",
    )
