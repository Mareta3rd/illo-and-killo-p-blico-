"""Run one external evidence collection into an immutable Core snapshot."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Sequence

from .evidence_snapshot import EvidenceSnapshot, build_evidence_snapshot
from .external_evidence_adapter import (
    ExternalEvidenceProvider,
    normalize_external_evidence,
)


@dataclass(frozen=True)
class ExternalEvidenceSession:
    """Auditable boundary result for one provider collection request."""

    requested_keys: tuple[str, ...]
    snapshot: EvidenceSnapshot


def collect_external_evidence(
    root: str,
    provider: ExternalEvidenceProvider,
    requested_keys: Sequence[str],
) -> ExternalEvidenceSession:
    """Collect, normalize, validate and freeze one external evidence set."""
    keys = tuple(requested_keys)
    if len(set(keys)) != len(keys):
        raise ValueError("Requested evidence keys must be unique")
    if not all(isinstance(key, str) and key.strip() for key in keys):
        raise TypeError("Requested evidence keys must be non-empty strings")

    records = provider.collect(keys)
    claims = normalize_external_evidence(records)
    snapshot = build_evidence_snapshot(root, claims)
    return ExternalEvidenceSession(keys, snapshot)


__all__ = ["ExternalEvidenceSession", "collect_external_evidence"]
