"""Groq/Qwen Responses-compatible transport and evidence parser."""

from __future__ import annotations

import base64
import json
from collections.abc import Mapping
from typing import Any, Sequence

from .evidence_state import EvidenceState
from .external_evidence_adapter import ExternalEvidenceRecord
from .real_evidence_provider import RealEvidenceProviderError


DEFAULT_GROQ_QWEN_MODEL = "qwen/qwen3.6-27b"
DEFAULT_GROQ_BASE_URL = "https://api.groq.com/openai/v1"
GROQ_QWEN_EVIDENCE_SCHEMA = {
    "type": "object",
    "additionalProperties": False,
    "properties": {
        "observations": {
            "type": "array",
            "items": {
                "type": "object",
                "additionalProperties": False,
                "properties": {
                    "claim_key": {"type": "string"},
                    "statement": {"type": "string"},
                    "verdict": {"type": "string", "enum": ["confirmed", "contradicted", "unknown"]},
                    "supporting_sources": {"type": "array", "items": {"type": "string"}},
                    "contradicting_sources": {"type": "array", "items": {"type": "string"}},
                },
                "required": ["claim_key", "statement", "verdict", "supporting_sources", "contradicting_sources"],
            },
        }
    },
    "required": ["observations"],
}
_SUPPORTED_VERDICTS = {
    "confirmed": EvidenceState.CONFIRMED,
    "contradicted": EvidenceState.CONTRADICTED,
    "unknown": EvidenceState.UNKNOWN,
}
_FORBIDDEN_DECISIONS = {"accept", "continue", "human_review"}


def build_groq_qwen_client(*, api_key: str | None = None, base_url: str = DEFAULT_GROQ_BASE_URL) -> Any:
    """Construct an OpenAI-compatible client for Groq without making a request."""
    from openai import OpenAI

    return OpenAI(api_key=api_key, base_url=base_url)


def parse_groq_qwen_structured_evidence(
    payload: Any,
    requested_keys: Sequence[str],
) -> tuple[ExternalEvidenceRecord, ...]:
    """Normalize a Groq/Qwen structured response into external evidence records."""
    if isinstance(payload, str):
        try:
            data = json.loads(payload)
        except json.JSONDecodeError as exc:
            raise RealEvidenceProviderError("groq qwen structured response was not valid JSON") from exc
    elif isinstance(payload, Mapping):
        data = payload
    else:
        raise RealEvidenceProviderError("groq qwen structured response has an invalid payload type")

    observations = data.get("observations")
    if not isinstance(observations, list):
        raise RealEvidenceProviderError("groq qwen structured response missing observations")
    requested = tuple(requested_keys)
    records: list[ExternalEvidenceRecord] = []
    seen: set[str] = set()
    allowed = {"claim_key", "statement", "verdict", "supporting_sources", "contradicting_sources"}
    required = tuple(allowed)
    for item in observations:
        if not isinstance(item, Mapping):
            raise RealEvidenceProviderError("groq qwen observation is not an object")
        if set(item) - allowed:
            raise RealEvidenceProviderError("groq qwen observation contains an unsupported field")
        if any(item.get(key) in _FORBIDDEN_DECISIONS for key in ("decision", "status", "outcome")):
            raise RealEvidenceProviderError("groq qwen response contained a Core decision")
        if any(field not in item for field in required):
            raise RealEvidenceProviderError("groq qwen observation is missing an evidence field")

        claim_key = item["claim_key"]
        statement = item["statement"]
        verdict = item["verdict"]
        supporting = item["supporting_sources"]
        contradicting = item["contradicting_sources"]
        if not isinstance(claim_key, str) or not claim_key.strip():
            raise RealEvidenceProviderError("groq qwen claim_key is required")
        if claim_key not in requested:
            raise RealEvidenceProviderError("groq qwen returned an unrequested claim")
        if claim_key in seen:
            raise RealEvidenceProviderError("groq qwen returned a duplicate claim")
        if verdict not in _SUPPORTED_VERDICTS:
            raise RealEvidenceProviderError("groq qwen returned an unsupported verdict")
        if not isinstance(statement, str) or not statement.strip():
            raise RealEvidenceProviderError("groq qwen observation statement is required")
        if not isinstance(supporting, list) or not all(isinstance(source, str) and source.strip() for source in supporting):
            raise RealEvidenceProviderError("groq qwen supporting sources are invalid")
        if not isinstance(contradicting, list) or not all(isinstance(source, str) and source.strip() for source in contradicting):
            raise RealEvidenceProviderError("groq qwen contradicting sources are invalid")

        state = _SUPPORTED_VERDICTS[verdict]
        if state is EvidenceState.CONFIRMED and not supporting:
            raise RealEvidenceProviderError("confirmed Groq Qwen evidence requires supporting sources")
        if state is EvidenceState.CONTRADICTED and not contradicting:
            raise RealEvidenceProviderError("contradicted Groq Qwen evidence requires contradicting sources")
        if state is EvidenceState.UNKNOWN and (supporting or contradicting):
            raise RealEvidenceProviderError("unknown Groq Qwen evidence must not claim support or contradiction")
        records.append(ExternalEvidenceRecord(
            claim_key, statement, state,
            supporting_sources=tuple(supporting),
            contradicting_sources=tuple(contradicting),
        ))
        seen.add(claim_key)
    if seen != set(requested):
        raise RealEvidenceProviderError("groq qwen response does not cover all requested claims")
    return tuple(records)


def build_groq_qwen_responses_transport(
    client: Any | None = None,
    *,
    model: str = DEFAULT_GROQ_QWEN_MODEL,
    api_key: str | None = None,
    base_url: str = DEFAULT_GROQ_BASE_URL,
    image_bytes: bytes,
    mime_type: str,
) -> Any:
    """Build an injected Groq/Qwen Responses API request function."""
    if client is None:
        client = build_groq_qwen_client(api_key=api_key, base_url=base_url)

    def request(payload: dict[str, Any]) -> Any:
        image_url = f"data:{mime_type};base64,{base64.b64encode(image_bytes).decode('ascii')}"
        try:
            response = client.responses.create(
                model=model,
                input=[{"role": "user", "content": [
                    {"type": "input_text", "text": payload["prompt"]},
                    {"type": "input_image", "image_url": image_url, "detail": "auto"},
                ]}],
                text={"format": {
                    "type": "json_schema",
                    "name": "external_evidence_observations",
                    "strict": True,
                    "schema": GROQ_QWEN_EVIDENCE_SCHEMA,
                }},
            )
        except Exception as exc:
            raise RealEvidenceProviderError("groq qwen responses request failed") from exc
        output_text = getattr(response, "output_text", None)
        if not isinstance(output_text, str) or not output_text.strip():
            raise RealEvidenceProviderError("groq qwen responses response contained no structured text")
        return output_text
    return request


__all__ = [
    "DEFAULT_GROQ_BASE_URL",
    "DEFAULT_GROQ_QWEN_MODEL",
    "GROQ_QWEN_EVIDENCE_SCHEMA",
    "build_groq_qwen_client",
    "build_groq_qwen_responses_transport",
    "parse_groq_qwen_structured_evidence",
]