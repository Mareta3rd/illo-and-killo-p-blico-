"""Build a bounded, deterministic semantic context for Core prompt compilation.

This module transforms authoritative repository knowledge into a compact,
provider-neutral representation. It does not invent canon, call providers,
or make acceptance decisions.
"""

from __future__ import annotations

from dataclasses import dataclass
import re
import unicodedata
from typing import Any, Mapping


_MAX_ENTRIES = 32
_MAX_LINE_LENGTH = 260

_ROUTE_SECTIONS: dict[str, tuple[tuple[str, str, int], ...]] = {
    "character": (
        ("humor", "## Dinámica Arsa / Pisha", 4),
        ("semantic", "## 2. Invariante", 6),
        ("palette", "## Base de personajes", 6),
    ),
    "gag": (
        ("humor", "## Principios", 3),
        ("humor", "## Gramática del gag", 3),
        ("humor", "## Andalucía", 4),
        ("semantic", "## 16. Gag", 4),
        ("semantic", "## 17. Lenguaje visual", 2),
    ),
    "parody": (
        ("humor", "## Principios", 3),
        ("humor", "## Andalucía", 4),
        ("semantic", "## 15. Parodia", 5),
        ("semantic", "## 17. Lenguaje visual", 3),
        ("palette", "## Principio", 2),
    ),
    "merchandising": (
        ("semantic", "## 2. Invariante", 5),
        ("palette", "## Base de personajes", 7),
        ("palette", "## Producción", 5),
    ),
    "3d": (
        ("semantic", "## 2. Invariante", 6),
        ("semantic", "## 10. Identidad frente a representación", 5),
        ("semantic", "## 17. Lenguaje visual", 3),
    ),
    "general": (
        ("semantic", "## 2. Invariante", 5),
        ("semantic", "## 16. Gag", 5),
        ("semantic", "## 17. Lenguaje visual", 3),
    ),
}

_ROUTE_DECISION_LIMITS = {
    "character": 2,
    "gag": 2,
    "parody": 2,
    "merchandising": 2,
    "3d": 2,
    "general": 3,
}


@dataclass(frozen=True)
class SemanticContext:
    """Immutable, bounded semantic context passed to an execution layer."""

    entries: tuple[str, ...]

    def __post_init__(self) -> None:
        if len(self.entries) > _MAX_ENTRIES:
            raise ValueError("Semantic context exceeds the maximum entry count.")
        if any(len(entry) > _MAX_LINE_LENGTH for entry in self.entries):
            raise ValueError("Semantic context contains an oversized entry.")


def _normalize(value: str) -> str:
    decomposed = unicodedata.normalize("NFKD", value.lower())
    return "".join(char for char in decomposed if not unicodedata.combining(char))


def _tokens(value: str) -> set[str]:
    return {
        token
        for token in re.findall(r"[a-z0-9]+", _normalize(value))
        if len(token) >= 4
    }


def _compact(value: Any, limit: int = 220) -> str:
    text = " ".join(str(value).split())
    if len(text) <= limit:
        return text
    return text[: limit - 1].rstrip() + "…"


def _extract_section(markdown: str, heading: str, limit: int) -> list[str]:
    lines = markdown.splitlines()
    start = None

    for index, line in enumerate(lines):
        if line.strip() == heading:
            start = index + 1
            break

    if start is None:
        return []

    extracted: list[str] = []
    for line in lines[start:]:
        stripped = line.strip()
        if stripped.startswith("## ") and stripped != heading:
            break
        if (
            stripped.startswith("- ")
            or stripped.startswith("**")
            or stripped.startswith("### ")
        ):
            extracted.append(_compact(stripped))
        elif stripped and stripped.startswith("La "):
            extracted.append(_compact(stripped))
        if len(extracted) >= limit:
            break

    return extracted


def _character_entries(characters: Mapping[str, Any]) -> list[str]:
    entries: list[str] = []

    for key in sorted(characters):
        value = characters[key] or {}
        body = value.get("body", {}) if isinstance(value, dict) else {}
        arms = body.get("arms", {}) if isinstance(body, dict) else {}
        hands = arms.get("hands", {}) if isinstance(arms, dict) else {}
        legs = body.get("legs", {}) if isinstance(body, dict) else {}
        feet = legs.get("feet", {}) if isinstance(legs, dict) else {}
        behavior = value.get("behavioral_grammar", {}) if isinstance(value, dict) else {}
        invariants = value.get("invariants", []) if isinstance(value, dict) else []

        entries.append(
            _compact(
                "character="
                f"{key}; "
                f"name={value.get('name', key)}; "
                f"species_hint={value.get('species_hint', 'unspecified')}; "
                f"invariants={','.join(str(item) for item in invariants)}; "
                f"hands={hands.get('color', 'unspecified')},{hands.get('fingers', 'unspecified')}_finger; "
                f"hooves={feet.get('color', 'unspecified')},{feet.get('type', 'unspecified')}; "
                f"behavior={','.join(f'{item}:{behavior[item]}' for item in sorted(behavior))}"
            )
        )

    return entries


def _relationship_entries(relationships: Mapping[str, Any]) -> list[str]:
    root = relationships.get("relationships", {}) if isinstance(relationships, dict) else {}
    entries: list[str] = []

    for key in sorted(root):
        value = root[key] or {}
        dynamics = value.get("dynamics", []) if isinstance(value, dict) else []
        entries.append(
            _compact(
                "relationship="
                f"{key}; "
                f"participants={','.join(value.get('participants', []))}; "
                f"dynamics={','.join(str(item) for item in dynamics)}; "
                f"protagonist_balance={value.get('protagonist_balance', 'unspecified')}; "
                f"conflict_style={value.get('conflict_style', 'unspecified')}; "
                f"loyalty={value.get('loyalty', 'unspecified')}"
            )
        )

    return entries


