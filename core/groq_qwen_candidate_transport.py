"""Groq/Qwen Responses-compatible transport for structured candidate generation.

Separates provider-specific request/response handling from the Executor interface.
Follows the same pattern as groq_qwen_evidence_adapter for consistency but is
independent: candidate generation has different constraints and schema than evidence.
"""

from __future__ import annotations

import json
import re
from dataclasses import dataclass
from typing import Any

from .candidate_executor import InvalidCandidateError, ProviderCandidateError
from .prompt_compiler import CompiledPrompt
from .real_evidence_provider import RealEvidenceProviderError


DEFAULT_GROQ_QWEN_CANDIDATE_MODEL = "qwen/qwen3.8-27b"
DEFAULT_GROQ_BASE_URL = "https://api.groq.com/openai/v1"


@dataclass(frozen=True)
class CandidateModelProfile:
    """Groq/Qwen model capabilities relevant to candidate generation."""
    model_id: str
    structured_outputs: bool
    """Only qwen3.8-27b supports JSON Schema for candidates."""


GROQ_QWEN_CANDIDATE_MODEL_PROFILES = {
    "qwen/qwen3.8-27b": CandidateModelProfile("qwen/qwen3.8-27b", True),
    "qwen/qwen3.6-27b": CandidateModelProfile("qwen/qwen3.6-27b", False),
}

GROQ_QWEN_CANDIDATE_SCHEMA = {
    "type": "object",
    "additionalProperties": False,
    "properties": {
        "content": {
            "type": "string",
            "description": "Primary creative content or proposal",
        },
        "characters": {
            "type": "array",
            "items": {"type": "string"},
            "description": "Character names involved",
        },
        "roles": {
            "type": "array",
            "items": {"type": "string"},
            "description": "Character roles or relationships",
        },
        "elements": {
            "type": "array",
            "description": "Structured elements introduced by the candidate. Never use bare strings.",
            "items": {
                "type": "object",
                "additionalProperties": False,
                "properties": {
                    "id": {"type": "string"},
                    "intention": {"type": "string"},
                    "library": {"type": ["string", "null"]},
                    "count": {"type": ["integer", "null"]},
                    "color": {"type": ["string", "null"]},
                    "very_small": {"type": ["boolean", "null"]},
                    "role": {"type": ["string", "null"]},
                },
                "required": [
                    "id",
                    "intention",
                    "library",
                    "count",
                    "color",
                    "very_small",
                    "role",
                ],
            },
        },
        "checks": {
            "type": "object",
            "additionalProperties": False,
            "description": "Pre-validation checks by the generator",
            "required": [
                "intention",
                "canon",
                "coherence",
                "reuse_intention",
            ],
            "properties": {
                "intention": {
                    "oneOf": [
                        {"type": "boolean"},
                        {
                            "type": "object",
                            "properties": {
                                "decision": {"enum": ["pass", "fail", "unknown"]},
                                "reason": {"type": "string"},
                            },
                            "required": ["decision", "reason"],
                            "additionalProperties": False,
                        },
                    ],
                    "description": "Is the proposal intention clear and present?",
                },
                "canon": {
                    "oneOf": [
                        {"type": "boolean"},
                        {
                            "type": "object",
                            "properties": {
                                "decision": {"enum": ["pass", "fail", "unknown"]},
                                "reason": {"type": "string"},
                            },
                            "required": ["decision", "reason"],
                            "additionalProperties": False,
                        },
                    ],
                    "description": "Does the proposal respect canonical invariants?",
                },
                "coherence": {
                    "oneOf": [
                        {"type": "boolean"},
                        {
                            "type": "object",
                            "properties": {
                                "decision": {"enum": ["pass", "fail", "unknown"]},
                                "reason": {"type": "string"},
                            },
                            "required": ["decision", "reason"],
                            "additionalProperties": False,
                        },
                    ],
                    "description": "Is the proposal internally consistent?",
                },
                "reuse_intention": {
                    "oneOf": [
                        {"type": "boolean"},
                        {
                            "type": "object",
                            "properties": {
                                "decision": {"enum": ["pass", "fail", "unknown"]},
                                "reason": {"type": "string"},
                            },
                            "required": ["decision", "reason"],
                            "additionalProperties": False,
                        },
                    ],
                    "description": "If reusing existing assets, are they intentional?",
                },
            },
        },
    },
    "required": [
        "content",
        "characters",
        "roles",
        "elements",
        "checks",
    ],
}

