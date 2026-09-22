"""Real Codex CLI transport for the provider-neutral execution bridge."""

from __future__ import annotations

import hashlib
import json
import subprocess
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from .codex_task import CodexTask, CodexTaskResult


def _run_git(root: Path, *args: str) -> str:
    completed = subprocess.run(
        ["git", *args],
        cwd=root,
        check=True,
        capture_output=True,
        text=True,
    )
    return completed.stdout.strip()


def _current_branch(root: Path) -> str:
    return _run_git(root, "rev-parse", "--abbrev-ref", "HEAD")


def _current_commit(root: Path) -> str:
    return _run_git(root, "rev-parse", "HEAD")


def _working_tree_is_clean(root: Path) -> bool:
    return not _run_git(root, "status", "--porcelain", "--untracked-files=all")


def _changed_files(root: Path, base_commit: str) -> tuple[str, ...]:
    names = set(filter(None, _run_git(root, "diff", "--name-only", base_commit).splitlines()))
    names.update(
        filter(
            None,
            _run_git(root, "ls-files", "--others", "--exclude-standard").splitlines(),
        )
    )
    return tuple(sorted(names))


def _diff_digest(root: Path, base_commit: str, changed_files: tuple[str, ...]) -> str | None:
    if not changed_files:
        return None

    diff = subprocess.run(
        ["git", "diff", "--binary", base_commit],
        cwd=root,
        check=True,
        capture_output=True,
    ).stdout

    payload = bytearray(diff)
    tracked = set(_run_git(root, "ls-files").splitlines())
    for relative_path in changed_files:
        if relative_path in tracked:
            continue
        path = root / relative_path
        if path.is_file():
            payload.extend(relative_path.encode("utf-8"))
            payload.extend(b"\0")
            payload.extend(path.read_bytes())
            payload.extend(b"\0")

    return hashlib.sha256(bytes(payload)).hexdigest()


def _build_prompt(task: CodexTask) -> str:
    allowed = "\n".join(f"- {item}" for item in task.allowed_paths) or "- none (read-only analysis)"
    protected = "\n".join(f"- {item}" for item in task.protected_paths) or "- none explicitly listed"
    constraints = "\n".join(f"- {item}" for item in task.constraints) or "- none"
    acceptance = "\n".join(f"- {item}" for item in task.acceptance_criteria)
    verification = "\n".join(f"- {item}" for item in task.verification_commands)

    return (
        f"You are executing a controlled Codex task issued by {task.issuer}.\n\n"
        "Authority: execution_only. Human approval has already been verified by the host bridge.\n"
        "Do not redefine canon, Core authority, or task scope.\n"
        "Do not commit changes. Return a concise final summary of what you actually did.\n\n"
        f"TASK ID: {task.task_id}\n"
        f"MODE: {task.mode}\n\n"
        f"OBJECTIVE:\n{task.objective}\n\n"
        f"CONTEXT:\n{task.context}\n\n"
        f"ALLOWED PATHS:\n{allowed}\n\n"
        f"PROTECTED PATHS:\n{protected}\n\n"
        f"CONSTRAINTS:\n{constraints}\n\n"
        f"ACCEPTANCE CRITERIA:\n{acceptance}\n\n"
        f"VERIFICATION COMMANDS:\n{verification}\n\n"
        "Before finishing, inspect your changes and verify the acceptance criteria."
    )


def _parse_jsonl(stdout: str) -> tuple[list[dict[str, Any]], str | None, list[str]]:
    events: list[dict[str, Any]] = []
    messages: list[str] = []
    errors: list[str] = []

    for line in stdout.splitlines():
        if not line.strip():
            continue
        try:
            event = json.loads(line)
        except json.JSONDecodeError:
            errors.append("codex emitted a non-JSON line")
            continue
        if not isinstance(event, dict):
            errors.append("codex emitted a non-object JSON event")
            continue

        events.append(event)
        item = event.get("item")
        if isinstance(item, dict) and item.get("type") == "agent_message":
            text = item.get("text")
            if isinstance(text, str) and text.strip():
                messages.append(text.strip())

    return events, (messages[-1] if messages else None), errors


