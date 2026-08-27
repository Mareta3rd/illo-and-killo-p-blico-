"""Closed, provider-neutral JSON records for completed evidence executions."""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Mapping

from .evidence_snapshot import EvidenceSnapshot
from .evidence_state import EvidenceState
from .provider_evidence_observation import ProviderEvidenceObservation


SCHEMA_VERSION = 1
_CORE_DECISIONS = {"accept", "continue", "human_review"}
_ARTIFACT_KEYS = {
    "schema_version",
    "run_id",
    "provider",
    "model",
    "image",
    "claims",
    "canonical_evaluations",
    "core_decision",
}
_CLAIM_KEYS = {
    "claim_key",
    "state",
    "statement",
    "supporting_sources",
    "contradicting_sources",
}
_EVALUATION_KEYS = {"catalog", "entry", "invariant", "decision"}


@dataclass(frozen=True)
class ExecutionArtifactClaim:
    claim_key: str
    state: EvidenceState
    statement: str
    supporting_sources: tuple[str, ...]
    contradicting_sources: tuple[str, ...]


@dataclass(frozen=True)
class ExecutionArtifactEvaluation:
    catalog: str
    entry: str
    invariant: str
    decision: str


@dataclass(frozen=True)
class ExecutionArtifact:
    """Frozen historical data; loading it never evaluates or decides anything."""

    schema_version: int
    run_id: str
    provider: str
    model: str
    image: str
    claims: tuple[ExecutionArtifactClaim, ...]
    canonical_evaluations: tuple[ExecutionArtifactEvaluation, ...]
    core_decision: str | None

    def to_dict(self) -> dict[str, Any]:
        return {
            "schema_version": self.schema_version,
            "run_id": self.run_id,
            "provider": self.provider,
            "model": self.model,
            "image": self.image,
            "claims": [
                {
                    "claim_key": claim.claim_key,
                    "state": claim.state.value,
                    "statement": claim.statement,
                    "supporting_sources": list(claim.supporting_sources),
                    "contradicting_sources": list(claim.contradicting_sources),
                }
                for claim in self.claims
            ],
            "canonical_evaluations": [
                {
                    "catalog": evaluation.catalog,
                    "entry": evaluation.entry,
                    "invariant": evaluation.invariant,
                    "decision": evaluation.decision,
                }
                for evaluation in self.canonical_evaluations
            ],
            "core_decision": self.core_decision,
        }


def build_execution_artifact(
    observation: ProviderEvidenceObservation,
    snapshot: EvidenceSnapshot,
    *,
    model: str,
    image: str,
    core_decision: str | None,
) -> ExecutionArtifact:
    """Capture already-produced observation/snapshot data without re-evaluation."""
    if not isinstance(observation, ProviderEvidenceObservation):
        raise TypeError("observation must be a ProviderEvidenceObservation")
    if not isinstance(snapshot, EvidenceSnapshot):
        raise TypeError("snapshot must be an EvidenceSnapshot")
    if not isinstance(model, str) or not model.strip():
        raise ValueError("model is required")
    if not isinstance(image, str) or not image.strip():
        raise ValueError("image is required")
    if core_decision is not None and core_decision not in _CORE_DECISIONS:
        raise ValueError("invalid Core decision")

    claims = tuple(
        ExecutionArtifactClaim(
            claim_key=record.claim_key,
            state=record.state,
            statement=record.statement,
            supporting_sources=record.supporting_sources,
            contradicting_sources=record.contradicting_sources,
        )
        for record in sorted(observation.records, key=lambda item: item.claim_key)
    )
    evaluations = tuple(
        ExecutionArtifactEvaluation(
            catalog=evaluation.catalog,
            entry=evaluation.entry,
            invariant=evaluation.invariant,
            decision=evaluation.evaluation.decision,
        )
        for evaluation in sorted(
            snapshot.canonical_evaluations,
            key=lambda item: (item.catalog, item.entry, item.invariant),
        )
    )
    snapshot_claim_keys = set(snapshot.claims)
    if {claim.claim_key for claim in claims} != snapshot_claim_keys:
        raise ValueError("observation and snapshot claims do not match")
    return ExecutionArtifact(
        schema_version=SCHEMA_VERSION,
        run_id=observation.run_id,
        provider=observation.provider,
        model=model,
        image=image,
        claims=claims,
        canonical_evaluations=evaluations,
        core_decision=core_decision,
    )


