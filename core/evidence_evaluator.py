"""Evaluation boundary that consumes explicit repository evidence.

This module connects the read-only Evidence layer to the existing deterministic
Evaluator without changing the evaluator's core decision rules.
"""

from __future__ import annotations

from typing import Any, Mapping

from .canon_guard import ValidationResult
from .evidence_adapter import claims_to_checks
from .evidence_state import EvidenceClaim
from .evaluator import EvaluationReport, evaluate_candidate
from .loop import Evaluation


def _check_decision(value: Any) -> str:
    """Normalise a candidate-supplied check for conflict detection."""
    if isinstance(value, bool):
        return "pass" if value else "fail"
    if isinstance(value, dict):
        decision = value.get("decision")
        return decision if decision in {"pass", "fail", "unknown"} else "unknown"
    return "unknown"


def evaluate_candidate_with_evidence(
    candidate: dict[str, Any],
    validation: ValidationResult,
    claims: Mapping[str, EvidenceClaim],
) -> EvaluationReport:
    """Evaluate a candidate after adding explicit Evidence-derived checks.

    The original candidate mapping is never mutated. Evidence-derived checks
    are merged into a fresh checks mapping and passed through the existing
    evaluator. An Evidence claim therefore cannot bypass validation or create
    a new decision rule: it only supplies an explicit check result.

    Evidence-backed invariants are evaluated before the generic quality-check
    policy. A contradicted claim forces continuation and an unknown claim forces
    human review, even when the claim name is not one of the legacy required
    quality checks. Matching candidate checks are harmlessly coalesced, while
    conflicting explicit results force human review rather than silent choice.
    """

    evidence_checks = claims_to_checks(claims)
    existing = candidate.get("checks", {})
    existing_checks = dict(existing) if isinstance(existing, dict) else {}

    conflicts = [
        name
        for name, evidence_check in evidence_checks.items()
        if name in existing_checks
        and _check_decision(existing_checks[name]) != evidence_check["decision"]
    ]

    if conflicts:
        return EvaluationReport(
            Evaluation(
                "human_review",
                f"conflicting candidate/evidence checks: {', '.join(sorted(conflicts))}",
            ),
            (),
        )

    failed_evidence = [
        name for name, check in evidence_checks.items() if check["decision"] == "fail"
    ]
    if failed_evidence:
        return EvaluationReport(
            Evaluation(
                "continue",
                f"evidence claims contradicted: {', '.join(sorted(failed_evidence))}",
            ),
            (),
        )

    unknown_evidence = [
        name for name, check in evidence_checks.items() if check["decision"] == "unknown"
    ]
    if unknown_evidence:
        return EvaluationReport(
            Evaluation(
                "human_review",
                f"evidence claims remain unknown: {', '.join(sorted(unknown_evidence))}",
            ),
            (),
        )

    merged_checks = {**existing_checks, **evidence_checks}
    enriched_candidate = dict(candidate)
    enriched_candidate["checks"] = merged_checks

    return evaluate_candidate(enriched_candidate, validation)
