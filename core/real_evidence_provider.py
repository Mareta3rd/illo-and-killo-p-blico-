"""First real-provider transport boundary, kept independent from Core policy."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Callable, Mapping, Sequence

from .external_evidence_adapter import ExternalEvidenceRecord
from .evidence_state import EvidenceState


class RealEvidenceProviderError(RuntimeError):
    """Operational failure while calling a real external provider."""


@dataclass(frozen=True)
class RealProviderResponse:
    """Provider response payload before canonical normalization."""

    payload: Any


@dataclass(frozen=True)
class RealEvidenceProviderAdapter:
    """Minimal injected transport/parser boundary for a real provider.

    The adapter does not access Core policy. It only turns a provider payload
    into ExternalEvidenceRecord values or raises RealEvidenceProviderError.
    """

    fetch: Callable[[Sequence[str]], Any]
    parse: Callable[[Any], Sequence[ExternalEvidenceRecord]]

    def collect(self, requested_keys: Sequence[str]) -> Sequence[ExternalEvidenceRecord]:
        try:
            payload = self.fetch(tuple(requested_keys))
        except Exception as exc:
            raise RealEvidenceProviderError("real provider request failed") from exc
        try:
            records = tuple(self.parse(payload))
        except Exception as exc:
            raise RealEvidenceProviderError("real provider response could not be parsed") from exc
        for record in records:
            if not isinstance(record, ExternalEvidenceRecord):
                raise RealEvidenceProviderError("real provider parser returned an invalid record")
        return records


__all__ = ["RealEvidenceProviderAdapter", "RealEvidenceProviderError", "RealProviderResponse"]
