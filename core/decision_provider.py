"""Provider-neutral contract for bounded decisions.

Providers return judgments only. Callers retain responsibility for any action
or authority that follows from a result.
"""

from __future__ import annotations

import json
import math
from dataclasses import dataclass
from typing import Any, Mapping, Protocol, TypeAlias


SCHEMA_VERSION = 1
DECISION_KINDS = frozenset({"boolean", "choice", "score"})
DecisionValue: TypeAlias = bool | str | float


def _nonempty(name: str, value: Any) -> str:
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"{name} must be a non-empty string")
    return value.strip()


def _json_value(value: Any, name: str) -> Any:
    """Copy JSON-compatible state while rejecting ambiguous/non-finite data."""
    try:
        encoded = json.dumps(value, allow_nan=False)
        return json.loads(encoded)
    except (TypeError, ValueError) as exc:
        raise ValueError(f"{name} must contain only finite JSON values") from exc


@dataclass(frozen=True)
class DecisionRequest:
    question_id: str
    kind: str
    context: Mapping[str, Any]
    question: str
    choices: tuple[str, ...] | None = None

    def __post_init__(self) -> None:
        _nonempty("question_id", self.question_id)
        _nonempty("question", self.question)
        if self.kind not in DECISION_KINDS:
            raise ValueError(f"unsupported decision kind: {self.kind!r}")
        if not isinstance(self.context, Mapping):
            raise ValueError("context must be a mapping")
        context = _json_value(dict(self.context), "context")
        if not isinstance(context, dict):
            raise ValueError("context must be a JSON object")
        object.__setattr__(self, "context", context)
        if self.kind == "choice":
            if not isinstance(self.choices, (tuple, list)) or not self.choices:
                raise ValueError("choice decisions require non-empty allowed choices")
            choices = tuple(_nonempty("choice", choice) for choice in self.choices)
            if len(set(choices)) != len(choices):
                raise ValueError("choices must not contain duplicates")
            object.__setattr__(self, "choices", choices)
        elif self.choices is not None:
            raise ValueError("choices are only valid for choice decisions")

    def to_dict(self) -> dict[str, Any]:
        return {
            "schema_version": SCHEMA_VERSION,
            "question_id": self.question_id,
            "kind": self.kind,
            "context": self.context,
            "question": self.question,
            "choices": list(self.choices) if self.choices is not None else None,
        }


@dataclass(frozen=True)
class DecisionResult:
    question_id: str
    kind: str
    value: DecisionValue
    provider_id: str
    confidence: float | None = None
    model_id: str | None = None

    def __post_init__(self) -> None:
        _nonempty("question_id", self.question_id)
        _nonempty("provider_id", self.provider_id)
        if self.kind not in DECISION_KINDS:
            raise ValueError(f"unsupported decision kind: {self.kind!r}")
        if self.model_id is not None:
            _nonempty("model_id", self.model_id)
        if self.kind == "boolean":
            if not isinstance(self.value, bool):
                raise ValueError("boolean decisions require a boolean value")
        elif self.kind == "choice":
            _nonempty("choice value", self.value)
        elif isinstance(self.value, bool) or not isinstance(self.value, (int, float)):
            raise ValueError("score decisions require a finite number")
        elif not math.isfinite(self.value):
            raise ValueError("score decisions require a finite number")
        if self.confidence is not None:
            if isinstance(self.confidence, bool) or not isinstance(self.confidence, (int, float)):
                raise ValueError("confidence must be a number between 0 and 1")
            if not math.isfinite(self.confidence) or not 0 <= self.confidence <= 1:
                raise ValueError("confidence must be a number between 0 and 1")

    def validate_for(self, request: DecisionRequest) -> None:
        if self.question_id != request.question_id or self.kind != request.kind:
            raise ValueError("result does not match request question_id and kind")
        if self.kind == "choice" and self.value not in request.choices:
            raise ValueError("choice result must be one of the request's allowed choices")

    def to_dict(self) -> dict[str, Any]:
        return {
            "schema_version": SCHEMA_VERSION,
            "question_id": self.question_id,
            "kind": self.kind,
            "value": self.value,
            "confidence": self.confidence,
            "provider_id": self.provider_id,
            "model_id": self.model_id,
        }


class DecisionProvider(Protocol):
    """A provider that answers a bounded request without executing actions."""

    def decide(self, request: DecisionRequest) -> DecisionResult: ...


_REQUEST_KEYS = {"schema_version", "question_id", "kind", "context", "question", "choices"}
_RESULT_KEYS = {"schema_version", "question_id", "kind", "value", "confidence", "provider_id", "model_id"}


def _decode(payload: str, keys: set[str], name: str) -> dict[str, Any]:
    try:
        data = json.loads(payload)
    except (TypeError, json.JSONDecodeError) as exc:
        raise ValueError(f"invalid {name} JSON") from exc
    if not isinstance(data, dict) or set(data) != keys:
        raise ValueError(f"{name} must contain exactly the contract fields")
    if data["schema_version"] != SCHEMA_VERSION:
        raise ValueError(f"unsupported {name} schema_version")
    return data


def serialize_decision_request(request: DecisionRequest) -> str:
    return json.dumps(request.to_dict(), sort_keys=True, separators=(",", ":"), ensure_ascii=False, allow_nan=False)


def deserialize_decision_request(payload: str) -> DecisionRequest:
    data = _decode(payload, _REQUEST_KEYS, "decision request")
    return DecisionRequest(data["question_id"], data["kind"], data["context"], data["question"], data["choices"])


def serialize_decision_result(result: DecisionResult) -> str:
    return json.dumps(result.to_dict(), sort_keys=True, separators=(",", ":"), ensure_ascii=False, allow_nan=False)


def deserialize_decision_result(payload: str) -> DecisionResult:
    data = _decode(payload, _RESULT_KEYS, "decision result")
    return DecisionResult(data["question_id"], data["kind"], data["value"], data["provider_id"], data["confidence"], data["model_id"])
