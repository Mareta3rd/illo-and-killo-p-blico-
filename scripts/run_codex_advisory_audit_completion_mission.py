#!/usr/bin/env python3
"""Complete the auditable placement of Core advisory decision evidence."""

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
        task_id="codex-live-advisory-audit-completion-001",
        issuer="digital_ricard",
        mode="implementation",
        objective=(
            "Complete the audit placement of the existing advisory DecisionExecutionRecord "
            "inside the Core execution audit boundary. Modify only core/execution_audit.py, "
            "core/orchestrator.py, tests/test_execution_audit.py and tests/test_orchestrator.py. "
            "ExecutionAudit must optionally carry the exact immutable advisory DecisionExecutionRecord, "
            "and build_execution_audit() must accept it without changing existing callers. "
            "run_vertical_slice() must pass the same advisory record into the execution audit while "
            "preserving the existing top-level VerticalSliceResult advisory_decision convenience field. "
            "No advisory decision may affect route, authorization, action execution or Core policy."
        ),
        context=(
            "The repository now has a provider-neutral DecisionProvider, deterministic reference provider, "
            "auditable execute_decision() seam, Core decision flow, and an advisory integration in "
            "run_vertical_slice(). Architectural review determined that durable execution audit must also "
            "retain the advisory judgment; otherwise the in-memory result and reconstructable audit diverge. "
            "The same immutable record should be exposed at both boundaries rather than duplicated or "
            "recomputed. Existing no-provider behavior must remain unchanged."
        ),
        allowed_paths=(
            "core/execution_audit.py",
            "core/orchestrator.py",
            "tests/test_execution_audit.py",
            "tests/test_orchestrator.py",
        ),
        protected_paths=(
            "core/decision_provider.py",
            "core/deterministic_decision_provider.py",
            "core/decision_execution.py",
            "core/decision_flow.py",
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
            "Do not modify files outside the four allowed paths.",
            "Do not alter DecisionProvider, deterministic provider, decision execution or decision flow contracts.",
            "Do not integrate Jev, an LLM, or any external provider.",
            "Do not add external dependencies.",
            "Keep advisory evidence informational and non-authoritative.",
            "Preserve the existing execution audit fields and serialization/use semantics.",
            "Reuse the exact advisory DecisionExecutionRecord produced by execute_decision(); do not reconstruct it.",
            "Preserve backward compatibility when no advisory provider is supplied.",
            "Do not commit or push.",
        ),
        acceptance_criteria=(
            "ExecutionAudit optionally exposes advisory_decision as the exact DecisionExecutionRecord.",
            "build_execution_audit() accepts advisory_decision without breaking existing callers.",
            "run_vertical_slice() passes the same advisory record into both VerticalSliceResult and ExecutionAudit.",
            "No-provider runs have advisory_decision=None and retain prior behavior.",
            "The advisory value cannot change route, authorization, stopping or action execution.",
            "Tests verify audit propagation, object identity or equality, no-provider compatibility and existing orchestrator behavior.",
            "Complete focused execution-audit and orchestrator tests pass.",
        ),
        verification_commands=(
            "PYTHONPATH=. pytest -q tests/test_execution_audit.py tests/test_orchestrator.py",
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
        default="/tmp/arsa-pisha-codex-advisory-audit-completion.json",
    )
    args = parser.parse_args()

    if not args.approve:
        parser.error("Pass --approve to authorize the advisory-audit completion mission.")

    root = Path(__file__).resolve().parents[1]
    task = build_task(root)
    result = CodexExecutionBridge(
        CodexCliTransport(root=root, trace_path=args.trace_path)
    ).execute(task, human_approved=True)
    print(json.dumps(result.to_dict(), ensure_ascii=False, indent=2, sort_keys=True))

    expected = {
        "core/execution_audit.py",
        "core/orchestrator.py",
        "tests/test_execution_audit.py",
        "tests/test_orchestrator.py",
    }
    return 0 if result.status == "completed" and set(result.changed_files) == expected else 2


if __name__ == "__main__":
    raise SystemExit(main())
