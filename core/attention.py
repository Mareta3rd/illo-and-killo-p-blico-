"""Pure operational translation of application results into human attention."""

from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass
from enum import Enum

from .application import ApplicationResult
from .evidence_state import EvidenceState


class AttentionSeverity(str, Enum):
    INFO = "INFO"
    ATTENTION = "ATTENTION"
    CRITICAL = "CRITICAL"


class AttentionCategory(str, Enum):
    CORE_HUMAN_REVIEW = "CORE_HUMAN_REVIEW"
    EVIDENCE_UNKNOWN = "EVIDENCE_UNKNOWN"
    EVIDENCE_CONFLICT = "EVIDENCE_CONFLICT"
    EVIDENCE_MISSING = "EVIDENCE_MISSING"
    CANON_REVIEW = "CANON_REVIEW"
    PROVIDER_FAILURE = "PROVIDER_FAILURE"
    ARTIFACT_FAILURE = "ARTIFACT_FAILURE"
    SYSTEM_ERROR = "SYSTEM_ERROR"


class AttentionStatus(str, Enum):
    PENDING = "PENDING"
    ACKNOWLEDGED = "ACKNOWLEDGED"
    RESOLVED = "RESOLVED"
    DISMISSED = "DISMISSED"


@dataclass(frozen=True)
class AttentionEvent:
    event_id: str
    run_id: str
    severity: AttentionSeverity
    category: AttentionCategory
    status: AttentionStatus
    reason: str
    claim_key: str | None = None
    catalog: str | None = None
    entry: str | None = None
    invariant: str | None = None
    source_stop_reason: str | None = None
    created_at: str | None = None
    deduplication_key: str | None = None

    def __post_init__(self) -> None:
        if not self.run_id.strip():
            raise ValueError("run_id is required")
        if not self.event_id.strip():
            raise ValueError("event_id is required")
        if not self.reason.strip():
            raise ValueError("reason is required")


def build_attention_events(result: ApplicationResult) -> tuple[AttentionEvent, ...]:
    """Translate an application result without executing or mutating anything."""
    if not isinstance(result, ApplicationResult):
        raise TypeError("result must be an ApplicationResult")

    events: list[AttentionEvent] = []
    stop_reason = result.stop_reason
    core_decision = _core_decision(result)
    core_reason = _core_reason(result)
    unknown_records = [
        record
        for record in (result.observation.records if result.observation is not None else ())
        if record.state is EvidenceState.UNKNOWN
    ]
    conflict = (
        core_decision == "human_review"
        and core_reason.startswith("conflicting candidate/evidence checks:")
    )
    unknown_caused_review = (
        core_decision == "human_review"
        and core_reason.startswith("evidence claims remain unknown:")
    )

    if result.artifact_error:
        events.append(_event(
            result,
            AttentionSeverity.CRITICAL,
            AttentionCategory.ARTIFACT_FAILURE,
            result.artifact_error,
            source_stop_reason=stop_reason,
        ))

    if stop_reason and stop_reason.startswith("external_evidence_provider_failed"):
        events.append(_event(
            result,
            AttentionSeverity.CRITICAL,
            AttentionCategory.PROVIDER_FAILURE,
            stop_reason,
            source_stop_reason=stop_reason,
        ))
    elif conflict:
        # Temporary compatibility with the current Core API; a future reason_code can replace text matching.
        events.append(_event(
            result,
            AttentionSeverity.ATTENTION,
            AttentionCategory.EVIDENCE_CONFLICT,
            core_reason,
            source_stop_reason=stop_reason,
        ))
    if result.core is not None and core_decision == "human_review" and not conflict and not unknown_caused_review:
        events.append(_event(
            result,
            AttentionSeverity.ATTENTION,
            AttentionCategory.CORE_HUMAN_REVIEW,
            core_reason,
            source_stop_reason=stop_reason,
        ))

    for record in unknown_records:
        events.append(_event(
            result,
            AttentionSeverity.ATTENTION,
            AttentionCategory.EVIDENCE_UNKNOWN,
            record.statement,
            claim_key=record.claim_key,
            source_stop_reason=stop_reason,
        ))

    return tuple(events)


def _event(
    result: ApplicationResult,
    severity: AttentionSeverity,
    category: AttentionCategory,
    reason: str,
    *,
    claim_key: str | None = None,
    source_stop_reason: str | None = None,
) -> AttentionEvent:
    catalog = entry = invariant = None
    if claim_key is not None and claim_key.count("/") == 2:
        catalog, entry, invariant = claim_key.split("/")
    identity = {
        "category": category.value,
        "claim_key": claim_key,
        "catalog": catalog,
        "entry": entry,
        "invariant": invariant,
        "reason": reason,
    }
    stable = json.dumps(identity, ensure_ascii=False, sort_keys=True)
    deduplication_key = hashlib.sha256(stable.encode("utf-8")).hexdigest()
    event_id = hashlib.sha256(
        json.dumps({"run_id": result.run_id, **identity}, ensure_ascii=False, sort_keys=True).encode("utf-8")
    ).hexdigest()
    return AttentionEvent(
        event_id=event_id,
        run_id=result.run_id,
        severity=severity,
        category=category,
        status=AttentionStatus.PENDING,
        reason=reason,
        claim_key=claim_key,
        catalog=catalog,
        entry=entry,
        invariant=invariant,
        source_stop_reason=source_stop_reason,
        deduplication_key=deduplication_key,
    )


def _core_decision(result: ApplicationResult) -> str | None:
    if result.core is None:
        return None
    if result.core.loop is not None and result.core.loop.iterations:
        return result.core.loop.iterations[-1].evaluation.decision
    if result.core.pipeline.evaluation is not None:
        return result.core.pipeline.evaluation.evaluation.decision
    return None


def _core_reason(result: ApplicationResult) -> str:
    if result.core is not None and result.core.pipeline.evaluation is not None:
        return result.core.pipeline.evaluation.evaluation.reason
    if result.core is not None and result.core.stop_reason:
        return result.core.stop_reason
    return "Core requires human review"


__all__ = [
    "AttentionCategory",
    "AttentionEvent",
    "AttentionSeverity",
    "AttentionStatus",
    "build_attention_events",
]