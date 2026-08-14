"""Canonical routing for explicit evidence claims.

Evidence claims enter the system under a canonical invariant key. This layer
ensures the claim is classified, contract-backed, and routed to the same
Evidence contract executor used by the full semantic path.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Mapping

from .evidence_contract_executor import EvidenceContractEvaluation, evaluate_evidence_contract
from .evidence_state import EvidenceClaim


@dataclass(frozen=True)
class EvidenceClaimKey:
    catalog: str
    entry: str
    invariant: str

    @classmethod
    def parse(cls, value: str) -> "EvidenceClaimKey":
        parts = value.split("/")
        if len(parts) != 3 or not all(part.strip() for part in parts):
            raise ValueError("Evidence claim keys must use catalog/entry/invariant")
        return cls(*parts)


def evaluate_canonical_evidence_claims(
    root: str,
    claims: Mapping[str, EvidenceClaim],
) -> tuple[EvidenceContractEvaluation, ...]:
    """Evaluate canonical evidence claims without inventing missing routes."""
    results: list[EvidenceContractEvaluation] = []
    for key, claim in claims.items():
        parsed = EvidenceClaimKey.parse(key)
        results.append(
            evaluate_evidence_contract(
                root,
                parsed.catalog,
                parsed.entry,
                parsed.invariant,
                claim,
            )
        )
    return tuple(results)
