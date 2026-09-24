#!/usr/bin/env python3
"""Run the first bounded application-boundary decision integration mission."""

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
        task_id="codex-live-application-decision-integration-001",
        issuer="digital_ricard",
        mode="implementation",
        objective=(
            "Integrate the existing provider-neutral decision capability through the "
            "application boundary. Modify only core/application.py and "
            "tests/test_application.py. Add an optional injected DecisionProvider to "
            "ApplicationRequest and pass it unchanged to run_vertical_slice(). "
            "Preserve ApplicationResult as the existing aggregate boundary, expose no "
            "duplicate decision structure, and ensure callers can inspect the same "
            "advisory DecisionExecutionRecord through result.core. No concrete provider "
            "must be selected or created by Application."
        ),
        context=(
            "The repository already has a provider-neutral DecisionProvider contract, "
            "a deterministic reference provider, an auditable execute_decision() seam, "
            "a Core decision flow, and an advisory decision integrated into "
            "run_vertical_slice() and ExecutionAudit. This mission proves that the "
            "decision capability can cross the existing Application boundary without "
            "creating a second authority or duplicate audit representation. Application "
            "should remain an orchestration/aggregation layer."
        ),
        allowed_paths=(
            "core/application.py",
            "tests/test_application.py",
        ),
        protected_paths=(
            "core/decision_provider.py",
            "core/deterministic_decision_provider.py",
            "core/decision_execution.py",
            "core/decision_flow.py",
            "core/execution_audit.py",
            "core/orchestrator.py",
            "core/router.py",
            "core/context.py",
            "core/pipeline.py",
            "core/semantic_audit.py",
            "core/codex_task.py",
            "core/codex_execution_bridge.py",
            "core/codex_cli_transport.py",
            "data/",
            "docs/",
            "AGENTS.md",
            "scripts/",
        ),
        constraints=(
            "Do not modify files outside the two allowed paths.",
            "Do not alter any DecisionProvider, decision_execution, decision_flow, execution_audit, or orchestrator contract.",
            "Do not integrate Jev, an LLM, or any external service.",
            "Do not add external dependencies.",
            "Do not create a second advisory decision record in ApplicationResult.",
            "Reuse run_vertical_slice() as the existing Core boundary.",
            "Preserve behavior exactly when no decision_provider is supplied.",
            "Do not execute any action represented by a decision.",
            "Do not commit or push.",
        ),
        acceptance_criteria=(
            "ApplicationRequest accepts an optional DecisionProvider without breaking existing callers.",
            "run_application() passes the injected DecisionProvider unchanged to run_vertical_slice().",
            "A successful application run with a deterministic provider exposes the same advisory DecisionExecutionRecord via result.core.",
            "The advisory record remains non-authoritative and does not alter the existing Core result.",
            "Provider failures propagate according to the existing Core decision boundary.",
            "Application runs without a provider remain backward compatible.",
            "Focused tests cover injected decision propagation, same-record visibility, no-provider compatibility, and failure propagation.",
        ),
        verification_commands=(
            "PYTHONPATH=. pytest -q tests/test_application.py",
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
        default="/tmp/arsa-pisha-codex-application-decision-integration.json",
    )
    args = parser.parse_args()

    if not args.approve:
        parser.error("Pass --approve to authorize the application decision integration mission.")

    root = Path(__file__).resolve().parents[1]
    task = build_task(root)
    result = CodexExecutionBridge(
        CodexCliTransport(root=root, trace_path=args.trace_path)
    ).execute(task, human_approved=True)
    print(json.dumps(result.to_dict(), ensure_ascii=False, indent=2, sort_keys=True))

    expected = {"core/application.py", "tests/test_application.py"}
    return 0 if result.status == "completed" and set(result.changed_files) == expected else 2


if __name__ == "__main__":
    raise SystemExit(main())
