"""Explicit tri-state boundary for evidence-backed invariant evaluation."""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING, Literal

if TYPE_CHECKING:
    from .evidence_state import EvidenceClaim


EvidenceDecision = Literal["pass", "fail", "unknown"]


@dataclass(frozen=True)
class EvidenceEvaluation:
    invariant: str
    decision: EvidenceDecision
    reason: str


def evaluate_evidence(
    invariant: str,
    evidence_state: EvidenceDecision,
    *,
    confirmed_reason: str = "evidence confirms the invariant",
    contradicted_reason: str = "evidence contradicts the invariant",
    unknown_reason: str = "evidence is insufficient to establish the invariant",
) -> EvidenceEvaluation:
    """Translate an already-normalized evidence state into a stable contract.

    This function deliberately does not infer truth from raw content. Evidence
    extraction belongs upstream; this boundary only normalizes the tri-state
    decision and its reason.
    """
    if evidence_state == "pass":
        return EvidenceEvaluation(invariant, "pass", confirmed_reason)
    if evidence_state == "fail":
        return EvidenceEvaluation(invariant, "fail", contradicted_reason)
    if evidence_state == "unknown":
        return EvidenceEvaluation(invariant, "unknown", unknown_reason)
    raise ValueError(f"unsupported evidence state: {evidence_state!r}")


def evaluate_evidence_claim(claim: EvidenceClaim) -> EvidenceEvaluation:
    """Evaluate one auditable EvidenceClaim through the shared boundary."""
    from .evidence_state import EvidenceClaim, EvidenceState

    if not isinstance(claim, EvidenceClaim):
        raise TypeError("claim must be an EvidenceClaim")

    decision_by_state = {
        EvidenceState.CONFIRMED: "pass",
        EvidenceState.CONTRADICTED: "fail",
        EvidenceState.UNKNOWN: "unknown",
    }
    decision = decision_by_state[claim.state]
    return evaluate_evidence(
        claim.claim,
        decision,
        confirmed_reason="evidence claim is confirmed",
        contradicted_reason="evidence claim is contradicted",
        unknown_reason="evidence claim remains unknown",
    )
