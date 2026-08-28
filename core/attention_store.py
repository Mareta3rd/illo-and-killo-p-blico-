"""Small deterministic local store for immutable human-attention events."""

from __future__ import annotations

import json
import os
import tempfile
from dataclasses import replace
from pathlib import Path
from typing import Protocol, Sequence

from .attention import (
    AttentionCategory,
    AttentionEvent,
    AttentionSeverity,
    AttentionStatus,
)


SCHEMA_VERSION = 1


class AttentionStore(Protocol):
    def save(self, event: AttentionEvent) -> AttentionEvent: ...

    def get(self, event_id: str) -> AttentionEvent | None: ...

    def list_pending(
        self,
        *,
        severity: AttentionSeverity | None = None,
        category: AttentionCategory | None = None,
        run_id: str | None = None,
        claim_key: str | None = None,
        event_id: str | None = None,
    ) -> tuple[AttentionEvent, ...]: ...

    def acknowledge(self, event_id: str) -> AttentionEvent: ...

    def resolve(self, event_id: str, note: str) -> AttentionEvent: ...

    def dismiss(self, event_id: str, note: str) -> AttentionEvent: ...


class JsonAttentionStore:
    """Persist attention events in one closed JSON document."""

    def __init__(self, path: str | Path):
        self.path = Path(path)

    def save(self, event: AttentionEvent) -> AttentionEvent:
        _validate_event(event)
        events = self._read_events()
        existing = next((item for item in events if item.event_id == event.event_id), None)
        if existing is not None and existing != event:
            raise ValueError(f"event_id already contains a different event: {event.event_id}")
        if existing is None:
            events.append(event)
        self._write_events(events)
        return event

    def get(self, event_id: str) -> AttentionEvent | None:
        return next((event for event in self._read_events() if event.event_id == event_id), None)

    def list_pending(
        self,
        *,
        severity: AttentionSeverity | None = None,
        category: AttentionCategory | None = None,
        run_id: str | None = None,
        claim_key: str | None = None,
        event_id: str | None = None,
    ) -> tuple[AttentionEvent, ...]:
        events = [event for event in self._read_events() if event.status in {
            AttentionStatus.PENDING,
            AttentionStatus.ACKNOWLEDGED,
        }]
        return tuple(
            event
            for event in events
            if (severity is None or event.severity is severity)
            and (category is None or event.category is category)
            and (run_id is None or event.run_id == run_id)
            and (claim_key is None or event.claim_key == claim_key)
            and (event_id is None or event.event_id == event_id)
        )

    def acknowledge(self, event_id: str) -> AttentionEvent:
        return self._transition(event_id, AttentionStatus.ACKNOWLEDGED)

    def resolve(self, event_id: str, note: str) -> AttentionEvent:
        return self._transition(event_id, AttentionStatus.RESOLVED, note)

    def dismiss(self, event_id: str, note: str) -> AttentionEvent:
        return self._transition(event_id, AttentionStatus.DISMISSED, note)

    def _transition(
        self,
        event_id: str,
        status: AttentionStatus,
        note: str | None = None,
    ) -> AttentionEvent:
        events = self._read_events()
        try:
            index = next(index for index, event in enumerate(events) if event.event_id == event_id)
        except StopIteration as exc:
            raise KeyError(f"unknown attention event: {event_id}") from exc
        event = events[index]
        if event.status not in {AttentionStatus.PENDING, AttentionStatus.ACKNOWLEDGED}:
            raise ValueError(f"invalid attention transition from {event.status.value}")
        if status in {AttentionStatus.RESOLVED, AttentionStatus.DISMISSED}:
            if not isinstance(note, str) or not note.strip():
                raise ValueError("resolution note is required")
        updated = replace(event, status=status, reason=f"{event.reason} | {note}" if note else event.reason)
        events[index] = updated
        self._write_events(events)
        return updated

    def _read_events(self) -> list[AttentionEvent]:
        if not self.path.exists():
            return []
        try:
            data = json.loads(self.path.read_text(encoding="utf-8"))
        except (OSError, ValueError, json.JSONDecodeError) as exc:
            raise ValueError("invalid attention store JSON") from exc
        if not isinstance(data, dict) or set(data) != {"schema_version", "events"}:
            raise ValueError("invalid attention store schema")
        if data["schema_version"] != SCHEMA_VERSION or not isinstance(data["events"], list):
            raise ValueError("unsupported attention store schema")
        events = [_event_from_dict(item) for item in data["events"]]
        if len({event.event_id for event in events}) != len(events):
            raise ValueError("duplicate attention event_id")
        return events

    def _write_events(self, events: Sequence[AttentionEvent]) -> None:
        self.path.parent.mkdir(parents=True, exist_ok=True)
        payload = {
            "schema_version": SCHEMA_VERSION,
            "events": [_event_to_dict(event) for event in sorted(events, key=lambda item: item.event_id)],
        }
        content = json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True) + "\n"
        descriptor, temporary = tempfile.mkstemp(prefix=f".{self.path.name}.", dir=self.path.parent)
        try:
            with os.fdopen(descriptor, "w", encoding="utf-8") as handle:
                handle.write(content)
                handle.flush()
                os.fsync(handle.fileno())
            os.replace(temporary, self.path)
        except OSError:
            try:
                os.unlink(temporary)
            except OSError:
                pass
            raise


def _event_to_dict(event: AttentionEvent) -> dict[str, object]:
    return {
        "event_id": event.event_id,
        "run_id": event.run_id,
        "severity": event.severity.value,
        "category": event.category.value,
        "status": event.status.value,
        "reason": event.reason,
        "claim_key": event.claim_key,
        "catalog": event.catalog,
        "entry": event.entry,
        "invariant": event.invariant,
        "source_stop_reason": event.source_stop_reason,
        "created_at": event.created_at,
        "deduplication_key": event.deduplication_key,
    }


def _event_from_dict(data: object) -> AttentionEvent:
    if not isinstance(data, dict) or set(data) != {
        "event_id", "run_id", "severity", "category", "status", "reason",
        "claim_key", "catalog", "entry", "invariant", "source_stop_reason",
        "created_at", "deduplication_key",
    }:
        raise ValueError("invalid attention event schema")
    try:
        event = AttentionEvent(
            event_id=_required_text(data["event_id"], "event_id"),
            run_id=_required_text(data["run_id"], "run_id"),
            severity=AttentionSeverity(data["severity"]),
            category=AttentionCategory(data["category"]),
            status=AttentionStatus(data["status"]),
            reason=_required_text(data["reason"], "reason"),
            claim_key=_optional_text(data["claim_key"]),
            catalog=_optional_text(data["catalog"]),
            entry=_optional_text(data["entry"]),
            invariant=_optional_text(data["invariant"]),
            source_stop_reason=_optional_text(data["source_stop_reason"]),
            created_at=_optional_text(data["created_at"]),
            deduplication_key=_optional_text(data["deduplication_key"]),
        )
    except (KeyError, TypeError, ValueError) as exc:
        raise ValueError("invalid attention event") from exc
    _validate_event(event)
    return event


def _validate_event(event: AttentionEvent) -> None:
    if not isinstance(event, AttentionEvent):
        raise TypeError("event must be an AttentionEvent")


def _required_text(value: object, field: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"{field} is required")
    return value


def _optional_text(value: object) -> str | None:
    if value is not None and (not isinstance(value, str) or not value.strip()):
        raise ValueError("optional attention fields must be strings or null")
    return value


__all__ = ["AttentionStore", "JsonAttentionStore", "SCHEMA_VERSION"]