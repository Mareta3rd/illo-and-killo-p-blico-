"""Immutable audit helpers for semantic candidate evaluation."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Mapping

from .evaluator import EvaluationReport
from .semantic_regression import SemanticRegression


@dataclass(frozen=True)
class SemanticAuditRecord:
    """Stable, read-only record of one candidate evaluation."""

    iteration: int
    candidate_fingerprint: str
    decision: str
    reason: str
    regressions: tuple[SemanticRegression, ...]


def _stable_repr(value: Any) -> str:
    if isinstance(value, Mapping):
        items = ",".join(
            f"{_stable_repr(key)}:{_stable_repr(value[key])}"
            for key in sorted(value, key=lambda item: repr(item))
        )
        return "{" + items + "}"
    if isinstance(value, (list, tuple)):
        return "[" + ",".join(_stable_repr(item) for item in value) + "]"
    if isinstance(value, set):
        return "{" + ",".join(sorted(_stable_repr(item) for item in value)) + "}"
    return repr(value)


def fingerprint_candidate(candidate: Mapping[str, Any]) -> str:
    """Return a deterministic representation suitable for audit comparison."""
    return _stable_repr(candidate)


def build_semantic_audit_record(
    iteration: int,
    candidate: Mapping[str, Any],
    report: EvaluationReport,
    regressions: tuple[SemanticRegression, ...] = (),
) -> SemanticAuditRecord:
    """Build one immutable audit record without mutating inputs."""
    return SemanticAuditRecord(
        iteration=iteration,
        candidate_fingerprint=fingerprint_candidate(candidate),
        decision=report.evaluation.decision,
        reason=report.evaluation.reason,
        regressions=tuple(regressions),
    )