_FORBIDDEN_CANDIDATE_FIELDS = {
    "accept",
    "continue",
    "human_review",
    "decision",
    "evidence",
    "claim_key",
    "supporting_sources",
    "contradicting_sources",
}

_SENSITIVE_EXCEPTION_PATTERNS = (
    (re.compile(r"(?i)(authorization\s*[:=]\s*bearer\s+)[^\s,;]+"), r"\1[REDACTED]"),
    (re.compile(r"(?i)(api[_-]?key\s*[:=]\s*)[^\s,;]+"), r"\1[REDACTED]"),
)


def _format_groq_qwen_exception(exc: Exception) -> str:
    """Format exception message, redacting sensitive fields."""
    message = str(exc)
    for pattern, replacement in _SENSITIVE_EXCEPTION_PATTERNS:
        message = pattern.sub(replacement, message)
    details = [type(exc).__name__, f"message={message}"]
    for attribute in ("status_code", "code"):
        value = getattr(exc, attribute, None)
        if value is not None:
            details.append(f"{attribute}={value}")
    return ", ".join(details)


def get_groq_qwen_candidate_model_profile(model_id: str) -> CandidateModelProfile:
    """Retrieve Groq/Qwen model capabilities for candidate generation."""
    try:
        return GROQ_QWEN_CANDIDATE_MODEL_PROFILES[model_id]
    except KeyError as exc:
        raise RealEvidenceProviderError(f"unsupported Groq Qwen candidate model: {model_id}") from exc


def _validate_candidate_model_capabilities(
    profile: CandidateModelProfile,
    required_capabilities: tuple[str, ...],
) -> None:
    """Ensure model supports required capabilities for candidate generation."""
    for capability in required_capabilities:
        if not hasattr(profile, capability):
            raise RealEvidenceProviderError(
                f"unknown Groq Qwen candidate model capability: {capability}"
            )
        if not getattr(profile, capability):
            raise RealEvidenceProviderError(
                f"Groq Qwen model {profile.model_id} does not support required capability: {capability}"
            )


def build_groq_qwen_candidate_client(
    *,
    api_key: str | None = None,
    base_url: str = DEFAULT_GROQ_BASE_URL,
) -> Any:
    """Construct an OpenAI-compatible client for Groq candidate generation."""
    from openai import OpenAI

    return OpenAI(api_key=api_key, base_url=base_url, max_retries=0)


def build_candidate_request_prompt(
    compiled: CompiledPrompt,
    iteration: int,
    previous: dict[str, Any] | None,
) -> str:
    """Build request prompt from compiled prompt and iteration context."""
    base = compiled.render()

    sections = [base, ""]

    if previous:
        sections.append("PREVIOUS CANDIDATE (for reference/improvement):")
        sections.append(json.dumps(previous, indent=2))
        sections.append("")

    sections.append(f"ITERATION: {iteration}")
    sections.append(
        "CANDIDATE CONTRACT: elements must be objects with id, intention, library, count, color, "
        "very_small, and role. Use null for non-applicable element fields. Never emit a bare "
        "string inside elements."
    )
    sections.append(
        'ELEMENT FORMAT: {"id":"...","intention":"...","library":null,"count":null,'
        '"color":null,"very_small":null,"role":null}'
    )
    sections.append("Return a JSON object that matches the strict schema exactly.")

    return "\n".join(sections)


