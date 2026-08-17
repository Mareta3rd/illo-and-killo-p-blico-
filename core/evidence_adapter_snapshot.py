"""Build immutable EvidenceSnapshot objects from adapter claims.

This boundary deliberately accepts only already-normalized EvidenceClaim values.
It does not interpret provider payloads, infer canon, or alter claim states.
"""

from __future__ import annotations

from collections.abc import Mapping
from pathlib import Path

from .evidence_adapter import EvidenceAdapter
from .evidence_snapshot import EvidenceSnapshot, build_evidence_snapshot
from .evidence_state import EvidenceClaim


def build_snapshot_from_adapter(
    root: str | Path,
    adapter: EvidenceAdapter,
    observations: Mapping[str, object],
) -> EvidenceSnapshot:
    """Convert adapter observations into one frozen canonical snapshot."""

    claims: dict[str, EvidenceClaim] = {}
    for invariant, observation in observations.items():
        claims[str(invariant)] = adapter.to_claim(str(invariant), observation)

    return build_evidence_snapshot(root, claims)
