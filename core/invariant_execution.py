"""Execute classified evidence-backed invariants at the correct boundary."""

from __future__ import annotations

from .evidence_boundary import EvidenceEvaluation, EvidenceDecision, evaluate_evidence
from .invariant_dispatcher import InvariantRoute, dispatch_invariant


def evaluate_classified_evidence(
    root: str,
    catalog: str,
    entry: str,
    invariant: str,
    evidence_state: EvidenceDecision,
) -> tuple[InvariantRoute, EvidenceEvaluation]:
    """Route a classified invariant, then evaluate only through its evidence boundary.

    Deterministic invariants are never evaluated through this function. The
    taxonomy therefore becomes an execution policy rather than documentation.
    """
    route = dispatch_invariant(root, catalog, entry, invariant)
    if route.mode != "evidence":
        raise ValueError(
            f"Invariant {catalog}/{entry}/{invariant} is not evidence-backed"
        )

    return route, evaluate_evidence(invariant, evidence_state)
