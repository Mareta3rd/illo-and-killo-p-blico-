"""Validate explicit references to the canonical content libraries."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from .loader import RepositoryKnowledge


LIBRARY_NAMES = ("objects", "fauna", "heritage")


@dataclass(frozen=True)
class LibraryIssue:
    code: str
    message: str
    severity: str = "error"


def _data_from_knowledge(knowledge: RepositoryKnowledge | dict[str, Any]) -> dict[str, Any]:
    if isinstance(knowledge, RepositoryKnowledge):
        return knowledge.data
    return knowledge


def validate_library_element(
    element: dict[str, Any],
    knowledge: RepositoryKnowledge | dict[str, Any],
) -> tuple[LibraryIssue, ...]:
    """Validate one explicitly namespaced library reference.

    Library references use ``library`` plus ``id``. The guard verifies that
    the requested entry exists in the canonical library and that its use has
    an explicit intention. It never infers a library or mutates the proposal.
    """

    library = element.get("library")
    element_id = element.get("id")
    issues: list[LibraryIssue] = []

    if library is None:
        return ()

    if not isinstance(library, str) or library not in LIBRARY_NAMES:
        issues.append(
            LibraryIssue(
                code="LIBRARY_INVALID",
                message=f"La biblioteca '{library}' no es una biblioteca canónica válida.",
            )
        )
        return tuple(issues)

    if not isinstance(element_id, str) or not element_id:
        issues.append(
            LibraryIssue(
                code="LIBRARY_ID_MISSING",
                message="Una referencia de biblioteca necesita un id explícito.",
            )
        )
        return tuple(issues)

    data = _data_from_knowledge(knowledge)
    library_data = data.get(library, {})
    entry = library_data.get(element_id) if isinstance(library_data, dict) else None

    if not isinstance(entry, dict):
        issues.append(
            LibraryIssue(
                code="LIBRARY_ENTRY_NOT_FOUND",
                message=f"El recurso '{element_id}' no existe en la biblioteca canónica '{library}'.",
            )
        )

    intention = element.get("intention")
    if not isinstance(intention, str) or not intention.strip():
        issues.append(
            LibraryIssue(
                code="LIBRARY_INTENTION_MISSING",
                message=f"El recurso de biblioteca '{element_id}' necesita una intención explícita.",
            )
        )

    return tuple(issues)


def validate_library_elements(
    elements: Any,
    knowledge: RepositoryKnowledge | dict[str, Any],
) -> tuple[LibraryIssue, ...]:
    """Validate all explicitly namespaced library references in a proposal."""

    issues: list[LibraryIssue] = []
    for element in elements or ():
        if isinstance(element, dict) and "library" in element:
            issues.extend(validate_library_element(element, knowledge))
    return tuple(issues)
