"""Gemini-specific external evidence adapter.

This module owns only provider-specific request/response handling. The Core
continues to receive canonical ExternalEvidenceRecord values and remains
responsible for evidence contracts, snapshots, evaluation, and decisions.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Callable, Sequence

from .external_evidence_adapter import ExternalEvidenceRecord
from .real_evidence_provider import RealEvidenceProviderError
from .gemini_real_transport import (
    build_gemini_interactions_transport,
    parse_gemini_structured_evidence,
)


@dataclass(frozen=True)
class GeminiEvidenceAdapter:
    """Provider adapter combining Gemini transport and canonical parsing."""

    request: Callable[[dict[str, Any]], Any]
    parse: Callable[[Any, Sequence[str]], Sequence[ExternalEvidenceRecord]] = parse_gemini_structured_evidence

    def collect(self, requested_keys: Sequence[str]) -> Sequence[ExternalEvidenceRecord]:
        keys = tuple(requested_keys)
        prompt = (
            "Evaluate only the requested canonical evidence claims. "
            "Return one observation per requested key. Preserve UNKNOWN when "
            "the image does not provide sufficient evidence.\n\n"
            + "\n".join(f"- {key}" for key in keys)
        )
        try:
            payload = self.request({"prompt": prompt, "requested_keys": keys})
            return tuple(self.parse(payload, keys))
        except RealEvidenceProviderError:
            raise
        except Exception as exc:
            raise RealEvidenceProviderError("gemini evidence adapter failed") from exc

    @classmethod
    def from_interactions_client(
        cls,
        client: Any,
        *,
        model: str,
        image_bytes: bytes,
        mime_type: str,
    ) -> "GeminiEvidenceAdapter":
        """Build the canonical adapter around Gemini's Interactions transport."""
        return cls(
            request=build_gemini_interactions_transport(
                client,
                model=model,
                image_bytes=image_bytes,
                mime_type=mime_type,
            ),
            parse=parse_gemini_structured_evidence,
        )


__all__ = ["GeminiEvidenceAdapter"]
