#!/usr/bin/env python3
"""Run one explicit human-approved, read-only Codex smoke test."""

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


def build_smoke_task(root: Path) -> CodexTask:
    return CodexTask(
        task_id="codex-live-smoke-001",
        issuer="digital_ricard",
        mode="analysis",
        objective=(
            "Inspect the current repository architecture and report: (1) whether the "
            "Codex project instructions were loaded, (2) one concrete observation about "
            "the current multi-agent architecture, and (3) one useful next technical risk "
            "or opportunity. Do not modify files."
        ),
        context=(
            "This is the first live execution through Ricard Digital -> CodexTask -> "
            "CodexExecutionBridge -> CodexCliTransport. It is a read-only smoke test."
        ),
        allowed_paths=(),
        protected_paths=(
            "data/characters.yaml",
            "docs/CANON_100.md",
            "docs/AI_HANDOFF.md",
            "AGENTS.md",
        ),
        constraints=("Read-only analysis.", "Do not commit or push.", "Return concise findings."),
        acceptance_criteria=("Codex completes the analysis without changing repository files.",),
        verification_commands=("git status --short",),
        base_ref=_git(root, "rev-parse", "--abbrev-ref", "HEAD"),
        base_commit=_git(root, "rev-parse", "HEAD"),
        human_approval_required=True,
    )


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--approve", action="store_true", help="Explicitly approve this live smoke test."
    )
    parser.add_argument(
        "--trace-path",
        default="/tmp/arsa-pisha-codex-smoke.jsonl",
        help="Optional local JSONL trace path.",
    )
    args = parser.parse_args()

    if not args.approve:
        parser.error("Pass --approve to explicitly authorize the live Codex smoke test.")

    root = Path(__file__).resolve().parents[1]
    task = build_smoke_task(root)
    bridge = CodexExecutionBridge(
        CodexCliTransport(root=root, trace_path=args.trace_path)
    )
    result = bridge.execute(task, human_approved=True)
    print(json.dumps(result.to_dict(), ensure_ascii=False, indent=2, sort_keys=True))
    return 0 if result.status == "completed" and not result.changed_files else 2


if __name__ == "__main__":
    raise SystemExit(main())
