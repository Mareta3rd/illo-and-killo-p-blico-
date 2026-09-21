"""Closed task contract for delegating controlled work to Codex.

Codex is an execution agent, not a Core authority. This module defines the
information required to issue a bounded task and to record its result without
granting the executor canon or final-decision authority.
"""

from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass
from pathlib import PurePosixPath
from typing import Any, Sequence


SCHEMA_VERSION = 1
TASK_MODES = {"analysis", "implementation", "repair", "improvement"}
RESULT_STATUSES = {"completed", "needs_review", "blocked", "failed"}
ISSUERS = {"human", "core", "orchestrator", "reviewer", "digital_ricard"}
REQUIRED_AUTHORITY = "execution_only"


def _require_nonempty_string(name: str, value: Any) -> str:
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"{name} must be a non-empty string")
    return value.strip()


def _normalize_string_sequence(name: str, values: Sequence[str], *, require_one: bool) -> tuple[str, ...]:
    if not isinstance(values, (list, tuple)):
        raise TypeError(f"{name} must be a list or tuple")
    normalized = tuple(_require_nonempty_string(f"{name}[{index}]", value) for index, value in enumerate(values))
    if require_one and not normalized:
        raise ValueError(f"{name} must contain at least one item")
    if len(set(normalized)) != len(normalized):
        raise ValueError(f"{name} must not contain duplicates")
    return normalized


def _normalize_repo_path(value: str) -> str:
    path = _require_nonempty_string("repository path", value)
    pure = PurePosixPath(path)
    if pure.is_absolute() or ".." in pure.parts:
        raise ValueError(f"repository path must stay inside the repository: {path!r}")
    if path in {".", ""}:
        raise ValueError("repository path must identify a file or directory")
    return path.rstrip("/") if path != "/" else path


def _path_covers(scope: str, candidate: str) -> bool:
    scope_norm = scope.rstrip("/")
    candidate_norm = candidate.rstrip("/")
    return candidate_norm == scope_norm or candidate_norm.startswith(scope_norm + "/")


def _validate_disjoint_scopes(allowed: Sequence[str], protected: Sequence[str]) -> None:
    for allowed_path in allowed:
        for protected_path in protected:
            if _path_covers(allowed_path, protected_path) or _path_covers(protected_path, allowed_path):
                raise ValueError(
                    "allowed_paths and protected_paths overlap: "
                    f"{allowed_path!r} vs {protected_path!r}"
                )


def _sha256(value: str) -> str:
    return hashlib.sha256(value.encode("utf-8")).hexdigest()


@dataclass(frozen=True)
class CodexTask:
    """A bounded, auditable request for Codex work."""

    task_id: str
    issuer: str
    mode: str
    objective: str
    context: str
    allowed_paths: tuple[str, ...]
    protected_paths: tuple[str, ...]
    constraints: tuple[str, ...]
    acceptance_criteria: tuple[str, ...]
    verification_commands: tuple[str, ...]
    base_ref: str
    base_commit: str | None = None
    authority: str = REQUIRED_AUTHORITY
    human_approval_required: bool = True

    def __post_init__(self) -> None:
        _require_nonempty_string("task_id", self.task_id)
        if self.issuer not in ISSUERS:
            raise ValueError(f"unsupported issuer: {self.issuer!r}")
        if self.mode not in TASK_MODES:
            raise ValueError(f"unsupported task mode: {self.mode!r}")
        _require_nonempty_string("objective", self.objective)
        _require_nonempty_string("context", self.context)
        if self.authority != REQUIRED_AUTHORITY:
            raise ValueError("Codex tasks cannot hold Core decision authority")
        if self.human_approval_required is not True:
            raise ValueError("Codex tasks require explicit human approval")
        if not isinstance(self.human_approval_required, bool):
            raise TypeError("human_approval_required must be a boolean")
        allowed = tuple(_normalize_repo_path(path) for path in self.allowed_paths)
        protected = tuple(_normalize_repo_path(path) for path in self.protected_paths)
        constraints = _normalize_string_sequence("constraints", self.constraints, require_one=False)
        acceptance = _normalize_string_sequence("acceptance_criteria", self.acceptance_criteria, require_one=True)
        verification = _normalize_string_sequence("verification_commands", self.verification_commands, require_one=True)
        _require_nonempty_string("base_ref", self.base_ref)
        if self.base_commit is not None:
            _require_nonempty_string("base_commit", self.base_commit)
        _validate_disjoint_scopes(allowed, protected)
        if len(set(allowed)) != len(allowed):
            raise ValueError("allowed_paths must not contain duplicates")
        if len(set(protected)) != len(protected):
            raise ValueError("protected_paths must not contain duplicates")
        object.__setattr__(self, "allowed_paths", allowed)
        object.__setattr__(self, "protected_paths", protected)
        object.__setattr__(self, "constraints", constraints)
        object.__setattr__(self, "acceptance_criteria", acceptance)
        object.__setattr__(self, "verification_commands", verification)

    def to_dict(self) -> dict[str, Any]:
        return {
            "schema_version": SCHEMA_VERSION,
            "task_id": self.task_id,
            "issuer": self.issuer,
            "mode": self.mode,
            "objective": self.objective,
            "context": self.context,
            "allowed_paths": list(self.allowed_paths),
            "protected_paths": list(self.protected_paths),
            "constraints": list(self.constraints),
            "acceptance_criteria": list(self.acceptance_criteria),
            "verification_commands": list(self.verification_commands),
            "base_ref": self.base_ref,
            "base_commit": self.base_commit,
            "authority": self.authority,
            "human_approval_required": self.human_approval_required,
        }

    def digest(self) -> str:
        return _sha256(serialize_codex_task(self))


