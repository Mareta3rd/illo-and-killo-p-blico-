"""Qualitative narrative and visual importance for canonical elements.

The model deliberately avoids arbitrary floating-point weights. Canonical
meaning is expressed with stable labels, while an internal ordinal rank keeps
comparison deterministic when orchestration needs it.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import IntEnum


class NarrativeRole(IntEnum):
    INCIDENTAL = 0
    SUPPORTING = 1
    SECONDARY = 2
    PRIMARY = 3

    @property
    def label(self) -> str:
        return self.name.lower()


class VisualSalience(IntEnum):
    LOW = 0
    MEDIUM = 1
    HIGH = 2
    DOMINANT = 3

    @property
    def label(self) -> str:
        return self.name.lower()


@dataclass(frozen=True)
class CanonicalSalience:
    """Stable importance metadata for one canonical element or claim."""

    narrative_role: NarrativeRole
    visual_salience: VisualSalience

    @property
    def narrative_weight(self) -> int:
        return int(self.narrative_role)

    @property
    def visual_weight(self) -> int:
        return int(self.visual_salience)


@dataclass(frozen=True)
class CanonicalClaim:
    """Canonical claim plus its human-readable meaning and salience."""

    key: str
    statement: str
    salience: CanonicalSalience

    def __post_init__(self) -> None:
        if not self.key.strip():
            raise ValueError("Canonical claim key is required")
        if not self.statement.strip():
            raise ValueError("Canonical claim statement is required")


__all__ = [
    "CanonicalClaim",
    "CanonicalSalience",
    "NarrativeRole",
    "VisualSalience",
]
