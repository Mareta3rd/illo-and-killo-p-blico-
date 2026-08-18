"""Concrete Gemini Interactions API transport and structured evidence parser."""

from __future__ import annotations

import json
from typing import Any, Sequence

from .evidence_state import EvidenceState
from .external_evidence_adapter import ExternalEvidenceRecord
from .real_evidence_provider import RealEvidenceProviderError


_SUPPORTED_VERDICTS = {
    "confirmed": EvidenceState.CONFIRMED,
    "contradicted": EvidenceState.CONTRADICTED,
    "unknown": EvidenceState.UNKNOWN,
}


def parse_gemini_structured_evidence(
    payload: Any,
    requested_keys: Sequence[str],
) -> tuple[ExternalEvidenceRecord, ...]:
    """Parse Gemini structured JSON into canonical ExternalEvidenceRecords."""
    if isinstance(payload, str):
        try:
            data = json.loads(payload)
        except json.JSONDecodeError as exc:
            raise RealEvidenceProviderError("gemini structured response was not valid JSON") from exc
    elif isinstance(payload, Mapping):
        data = payload
    else:
        raise RealEvidenceProviderError("gemini structured response has an invalid payload type")

    observations = data.get("observations")
    if not isinstance(observations, list):
        raise RealEvidenceProviderError("gemini structured response missing observations")

    requested = tuple(requested_keys)
    records: list[ExternalEvidenceRecord] = []
    seen: set[str] = set()
    for item in observations:
        if not isinstance(item, dict):
            raise RealEvidenceProviderError("gemini observation is not an object")
        claim_key = item.get("claim_key")
        verdict = item.get("verdict")
        statement = item.get("statement")
        supporting = tuple(item.get("supporting_sources", ()))
        contradicting = tuple(item.get("contradicting_sources", ()))

        if claim_key not in requested:
            raise RealEvidenceProviderError("gemini returned an unrequested claim")
        if claim_key in seen:
            raise RealEvidenceProviderError("gemini returned a duplicate claim")
        if verdict not in _SUPPORTED_VERDICTS:
            raise RealEvidenceProviderError("gemini returned an unsupported verdict")
        if not isinstance(statement, str) or not statement.strip():
            raise RealEvidenceProviderError("gemini observation statement is required")
        if not all(isinstance(source, str) and source.strip() for source in supporting):
            raise RealEvidenceProviderError("gemini supporting sources are invalid")
        if not all(isinstance(source, str) and source.strip() for source in contradicting):
            raise RealEvidenceProviderError("gemini contradicting sources are invalid")

        state = _SUPPORTED_VERDICTS[verdict]
        if state is EvidenceState.CONFIRMED and not supporting:
            raise RealEvidenceProviderError("confirmed Gemini evidence requires supporting sources")
        if state is EvidenceState.CONTRADICTED and not contradicting:
            raise RealEvidenceProviderError("contradicted Gemini evidence requires contradicting sources")
        if state is EvidenceState.UNKNOWN and (supporting or contradicting):
            raise RealEvidenceProviderError("unknown Gemini evidence must not claim support or contradiction")

        records.append(
            ExternalEvidenceRecord(
                claim_key,
                statement,
                state,
                supporting_sources=supporting,
                contradicting_sources=contradicting,
            )
        )
        seen.add(claim_key)

    if seen != set(requested):
        raise RealEvidenceProviderError("gemini response does not cover all requested claims")

    return tuple(records)


def build_gemini_interactions_transport(
    client: Any,
    *,
    model: str,
    image_bytes: bytes,
    mime_type: str,
) -> Any:
    """Build a concrete request function for Gemini's Interactions API.

    The returned function uses structured JSON output and supplies the candidate
    image alongside the evidence prompt. The actual Google SDK client is injected
    so Core tests never require network access or credentials.
    """

    def request(payload: dict[str, Any]) -> Any:
        try:
            interaction = client.interactions.create(
                model=model,
                input=[
                    {
                        "type": "image",
                        "data": image_bytes,
                        "mime_type": mime_type,
                    },
                    {"type": "text", "text": payload["prompt"]},
                ],
                response_format={
                    "type": "text",
                    "mime_type": "application/json",
                    "schema": {
                        "type": "object",
                        "properties": {
                            "observations": {
                                "type": "array",
                                "items": {
                                    "type": "object",
                                    "properties": {
                                        "claim_key": {"type": "string"},
                                        "verdict": {"type": "string", "enum": ["confirmed", "contradicted", "unknown"]},
                                        "statement": {"type": "string"},
                                        "supporting_sources": {"type": "array", "items": {"type": "string"}},
                                        "contradicting_sources": {"type": "array", "items": {"type": "string"}},
                                    },
                                    "required": ["claim_key", "verdict", "statement", "supporting_sources", "contradicting_sources"],
                                },
                            }
                        },
                        "required": ["observations"],
                    },
                },
            )
        except Exception as exc:
            raise RealEvidenceProviderError("gemini interactions request failed") from exc

        text = getattr(interaction, "output_text", None)
        if not isinstance(text, str) or not text.strip():
            raise RealEvidenceProviderError("gemini interactions response contained no structured text")
        return text

    return request


# Local import keeps runtime compatibility with the typing-only use above.
from typing import Mapping  # noqa: E402


__all__ = ["build_gemini_interactions_transport", "parse_gemini_structured_evidence"]
