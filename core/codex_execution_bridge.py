"""Provider-neutral execution bridge for controlled Codex tasks."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Protocol

from .codex_task import CodexTask, CodexTaskResult, validate_codex_task_result


class CodexTransport(Protocol):
    """Transport capable of executing one already-approved Codex task."""

    def execute(self, task: CodexTask) -> CodexTaskResult:
        ...


@dataclass(frozen=True)
class CodexExecutionBridge:
    """Enforce the task contract before and after a Codex transport call."""

    transport: CodexTransport

    def execute(self, task: CodexTask, *, human_approved: bool) -> CodexTaskResult:
        """Execute a bounded task only after explicit human approval."""
        if not isinstance(task, CodexTask):
            raise TypeError("task must be a CodexTask")
        if not isinstance(human_approved, bool):
            raise TypeError("human_approved must be a boolean")

        if task.human_approval_required and not human_approved:
            result = CodexTaskResult(
                task_id=task.task_id,
                task_digest=task.digest(),
                status="blocked",
                summary="Execution blocked pending explicit human approval.",
                changed_files=(),
                tests_run=(),
                blockers=("human_approval_required",),
            )
            validate_codex_task_result(task, result)
            return result

        result = self.transport.execute(task)
        if not isinstance(result, CodexTaskResult):
            raise TypeError("Codex transport must return a CodexTaskResult")
        validate_codex_task_result(task, result)
        return result


__all__ = [
    "CodexExecutionBridge",
    "CodexTransport",
]
