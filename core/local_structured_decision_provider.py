"""Local structured-model implementation of the provider-neutral DecisionProvider contract.

The provider is deliberately model-runtime agnostic: callers inject an OpenAI-compatible
client, while Core only receives a validated DecisionResult. No action is executed and the
model cannot return Core decisions, canon mutations, or routing commands.
"""

from __future__ import annotations

import json
import math
from collections.abc import Mapping
from typing import Any

from core.decision_provider import DecisionRequest, DecisionResult


def _decision_output_schema(request: DecisionRequest) -> dict[str, Any]:
    if request.kind == "boolean":
        value_schema: dict[str, Any] = {"type": "boolean"}
    elif request.kind == "choice":
        value_schema = {"type": "string", "enum": list(request.choices or ())}
    else:
        value_schema = {"type": "number"}
    return {
        "type": "object",
        "additionalProperties": False,
        "properties": {
            "value": value_schema,
            "confidence": {"type": ["number", "null"]},
        },
        "required": ["value", "confidence"],
    }


def build_decision_prompt(request: DecisionRequest) -> str:
    """Build a deterministic provider prompt from the bounded request contract."""
    payload = {
        "question_id": request.question_id,
        "kind": request.kind,
        "context": dict(request.context),
        "question": request.question,
        "choices": list(request.choices) if request.choices is not None else None,
    }
    instructions = [
        "Return exactly one JSON object matching the supplied schema.",
        "Answer only the bounded decision requested.",
        "Do not propose actions, change policy, modify canon, or emit routing commands.",
        "Do not add fields outside the schema.",
        "For confidence, return a number between 0 and 1 when the runtime provides a calibrated confidence; otherwise return null.",
        "Do not use confidence as authorization.",
        "The caller remains responsible for all Core validation and any later action.",
        "",
        "DECISION REQUEST:",
        json.dumps(payload, sort_keys=True, ensure_ascii=False),
    ]
    return "\n".join(instructions)


class LocalStructuredDecisionProvider:
    """Use an injected local OpenAI-compatible runtime as a bounded decision provider."""

    def __init__(
        self,
        client: Any,
        *,
        model: str,
        provider_id: str = "local-llm",
        temperature: float = 0.0,
    ) -> None:
        if client is None or not hasattr(client, "chat") or not hasattr(client.chat, "completions"):
            raise TypeError("client must expose chat.completions")
        if not isinstance(model, str) or not model.strip():
            raise ValueError("model must be a non-empty string")
        if isinstance(temperature, bool) or not isinstance(temperature, (int, float)) or not math.isfinite(temperature):
            raise ValueError("temperature must be a finite number")
        if temperature < 0:
            raise ValueError("temperature must be non-negative")
        if not isinstance(provider_id, str) or not provider_id.strip():
            raise ValueError("provider_id must be a non-empty string")
        self._client = client
        self._model = model.strip()
        self._provider_id = provider_id.strip()
        self._temperature = float(temperature)

    def decide(self, request: DecisionRequest) -> DecisionResult:
        prompt = build_decision_prompt(request)
        response_format = {
            "type": "json_schema",
            "json_schema": {
                "name": "DecisionResult",
                "schema": _decision_output_schema(request),
                "strict": True,
            },
        }
        response = self._client.chat.completions.create(
            model=self._model,
            temperature=self._temperature,
            messages=[{"role": "user", "content": prompt}],
            response_format=response_format,
        )
        choices = getattr(response, "choices", None)
        if not choices:
            raise ValueError("local decision provider response contained no choices")
        content = getattr(choices[0].message, "content", None)
        if not isinstance(content, str) or not content.strip():
            raise ValueError("local decision provider response contained no message content")
        try:
            payload = json.loads(content)
        except json.JSONDecodeError as exc:
            raise ValueError("local decision provider returned invalid JSON") from exc
        if not isinstance(payload, Mapping) or set(payload) != {"value", "confidence"}:
            raise ValueError("local decision provider returned an invalid decision object")

        confidence = payload["confidence"]
        if confidence is not None:
            if isinstance(confidence, bool) or not isinstance(confidence, (int, float)):
                raise ValueError("local decision provider confidence must be numeric or null")
            if not math.isfinite(confidence) or not 0 <= confidence <= 1:
                raise ValueError("local decision provider confidence must be between 0 and 1")

        result = DecisionResult(
            question_id=request.question_id,
            kind=request.kind,
            value=payload["value"],
            provider_id=self._provider_id,
            confidence=confidence,
            model_id=self._model,
        )
        result.validate_for(request)
        return result


__all__ = ["LocalStructuredDecisionProvider", "build_decision_prompt"]