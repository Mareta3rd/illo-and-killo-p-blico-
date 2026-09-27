"""Auditable orchestration seam for bounded collaborative work.

The seam invokes an injected collaboration provider, validates its handoff, and
records deterministic digests. It does not execute tools, authorize actions, or
change Core-owned canon.
"""

from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass
from typing import Protocol

from .work_envelope import CollaborationUpdate, WorkEnvelope


class CollaborationProvider(Protocol):
    """Provider that performs one bounded collaborative work pass."""

    provider_id: str

    def collaborate(self, envelope: WorkEnvelope) -> CollaborationUpdate: ...


def _digest(serialized: str) -> str:
    return hashlib.sha256(serialized.encode("utf-8")).hexdigest()


def _provider_id(provider: object) -> str:
    value = getattr(provider, "provider_id", None)
    if not isinstance(value, str) or not value.strip():
        raise TypeError("provider must expose a non-empty provider_id")
    return value.strip()


@dataclass(frozen=True)
class CollaborationExecutionRecord:
    """Immutable audit record for one validated collaboration handoff."""

    envelope: WorkEnvelope
    update: CollaborationUpdate
    provider_id: str
    envelope_digest: str
    update_digest: str

    def to_dict(self) -> dict[str, object]:
        return {
            "schema_version": 1,
            "envelope": self.envelope.to_dict(),
            "update": self.update.to_dict(),
            "provider_id": self.provider_id,
            "envelope_digest": self.envelope_digest,
            "update_digest": self.update_digest,
        }

    def to_json(self) -> str:
        return json.dumps(
            self.to_dict(),
            sort_keys=True,
            separators=(",", ":"),
            ensure_ascii=False,
            allow_nan=False,
        )


def execute_collaboration(
    provider: CollaborationProvider,
    envelope: WorkEnvelope,
) -> CollaborationExecutionRecord:
    """Run one bounded collaboration pass and record its validated handoff."""
    if not isinstance(envelope, WorkEnvelope):
        raise TypeError("envelope must be a WorkEnvelope")

    provider_id = _provider_id(provider)
    collaborate = getattr(provider, "collaborate", None)
    if not callable(collaborate):
        raise TypeError("provider must expose callable collaborate(envelope)")

    update = collaborate(envelope)
    if not isinstance(update, CollaborationUpdate):
        raise TypeError("provider must return a CollaborationUpdate")
    update.validate_for(envelope)

    return CollaborationExecutionRecord(
        envelope=envelope,
        update=update,
        provider_id=provider_id,
        envelope_digest=_digest(envelope.to_json()),
        update_digest=_digest(update.to_json()),
    )


__all__ = [
    "CollaborationExecutionRecord",
    "CollaborationProvider",
    "execute_collaboration",
]
