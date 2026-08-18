"""Immutable registry for interchangeable external evidence providers."""

from __future__ import annotations

from dataclasses import dataclass
from types import MappingProxyType
from typing import Mapping

from .external_evidence_adapter import ExternalEvidenceProvider


@dataclass(frozen=True)
class EvidenceProviderRegistry:
    """Resolve named providers without coupling Core to a vendor."""

    providers: Mapping[str, ExternalEvidenceProvider]

    def __post_init__(self) -> None:
        normalized = dict(self.providers)
        for name, provider in normalized.items():
            if not isinstance(name, str) or not name.strip():
                raise ValueError("Provider name must be a non-empty string")
            if not hasattr(provider, "collect") or not callable(provider.collect):
                raise TypeError(f"Provider {name!r} must expose callable collect()")
        object.__setattr__(self, "providers", MappingProxyType(normalized))

    @classmethod
    def empty(cls) -> "EvidenceProviderRegistry":
        return cls({})

    def register(
        self,
        name: str,
        provider: ExternalEvidenceProvider,
    ) -> "EvidenceProviderRegistry":
        if not isinstance(name, str) or not name.strip():
            raise ValueError("Provider name must be a non-empty string")
        if name in self.providers:
            raise ValueError(f"Provider already registered: {name}")
        updated = dict(self.providers)
        updated[name] = provider
        return type(self)(updated)

    def resolve(self, name: str) -> ExternalEvidenceProvider:
        try:
            return self.providers[name]
        except KeyError as exc:
            raise KeyError(f"Unknown evidence provider: {name}") from exc

    def names(self) -> tuple[str, ...]:
        return tuple(sorted(self.providers))


__all__ = ["EvidenceProviderRegistry"]
