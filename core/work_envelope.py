"""Bounded protocol for non-intrusive collaborative AI work.

A WorkEnvelope describes one bounded piece of work. A CollaborationUpdate reports
progress or a handoff state. Neither type authorizes tool execution or changes
Core authority.
"""

from __future__ import annotations

import json
from dataclasses import dataclass
from typing import Any, Mapping


_WORK_STATES = frozenset(
    {"available", "working", "needs_input", "ready_for_review", "blocked", "done"}
)
_AUTONOMY_MODES = frozenset(
    {"advisory", "bounded_execution", "human_approval_required"}
)
_INTERRUPT_POLICIES = frozenset(
    {"needs_input_only", "state_change_or_input", "explicit_request_only"}
)
_MAX_CONTEXT_KEYS = 24
_MAX_CONTEXT_VALUE_BYTES = 24_000
_MAX_OUTPUT_VALUE_BYTES = 24_000
_MAX_LIST_ENTRIES = 32
_MAX_TEXT_LENGTH = 2_000
_MAX_LIST_ITEM_LENGTH = 600


def _json_value(value: Any, name: str) -> Any:
    try:
        encoded = json.dumps(value, allow_nan=False, ensure_ascii=False)
        return json.loads(encoded)
    except (TypeError, ValueError) as exc:
        raise ValueError(f"{name} must contain only finite JSON values") from exc


def _text(value: Any, name: str, *, limit: int = _MAX_TEXT_LENGTH) -> str:
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"{name} must be a non-empty string")
    value = value.strip()
    if len(value) > limit:
        raise ValueError(f"{name} exceeds the maximum length of {limit}")
    return value


def _text_tuple(value: Any, name: str) -> tuple[str, ...]:
    if not isinstance(value, (tuple, list)):
        raise TypeError(f"{name} must be a tuple or list of strings")
    if len(value) > _MAX_LIST_ENTRIES:
        raise ValueError(f"{name} exceeds the maximum entry count of {_MAX_LIST_ENTRIES}")
    items = tuple(_text(item, name, limit=_MAX_LIST_ITEM_LENGTH) for item in value)
    if len(set(items)) != len(items):
        raise ValueError(f"{name} must not contain duplicates")
    return items


def _bounded_json_object(
    value: Mapping[str, Any] | None, name: str, max_bytes: int
) -> dict[str, Any] | None:
    if value is None:
        return None
    if not isinstance(value, Mapping):
        raise TypeError(f"{name} must be a mapping")
    normalized = _json_value(dict(value), name)
    if not isinstance(normalized, dict):
        raise ValueError(f"{name} must be a JSON object")
    encoded = json.dumps(
        normalized, ensure_ascii=False, separators=(",", ":"), allow_nan=False
    )
    if len(encoded.encode("utf-8")) > max_bytes:
        raise ValueError(
            f"{name} exceeds the maximum encoded size of {max_bytes} bytes"
        )
    return normalized


