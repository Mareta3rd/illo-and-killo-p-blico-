"""Local OpenAI-compatible collaborative provider.

The adapter maps one bounded WorkEnvelope to a structured CollaborationUpdate.
It never executes tools, changes canon, or returns a Core decision.
"""

from __future__ import annotations

import json
import math
from collections.abc import Mapping
from typing import Any

from core.work_envelope import CollaborationUpdate, WorkEnvelope


_OUTPUT_PROPERTIES: dict[str, Any] = {
    "answer": {"type": "string"},
    "rationale": {"type": "string"},
    "proposals": {"type": "array", "items": {"type": "string"}},
    "questions": {"type": "array", "items": {"type": "string"}},
}

_OUTPUT_REQUIRED = ["answer", "rationale", "proposals", "questions"]


def _output_schema() -> dict[str, Any]:
    return {
        "type": "object",
        "additionalProperties": False,
        "properties": _OUTPUT_PROPERTIES,
        "required": _OUTPUT_REQUIRED,
    }


def _collaboration_output_schema() -> dict[str, Any]:
    return {
        "type": "object",
        "additionalProperties": False,
        "properties": {
            "status": {
                "type": "string",
                "enum": [
                    "available",
                    "working",
                    "needs_input",
                    "ready_for_review",
                    "blocked",
                    "done",
                ],
            },
            "summary": {"type": "string"},
            "progress": {"type": "array", "items": {"type": "string"}},
            "needs_input": {"type": ["string", "null"]},
            "blockers": {"type": "array", "items": {"type": "string"}},
            "output": {"type": ["object", "null"], "additionalProperties": False, "properties": _OUTPUT_PROPERTIES, "required": _OUTPUT_REQUIRED},
            "attention_required": {"type": "boolean"},
        },
        "required": [
            "status",
            "summary",
            "progress",
            "needs_input",
            "blockers",
            "output",
            "attention_required",
        ],
    }


def build_collaboration_prompt(envelope: WorkEnvelope) -> str:
    """Build a deterministic prompt from the bounded collaboration contract."""
    instructions = [
        "Work as a bounded collaborator for the supplied WorkEnvelope.",
        "Return exactly one JSON object matching the supplied schema.",
        "Produce concrete, useful work rather than generic encouragement or vague advice.",
        "Use objective, context, prior work and known failures together; do not ignore inconvenient constraints.",
        "Treat canon and repository facts supplied in context as boundaries, not as permission to invent missing facts.",
        "Treat available_tools as capability metadata only. Do not call, execute or imply authorization to use any tool.",
        "Do not execute external actions, modify files, change canon, make Core decisions or issue routing commands.",
        "The output is a proposal or handoff for Core or a human reviewer, not an authorization.",
        "Use questions only for information that is genuinely required to continue.",
        "Use working when the task remains in progress, ready_for_review when a bounded result is ready for review, needs_input when a blocking human answer is required, blocked when progress cannot continue, and done only when the bounded objective is actually complete.",
        "Set attention_required true only when the selected status represents an actionable handoff.",
        "Keep proposals specific and testable. Avoid filler, repetition and unsupported certainty.",
        "",
        "WORK ENVELOPE:",
        envelope.to_json(),
    ]
    return "\n".join(instructions)


class LocalStructuredCollaborationProvider:
    """Use an injected OpenAI-compatible runtime for bounded collaboration."""

    def __init__(
        self,
        client: Any,
        *,
        model: str,
        provider_id: str = "local-qwen-collaboration",
        temperature: float = 0.0,
    ) -> None:
        if client is None or not hasattr(client, "chat") or not hasattr(client.chat, "completions"):
            raise TypeError("client must expose chat.completions")
        if not isinstance(model, str) or not model.strip():
            raise ValueError("model must be a non-empty string")
        if isinstance(temperature, bool) or not isinstance(temperature, (int, float)):
            raise ValueError("temperature must be a finite number")
        if not math.isfinite(temperature):
            raise ValueError("temperature must be a finite number")
        if temperature < 0:
            raise ValueError("temperature must be non-negative")
        if not isinstance(provider_id, str) or not provider_id.strip():
            raise ValueError("provider_id must be a non-empty string")

        self._client = client
        self._model = model.strip()
        self._provider_id = provider_id.strip()
        self._temperature = float(temperature)

    @property
    def provider_id(self) -> str:
        return self._provider_id

    @property
    def model_id(self) -> str:
        return self._model

    def collaborate(self, envelope: WorkEnvelope) -> CollaborationUpdate:
        if not isinstance(envelope, WorkEnvelope):
            raise TypeError("envelope must be a WorkEnvelope")

        response = self._client.chat.completions.create(
            model=self._model,
            temperature=self._temperature,
            messages=[{"role": "user", "content": build_collaboration_prompt(envelope)}],
            response_format={
                "type": "json_schema",
                "json_schema": {
                    "name": "CollaborationUpdate",
                    "schema": _collaboration_output_schema(),
                    "strict": True,
                },
            },
        )

        choices = getattr(response, "choices", None)
        if not choices:
            raise ValueError("local collaboration provider response contained no choices")
        content = getattr(choices[0].message, "content", None)
        if not isinstance(content, str) or not content.strip():
            raise ValueError(
                "local collaboration provider response contained no message content"
            )

        try:
            payload = json.loads(content)
        except json.JSONDecodeError as exc:
            raise ValueError("local collaboration provider returned invalid JSON") from exc

        if not isinstance(payload, Mapping):
            raise ValueError("local collaboration provider returned an invalid object")

        expected_keys = {
            "status",
            "summary",
            "progress",
            "needs_input",
            "blockers",
            "output",
            "attention_required",
        }
        if set(payload) != expected_keys:
            raise ValueError(
                "local collaboration provider returned an invalid collaboration object"
            )

        output = payload["output"]
        if output is not None:
            if not isinstance(output, Mapping) or set(output) != set(_OUTPUT_PROPERTIES):
                raise ValueError(
                    "local collaboration provider returned an invalid output object"
                )

        update = CollaborationUpdate(
            envelope_id=envelope.envelope_id,
            status=payload["status"],
            summary=payload["summary"],
            progress=tuple(payload["progress"]),
            needs_input=payload["needs_input"],
            blockers=tuple(payload["blockers"]),
            output=dict(output) if output is not None else None,
            attention_required=payload["attention_required"],
        )
        update.validate_for(envelope)
        return update


__all__ = ["LocalStructuredCollaborationProvider", "build_collaboration_prompt"]