@dataclass(frozen=True)
class CodexTaskResult:
    """Auditable result returned by a Codex task execution."""

    task_id: str
    task_digest: str
    status: str
    summary: str
    changed_files: tuple[str, ...]
    tests_run: tuple[str, ...]
    blockers: tuple[str, ...] = ()
    diff_digest: str | None = None

    def __post_init__(self) -> None:
        _require_nonempty_string("task_id", self.task_id)
        _require_nonempty_string("task_digest", self.task_digest)
        if self.status not in RESULT_STATUSES:
            raise ValueError(f"unsupported result status: {self.status!r}")
        _require_nonempty_string("summary", self.summary)
        changed = tuple(_normalize_repo_path(path) for path in self.changed_files)
        tests = _normalize_string_sequence("tests_run", self.tests_run, require_one=False)
        blockers = _normalize_string_sequence("blockers", self.blockers, require_one=False)
        if len(set(changed)) != len(changed):
            raise ValueError("changed_files must not contain duplicates")
        if self.diff_digest is not None:
            _require_nonempty_string("diff_digest", self.diff_digest)
        object.__setattr__(self, "changed_files", changed)
        object.__setattr__(self, "tests_run", tests)
        object.__setattr__(self, "blockers", blockers)

    def to_dict(self) -> dict[str, Any]:
        return {
            "schema_version": SCHEMA_VERSION,
            "task_id": self.task_id,
            "task_digest": self.task_digest,
            "status": self.status,
            "summary": self.summary,
            "changed_files": list(self.changed_files),
            "tests_run": list(self.tests_run),
            "blockers": list(self.blockers),
            "diff_digest": self.diff_digest,
        }


_TASK_KEYS = {
    "schema_version",
    "task_id",
    "issuer",
    "mode",
    "objective",
    "context",
    "allowed_paths",
    "protected_paths",
    "constraints",
    "acceptance_criteria",
    "verification_commands",
    "base_ref",
    "base_commit",
    "authority",
    "human_approval_required",
}

_RESULT_KEYS = {
    "schema_version",
    "task_id",
    "task_digest",
    "status",
    "summary",
    "changed_files",
    "tests_run",
    "blockers",
    "diff_digest",
}


def serialize_codex_task(task: CodexTask) -> str:
    """Serialize a task deterministically."""
    if not isinstance(task, CodexTask):
        raise TypeError("task must be a CodexTask")
    return json.dumps(task.to_dict(), ensure_ascii=False, sort_keys=True, separators=(",", ":"))


def deserialize_codex_task(payload: str | bytes) -> CodexTask:
    """Deserialize and validate a closed Codex task contract."""
    try:
        data = json.loads(payload)
    except (TypeError, ValueError, json.JSONDecodeError) as exc:
        raise ValueError("invalid Codex task JSON") from exc
    if not isinstance(data, dict) or set(data) != _TASK_KEYS:
        raise ValueError("Codex task has an invalid closed schema")
    if data["schema_version"] != SCHEMA_VERSION:
        raise ValueError("unsupported Codex task schema version")
    return CodexTask(
        task_id=data["task_id"],
        issuer=data["issuer"],
        mode=data["mode"],
        objective=data["objective"],
        context=data["context"],
        allowed_paths=tuple(data["allowed_paths"]),
        protected_paths=tuple(data["protected_paths"]),
        constraints=tuple(data["constraints"]),
        acceptance_criteria=tuple(data["acceptance_criteria"]),
        verification_commands=tuple(data["verification_commands"]),
        base_ref=data["base_ref"],
        base_commit=data["base_commit"],
        authority=data["authority"],
        human_approval_required=data["human_approval_required"],
    )


