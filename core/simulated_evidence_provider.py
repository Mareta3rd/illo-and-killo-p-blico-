"""Deterministic in-memory Evidence provider for end-to-end boundary tests."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Mapping, Sequence

from .external_evidence_adapter import ExternalEvidenceProvider, ExternalEvidenceRecord


@dataclass(frozen=True)
class SimulatedEvidenceProvider:
    """Return predeclared external observations for requested canonical keys."""

    records: Mapping[str, ExternalEvidenceRecord]

    def collect(self, requested_keys: Sequence[str]) -> Sequence[ExternalEvidenceRecord]:
        """Return only explicitly requested records, in request order."""
        return tuple(self.records[key] for key in requested_keys if key in self.records)


def build_simulated_provider(
    records: Sequence[ExternalEvidenceRecord],
) -> SimulatedEvidenceProvider:
    """Build a deterministic provider and reject duplicate canonical keys."""
    normalized: dict[str, ExternalEvidenceRecord] = {}
    for record in records:
        if not isinstance(record, ExternalEvidenceRecord):
            raise TypeError("Simulated provider accepts ExternalEvidenceRecord values only")
        if record.claim_key in normalized:
            raise ValueError(f"Duplicate simulated evidence claim: {record.claim_key}")
        normalized[record.claim_key] = record
    return SimulatedEvidenceProvider(dict(sorted(normalized.items())))


__all__ = ["ExternalEvidenceProvider", "SimulatedEvidenceProvider", "build_simulated_provider"]
