#!/usr/bin/env python3
"""Run the first explicit human-approved, bounded Codex write smoke test."""

from __future__ import annotations

import argparse
import json
import subprocess
from pathlib import Path

from core.codex_cli_transport import CodexCliTransport
from core.codex_execution_bridge import CodexExecutionBridge
from core.codex_task import CodexTask


def _git(root: Path, *args: str) -> str:
    completed = subprocess.run(
        ["git", *args], cwd=root, check=True, capture_output=True, text=True
    )
    return completed.stdout.strip()


def build_implementation_smoke_task(root: Path) -> CodexTask:
    return CodexTask(
        task_id="codex-live-implementation-smoke-001",
        issuer="digital_ricard",
        mode="implementation",
        objective=(
            "Add one focused regression test to tests/test_codex_cli_transport.py for "
            "the existing timeout failure path. The test must verify that a "
            "subprocess.TimeoutExpired condition is translated into a failed "
            "CodexTaskResult with blocker 'codex_execution_timeout'. Do not change "
            "production code."
        ),
        context=(
            "This is the first write-enabled Codex execution through "
            "Ricard Digital -> CodexTask -> CodexExecutionBridge -> "
            "CodexCliTransport. The mission is deliberately test-only and bounded "
            "so that workspace-write behavior can be validated without changing "
            "Core, canon or production transport behavior."
        ),
        allowed_paths=("tests/test_codex_cli_transport.py",),
        protected_paths=(
            "core/",
            "data/",
            "docs/",
            "AGENTS.md",
            ".github/",
            "scripts/close_work_block.sh",
        ),
        constraints=(
            "Do not modify production code.",
            "Do not modify files outside the allowed test path.",
            "Do not commit or push.",
            "Keep the change minimal and focused.",
        ),
        acceptance_criteria=(
            "tests/test_codex_cli_transport.py contains a focused regression test for the timeout failure path.",
            "The test asserts status='failed' and blocker='codex_execution_timeout'.",
            "No production files are modified.",
        ),
        verification_commands=(
            "PYTHONPATH=. pytest -q tests/test_codex_cli_transport.py",
        ),
        base_ref=_git(root, "rev-parse", "--abbrev-ref", "HEAD"),
        base_commit=_git(root, "rev-parse", "HEAD"),
        human_approval_required=True,
    )


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--approve",
        action="store_true",
        help="Explicitly approve this live write smoke test.",
    )
    parser.add_argument(
        "--trace-path",
        default="/tmp/arsa-pisha-codex-implementation-smoke.json",
        help="Optional local execution trace path.",
    )
    args = parser.parse_args()

    if not args.approve:
        parser.error("Pass --approve to explicitly authorize the live implementation smoke test.")

    root = Path(__file__).resolve().parents[1]
    task = build_implementation_smoke_task(root)
    bridge = CodexExecutionBridge(
        CodexCliTransport(root=root, trace_path=args.trace_path)
    )
    result = bridge.execute(task, human_approved=True)
    print(json.dumps(result.to_dict(), ensure_ascii=False, indent=2, sort_keys=True))

    expected = {"tests/test_codex_cli_transport.py"}
    changed = set(result.changed_files)
    return 0 if result.status == "completed" and changed.issubset(expected) else 2


if __name__ == "__main__":
    raise SystemExit(main())