def _decision_entries(decisions: Mapping[str, Any], route: str) -> list[str]:
    values = decisions.get("decisions", []) if isinstance(decisions, dict) else []
    entries: list[str] = []

    route_topics = {
        "character": ("hands", "spots", "clavel"),
        "gag": ("hands", "spots"),
        "parody": ("parody", "cultural"),
        "merchandising": ("hands", "spots", "cultural"),
        "3d": ("hands", "spots"),
        "general": ("hands", "spots", "parody", "cultural"),
    }
    wanted = route_topics.get(route, route_topics["general"])

    for decision in sorted(values, key=lambda item: str(item.get("id", ""))):
        topic = str(decision.get("topic", ""))
        if not any(fragment in _normalize(topic) for fragment in wanted):
            continue
        entries.append(
            _compact(
                "decision="
                f"{topic}; "
                f"status={decision.get('status', 'unspecified')}; "
                f"{decision.get('decision', '')}"
            )
        )

    return entries[: _ROUTE_DECISION_LIMITS.get(route, 3)]


def _option_entries(data: Mapping[str, Any], key: str, limit: int) -> list[str]:
    values = data.get(key, {}) if isinstance(data, dict) else {}
    entries: list[str] = []

    for item_key in sorted(values)[:limit]:
        value = values[item_key] or {}
        entries.append(
            _compact(
                f"{key[:-1] if key.endswith('s') else key}={item_key}; "
                f"name={value.get('name', item_key)}; "
                f"role={value.get('role', 'unspecified')}"
            )
        )

    return entries


def _relevant_claim_entries(
    claims: Mapping[str, Any],
    idea: str,
    route: str,
    objects: Mapping[str, Any],
) -> list[str]:
    if route != "gag" or not isinstance(claims, dict):
        return []

    idea_tokens = _tokens(idea)
    relevance_tokens = set(idea_tokens)

    if isinstance(objects, dict):
        for object_key, value in objects.items():
            value = value or {}
            name = str(value.get("name", object_key))
            object_tokens = _tokens(f"{object_key} {name}")
            if idea_tokens & object_tokens:
                affordances = value.get("affordances", [])
                relevance_tokens.update(_tokens(" ".join(str(item) for item in affordances)))

    entries: list[tuple[int, str]] = []

    for key in sorted(claims):
        value = claims[key] or {}
        source = (
            f"{key} {value.get('statement', '')}"
            if isinstance(value, dict)
            else f"{key} {value}"
        )
        score = len(relevance_tokens & _tokens(source))

        explicit_id = _normalize(key).replace("_", "/") in _normalize(idea).replace("_", "/")
        if explicit_id:
            score += 100

        if score > 0:
            entries.append(
                (
                    score,
                    _compact(
                        f"claim={key}; "
                        f"{value.get('statement', '')}; "
                        f"role={value.get('narrative_role', 'unspecified')}; "
                        f"salience={value.get('visual_salience', 'unspecified')}"
                    ),
                )
            )

    entries.sort(key=lambda item: (-item[0], item[1]))
    return [entry for _, entry in entries[:4]]


def build_semantic_context(
    *,
    idea: str,
    route: str,
    data: Mapping[str, Any],
    markdown: Mapping[str, str],
) -> SemanticContext:
    """Build a bounded semantic context from authoritative repository sources."""

    entries: list[str] = []

    characters = data.get("characters", {})
    entries.extend(_character_entries(characters))

    if route in {"gag", "parody", "general"}:
        entries.extend(_relationship_entries(data.get("relationships", {})))

    entries.extend(_decision_entries(data.get("decisions", {}), route))

    if route in {"gag", "merchandising"}:
        entries.extend(_option_entries(data, "objects", 6))

    if route == "parody":
        entries.extend(_option_entries(data, "heritage", 5))

    if route == "gag":
        entries.extend(
            _relevant_claim_entries(
                data.get("gag_001_claims", {}),
                idea,
                route,
                data.get("objects", {}),
            )
        )

    section_map = _ROUTE_SECTIONS.get(route, _ROUTE_SECTIONS["general"])
    for source_name, heading, limit in section_map:
        document = markdown.get(
            "HUMOR.md"
            if source_name == "humor"
            else "PALETA.md"
            if source_name == "palette"
            else "SEMANTIC_MODEL.md"
        )
        entries.extend(_extract_section(document or "", heading, limit))

    # Keep current semantic identity separate from historical development material.
    entries.append("historical_material=reference_only; excluded_from_active_canon")

    # Deterministic de-duplication while preserving source order.
    unique: list[str] = []
    seen: set[str] = set()
    for entry in entries:
        normalized = _normalize(entry)
        if normalized in seen:
            continue
        seen.add(normalized)
        unique.append(entry)

    # Reserve the final slot for the explicit historical boundary.
    boundary = "historical_material=reference_only; excluded_from_active_canon"
    bounded_entries = unique[: _MAX_ENTRIES - 1]
    if boundary in unique:
        bounded_entries = [
            entry for entry in bounded_entries
            if entry != boundary
        ]
        bounded_entries.append(boundary)

    return SemanticContext(entries=tuple(bounded_entries))