def validate_codex_task_result(task: CodexTask, result: CodexTaskResult) -> None:
    """Ensure an execution result stayed inside the task's authority and scope."""
    if not isinstance(task, CodexTask):
        raise TypeError("task must be a CodexTask")
    if not isinstance(result, CodexTaskResult):
        raise TypeError("result must be a CodexTaskResult")
    if result.task_id != task.task_id:
        raise ValueError("result task_id does not match task")
    if result.task_digest != task.digest():
        raise ValueError("result task_digest does not match task")

    for changed_path in result.changed_files:
        if any(_path_covers(protected, changed_path) for protected in task.protected_paths):
            raise ValueError(f"Codex result changed protected path: {changed_path!r}")
        if not any(_path_covers(allowed, changed_path) for allowed in task.allowed_paths):
            raise ValueError(f"Codex result changed path outside allowed scope: {changed_path!r}")

    if task.mode == "analysis" and result.changed_files:
        raise ValueError("analysis tasks must not report changed files")


def serialize_codex_task_result(result: CodexTaskResult) -> str:
    """Serialize a Codex result deterministically."""
    if not isinstance(result, CodexTaskResult):
        raise TypeError("result must be a CodexTaskResult")
    return json.dumps(result.to_dict(), ensure_ascii=False, sort_keys=True, separators=(",", ":"))


def deserialize_codex_task_result(payload: str | bytes) -> CodexTaskResult:
    """Deserialize and validate a closed Codex result contract."""
    try:
        data = json.loads(payload)
    except (TypeError, ValueError, json.JSONDecodeError) as exc:
        raise ValueError("invalid Codex result JSON") from exc
    if not isinstance(data, dict) or set(data) != _RESULT_KEYS:
        raise ValueError("Codex result has an invalid closed schema")
    if data["schema_version"] != SCHEMA_VERSION:
        raise ValueError("unsupported Codex result schema version")
    return CodexTaskResult(
        task_id=data["task_id"],
        task_digest=data["task_digest"],
        status=data["status"],
        summary=data["summary"],
        changed_files=tuple(data["changed_files"]),
        tests_run=tuple(data["tests_run"]),
        blockers=tuple(data["blockers"]),
        diff_digest=data["diff_digest"],
    )


def codex_task_contract() -> dict[str, Any]:
    """Return the provider-neutral JSON schema for a Codex task."""
    return {
        "type": "object",
        "additionalProperties": False,
        "properties": {
            "schema_version": {"type": "integer", "const": SCHEMA_VERSION},
            "task_id": {"type": "string"},
            "issuer": {"type": "string", "enum": sorted(ISSUERS)},
            "mode": {"type": "string", "enum": sorted(TASK_MODES)},
            "objective": {"type": "string"},
            "context": {"type": "string"},
            "allowed_paths": {"type": "array", "items": {"type": "string"}},
            "protected_paths": {"type": "array", "items": {"type": "string"}},
            "constraints": {"type": "array", "items": {"type": "string"}},
            "acceptance_criteria": {"type": "array", "items": {"type": "string"}, "minItems": 1},
            "verification_commands": {"type": "array", "items": {"type": "string"}, "minItems": 1},
            "base_ref": {"type": "string"},
            "base_commit": {"type": ["string", "null"]},
            "authority": {"type": "string", "const": REQUIRED_AUTHORITY},
            "human_approval_required": {"type": "boolean", "const": True},
        },
        "required": sorted(_TASK_KEYS),
    }


def codex_task_result_contract() -> dict[str, Any]:
    """Return the JSON schema for a Codex execution result."""
    return {
        "type": "object",
        "additionalProperties": False,
        "properties": {
            "schema_version": {"type": "integer", "const": SCHEMA_VERSION},
            "task_id": {"type": "string"},
            "task_digest": {"type": "string"},
            "status": {"type": "string", "enum": sorted(RESULT_STATUSES)},
            "summary": {"type": "string"},
            "changed_files": {"type": "array", "items": {"type": "string"}},
            "tests_run": {"type": "array", "items": {"type": "string"}},
            "blockers": {"type": "array", "items": {"type": "string"}},
            "diff_digest": {"type": ["string", "null"]},
        },
        "required": sorted(_RESULT_KEYS),
    }


__all__ = [
    "CodexTask",
    "CodexTaskResult",
    "ISSUERS",
    "RESULT_STATUSES",
    "TASK_MODES",
    "codex_task_contract",
    "codex_task_result_contract",
    "deserialize_codex_task",
    "deserialize_codex_task_result",
    "serialize_codex_task",
    "serialize_codex_task_result",
    "validate_codex_task_result",
]
