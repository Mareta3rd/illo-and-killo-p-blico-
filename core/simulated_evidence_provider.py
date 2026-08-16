"""Deterministic external evidence provider used to exercise the v0.2 boundary."""

from __future__ import annotations

from dataclasses import dataclass

from .evidence_state import EvidenceClaim
from .external_evidence_adapter import ExternalEvidenceRecord, normalize_external_evidence


@dataclass(frozen=True)
class SimulatedEvidenceProvider:
    """Small provider stub with no knowledge of Core evaluation semantics."""

    records: tuple[ExternalEvidenceRecord, ...]

    def collect(self) -> tuple[ExternalEvidenceRecord, ...]:
        return self.records

    def collect_claims(self) -> dict[str, EvidenceClaim]:
        return normalize_external_evidence(self.collect())
