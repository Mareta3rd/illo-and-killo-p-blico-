"""Gemini-specific external evidence adapter.

This module owns only provider-specific request/response handling. The Core
continues to receive canonical ExternalEvidenceRecord values and remains
responsible for evidence contracts, snapshots, evaluation, and decisions.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Callable, Sequence

from .external_evidence_adapter import ExternalEvidenceRecord
from .real_evidence_provider import RealEvidenceProviderAdapter, RealEvidenceProviderError
from .evidence_state import EvidenceState


@dataclass(frozen=True)
class GeminiEvidenceAdapter:
    """Adapter around an injected Gemini client callable.

    The callable must accept a request mapping and return a provider payload.
    Parsing is injected so tests remain deterministic and credentials never
    enter Core tests.
    """

    request: Callable[[dict[str, Any]], Any]
    parse: Callable[[Any, Sequence[str]], Sequence[ExternalEvidenceRecord]]

    def collect(self, requested_keys: Sequence[str]) -> Sequence[ExternalEvidenceRecord]:
        keys = tuple(requested_keys)
        prompt = (
            "Evaluate only the requested canonical evidence claims. "
            "Return one observation per requested key. Preserve UNKNOWN when "
            "the image does not provide sufficient evidence.\n\n"
            + "\n".join(f"- {key}" for key in keys)
        )
        payload = self.request({"prompt": prompt, "requested_keys": keys})
        return tuple(self.parse(payload, keys))


def build_gemini_transport(
    client_generate: Callable[..., Any],
    *,
    model: str,
) -> Callable[[dict[str, Any]], Any]:
    """Build a tiny transport function for a Gemini generate-content client."""

    def request(payload: dict[str, Any]) -> Any:
        try:
            return client_generate(model=model, prompt=payload["prompt"])
        except Exception as exc:  # provider boundary: normalize operational failures
            raise RealEvidenceProviderError("gemini request failed") from exc

    return request


__all__ = ["GeminiEvidenceAdapter", "build_gemini_transport"]