def serialize_execution_artifact(artifact: ExecutionArtifact) -> str:
    """Serialize one artifact deterministically as UTF-8-compatible JSON text."""
    if not isinstance(artifact, ExecutionArtifact):
        raise TypeError("artifact must be an ExecutionArtifact")
    return json.dumps(
        artifact.to_dict(),
        ensure_ascii=False,
        indent=2,
        sort_keys=True,
    ) + "\n"


def deserialize_execution_artifact(payload: str | bytes) -> ExecutionArtifact:
    """Load historical data only; this function never creates Core decisions."""
    try:
        data = json.loads(payload)
    except (TypeError, ValueError, json.JSONDecodeError) as exc:
        raise ValueError("invalid execution artifact JSON") from exc
    if not isinstance(data, dict) or set(data) != _ARTIFACT_KEYS:
        raise ValueError("execution artifact has an invalid closed schema")
    if data["schema_version"] != SCHEMA_VERSION:
        raise ValueError("unsupported execution artifact schema version")
    for key in ("run_id", "provider", "model", "image"):
        if not isinstance(data[key], str) or not data[key].strip():
            raise ValueError(f"{key} is required")
    if data["core_decision"] is not None and data["core_decision"] not in _CORE_DECISIONS:
        raise ValueError("invalid Core decision")
    if not isinstance(data["claims"], list) or not isinstance(data["canonical_evaluations"], list):
        raise ValueError("claims and canonical_evaluations must be arrays")

    claims: list[ExecutionArtifactClaim] = []
    seen_keys: set[str] = set()
    for item in data["claims"]:
        if not isinstance(item, dict) or set(item) != _CLAIM_KEYS:
            raise ValueError("invalid execution artifact claim")
        claim_key = item["claim_key"]
        statement = item["statement"]
        if not isinstance(claim_key, str) or not claim_key.strip() or claim_key in seen_keys:
            raise ValueError("claim_key must be unique and non-empty")
        if not isinstance(statement, str) or not statement.strip():
            raise ValueError("claim statement is required")
        try:
            state = EvidenceState(item["state"])
        except (KeyError, TypeError, ValueError) as exc:
            raise ValueError("invalid evidence state") from exc
        supporting = _sources(item["supporting_sources"])
        contradicting = _sources(item["contradicting_sources"])
        claims.append(ExecutionArtifactClaim(claim_key, state, statement, supporting, contradicting))
        seen_keys.add(claim_key)

    evaluations: list[ExecutionArtifactEvaluation] = []
    for item in data["canonical_evaluations"]:
        if not isinstance(item, dict) or set(item) != _EVALUATION_KEYS:
            raise ValueError("invalid canonical evaluation")
        values = [item[key] for key in ("catalog", "entry", "invariant")]
        if not all(isinstance(value, str) and value.strip() for value in values):
            raise ValueError("canonical evaluation identity is required")
        if item["decision"] not in {"pass", "fail", "unknown"}:
            raise ValueError("invalid canonical evaluation decision")
        evaluations.append(ExecutionArtifactEvaluation(*values, item["decision"]))

    return ExecutionArtifact(
        schema_version=SCHEMA_VERSION,
        run_id=data["run_id"],
        provider=data["provider"],
        model=data["model"],
        image=data["image"],
        claims=tuple(claims),
        canonical_evaluations=tuple(evaluations),
        core_decision=data["core_decision"],
    )


def write_execution_artifact(path: str | Path, artifact: ExecutionArtifact) -> None:
    """Persist an artifact without adding it to any Core input path."""
    Path(path).write_text(serialize_execution_artifact(artifact), encoding="utf-8")


def read_execution_artifact(path: str | Path) -> ExecutionArtifact:
    """Read and validate one persisted historical artifact."""
    return deserialize_execution_artifact(Path(path).read_text(encoding="utf-8"))


def _sources(value: Any) -> tuple[str, ...]:
    if not isinstance(value, list) or not all(isinstance(item, str) and item.strip() for item in value):
        raise ValueError("sources must be non-empty strings")
    return tuple(value)


__all__ = [
    "ExecutionArtifact",
    "ExecutionArtifactClaim",
    "ExecutionArtifactEvaluation",
    "build_execution_artifact",
    "deserialize_execution_artifact",
    "read_execution_artifact",
    "serialize_execution_artifact",
    "write_execution_artifact",
]