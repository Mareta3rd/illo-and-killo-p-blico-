#!/usr/bin/env python3
"""Run the first bounded production-code Codex mission for capability routing."""

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


def build_task(root: Path) -> CodexTask:
    return CodexTask(
        task_id="codex-live-decision-provider-001",
        issuer="digital_ricard",
        mode="implementation",
        objective=(
            "Implement the provider-neutral DecisionProvider contract described in "
            "docs/CAPABILITY_ROUTING.md. Create core/decision_provider.py and "
            "tests/test_decision_provider.py. Keep the implementation small and "
            "provider-neutral; do not integrate Jev or any external API."
        ),
        context=(
            "This is the first bounded production-code Codex mission after the "
            "successful read-only and test-only write smokes. The purpose is to "
            "establish a stable capability-oriented decision seam while preserving "
            "Core authority and provider neutrality."
        ),
        allowed_paths=(
            "core/decision_provider.py",
            "tests/test_decision_provider.py",
        ),
        protected_paths=(
            "core/codex_task.py",
            "core/codex_execution_bridge.py",
            "core/codex_cli_transport.py",
            "core/loader.py",
            "core/prompt_compiler.py",
            "core/semantic_context.py",
            "core/orchestrator.py",
            "core/semantic_audit.py",
            "data/",
            "docs/CANON_100.md",
            "docs/AI_HANDOFF.md",
            "AGENTS.md",
        ),
        constraints=(
            "Do not modify existing production files.",
            "Do not modify files outside the two allowed paths.",
            "Do not integrate a real external provider.",
            "Do not commit or push.",
            "Follow docs/CAPABILITY_ROUTING.md.",
            "Keep JSON serialization deterministic.",
        ),
        acceptance_criteria=(
            "core/decision_provider.py defines a provider-neutral DecisionProvider protocol and closed request/result structures.",
            "Boolean, choice and score decisions are supported.",
            "Invalid kinds, invalid choices and out-of-range confidence are rejected.",
            "tests/test_decision_provider.py covers the contract and deterministic serialization.",
            "The focused test suite for the new contract passes.",
        ),
        verification_commands=(
            "PYTHONPATH=. pytest -q tests/test_decision_provider.py",
        ),
        base_ref=_git(root, "rev-parse", "--abbrev-ref", "HEAD"),
        base_commit=_git(root, "rev-parse", "HEAD"),
        human_approval_required=True,
    )


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--approve", action="store_true")
    parser.add_argument(
        "--trace-path",
        default="/tmp/arsa-pisha-codex-decision-provider.json",
    )
    args = parser.parse_args()
    if not args.approve:
        parser.error("Pass --approve to authorize the production-code Codex mission.")

    root = Path(__file__).resolve().parents[1]
    task = build_task(root)
    result = CodexExecutionBridge(
        CodexCliTransport(root=root, trace_path=args.trace_path)
    ).execute(task, human_approved=True)
    print(json.dumps(result.to_dict(), ensure_ascii=False, indent=2, sort_keys=True))

    expected = {
        "core/decision_provider.py",
        "tests/test_decision_provider.py",
    }
    if result.status != "completed":
        return 2
    if set(result.changed_files) != expected:
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
