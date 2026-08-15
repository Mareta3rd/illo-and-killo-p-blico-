"""Immutable Evidence snapshot for one execution boundary."""

from __future__ import annotations

from dataclasses import dataclass
from types import MappingProxyType
from typing import Mapping

from .evidence_claim_router import evaluate_canonical_evidence_claims
from .evidence_contract_executor import EvidenceContractEvaluation
from .evidence_state import EvidenceClaim


@dataclass(frozen=True)
class EvidenceSnapshot:
    """Frozen set of explicit claims validated once for an execution."""

    _items: tuple[tuple[str, EvidenceClaim], ...]
    canonical_evaluations: tuple[EvidenceContractEvaluation, ...] = ()

    @property
    def claims(self) -> Mapping[str, EvidenceClaim]:
        return MappingProxyType(dict(self._items))

    def get(self, key: str) -> EvidenceClaim | None:
        return dict(self._items).get(key)

    def __len__(self) -> int:
        return len(self._items)


def build_evidence_snapshot(
    root: str,
    claims: Mapping[str, EvidenceClaim],
) -> EvidenceSnapshot:
    """Validate canonical claims once and freeze all explicit claims."""
    normalized: list[tuple[str, EvidenceClaim]] = []
    canonical: dict[str, EvidenceClaim] = {}
    for key, claim in claims.items():
        if not isinstance(claim, EvidenceClaim):
            raise TypeError(f"Evidence claim for '{key}' is not an EvidenceClaim")
        key_text = str(key)
        normalized.append((key_text, claim))
        if key_text.count("/") == 2:
            canonical[key_text] = claim

    evaluations = evaluate_canonical_evidence_claims(root, canonical)
    normalized.sort(key=lambda item: item[0])
    return EvidenceSnapshot(tuple(normalized), evaluations)
