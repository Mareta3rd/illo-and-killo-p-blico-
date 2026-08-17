"""Provider-neutral boundary for normalizing external evidence.

Adapters translate provider observations into the canonical EvidenceClaim model.
They do not validate canon, execute invariants, or choose acceptance decisions.
Provider failures and ambiguous/malformed observations become UNKNOWN rather
than FAIL or CONTRADICTED.
"""

from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass
from typing import Any, Protocol

from .evidence_state import EvidenceClaim, EvidenceState, EvidenceConflictError, assess_claim


class EvidenceProviderFailure(RuntimeError):
    """Operational failure reported explicitly by an external provider."""


@dataclass(frozen=True)
class ExternalObservation:
    """Provider-neutral observation after transport-level normalization."""

    claim: str
    verdict: str
    source: str | None = None


class EvidenceAdapter(Protocol):
    """Minimal adapter contract consumed by Core."""

    def adapt(self, observation: Any) -> EvidenceClaim:
        """Convert one provider observation into a canonical EvidenceClaim."""
        ...


def _unknown_claim(claim: str) -> EvidenceClaim:
    return EvidenceClaim(claim=claim, state=EvidenceState.UNKNOWN)


def normalize_external_observation(value: Any) -> ExternalObservation | None:
    """Normalize an untrusted provider payload without interpreting canon."""
    if not isinstance(value, Mapping):
        return None

    claim = value.get("claim")
    verdict = value.get("verdict")
    source = value.get("source")

    if not isinstance(claim, str) or not claim.strip():
        return None
    if not isinstance(verdict, str):
        return None
    if source is not None and not isinstance(source, str):
        return None

    return ExternalObservation(
        claim=claim.strip(),
        verdict=verdict.strip().lower(),
        source=source.strip() if isinstance(source, str) and source.strip() else None,
    )


@dataclass(frozen=True)
class DefaultEvidenceAdapter:
    """Canonical adapter for provider-neutral observation payloads."""

    def adapt(self, observation: Any) -> EvidenceClaim:
        normalized = normalize_external_observation(observation)
        if normalized is None:
            return _unknown_claim("external observation could not be normalized")

        source = (normalized.source,) if normalized.source else ()

        try:
            if normalized.verdict == "confirmed":
                return assess_claim(normalized.claim, supporting_sources=source)
            if normalized.verdict == "contradicted":
                return assess_claim(normalized.claim, contradicting_sources=source)
            if normalized.verdict == "unknown":
                return _unknown_claim(normalized.claim)
        except EvidenceConflictError:
            return _unknown_claim(normalized.claim)

        return _unknown_claim(normalized.claim)


def adapt_external_observation(observation: Any) -> EvidenceClaim:
    """Convenience entry point for the provider-neutral adapter boundary."""
    return DefaultEvidenceAdapter().adapt(observation)


def adapt_provider_call(callable_: Any) -> EvidenceClaim:
    """Execute an injected provider call and preserve explicit provider failure as UNKNOWN."""
    try:
        return adapt_external_observation(callable_())
    except EvidenceProviderFailure:
        return _unknown_claim("external evidence provider unavailable")
