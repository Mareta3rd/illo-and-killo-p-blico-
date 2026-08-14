"""Validate proposed pieces against canon and intention rules.

The guard is deliberately deterministic. It validates proposals but never
rewrites them, invents intentions, or mutates repository knowledge.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any

from .categorical_evaluator import evaluate_categorical
from .invariant_constraints import load_categorical_constraint
from .invariant_evaluator import evaluate_quantitative
from .invariant_taxonomy import load_invariant_classification
from .library_guard import validate_library_elements
from .loader import RepositoryKnowledge
from .structural_constraints import load_structural_constraint
from .structural_evaluator import evaluate_structural


@dataclass(frozen=True)
class ValidationIssue:
    code: str
    message: str
    severity: str = "error"


@dataclass(frozen=True)
class ValidationResult:
    valid: bool
    requires_human_review: bool
    issues: tuple[ValidationIssue, ...]


RECURRING_ASSETS = {"mosquito", "shark", "ham", "espeto"}


def _character_present(proposal: dict[str, Any], character: str) -> bool:
    characters = proposal.get("characters", ())
    return character in characters


def _has_intention(element: dict[str, Any]) -> bool:
    intention = element.get("intention")
    return isinstance(intention, str) and bool(intention.strip())


def _data_from_knowledge(knowledge: RepositoryKnowledge | dict[str, Any]) -> dict[str, Any]:
    """Accept the canonical loader object while keeping the helper testable."""
    if isinstance(knowledge, RepositoryKnowledge):
        return knowledge.data
    return knowledge


def _validate_killo(
    proposal: dict[str, Any],
    killo: dict[str, Any],
    issues: list[ValidationIssue],
) -> None:
    invariants = set(killo.get("invariants", ()))
    elements = proposal.get("elements", ())
    has_clavel = any(
        isinstance(element, dict) and element.get("id") == "clavel"
        for element in elements
    )
    exception = proposal.get("documented_exceptions", ())

    if "clavel" in invariants and not has_clavel and "killo_clavel" not in exception:
        issues.append(
            ValidationIssue(
                code="CANON_KILLO_CLAVEL_MISSING",
                message="Killo está presente pero falta su clavel canónico.",
            )
        )

    body = killo.get("body", {})
    spots_rule = body.get("spots", {}) if isinstance(body, dict) else {}
    count_rule = spots_rule.get("count", {}) if isinstance(spots_rule, dict) else {}
    black_spots = next(
        (
            element
            for element in elements
            if isinstance(element, dict) and element.get("id") == "black_spots"
        ),
        None,
    )

    if "black_spots" in invariants and black_spots is None:
        issues.append(
            ValidationIssue(
                code="CANON_KILLO_SPOTS_MISSING",
                message="Killo está presente pero faltan sus manchas negras canónicas.",
            )
        )

    if isinstance(black_spots, dict) and "count" in black_spots and isinstance(count_rule, dict):
        spot_count = black_spots["count"]
        evaluation = evaluate_quantitative(
            "count",
            spot_count,
            minimum=count_rule.get("min"),
            maximum=count_rule.get("max"),
        )
        if evaluation.decision == "fail":
            issues.append(
                ValidationIssue(
                    code="CANON_KILLO_SPOTS_OUT_OF_RANGE",
                    message=f"Killo tiene {spot_count} manchas negras; {evaluation.reason}.",
                )
            )

        expected_color = spots_rule.get("color")
        actual_color = black_spots.get("color")
        if (
            isinstance(expected_color, str)
            and isinstance(actual_color, str)
            and actual_color != expected_color
        ):
            issues.append(
                ValidationIssue(
                    code="CANON_KILLO_SPOTS_COLOR_INVALID",
                    message=(
                        f"Killo tiene manchas negras de color {actual_color}; "
                        f"el color canónico permitido es {expected_color}."
                    ),
                )
            )


def _validate_categorical_library_invariants(
    proposal: dict[str, Any],
    issues: list[ValidationIssue],
) -> None:
    """Apply only explicitly classified categorical constraints to library elements."""
    root = Path(__file__).resolve().parents[1]
    classifications = load_invariant_classification(root)
    categorical: dict[tuple[str, str], list[str]] = {}
    for item in classifications:
        if item.family == "categorical":
            categorical.setdefault((item.catalog, item.entry), []).append(item.invariant)

    for element in proposal.get("elements", ()):
        if not isinstance(element, dict):
            continue
        catalog = element.get("library")
        entry = element.get("id")
        if not isinstance(catalog, str) or not isinstance(entry, str):
            continue

        for invariant in categorical.get((catalog, entry), []):
            expected = load_categorical_constraint(root, catalog, entry, invariant)
            if expected is None:
                issues.append(
                    ValidationIssue(
                        code="CANON_CATEGORICAL_INVARIANT_UNKNOWN",
                        message=(
                            f"El invariant categórico '{invariant}' de "
                            f"'{catalog}/{entry}' no tiene restricción canónica explícita."
                        ),
                    )
                )
                continue

            evaluation = evaluate_categorical(
                invariant,
                element.get(invariant),
                expected=expected,
            )
            if evaluation.decision == "fail":
                issues.append(
                    ValidationIssue(
                        code="CANON_CATEGORICAL_INVARIANT_FAILED",
                        message=evaluation.reason,
                    )
                )
            elif evaluation.decision == "unknown":
                issues.append(
                    ValidationIssue(
                        code="CANON_CATEGORICAL_INVARIANT_UNKNOWN",
                        message=evaluation.reason,
                    )
                )


def _validate_structural_library_invariants(
    proposal: dict[str, Any],
    issues: list[ValidationIssue],
) -> None:
    """Apply only explicitly classified structural constraints to library elements."""
    root = Path(__file__).resolve().parents[1]
    classifications = load_invariant_classification(root)
    structural: dict[tuple[str, str], list[str]] = {}
    for item in classifications:
        if item.family == "structural":
            structural.setdefault((item.catalog, item.entry), []).append(item.invariant)

    for element in proposal.get("elements", ()):
        if not isinstance(element, dict):
            continue
        catalog = element.get("library")
        entry = element.get("id")
        if not isinstance(catalog, str) or not isinstance(entry, str):
            continue

        for invariant in structural.get((catalog, entry), []):
            constraint = load_structural_constraint(root, catalog, entry, invariant)
            if constraint is None:
                continue
            required_paths, expected = constraint
            evaluation = evaluate_structural(
                invariant,
                element,
                required_paths=required_paths,
                expected=expected,
            )
            if evaluation.decision == "fail":
                issues.append(
                    ValidationIssue(
                        code="CANON_STRUCTURAL_INVARIANT_FAILED",
                        message=evaluation.reason,
                    )
                )
            elif evaluation.decision == "unknown":
                issues.append(
                    ValidationIssue(
                        code="CANON_STRUCTURAL_INVARIANT_UNKNOWN",
                        message=evaluation.reason,
                    )
                )


def validate_piece(
    proposal: dict[str, Any],
    knowledge: RepositoryKnowledge | dict[str, Any],
) -> ValidationResult:
    """Validate a proposed piece against loaded repository knowledge.

    ``proposal`` and ``knowledge`` are treated as read-only. No missing
    intention is inferred by this function.
    """

    issues: list[ValidationIssue] = []
    data = _data_from_knowledge(knowledge)
    characters = data.get("characters", {})

    if _character_present(proposal, "killo"):
        killo = characters.get("killo", {})
        _validate_killo(proposal, killo, issues)

    library_issues = validate_library_elements(proposal.get("elements", ()), knowledge)
    issues.extend(
        ValidationIssue(
            code=issue.code,
            message=issue.message,
            severity=issue.severity,
        )
        for issue in library_issues
    )

    _validate_categorical_library_invariants(proposal, issues)
    _validate_structural_library_invariants(proposal, issues)

    # Every explicit element needs an explainable intention.
    for element in proposal.get("elements", ()):
        if not isinstance(element, dict):
            issues.append(
                ValidationIssue(
                    code="ELEMENT_INVALID",
                    message="Cada elemento debe representarse como un objeto.",
                )
            )
            continue

        if not _has_intention(element):
            issues.append(
                ValidationIssue(
                    code="INTENTION_MISSING",
                    message=f"El elemento '{element.get('id', 'unknown')}' no tiene intención explícita.",
                )
            )

        element_id = str(element.get("id", "")).lower()
        if element_id in RECURRING_ASSETS and not _has_intention(element):
            issues.append(
                ValidationIssue(
                    code="REUSE_WITHOUT_INTENTION",
                    message=f"El recurso recurrente '{element_id}' no puede reutilizarse sin intención narrativa o cómica explícita.",
                )
            )

    requires_human_review = any(
        issue.code in {
            "CANON_KILLO_CLAVEL_MISSING",
            "CANON_KILLO_SPOTS_MISSING",
            "REUSE_WITHOUT_INTENTION",
            "LIBRARY_INVALID",
            "LIBRARY_ID_MISSING",
            "LIBRARY_ENTRY_NOT_FOUND",
            "LIBRARY_INTENTION_MISSING",
            "CANON_CATEGORICAL_INVARIANT_UNKNOWN",
            "CANON_STRUCTURAL_INVARIANT_UNKNOWN",
        }
        for issue in issues
    )

    return ValidationResult(
        valid=not issues,
        requires_human_review=requires_human_review,
        issues=tuple(issues),
    )