def parse_groq_qwen_candidate(payload: Any) -> dict[str, Any]:
    """Parse and validate a Groq/Qwen candidate generation response.

    Args:
        payload: Response from the model (str JSON or dict)

    Returns:
        Validated candidate dict

    Raises:
        InvalidCandidateError: If payload is malformed or validation fails
        ProviderCandidateError: If parsing fails
    """
    if isinstance(payload, str):
        try:
            data = json.loads(payload)
        except json.JSONDecodeError as exc:
            raise ProviderCandidateError(
                "groq qwen candidate response was not valid JSON"
            ) from exc
    elif isinstance(payload, dict):
        data = payload
    else:
        raise ProviderCandidateError(
            f"groq qwen candidate response has invalid payload type: {type(payload).__name__}"
        )

    if not isinstance(data, dict):
        raise InvalidCandidateError(
            f"groq qwen candidate response is not a dict (got {type(data).__name__})"
        )

    # Reject fields that cross the provider/Core boundary before checking
    # completeness, so the error identifies the more specific contract
    # violation even when the candidate is otherwise malformed.
    for forbidden in _FORBIDDEN_CANDIDATE_FIELDS:
        if forbidden in data:
            raise InvalidCandidateError(
                f"groq qwen candidate contains forbidden field: {forbidden}"
            )

    required_fields = {"content", "characters", "roles", "elements", "checks"}
    missing = required_fields - set(data)
    if missing:
        raise InvalidCandidateError(
            f"groq qwen candidate missing required fields: {', '.join(sorted(missing))}"
        )

    unknown = set(data) - required_fields
    if unknown:
        raise InvalidCandidateError(
            f"groq qwen candidate contains unknown fields: {', '.join(sorted(unknown))}"
        )

    if not isinstance(data["content"], str):
        raise InvalidCandidateError("groq qwen candidate 'content' must be string")

    for field in ("characters", "roles"):
        value = data[field]
        if not isinstance(value, list):
            raise InvalidCandidateError(f"groq qwen candidate '{field}' must be an array")
        if not all(isinstance(item, str) and item.strip() for item in value):
            raise InvalidCandidateError(
                f"groq qwen candidate '{field}' must contain only non-empty strings"
            )

    elements = data["elements"]
    if not isinstance(elements, list):
        raise InvalidCandidateError("groq qwen candidate 'elements' must be an array")
    element_fields = {
        "id", "intention", "library", "count", "color", "very_small", "role"
    }
    for index, element in enumerate(elements):
        if not isinstance(element, dict):
            raise InvalidCandidateError(
                f"groq qwen candidate element {index} must be an object"
            )
        if set(element) != element_fields:
            missing_element = element_fields - set(element)
            unknown_element = set(element) - element_fields
            detail = []
            if missing_element:
                detail.append("missing=" + ",".join(sorted(missing_element)))
            if unknown_element:
                detail.append("unknown=" + ",".join(sorted(unknown_element)))
            raise InvalidCandidateError(
                f"groq qwen candidate element {index} fields invalid ({'; '.join(detail)})"
            )
        if not isinstance(element["id"], str) or not element["id"].strip():
            raise InvalidCandidateError(
                f"groq qwen candidate element {index} 'id' must be a non-empty string"
            )
        if not isinstance(element["intention"], str) or not element["intention"].strip():
            raise InvalidCandidateError(
                f"groq qwen candidate element {index} 'intention' must be a non-empty string"
            )
        if element["library"] is not None and not isinstance(element["library"], str):
            raise InvalidCandidateError(
                f"groq qwen candidate element {index} 'library' must be string or null"
            )
        if element["count"] is not None and (
            not isinstance(element["count"], int)
            or isinstance(element["count"], bool)
            or element["count"] < 0
        ):
            raise InvalidCandidateError(
                f"groq qwen candidate element {index} 'count' must be a non-negative integer or null"
            )
        if element["color"] is not None and not isinstance(element["color"], str):
            raise InvalidCandidateError(
                f"groq qwen candidate element {index} 'color' must be string or null"
            )
        if element["very_small"] is not None and not isinstance(element["very_small"], bool):
            raise InvalidCandidateError(
                f"groq qwen candidate element {index} 'very_small' must be boolean or null"
            )
        if element["role"] is not None and not isinstance(element["role"], str):
            raise InvalidCandidateError(
                f"groq qwen candidate element {index} 'role' must be string or null"
            )

    checks = data["checks"]
    if not isinstance(checks, dict):
        raise InvalidCandidateError("groq qwen candidate 'checks' must be an object")
    required_checks = {"intention", "canon", "coherence", "reuse_intention"}
    if set(checks) != required_checks:
        missing_checks = required_checks - set(checks)
        unknown_checks = set(checks) - required_checks
        detail = []
        if missing_checks:
            detail.append("missing=" + ",".join(sorted(missing_checks)))
        if unknown_checks:
            detail.append("unknown=" + ",".join(sorted(unknown_checks)))
        raise InvalidCandidateError(
            f"groq qwen candidate checks are invalid ({'; '.join(detail)})"
        )
    for name, value in checks.items():
        if isinstance(value, bool):
            continue
        if not isinstance(value, dict) or set(value) != {"decision", "reason"}:
            raise InvalidCandidateError(
                f"groq qwen candidate check '{name}' must be boolean or decision/reason object"
            )
        if value["decision"] not in {"pass", "fail", "unknown"}:
            raise InvalidCandidateError(
                f"groq qwen candidate check '{name}' has an invalid decision"
            )
        if not isinstance(value["reason"], str):
            raise InvalidCandidateError(
                f"groq qwen candidate check '{name}' reason must be a string"
            )

    return data


