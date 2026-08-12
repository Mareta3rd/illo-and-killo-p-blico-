"""Validate proposed pieces against canon and intention rules.

The guard is deliberately deterministic. It validates proposals but never
rewrites them, invents intentions, or mutates repository knowledge.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from .library_guard import validate_library_elements
from .loader import RepositoryKnowledge


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

    if (
        isinstance(black_spots, dict)
        and isinstance(black_spots.get("count"), int)
        and isinstance(count_rule, dict)
    ):
        spot_count = black_spots["count"]
        min_count = count_rule.get("min")
        max_count = count_rule.get("max")

        if (
            isinstance(min_count, int)
            and spot_count < min_count
            or isinstance(max_count, int)
            and spot_count > max_count
        ):
            issues.append(
                ValidationIssue(
                    code="CANON_KILLO_SPOTS_OUT_OF_RANGE",
                    message=(
                        f"Killo tiene {spot_count} manchas negras; "
                        f"el rango canónico permitido es {min_count}-{max_count}."
                    ),
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
        }
        for issue in issues
    )

    return ValidationResult(
        valid=not issues,
        requires_human_review=requires_human_review,
        issues=tuple(issues),
    )
