"""Tri-state assessment model for repository evidence.

This module deliberately separates evidence state from canon and from
historical usage categories. It does not infer absence from missing evidence.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Iterable


class EvidenceState(str, Enum):
    """State of a specific claim after evaluating available evidence."""

    CONFIRMED = "CONFIRMED"
    CONTRADICTED = "CONTRADICTED"
    UNKNOWN = "UNKNOWN"


class EvidenceConflictError(ValueError):
    """Raised when positive and negative evidence coexist for one claim."""


@dataclass(frozen=True)
class EvidenceClaim:
    """Auditable tri-state result for one claim."""

    claim: str
    state: EvidenceState
    supporting_sources: tuple[str, ...] = ()
    contradicting_sources: tuple[str, ...] = ()


def assess_claim(
    claim: str,
    supporting_sources: Iterable[str] = (),
    contradicting_sources: Iterable[str] = (),
) -> EvidenceClaim:
    """Assess a claim without treating missing evidence as contradiction.

    A claim is CONFIRMED when explicit supporting evidence exists and no
    explicit contradictory evidence exists. It is CONTRADICTED when the
    reverse is true. With neither side established, the result is UNKNOWN.

    If both sides contain evidence, the function refuses to choose silently;
    the caller must handle that conflict explicitly.
    """

    supporting = tuple(str(source) for source in supporting_sources)
    contradicting = tuple(str(source) for source in contradicting_sources)

    if supporting and contradicting:
        raise EvidenceConflictError(
            f"Conflicting evidence for claim: {claim}"
        )

    if supporting:
        state = EvidenceState.CONFIRMED
    elif contradicting:
        state = EvidenceState.CONTRADICTED
    else:
        state = EvidenceState.UNKNOWN

    return EvidenceClaim(
        claim=str(claim),
        state=state,
        supporting_sources=supporting,
        contradicting_sources=contradicting,
    )
