"""Route classified invariants to the mechanism their taxonomy declares."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Literal

from .invariant_taxonomy import InvariantClassification, load_invariant_classification


DispatchMode = Literal["deterministic", "evidence", "unsupported"]


@dataclass(frozen=True)
class InvariantRoute:
    catalog: str
    entry: str
    invariant: str
    family: str
    mechanism: str
    mode: DispatchMode
    evidence_required: bool


_EVIDENCE_MECHANISMS = {"evidence_perceptual", "evidence_style", "evidence_context"}
_DETERMINISTIC_MECHANISMS = {
    "deterministic_range",
    "deterministic_value",
    "deterministic_structure",
    "deterministic_relation",
}


def _mode_for(mechanism: str) -> DispatchMode:
    if mechanism in _DETERMINISTIC_MECHANISMS:
        return "deterministic"
    if mechanism in _EVIDENCE_MECHANISMS:
        return "evidence"
    return "unsupported"


def dispatch_invariant(
    root: str,
    catalog: str,
    entry: str,
    invariant: str,
) -> InvariantRoute:
    """Resolve one canonical invariant to its declared evaluation boundary.

    The dispatcher is deliberately a router, not an evaluator. It never
    infers a family or mechanism when the classification registry does not
    contain the requested invariant.
    """
    classifications = load_invariant_classification(root)
    matches = [
        item
        for item in classifications
        if (item.catalog, item.entry, item.invariant)
        == (catalog, entry, invariant)
    ]
    if not matches:
        raise KeyError(f"Unknown invariant classification: {catalog}/{entry}/{invariant}")

    item: InvariantClassification = matches[0]
    mode = _mode_for(item.mechanism)
    if mode == "unsupported":
        raise ValueError(f"Unsupported invariant mechanism: {item.mechanism}")

    if item.evidence_required != (mode == "evidence"):
        raise ValueError(
            f"Classification evidence flag disagrees with mechanism for {catalog}/{entry}/{invariant}"
        )

    return InvariantRoute(
        catalog=item.catalog,
        entry=item.entry,
        invariant=item.invariant,
        family=item.family,
        mechanism=item.mechanism,
        mode=mode,
        evidence_required=item.evidence_required,
    )
