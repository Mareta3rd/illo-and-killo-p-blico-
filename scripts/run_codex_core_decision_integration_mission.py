#!/usr/bin/env python3
"""Run the first bounded Core workflow integration mission for decisions."""

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
        task_id="codex-live-core-decision-integration-001",
        issuer="digital_ricard",
        mode="implementation",
        objective=(
            "Integrate the existing provider-neutral decision capability into the "
            "existing Core run_vertical_slice workflow as an explicitly advisory, "
            "non-authoritative decision observation. Modify only "
            "core/orchestrator.py and tests/test_orchestrator.py. Add an optional "
            "injected DecisionProvider parameter to run_vertical_slice; when supplied "
            "on a viable workflow path, create a bounded boolean DecisionRequest about "
            "whether the Core-selected route is appropriate for the current idea, "
            "execute it through execute_decision(), and expose the resulting immutable "
            "DecisionExecutionRecord on VerticalSliceResult. The advisory result must "
            "never replace, gate, authorize, or otherwise mutate the existing Core "
            "route or action path."
        ),
        context=(
            "The repository already has a provider-neutral DecisionProvider contract, "
            "a deterministic reference provider, an auditable execute_decision() seam, "
            "and a Core decision flow. This mission is the first real use of that "
            "capability inside an existing Core workflow. The provider is an injected "
            "source of advisory judgment only. Core remains the authority for routing, "
            "canon, evaluation, execution and action. The integration must preserve "
            "existing behavior when no provider is supplied."
        ),
        allowed_paths=(
            "core/orchestrator.py",
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
            "Do not modify existing production files other than core/orchestrator.py.",
            "Do not modify files outside the two allowed paths.",
            "Do not alter any existing DecisionProvider, decision_execution, decision_flow, router, pipeline, or audit contract.",
            "Do not integrate Jev, an LLM, or any external service.",
            "Do not add external dependencies.",
            "Do not execute any action represented by the decision.",
            "Do not let the advisory decision change or gate the existing Core route.",
            "Preserve existing run_vertical_slice behavior when decision_provider is None.",
            "Reuse execute_decision() rather than duplicating validation or digest logic.",
            "Do not commit or push.",
        ),
        acceptance_criteria=(
            "run_vertical_slice accepts an optional injected DecisionProvider without breaking existing callers.",
            "When a provider is supplied on a viable workflow path, the Core workflow constructs a bounded boolean DecisionRequest with the idea and current Core route in context.",
            "The provider decision is executed through execute_decision() and exposed as an immutable advisory DecisionExecutionRecord on VerticalSliceResult.",
            "A provider returning false or an otherwise valid advisory judgment never changes the Core-selected route or authorizes/stops the workflow.",
            "Provider/result validation failures propagate through the existing decision_execution boundary.",
            "When no provider is supplied, the new advisory field is absent/None and existing behavior remains unchanged.",
            "Focused orchestrator tests cover successful advisory execution, non-authority on conflicting advice, provider failure propagation, and backward-compatible operation without a provider.",
        ),
        verification_commands=(
            "PYTHONPATH=. pytest -q tests/test_orchestrator.py",
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
        default="/tmp/arsa-pisha-codex-core-decision-integration.json",
    )
    args = parser.parse_args()

    if not args.approve:
        parser.error("Pass --approve to authorize the Core decision integration mission.")

    root = Path(__file__).resolve().parents[1]
    task = build_task(root)
    result = CodexExecutionBridge(
        CodexCliTransport(root=root, trace_path=args.trace_path)
    ).execute(task, human_approved=True)
    print(json.dumps(result.to_dict(), ensure_ascii=False, indent=2, sort_keys=True))

    expected = {
        "core/orchestrator.py",
        "tests/test_orchestrator.py",
    }
    return 0 if result.status == "completed" and set(result.changed_files) == expected else 2


if __name__ == "__main__":
    raise SystemExit(main())
