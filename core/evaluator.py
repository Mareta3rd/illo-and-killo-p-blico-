"""Deterministic evaluator for Core candidates.

The evaluator is deliberately separate from generation and from the Canon
Guard. It consumes upstream validation plus explicit candidate checks and
returns one of the loop's bounded decisions. It never invents a missing
criterion, repairs a candidate, or changes repository knowledge.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Literal

from .canon_guard import ValidationResult
from .loop import Evaluation


CheckDecision = Literal["pass", "fail", "unknown"]

REQUIRED_CHECKS = (
    "intention",
    "canon",
    "coherence",
    "reuse_intention",
)


@dataclass(frozen=True)
class CandidateCheck:
    """One explicit quality check supplied by an execution/evaluation layer."""

    name: str
    decision: CheckDecision
    reason: str


@dataclass(frozen=True)
class EvaluationReport:
    """Auditable evaluation result used to drive the loop."""

    evaluation: Evaluation
    checks: tuple[CandidateCheck, ...]


def _normalise_checks(candidate: dict[str, Any]) -> tuple[CandidateCheck, ...]:
    raw = candidate.get("checks")
    if not isinstance(raw, dict):
        return ()

    checks: list[CandidateCheck] = []
    for name, value in raw.items():
        if isinstance(value, bool):
            decision: CheckDecision = "pass" if value else "fail"
            reason = "explicit boolean check"
        elif isinstance(value, dict):
            raw_decision = value.get("decision")
            decision = raw_decision if raw_decision in {"pass", "fail", "unknown"} else "unknown"
            reason = str(value.get("reason", ""))
        else:
            decision = "unknown"
            reason = "check has no recognised result"

        checks.append(CandidateCheck(str(name), decision, reason))

    return tuple(sorted(checks, key=lambda item: item.name))


def evaluate_candidate(
    candidate: dict[str, Any],
    validation: ValidationResult,
) -> EvaluationReport:
    """Evaluate a candidate without guessing missing quality information.

    Decision policy:
    - canon/intention ambiguity requiring review -> ``human_review``;
    - invalid but potentially repairable validation -> ``continue``;
    - missing required quality checks -> ``human_review``;
    - any failed required check -> ``continue``;
    - all required checks pass -> ``accept``.
    """
    checks = _normalise_checks(candidate)

    if validation.requires_human_review:
        return EvaluationReport(
            Evaluation("human_review", "canon validation requires human review"),
            checks,
        )

    if not validation.valid:
        return EvaluationReport(
            Evaluation("continue", "candidate failed deterministic canon validation"),
            checks,
        )

    by_name = {check.name: check for check in checks}
    missing = [name for name in REQUIRED_CHECKS if name not in by_name]
    if missing:
        return EvaluationReport(
            Evaluation(
                "human_review",
                f"missing required checks: {', '.join(missing)}",
            ),
            checks,
        )

    unknown = [name for name in REQUIRED_CHECKS if by_name[name].decision == "unknown"]
    if unknown:
        return EvaluationReport(
            Evaluation(
                "human_review",
                f"required checks are ambiguous: {', '.join(unknown)}",
            ),
            checks,
        )

    failed = [name for name in REQUIRED_CHECKS if by_name[name].decision == "fail"]
    if failed:
        return EvaluationReport(
            Evaluation(
                "continue",
                f"required checks failed: {', '.join(failed)}",
            ),
            checks,
        )

    return EvaluationReport(
        Evaluation("accept", "all required quality checks passed"),
        checks,
    )
