#!/usr/bin/env python3
"""Run the first bounded Core-owned decision-flow integration mission."""

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
        task_id="codex-live-decision-flow-001",
        issuer="digital_ricard",
        mode="implementation",
        objective=(
            "Implement the first small Core-owned decision-flow integration on top "
            "of the existing DecisionProvider and decision_execution seams. Create "
            "core/decision_flow.py and tests/test_decision_flow.py. The flow must "
            "accept a bounded DecisionRequest, obtain a DecisionProvider through an "
            "explicit injected resolver, execute the provider through execute_decision(), "
            "and return a small immutable Core-owned record exposing the auditable "
            "DecisionExecutionRecord. Provider selection must remain replaceable and "
            "must not execute any action."
        ),
        context=(
            "The DecisionProvider contract, deterministic provider, and auditable "
            "execute_decision() seam are already verified and committed. This mission "
            "connects them into a Core-owned integration point without hard-coding "
            "Jev, an LLM, or any provider. The resolver is an injection boundary: "
            "Core may ask it for a provider, but the provider remains responsible "
            "only for returning a DecisionResult. The flow is evidence-producing, "
            "not an action executor and not a canon authority."
        ),
        allowed_paths=(
            "core/decision_flow.py",
            "tests/test_decision_flow.py",
        ),
        protected_paths=(
            "core/decision_provider.py",
            "core/deterministic_decision_provider.py",
            "core/decision_execution.py",
            "core/router.py",
            "core/context.py",
            "core/pipeline.py",
            "core/orchestrator.py",
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
            "Do not alter the DecisionProvider or decision_execution contracts.",
            "Do not integrate Jev, an LLM, or any external service.",
            "Do not add external dependencies.",
            "Do not execute any action represented by a decision.",
            "Do not commit or push.",
            "Keep the resolver/provider boundary explicit and provider-neutral.",
            "Reuse execute_decision() rather than duplicating provider-result validation or digest logic.",
            "Keep the Core-owned record immutable and small.",
        ),
        acceptance_criteria=(
            "A valid DecisionRequest can be resolved to an injected provider and executed through execute_decision().",
            "The flow exposes the resulting DecisionExecutionRecord without changing it.",
            "The returned Core-owned record is immutable.",
            "A resolver returning a non-provider-like object is rejected clearly.",
            "A provider returning a malformed or mismatched DecisionResult is still rejected by the existing decision_execution seam.",
            "Repeated execution with the deterministic provider remains auditable and produces stable nested digests.",
            "Focused tests cover provider resolution, successful execution, immutability, and failure propagation.",
        ),
        verification_commands=(
            "PYTHONPATH=. pytest -q tests/test_decision_flow.py",
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
        default="/tmp/arsa-pisha-codex-decision-flow.json",
    )
    args = parser.parse_args()

    if not args.approve:
        parser.error("Pass --approve to authorize the decision-flow mission.")

    root = Path(__file__).resolve().parents[1]
    task = build_task(root)
    result = CodexExecutionBridge(
        CodexCliTransport(root=root, trace_path=args.trace_path)
    ).execute(task, human_approved=True)
    print(json.dumps(result.to_dict(), ensure_ascii=False, indent=2, sort_keys=True))

    expected = {
        "core/decision_flow.py",
        "tests/test_decision_flow.py",
    }
    return 0 if result.status == "completed" and set(result.changed_files) == expected else 2


if __name__ == "__main__":
    raise SystemExit(main())
