"""Detect regressions in explicit semantic checks between candidate versions."""

from __future__ import annotations

from dataclasses import dataclass

from .evaluator import EvaluationReport


@dataclass(frozen=True)
class SemanticRegression:
    """One previously passing check that no longer passes."""

    name: str
    previous_decision: str
    current_decision: str
    reason: str


def detect_semantic_regressions(
    previous: EvaluationReport,
    current: EvaluationReport,
) -> tuple[SemanticRegression, ...]:
    """Return checks that regress from ``pass`` to a non-passing decision.

    Missing checks in the current candidate are treated as regressions when
    they were explicitly passing before. The reports are read-only; neither
    report nor its check collections are modified.
    """
    previous_checks = {check.name: check for check in previous.checks}
    current_checks = {check.name: check for check in current.checks}

    regressions: list[SemanticRegression] = []
    for name, previous_check in previous_checks.items():
        if previous_check.decision != "pass":
            continue

        current_check = current_checks.get(name)
        current_decision = current_check.decision if current_check else "missing"
        if current_check is not None and current_check.decision == "pass":
            continue

        reason = (
            current_check.reason
            if current_check is not None
            else "check disappeared from the current evaluation"
        )
        regressions.append(
            SemanticRegression(
                name=name,
                previous_decision=previous_check.decision,
                current_decision=current_decision,
                reason=reason,
            )
        )

    return tuple(sorted(regressions, key=lambda item: item.name))
