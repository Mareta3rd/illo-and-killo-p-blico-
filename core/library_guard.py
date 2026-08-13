"""Validate explicit references and structural integrity of canonical libraries."""

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


def validate_library_catalog(
    knowledge: RepositoryKnowledge | dict[str, Any],
) -> tuple[LibraryIssue, ...]:
    """Validate the structural contract of every canonical library entry.

    This intentionally validates structure, not the semantic meaning of an
    invariant. Invariant semantics need a separate explicit contract rather
    than being inferred from their names.
    """

    data = _data_from_knowledge(knowledge)
    issues: list[LibraryIssue] = []

    for library_name in LIBRARY_NAMES:
        library = data.get(library_name, {})
        if not isinstance(library, dict):
            issues.append(
                LibraryIssue(
                    code="LIBRARY_CATALOG_INVALID",
                    message=f"La biblioteca canónica '{library_name}' debe ser un mapa de recursos.",
                )
            )
            continue

        for entry_id, entry in library.items():
            prefix = f"{library_name}.{entry_id}"
            if not isinstance(entry, dict):
                issues.append(
                    LibraryIssue(
                        code="LIBRARY_ENTRY_INVALID",
                        message=f"La entrada '{prefix}' debe ser un objeto.",
                    )
                )
                continue

            name = entry.get("name")
            if not isinstance(name, str) or not name.strip():
                issues.append(
                    LibraryIssue(
                        code="LIBRARY_NAME_MISSING",
                        message=f"La entrada '{prefix}' necesita un nombre canónico.",
                    )
                )

            role = entry.get("role")
            if not isinstance(role, str) or not role.strip():
                issues.append(
                    LibraryIssue(
                        code="LIBRARY_ROLE_MISSING",
                        message=f"La entrada '{prefix}' necesita un rol canónico.",
                    )
                )

            invariants = entry.get("invariants")
            if not isinstance(invariants, list) or not invariants:
                issues.append(
                    LibraryIssue(
                        code="LIBRARY_INVARIANTS_MISSING",
                        message=f"La entrada '{prefix}' necesita al menos un invariante canónico.",
                    )
                )
            elif any(not isinstance(item, str) or not item.strip() for item in invariants):
                issues.append(
                    LibraryIssue(
                        code="LIBRARY_INVARIANT_INVALID",
                        message=f"La entrada '{prefix}' contiene invariantes no válidos.",
                    )
                )

    return tuple(issues)
