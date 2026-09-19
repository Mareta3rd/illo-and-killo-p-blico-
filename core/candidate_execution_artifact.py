"""Closed, provider-neutral audit record for a candidate-generation execution.

This artifact records what the external candidate provider was actually asked to
produce, what it returned on each iteration, and what Core evaluated afterwards.
It does not make, change, or reinterpret Core decisions.
"""

from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass, replace
from pathlib import Path
from typing import Any, Mapping, Sequence

from .creative_feedback import build_creative_feedback
from .loop import IterationRecord
from .prompt_compiler import CompiledPrompt


SCHEMA_VERSION = 1
_ALLOWED_DECISIONS = {"continue", "accept", "human_review"}
_ALLOWED_FINAL_STATUSES = {"accepted", "human_review", "max_iterations", "stopped_before_loop"}

_ARTIFACT_KEYS = {
    "schema_version",
    "run_id",
    "provider",
    "model",
    "image",
    "idea",
    "route",
    "compiled_prompt",
    "compiled_prompt_digest",
    "semantic_context_entries",
    "iterations",
    "final_status",
    "stop_reason",
    "core_decision",
}
_ITERATION_KEYS = {
    "iteration",
    "request_prompt",
    "request_prompt_digest",
    "candidate_json",
    "candidate_digest",
    "decision",
    "reason",
}


@dataclass(frozen=True)
class CandidateExecutionIteration:
    """Immutable record of one provider request and Core evaluation."""

    iteration: int
    request_prompt: str
    request_prompt_digest: str
    candidate_json: str
    candidate_digest: str
    decision: str
    reason: str

    def to_dict(self) -> dict[str, Any]:
        return {
            "iteration": self.iteration,
            "request_prompt": self.request_prompt,
            "request_prompt_digest": self.request_prompt_digest,
            "candidate_json": self.candidate_json,
            "candidate_digest": self.candidate_digest,
            "decision": self.decision,
            "reason": self.reason,
        }


@dataclass(frozen=True)
class CandidateExecutionArtifact:
    """Closed historical record of one compiled candidate-generation run."""

    schema_version: int
    run_id: str
    provider: str
    model: str
    image: str
    idea: str
    route: str
    compiled_prompt: str
    compiled_prompt_digest: str
    semantic_context_entries: tuple[str, ...]
    iterations: tuple[CandidateExecutionIteration, ...]
    final_status: str
    stop_reason: str | None
    core_decision: str | None

    def to_dict(self) -> dict[str, Any]:
        return {
            "schema_version": self.schema_version,
            "run_id": self.run_id,
            "provider": self.provider,
            "model": self.model,
            "image": self.image,
            "idea": self.idea,
            "route": self.route,
            "compiled_prompt": self.compiled_prompt,
            "compiled_prompt_digest": self.compiled_prompt_digest,
            "semantic_context_entries": list(self.semantic_context_entries),
            "iterations": [item.to_dict() for item in self.iterations],
            "final_status": self.final_status,
            "stop_reason": self.stop_reason,
            "core_decision": self.core_decision,
        }


def _sha256(value: str) -> str:
    return hashlib.sha256(value.encode("utf-8")).hexdigest()


def _canonical_json(value: Mapping[str, Any]) -> str:
    return json.dumps(
        value,
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
    )


