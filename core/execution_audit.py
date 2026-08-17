"""Immutable execution-level audit for the semantic vertical slice."""

from __future__ import annotations

from dataclasses import dataclass
from hashlib import sha256
from typing import Mapping, Sequence

from .context import CoreContext
from .evidence_snapshot import EvidenceSnapshot
from .semantic_audit import SemanticAuditRecord


@dataclass(frozen=True)
class ExecutionAudit:
    """Reconstructable, read-only summary of one Core execution."""

    idea: str
    route: str
    confidence: float
    route_reason: str
    evidence_keys: tuple[str, ...]
    evidence_digest: str | None
    iterations: tuple[SemanticAuditRecord, ...]
    final_status: str
    stop_reason: str | None


def fingerprint_evidence(snapshot: EvidenceSnapshot) -> str:
    """Return a deterministic digest of the frozen evidence boundary."""
    parts: list[str] = []
    for key, claim in sorted(snapshot.claims.items(), key=lambda item: item[0]):
        parts.append(
            "|".join(
                (
                    key,
                    claim.state.value,
                    claim.claim,
                    ",".join(claim.supporting_sources),
                    ",".join(claim.contradicting_sources),
                )
            )
        )
    return sha256("\n".join(parts).encode("utf-8")).hexdigest()


def build_execution_audit(
    context: CoreContext,
    snapshot: EvidenceSnapshot | None,
    iterations: Sequence[SemanticAuditRecord],
    *,
    final_status: str,
    stop_reason: str | None,
) -> ExecutionAudit:
    """Build an immutable execution summary without mutating inputs."""
    claims = snapshot.claims if snapshot is not None else {}
    route = getattr(context.route, "value", context.route)
    return ExecutionAudit(
        idea=context.idea,
        route=str(route),
        confidence=context.confidence,
        route_reason=context.reason,
        evidence_keys=tuple(sorted(str(key) for key in claims)),
        evidence_digest=fingerprint_evidence(snapshot) if snapshot is not None else None,
        iterations=tuple(iterations),
        final_status=final_status,
        stop_reason=stop_reason,
    )
