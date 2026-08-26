"""Immutable provider observations retained before Core aggregation."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Sequence

from .external_evidence_adapter import ExternalEvidenceRecord


@dataclass(frozen=True)
class ProviderEvidenceObservation:
    """One provider response preserved as an observation, not a Core decision."""

    provider: str
    run_id: str
    records: tuple[ExternalEvidenceRecord, ...]

    def __post_init__(self) -> None:
        if not self.provider.strip():
            raise ValueError("provider is required")
        if not self.run_id.strip():
            raise ValueError("run_id is required")
        if not isinstance(self.records, tuple):
            raise TypeError("records must be an immutable tuple")
        keys = [record.claim_key for record in self.records]
        if len(keys) != len(set(keys)):
            raise ValueError("one provider observation cannot contain duplicate claim keys")


def freeze_provider_observation(
    provider: str,
    run_id: str,
    records: Sequence[ExternalEvidenceRecord],
) -> ProviderEvidenceObservation:
    """Freeze one provider response without merging or interpreting it."""
    return ProviderEvidenceObservation(
        provider=str(provider),
        run_id=str(run_id),
        records=tuple(records),
    )
