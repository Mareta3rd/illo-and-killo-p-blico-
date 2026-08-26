"""Immutable provider observations retained before Core aggregation."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Sequence

from .evidence_snapshot import EvidenceSnapshot, build_evidence_snapshot
from .external_evidence_adapter import (
    ExternalEvidenceRecord,
    normalize_external_observations,
)


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


def snapshot_from_provider_observation(
    root: str,
    observation: ProviderEvidenceObservation,
) -> EvidenceSnapshot:
    """Convert one frozen provider observation into the Core snapshot boundary.

    Provider metadata stays on the observation. Records are normalized into the
    provider-agnostic evidence claim representation before Core freezes and
    evaluates the snapshot. No cross-provider aggregation or provider-specific
    interpretation is performed here.
    """
    if not isinstance(observation, ProviderEvidenceObservation):
        raise TypeError("observation must be a ProviderEvidenceObservation")
    claims = normalize_external_observations(observation.records)
    return build_evidence_snapshot(root, claims)
