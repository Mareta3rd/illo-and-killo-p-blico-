"""Provider-agnostic adapter contract for turning external observations into EvidenceClaims."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Mapping, Protocol, Sequence

from .evidence_state import EvidenceClaim, EvidenceState


@dataclass(frozen=True)
class ExternalEvidenceRecord:
    """Normalized observation supplied by an external system."""

    claim_key: str
    statement: str
    state: EvidenceState
    supporting_sources: tuple[str, ...] = ()
    contradicting_sources: tuple[str, ...] = ()


class ExternalEvidenceProvider(Protocol):
    """Minimal provider interface; Core does not depend on a concrete vendor."""

    def collect(self, requested_keys: Sequence[str]) -> Sequence[ExternalEvidenceRecord]:
        """Return normalized observations for requested canonical claim keys."""
        ...


def normalize_external_evidence(
    records: Sequence[ExternalEvidenceRecord],
) -> Mapping[str, EvidenceClaim]:
    """Convert external records into immutable Core EvidenceClaims.

    Duplicate claim keys or malformed source/state combinations are rejected.
    No claim semantics are inferred from text: the external adapter supplies
    the explicit state and source references, while Core remains responsible
    for contracts, snapshots, and execution policy.
    """
    result: dict[str, EvidenceClaim] = {}
    for record in records:
        if not isinstance(record, ExternalEvidenceRecord):
            raise TypeError("External evidence records must use ExternalEvidenceRecord")
        if not record.claim_key.strip() or record.claim_key.count("/") != 2:
            raise ValueError("External evidence claim_key must be canonical catalog/entry/invariant")
        if record.claim_key in result:
            raise ValueError(f"Duplicate external evidence claim: {record.claim_key}")
        if not isinstance(record.state, EvidenceState):
            raise TypeError(f"Invalid evidence state for {record.claim_key}")
        if not record.statement.strip():
            raise ValueError(f"Evidence statement is required: {record.claim_key}")
        if not isinstance(record.supporting_sources, tuple) or not all(
            isinstance(source, str) and source.strip() for source in record.supporting_sources
        ):
            raise TypeError(f"Supporting sources must be non-empty strings: {record.claim_key}")
        if not isinstance(record.contradicting_sources, tuple) or not all(
            isinstance(source, str) and source.strip() for source in record.contradicting_sources
        ):
            raise TypeError(f"Contradicting sources must be non-empty strings: {record.claim_key}")

        result[record.claim_key] = EvidenceClaim(
            record.statement,
            record.state,
            supporting_sources=record.supporting_sources,
            contradicting_sources=record.contradicting_sources,
        )

    return dict(sorted(result.items()))
