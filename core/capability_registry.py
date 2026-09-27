"""Machine-readable capability registry for provider-neutral routing infrastructure.

The registry is descriptive only. It does not select providers or authorize actions.
"""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any


_REGISTRY_FIELDS = {"version", "reviewed", "principle", "capabilities"}
_RECORD_FIELDS = {
    "id",
    "capability",
    "provider",
    "product_or_runtime",
    "status",
    "integration",
    "cost_model",
    "latency_character",
    "strengths",
    "limitations",
    "dependencies",
    "security_boundary",
    "replaceable_by",
    "last_reviewed",
    "evidence",
}
_STRING_FIELDS = {
    "id",
    "capability",
    "provider",
    "product_or_runtime",
    "status",
    "integration",
    "cost_model",
    "latency_character",
    "security_boundary",
    "last_reviewed",
}
_LIST_FIELDS = {"strengths", "limitations", "dependencies", "replaceable_by", "evidence"}


def _non_empty_text(value: Any, name: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"{name} must be a non-empty string")
    return value.strip()


def _string_list(value: Any, name: str) -> tuple[str, ...]:
    if not isinstance(value, list):
        raise ValueError(f"{name} must be a list")
    result = tuple(_non_empty_text(item, name) for item in value)
    if len(set(result)) != len(result):
        raise ValueError(f"{name} must not contain duplicates")
    return result


@dataclass(frozen=True)
class CapabilityRecord:
    id: str
    capability: str
    provider: str
    product_or_runtime: str
    status: str
    integration: str
    cost_model: str
    latency_character: str
    strengths: tuple[str, ...]
    limitations: tuple[str, ...]
    dependencies: tuple[str, ...]
    security_boundary: str
    replaceable_by: tuple[str, ...]
    last_reviewed: str
    evidence: tuple[str, ...]

    def __post_init__(self) -> None:
        for field_name in _STRING_FIELDS:
            _non_empty_text(getattr(self, field_name), field_name)
        for field_name in _LIST_FIELDS:
            values = getattr(self, field_name)
            if not isinstance(values, tuple):
                raise TypeError(f"{field_name} must be a tuple of strings")
            _string_list(list(values), field_name)

    def to_dict(self) -> dict[str, Any]:
        return {
            "id": self.id,
            "capability": self.capability,
            "provider": self.provider,
            "product_or_runtime": self.product_or_runtime,
            "status": self.status,
            "integration": self.integration,
            "cost_model": self.cost_model,
            "latency_character": self.latency_character,
            "strengths": list(self.strengths),
            "limitations": list(self.limitations),
            "dependencies": list(self.dependencies),
            "security_boundary": self.security_boundary,
            "replaceable_by": list(self.replaceable_by),
            "last_reviewed": self.last_reviewed,
            "evidence": list(self.evidence),
        }


@dataclass(frozen=True)
class CapabilityRegistry:
    version: int
    reviewed: str
    principle: str
    records: tuple[CapabilityRecord, ...]

    def __post_init__(self) -> None:
        if isinstance(self.version, bool) or not isinstance(self.version, int) or self.version < 1:
            raise ValueError("version must be a positive integer")
        _non_empty_text(self.reviewed, "reviewed")
        _non_empty_text(self.principle, "principle")
        if not self.records:
            raise ValueError("records must be non-empty")
        if any(not isinstance(record, CapabilityRecord) for record in self.records):
            raise TypeError("records must contain only CapabilityRecord values")
        ids = tuple(record.id for record in self.records)
        if len(set(ids)) != len(ids):
            raise ValueError("capability ids must be unique")

    def get(self, capability_id: str) -> CapabilityRecord:
        normalized_id = _non_empty_text(capability_id, "capability_id")
        for record in self.records:
            if record.id == normalized_id:
                return record
        raise KeyError(normalized_id)

    def for_capability(self, capability: str) -> tuple[CapabilityRecord, ...]:
        normalized_capability = _non_empty_text(capability, "capability")
        return tuple(record for record in self.records if record.capability == normalized_capability)

    def to_dict(self) -> dict[str, Any]:
        return {
            "version": self.version,
            "reviewed": self.reviewed,
            "principle": self.principle,
            "capabilities": [record.to_dict() for record in self.records],
        }

    def to_json(self) -> str:
        return json.dumps(
            self.to_dict(),
            sort_keys=True,
            separators=(",", ":"),
            ensure_ascii=False,
            allow_nan=False,
        )


def load_capability_registry(path: str | Path | None = None) -> CapabilityRegistry:
    """Load the authoritative capability registry with strict schema validation."""
    registry_path = Path(path) if path is not None else (
        Path(__file__).resolve().parents[1] / "data" / "capabilities.json"
    )
    try:
        payload = json.loads(registry_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise ValueError(f"could not read capability registry: {registry_path}") from exc

    if not isinstance(payload, dict) or set(payload) != _REGISTRY_FIELDS:
        raise ValueError("capability registry must contain exactly the registry fields")
    if isinstance(payload["version"], bool) or not isinstance(payload["version"], int) or payload["version"] != 1:
        raise ValueError("unsupported capability registry version")

    capabilities = payload["capabilities"]
    if not isinstance(capabilities, list) or not capabilities:
        raise ValueError("capabilities must be a non-empty list")

    records: list[CapabilityRecord] = []
    ids: set[str] = set()
    for index, raw in enumerate(capabilities):
        if not isinstance(raw, dict) or set(raw) != _RECORD_FIELDS:
            raise ValueError(f"capability {index} must contain exactly the record fields")

        values: dict[str, Any] = {}
        for field_name in _STRING_FIELDS:
            values[field_name] = _non_empty_text(raw[field_name], f"capability {index}.{field_name}")
        for field_name in _LIST_FIELDS:
            values[field_name] = _string_list(raw[field_name], f"capability {index}.{field_name}")

        if values["id"] in ids:
            raise ValueError(f"duplicate capability id: {values['id']}")
        ids.add(values["id"])
        records.append(CapabilityRecord(**values))

    return CapabilityRegistry(
        version=payload["version"],
        reviewed=_non_empty_text(payload["reviewed"], "reviewed"),
        principle=_non_empty_text(payload["principle"], "principle"),
        records=tuple(records),
    )