def _tests_from_events(events: list[dict[str, Any]], task: CodexTask) -> tuple[str, ...]:
    commands: set[str] = set()
    for event in events:
        if event.get("type") != "item.completed":
            continue
        item = event.get("item")
        if not isinstance(item, dict) or item.get("type") != "command_execution":
            continue
        command = item.get("command")
        if not isinstance(command, str):
            continue
        if any(expected in command for expected in task.verification_commands):
            commands.add(command)
    return tuple(sorted(commands))


@dataclass(frozen=True)
class CodexCliTransport:
    """Execute Codex CLI non-interactively and translate its run into a task result."""

    root: str | Path = "."
    executable: str = "codex"
    trace_path: str | Path | None = None
    timeout_seconds: int = 1800

    def execute(self, task: CodexTask) -> CodexTaskResult:
        root = Path(self.root).resolve()
        if not root.is_dir():
            raise ValueError("Codex CLI root must be an existing directory")

        if _current_branch(root) != task.base_ref:
            raise RuntimeError("repository branch does not match Codex task base_ref")

        current_commit = _current_commit(root)
        if task.base_commit is not None and current_commit != task.base_commit:
            raise RuntimeError("repository HEAD does not match Codex task base_commit")

        if not _working_tree_is_clean(root):
            raise RuntimeError("Codex CLI transport requires a clean working tree")

        sandbox = "read-only" if task.mode == "analysis" else "workspace-write"
        command = [
            self.executable,
            "exec",
            "--json",
            "--ephemeral",
            "--sandbox",
            sandbox,
            "-a",
            "never",
            _build_prompt(task),
        ]

        try:
            completed = subprocess.run(
                command,
                cwd=root,
                capture_output=True,
                text=True,
                timeout=self.timeout_seconds,
                check=False,
            )
        except FileNotFoundError:
            return CodexTaskResult(
                task_id=task.task_id,
                task_digest=task.digest(),
                status="failed",
                summary="Codex executable was not found.",
                changed_files=(),
                tests_run=(),
                blockers=("codex_executable_not_found",),
            )
        except subprocess.TimeoutExpired:
            return CodexTaskResult(
                task_id=task.task_id,
                task_digest=task.digest(),
                status="failed",
                summary="Codex execution timed out.",
                changed_files=(),
                tests_run=(),
                blockers=("codex_execution_timeout",),
            )

        if self.trace_path is not None:
            trace = Path(self.trace_path)
            trace.parent.mkdir(parents=True, exist_ok=True)
            trace.write_text(
                json.dumps(
                    {"stdout": completed.stdout, "stderr": completed.stderr},
                    ensure_ascii=False,
                    indent=2,
                ),
                encoding="utf-8",
            )

        events, final_message, parse_errors = _parse_jsonl(completed.stdout)
        changed_files = _changed_files(root, current_commit)
        diff_digest = _diff_digest(root, current_commit, changed_files)
        tests_run = _tests_from_events(events, task)

        blockers = list(parse_errors)
        if completed.stderr.strip():
            blockers.append("codex_stderr:" + completed.stderr.strip()[-4000:])
        if completed.returncode != 0:
            blockers.append(f"codex_exit_code:{completed.returncode}")
        if task.mode == "analysis" and changed_files:
            blockers.append("analysis_task_changed_files")

        if completed.returncode == 0 and not blockers:
            status = "completed"
            summary = final_message or "Codex completed without a final agent message."
        else:
            status = "failed"
            summary = final_message or "Codex execution did not complete successfully."

        return CodexTaskResult(
            task_id=task.task_id,
            task_digest=task.digest(),
            status=status,
            summary=summary,
            changed_files=changed_files,
            tests_run=tests_run,
            blockers=tuple(blockers),
            diff_digest=diff_digest,
        )


__all__ = ["CodexCliTransport"]
