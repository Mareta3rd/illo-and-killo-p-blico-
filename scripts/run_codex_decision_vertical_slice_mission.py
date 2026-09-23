#!/usr/bin/env python3
"""Run the first bounded auditable DecisionProvider vertical-slice mission."""

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
        ["git", *args],
        cwd=root,
        check=True,
        capture_output=True,
        text=True,
    )
    return completed.stdout.strip()


def build_task(root: Path) -> CodexTask:
    return CodexTask(
        task_id="codex-live-decision-vertical-slice-001",
        issuer="digital_ricard",
        mode="implementation",
        objective=(
            "Implement the first small auditable decision execution seam on top of "
            "the existing DecisionProvider contract. Create "
            "core/decision_execution.py and tests/test_decision_execution.py. "
            "The seam must accept an injected DecisionProvider and a bounded "
            "DecisionRequest, call provider.decide(request), reject malformed "
            "provider returns, validate the DecisionResult against the request, "
            "and return a small immutable audit record containing the request/result "
            "and deterministic digests. It must never execute the decision's action."
        ),
        context=(
            "The DecisionProvider contract and deterministic reference provider are "
            "already verified and committed. This mission connects that capability "
            "to a Core-owned execution seam without choosing a production provider. "
            "The returned object is evidence about one decision execution, not Core "
            "policy, canon, authorization, or action execution. Future Jev, model "
            "and human implementations must be able to occupy the same seam."
        ),
        allowed_paths=(
            "core/decision_execution.py",
            "tests/test_decision_execution.py",
        ),
        protected_paths=(
            "core/decision_provider.py",
            "core/deterministic_decision_provider.py",
            "core/orchestrator.py",
            "core/router.py",
            "core/context.py",
            "core/pipeline.py",
            "core/semantic_audit.py",
            "core/execution_audit.py",
            "core/codex_task.py",
            "core/codex_execution_bridge.py",
            "core/codex_cli_transport.py",
            "data/",
            "docs/",
            "AGENTS.md",
            "scripts/",
        ),
        constraints=(
            "Do not modify existing production files.",
            "Do not modify files outside the two allowed paths.",
            "Do not alter the DecisionProvider contract.",
            "Do not integrate Jev, an LLM, or any external service.",
            "Do not add external dependencies.",
            "Do not execute any action represented by a decision.",
            "Do not commit or push.",
            "Reuse the existing deterministic decision serialization helpers for digests.",
            "Keep the seam small, immutable, provider-neutral, and replaceable.",
        ),
        acceptance_criteria=(
            "An injected DecisionProvider can execute a valid DecisionRequest through the new seam.",
            "The seam rejects a provider that does not return DecisionResult.",
            "The seam validates the returned DecisionResult against the original request before accepting it.",
            "The returned audit record is immutable and includes the request, result, request digest, and result digest.",
            "Repeated execution of the same deterministic request produces stable digests.",
            "Tests cover a valid deterministic execution plus malformed/mismatched results and digest repeatability.",
        ),
        verification_commands=(
            "PYTHONPATH=. pytest -q tests/test_decision_execution.py",
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
        default="/tmp/arsa-pisha-codex-decision-vertical-slice.json",
    )
    args = parser.parse_args()

    if not args.approve:
        parser.error("Pass --approve to authorize the decision vertical-slice mission.")

    root = Path(__file__).resolve().parents[1]
    task = build_task(root)
    result = CodexExecutionBridge(
        CodexCliTransport(root=root, trace_path=args.trace_path)
    ).execute(task, human_approved=True)
    print(json.dumps(result.to_dict(), ensure_ascii=False, indent=2, sort_keys=True))

    expected = {
        "core/decision_execution.py",
        "tests/test_decision_execution.py",
    }
    return 0 if result.status == "completed" and set(result.changed_files) == expected else 2


if __name__ == "__main__":
    raise SystemExit(main())
