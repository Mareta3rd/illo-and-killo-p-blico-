"""OpenAI-specific external evidence adapter."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Callable, Sequence

from .external_evidence_adapter import ExternalEvidenceRecord
from .openai_real_transport import (
    build_openai_responses_transport,
    parse_openai_structured_evidence,
)
from .real_evidence_provider import RealEvidenceProviderError


@dataclass(frozen=True)
class OpenAIEvidenceAdapter:
    """Combine an injected OpenAI transport with canonical evidence parsing."""

    request: Callable[[dict[str, Any]], Any]
    parse: Callable[[Any, Sequence[str]], Sequence[ExternalEvidenceRecord]] = parse_openai_structured_evidence

    def collect(self, requested_keys: Sequence[str]) -> Sequence[ExternalEvidenceRecord]:
        keys = tuple(requested_keys)
        prompt = (
            "Evaluate only the requested canonical evidence claims. Return one observation per requested key. "
            "Preserve UNKNOWN when the image is insufficient. Return claim_key, statement, verdict, "
            "supporting_sources, and contradicting_sources. Return evidence observations only.\n\n"
            + "\n".join(f"- {key}" for key in keys)
        )
        try:
            payload = self.request({"prompt": prompt, "requested_keys": keys})
            records = tuple(self.parse(payload, keys))
        except RealEvidenceProviderError:
            raise
        except Exception as exc:
            raise RealEvidenceProviderError("openai evidence adapter failed") from exc
        return records

    @classmethod
    def from_responses_client(
        cls,
        client: Any,
        *,
        model: str,
        image_bytes: bytes,
        mime_type: str,
    ) -> "OpenAIEvidenceAdapter":
        return cls(
            request=build_openai_responses_transport(
                client,
                model=model,
                image_bytes=image_bytes,
                mime_type=mime_type,
            ),
            parse=parse_openai_structured_evidence,
        )


__all__ = ["OpenAIEvidenceAdapter"]