def build_candidate_execution_artifact(
    *,
    run_id: str,
    provider: str,
    model: str,
    image: str,
    idea: str,
    route: str,
    compiled_prompt: CompiledPrompt,
    loop_iterations: Sequence[IterationRecord[dict[str, Any]]],
    initial_candidate: Mapping[str, Any] | None,
    final_status: str,
    stop_reason: str | None,
    core_decision: str | None,
) -> CandidateExecutionArtifact:
    """Capture the exact compiled/request prompts and candidate outputs.

    The function is intentionally observational. It does not call a provider,
    evaluate a candidate, or alter a Core decision.
    """
    for name, value in {
        "run_id": run_id,
        "provider": provider,
        "model": model,
        "image": image,
        "idea": idea,
        "route": route,
    }.items():
        if not isinstance(value, str) or not value.strip():
            raise ValueError(f"{name} is required")

    if not isinstance(compiled_prompt, CompiledPrompt):
        raise TypeError("compiled_prompt must be a CompiledPrompt")
    if final_status not in _ALLOWED_FINAL_STATUSES:
        raise ValueError(f"invalid final_status: {final_status!r}")
    if core_decision is not None and core_decision not in _ALLOWED_DECISIONS:
        raise ValueError(f"invalid core_decision: {core_decision!r}")

    compiled_text = compiled_prompt.render()
    semantic_entries = (
        compiled_prompt.semantic_context.entries
        if compiled_prompt.semantic_context is not None
        else compiled_prompt.context_summary
    )

    previous: dict[str, Any] | None = (
        dict(initial_candidate) if initial_candidate is not None else None
    )
    prompt_for_iteration = compiled_prompt
    iterations: list[CandidateExecutionIteration] = []

    from .groq_qwen_candidate_transport import build_candidate_request_prompt

    for record in loop_iterations:
        if not isinstance(record.iteration, int) or record.iteration < 1:
            raise ValueError("iteration must be a positive integer")
        candidate = record.candidate
        if not isinstance(candidate, dict):
            raise ValueError("loop candidate must be a dictionary")
        candidate_json = _canonical_json(candidate)
        request_prompt = build_candidate_request_prompt(
            prompt_for_iteration,
            record.iteration,
            previous,
        )
        iterations.append(
            CandidateExecutionIteration(
                iteration=record.iteration,
                request_prompt=request_prompt,
                request_prompt_digest=_sha256(request_prompt),
                candidate_json=candidate_json,
                candidate_digest=_sha256(candidate_json),
                decision=record.evaluation.decision,
                reason=record.evaluation.reason,
            )
        )
        creative_feedback = build_creative_feedback(candidate)
        if creative_feedback.guidance:
            prompt_for_iteration = replace(
                prompt_for_iteration,
                iteration_guidance=creative_feedback.guidance,
            )
        previous = candidate

    return CandidateExecutionArtifact(
        schema_version=SCHEMA_VERSION,
        run_id=run_id,
        provider=provider,
        model=model,
        image=image,
        idea=idea,
        route=route,
        compiled_prompt=compiled_text,
        compiled_prompt_digest=_sha256(compiled_text),
        semantic_context_entries=tuple(semantic_entries),
        iterations=tuple(iterations),
        final_status=final_status,
        stop_reason=stop_reason,
        core_decision=core_decision,
    )


def serialize_candidate_execution_artifact(artifact: CandidateExecutionArtifact) -> str:
    """Serialize one candidate execution artifact deterministically."""
    if not isinstance(artifact, CandidateExecutionArtifact):
        raise TypeError("artifact must be a CandidateExecutionArtifact")
    return json.dumps(
        artifact.to_dict(),
        ensure_ascii=False,
        indent=2,
        sort_keys=True,
    ) + "\n"