def build_groq_qwen_responses_transport(
    client: Any,
    *,
    model: str = DEFAULT_GROQ_QWEN_CANDIDATE_MODEL,
    model_profile: CandidateModelProfile | None = None,
) -> Any:
    """Build a function that generates candidates via Groq/Qwen API.

    Args:
        client: Configured OpenAI-compatible client
        model: Model ID (must support structured outputs)
        model_profile: Optional pre-loaded model profile (for testing)

    Returns:
        Callable that takes (prompt, iteration, previous) and returns parsed Candidate
    """
    if model_profile is None:
        model_profile = get_groq_qwen_candidate_model_profile(model)

    _validate_candidate_model_capabilities(model_profile, ("structured_outputs",))

    def transport(
        compiled: CompiledPrompt,
        iteration: int,
        previous: dict[str, Any] | None,
    ) -> dict[str, Any]:
        """Request candidate from Groq/Qwen with structured output."""
        prompt_text = build_candidate_request_prompt(compiled, iteration, previous)

        try:
            response = client.chat.completions.create(
                model=model,
                messages=[
                    {
                        "role": "user",
                        "content": prompt_text,
                    }
                ],
                response_format={
                    "type": "json_schema",
                    "json_schema": {
                        "name": "Candidate",
                        "schema": GROQ_QWEN_CANDIDATE_SCHEMA,
                        "strict": True,
                    },
                },
            )
        except Exception as exc:
            formatted_exc = _format_groq_qwen_exception(exc)
            raise ProviderCandidateError(
                f"groq qwen candidate request failed: {formatted_exc}"
            ) from exc

        if response.choices:
            content = getattr(response.choices[0].message, "content", None)
            if content:
                return parse_groq_qwen_candidate(content)
        raise ProviderCandidateError(
            "groq qwen candidate response missing content"
        )

    return transport


__all__ = [
    "build_groq_qwen_candidate_client",
    "build_groq_qwen_responses_transport",
    "build_candidate_request_prompt",
    "parse_groq_qwen_candidate",
    "get_groq_qwen_candidate_model_profile",
    "GROQ_QWEN_CANDIDATE_SCHEMA",
]
