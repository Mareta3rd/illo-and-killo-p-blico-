"""Groq/Qwen-specific external evidence adapter."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Callable, Sequence

from .external_evidence_adapter import ExternalEvidenceRecord
from .groq_qwen_real_transport import (
    DEFAULT_GROQ_QWEN_MODEL,
    build_groq_qwen_responses_transport,
    parse_groq_qwen_structured_evidence,
)
from .real_evidence_provider import RealEvidenceProviderError


@dataclass(frozen=True)
class GroqQwenEvidenceAdapter:
    request: Callable[[dict[str, Any]], Any]
    parse: Callable[[Any, Sequence[str]], Sequence[ExternalEvidenceRecord]] = parse_groq_qwen_structured_evidence

    def collect(self, requested_keys: Sequence[str]) -> Sequence[ExternalEvidenceRecord]:
        keys = tuple(requested_keys)
        prompt = (
            "Evaluate only the requested canonical evidence claims. Return one observation per requested key. "
            "Preserve UNKNOWN when the image is insufficient. Return claim_key, statement, verdict, "
            "supporting_sources, and contradicting_sources. Return evidence observations only.\n\n"
            + "\n".join(f"- {key}" for key in keys)
        )
        try:
            return tuple(self.parse(self.request({"prompt": prompt, "requested_keys": keys}), keys))
        except RealEvidenceProviderError:
            raise
        except Exception as exc:
            raise RealEvidenceProviderError("groq qwen evidence adapter failed") from exc

    @classmethod
    def from_responses_client(
        cls,
        client: Any,
        *,
        model: str = DEFAULT_GROQ_QWEN_MODEL,
        image_bytes: bytes,
        mime_type: str,
    ) -> "GroqQwenEvidenceAdapter":
        """Build an adapter around an already configured OpenAI-compatible client."""
        return cls(build_groq_qwen_responses_transport(
            client, model=model, image_bytes=image_bytes, mime_type=mime_type
        ))


__all__ = ["GroqQwenEvidenceAdapter"]