def deserialize_candidate_execution_artifact(
    payload: str | bytes,
) -> CandidateExecutionArtifact:
    """Load an audit artifact without creating or changing Core decisions."""
    try:
        data = json.loads(payload)
    except (TypeError, ValueError, json.JSONDecodeError) as exc:
        raise ValueError("invalid candidate execution artifact JSON") from exc

    if not isinstance(data, dict) or set(data) != _ARTIFACT_KEYS:
        raise ValueError("candidate execution artifact has an invalid closed schema")
    if data["schema_version"] != SCHEMA_VERSION:
        raise ValueError("unsupported candidate execution artifact schema version")

    for key in ("run_id", "provider", "model", "image", "idea", "route", "compiled_prompt"):
        if not isinstance(data[key], str) or not data[key].strip():
            raise ValueError(f"{key} is required")

    compiled_digest = data["compiled_prompt_digest"]
    if not isinstance(compiled_digest, str) or compiled_digest != _sha256(data["compiled_prompt"]):
        raise ValueError("compiled_prompt_digest does not match compiled_prompt")

    semantic_entries = data["semantic_context_entries"]
    if (
        not isinstance(semantic_entries, list)
        or not all(isinstance(item, str) for item in semantic_entries)
    ):
        raise ValueError("semantic_context_entries must be a string array")

    if data["final_status"] not in _ALLOWED_FINAL_STATUSES:
        raise ValueError("invalid final_status")
    if data["core_decision"] is not None and data["core_decision"] not in _ALLOWED_DECISIONS:
        raise ValueError("invalid core_decision")
    if not isinstance(data["stop_reason"], (str, type(None))):
        raise ValueError("stop_reason must be a string or null")
    if not isinstance(data["iterations"], list):
        raise ValueError("iterations must be an array")

    iterations: list[CandidateExecutionIteration] = []
    seen_iterations: set[int] = set()
    for item in data["iterations"]:
        if not isinstance(item, dict) or set(item) != _ITERATION_KEYS:
            raise ValueError("invalid candidate execution iteration")
        iteration = item["iteration"]
        if not isinstance(iteration, int) or iteration < 1 or iteration in seen_iterations:
            raise ValueError("iteration must be unique and positive")
        for key in ("request_prompt", "request_prompt_digest", "candidate_json", "candidate_digest", "decision", "reason"):
            if not isinstance(item[key], str):
                raise ValueError(f"{key} must be a string")
        if not item["request_prompt"].strip() or not item["candidate_json"].strip():
            raise ValueError("request_prompt and candidate_json are required")
        if item["request_prompt_digest"] != _sha256(item["request_prompt"]):
            raise ValueError("request_prompt_digest does not match request_prompt")
        try:
            candidate = json.loads(item["candidate_json"])
        except (TypeError, ValueError, json.JSONDecodeError) as exc:
            raise ValueError("candidate_json is not valid JSON") from exc
        if not isinstance(candidate, dict):
            raise ValueError("candidate_json must contain an object")
        if _canonical_json(candidate) != item["candidate_json"]:
            raise ValueError("candidate_json is not canonical")
        if item["candidate_digest"] != _sha256(item["candidate_json"]):
            raise ValueError("candidate_digest does not match candidate_json")
        if item["decision"] not in _ALLOWED_DECISIONS:
            raise ValueError("invalid iteration decision")
        iterations.append(
            CandidateExecutionIteration(
                iteration=iteration,
                request_prompt=item["request_prompt"],
                request_prompt_digest=item["request_prompt_digest"],
                candidate_json=item["candidate_json"],
                candidate_digest=item["candidate_digest"],
                decision=item["decision"],
                reason=item["reason"],
            )
        )
        seen_iterations.add(iteration)

    iterations.sort(key=lambda item: item.iteration)
    return CandidateExecutionArtifact(
        schema_version=SCHEMA_VERSION,
        run_id=data["run_id"],
        provider=data["provider"],
        model=data["model"],
        image=data["image"],
        idea=data["idea"],
        route=data["route"],
        compiled_prompt=data["compiled_prompt"],
        compiled_prompt_digest=data["compiled_prompt_digest"],
        semantic_context_entries=tuple(semantic_entries),
        iterations=tuple(iterations),
        final_status=data["final_status"],
        stop_reason=data["stop_reason"],
        core_decision=data["core_decision"],
    )


def write_candidate_execution_artifact(
    path: str | Path,
    artifact: CandidateExecutionArtifact,
) -> None:
    """Persist an audit artifact without adding it to any Core input path."""
    Path(path).write_text(
        serialize_candidate_execution_artifact(artifact),
        encoding="utf-8",
    )


def read_candidate_execution_artifact(path: str | Path) -> CandidateExecutionArtifact:
    """Read and validate one persisted candidate execution artifact."""
    return deserialize_candidate_execution_artifact(Path(path).read_text(encoding="utf-8"))


__all__ = [
    "CandidateExecutionArtifact",
    "CandidateExecutionIteration",
    "build_candidate_execution_artifact",
    "deserialize_candidate_execution_artifact",
    "read_candidate_execution_artifact",
    "serialize_candidate_execution_artifact",
    "write_candidate_execution_artifact",
]
