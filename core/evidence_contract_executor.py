"""Execute declarative Evidence contracts without inferring claim state."""

from __future__ import annotations

from dataclasses import dataclass

from .evidence_boundary import EvidenceEvaluation, evaluate_evidence_claim
from .evidence_contracts import EvidenceContract, load_evidence_contract
from .evidence_state import EvidenceClaim
from .invariant_dispatcher import dispatch_invariant


@dataclass(frozen=True)
class EvidenceContractEvaluation:
    catalog: str
    entry: str
    invariant: str
    family: str
    mechanism: str
    evaluation: EvidenceEvaluation


def evaluate_evidence_contract(
    root: str,
    catalog: str,
    entry: str,
    invariant: str,
    claim: EvidenceClaim,
) -> EvidenceContractEvaluation:
    """Validate the canonical route and contract, then evaluate one claim."""
    route = dispatch_invariant(root, catalog, entry, invariant)
    if route.mode != "evidence" or not route.evidence_required:
        raise ValueError(
            f"Invariant is not evidence-backed: {catalog}/{entry}/{invariant}"
        )

    contract: EvidenceContract = load_evidence_contract(
        root, catalog, entry, invariant
    )
    if contract.family != route.family or contract.mechanism != route.mechanism:
        raise ValueError(
            f"Evidence contract disagrees with classification for "
            f"{catalog}/{entry}/{invariant}"
        )

    if contract.explicit_support_required and not (
        claim.supporting_sources or claim.contradicting_sources
    ):
        raise ValueError(
            f"Evidence claim has no explicit sources: {catalog}/{entry}/{invariant}"
        )

    evaluation = evaluate_evidence_claim(claim)
    return EvidenceContractEvaluation(
        catalog=catalog,
        entry=entry,
        invariant=invariant,
        family=route.family,
        mechanism=route.mechanism,
        evaluation=evaluation,
    )
