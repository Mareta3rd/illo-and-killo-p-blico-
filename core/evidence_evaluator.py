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

    When an Evidence claim uses the same check name as a candidate-supplied
    check, the Evidence result is authoritative for that repository-evidence
    check. Its original claim and sources remain available in the merged
    check payload used by the evaluator.
    """

    evidence_checks = claims_to_checks(claims)
    existing = candidate.get("checks", {})
    existing_checks = dict(existing) if isinstance(existing, dict) else {}

    merged_checks = {**existing_checks, **evidence_checks}
    enriched_candidate = dict(candidate)
    enriched_candidate["checks"] = merged_checks

    return evaluate_candidate(enriched_candidate, validation)