@dataclass(frozen=True)
class WorkEnvelope:
    """Immutable description of one bounded collaborative work item."""

    envelope_id: str
    objective: str
    project: str
    state: str = "available"
    context: Mapping[str, Any] | None = None
    constraints: tuple[str, ...] = ()
    available_tools: tuple[str, ...] = ()
    prior_work: tuple[str, ...] = ()
    known_failures: tuple[str, ...] = ()
    expected_output: str = ""
    autonomy: str = "advisory"
    interrupt_policy: str = "state_change_or_input"

    def __post_init__(self) -> None:
        _text(self.envelope_id, "envelope_id")
        _text(self.objective, "objective")
        _text(self.project, "project")
        if self.state not in _WORK_STATES:
            raise ValueError(f"unsupported work state: {self.state!r}")
        if self.autonomy not in _AUTONOMY_MODES:
            raise ValueError(f"unsupported autonomy mode: {self.autonomy!r}")
        if self.interrupt_policy not in _INTERRUPT_POLICIES:
            raise ValueError(f"unsupported interrupt policy: {self.interrupt_policy!r}")

        if self.context is not None and not isinstance(self.context, Mapping):
            raise TypeError("context must be a mapping")
        raw_context = self.context
        if raw_context is not None and len(raw_context) > _MAX_CONTEXT_KEYS:
            raise ValueError(
                f"context exceeds the maximum key count of {_MAX_CONTEXT_KEYS}"
            )
        normalized_context = _bounded_json_object(
            raw_context, "context", _MAX_CONTEXT_VALUE_BYTES
        )
        object.__setattr__(self, "context", normalized_context or {})

        for field_name in (
            "constraints",
            "available_tools",
            "prior_work",
            "known_failures",
        ):
            object.__setattr__(
                self, field_name, _text_tuple(getattr(self, field_name), field_name)
            )

        if not isinstance(self.expected_output, str):
            raise TypeError("expected_output must be a string")
        if self.expected_output:
            object.__setattr__(
                self,
                "expected_output",
                _text(self.expected_output, "expected_output"),
            )

    def to_dict(self) -> dict[str, Any]:
        return {
            "schema_version": 1,
            "envelope_id": self.envelope_id,
            "objective": self.objective,
            "project": self.project,
            "state": self.state,
            "context": self.context,
            "constraints": list(self.constraints),
            "available_tools": list(self.available_tools),
            "prior_work": list(self.prior_work),
            "known_failures": list(self.known_failures),
            "expected_output": self.expected_output,
            "autonomy": self.autonomy,
            "interrupt_policy": self.interrupt_policy,
        }

    def to_json(self) -> str:
        return json.dumps(
            self.to_dict(),
            sort_keys=True,
            separators=(",", ":"),
            ensure_ascii=False,
            allow_nan=False,
        )


@dataclass(frozen=True)
class CollaborationUpdate:
    """Immutable progress/handoff update for one WorkEnvelope."""

    envelope_id: str
    status: str
    summary: str
    progress: tuple[str, ...] = ()
    needs_input: str | None = None
    blockers: tuple[str, ...] = ()
    output: Mapping[str, Any] | None = None
    attention_required: bool = False

    def __post_init__(self) -> None:
        _text(self.envelope_id, "envelope_id")
        if self.status not in _WORK_STATES:
            raise ValueError(f"unsupported collaboration status: {self.status!r}")
        _text(self.summary, "summary")
        object.__setattr__(self, "progress", _text_tuple(self.progress, "progress"))
        object.__setattr__(self, "blockers", _text_tuple(self.blockers, "blockers"))

        if self.needs_input is not None:
            object.__setattr__(
                self,
                "needs_input",
                _text(self.needs_input, "needs_input"),
            )

        normalized_output = _bounded_json_object(
            self.output, "output", _MAX_OUTPUT_VALUE_BYTES
        )
        object.__setattr__(self, "output", normalized_output)

        if not isinstance(self.attention_required, bool):
            raise TypeError("attention_required must be a boolean")

        if self.status == "needs_input" and self.needs_input is None:
            raise ValueError("needs_input status requires a needs_input message")
        if self.status != "needs_input" and self.needs_input is not None:
            raise ValueError("needs_input message is only valid with needs_input status")

        if self.attention_required:
            allowed = {"needs_input", "ready_for_review", "blocked", "done"}
            if self.status not in allowed:
                raise ValueError(
                    "attention_required is only valid for an actionable handoff state"
                )

    def validate_for(self, envelope: WorkEnvelope) -> None:
        if not isinstance(envelope, WorkEnvelope):
            raise TypeError("envelope must be a WorkEnvelope")
        if self.envelope_id != envelope.envelope_id:
            raise ValueError("collaboration update does not match the work envelope")

    def to_dict(self) -> dict[str, Any]:
        return {
            "schema_version": 1,
            "envelope_id": self.envelope_id,
            "status": self.status,
            "summary": self.summary,
            "progress": list(self.progress),
            "needs_input": self.needs_input,
            "blockers": list(self.blockers),
            "output": self.output,
            "attention_required": self.attention_required,
        }

    def to_json(self) -> str:
        return json.dumps(
            self.to_dict(),
            sort_keys=True,
            separators=(",", ":"),
            ensure_ascii=False,
            allow_nan=False,
        )


__all__ = ["WorkEnvelope", "CollaborationUpdate"]
