"""Deterministic gateway between an external evidence provider and Core."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Sequence

from .evidence_snapshot import EvidenceSnapshot, build_evidence_snapshot
from .evidence_state import EvidenceClaim
from .external_evidence_adapter import ExternalEvidenceProvider, normalize_external_evidence


@dataclass(frozen=True)
class ExternalEvidenceGatewayResult:
    """Immutable result of one provider collection attempt."""

    snapshot: EvidenceSnapshot | None
    claims: dict[str, EvidenceClaim]
    missing_keys: tuple[str, ...]
    stopped: bool
    stop_reason: str | None


class ExternalEvidenceGateway:
    """Provider-facing gateway that returns normalized, frozen evidence."""

    def __init__(self, root: str | Path):
        self._root = Path(root)

    def collect(
        self,
        provider: ExternalEvidenceProvider,
        requested_keys: Sequence[str],
    ) -> ExternalEvidenceGatewayResult:
        return collect_external_evidence(self._root, provider, requested_keys)


def collect_external_evidence(
    root: str | Path,
    provider: ExternalEvidenceProvider,
    requested_keys: Sequence[str],
) -> ExternalEvidenceGatewayResult:
    """Collect requested evidence, normalize it, and freeze it into a snapshot.

    Provider failures are surfaced as an explicit stop. Missing requested keys
    are also surfaced rather than silently treated as confirmed or invented.
    """

    requested = tuple(dict.fromkeys(str(key) for key in requested_keys if str(key).strip()))
    try:
        records = tuple(provider.collect(requested))
    except Exception as exc:  # provider boundary: preserve failure as a visible stop
        return ExternalEvidenceGatewayResult(
            snapshot=None,
            claims={},
            missing_keys=requested,
            stopped=True,
            stop_reason=f"external_evidence_provider_failed: {exc}",
        )

    claims = dict(normalize_external_evidence(records))
    missing = tuple(key for key in requested if key not in claims)

    snapshot = None
    if claims:
        snapshot = build_evidence_snapshot(str(root), claims)

    if missing:
        return ExternalEvidenceGatewayResult(
            snapshot=snapshot,
            claims=claims,
            missing_keys=missing,
            stopped=True,
            stop_reason="external_evidence_missing_requested_keys",
        )

    return ExternalEvidenceGatewayResult(
        snapshot=snapshot,
        claims=claims,
        missing_keys=(),
        stopped=False,
        stop_reason=None,
    )


__all__ = ["ExternalEvidenceGateway", "ExternalEvidenceGatewayResult", "collect_external_evidence"]
