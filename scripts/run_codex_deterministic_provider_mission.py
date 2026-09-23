#!/usr/bin/env python3
"""Run a bounded Codex mission to build the deterministic decision baseline."""

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
        task_id="codex-live-deterministic-provider-001",
        issuer="digital_ricard",
        mode="implementation",
        objective=(
            "Implement a small provider-neutral DeterministicDecisionProvider in "
            "core/deterministic_decision_provider.py using the existing "
            "DecisionProvider contract. It must serve predeclared deterministic "
            "answers keyed by question_id, construct valid DecisionResult values, "
            "validate them against the incoming DecisionRequest, and reject missing "
            "answers. Add focused tests in tests/test_deterministic_decision_provider.py. "
            "Do not modify the existing DecisionProvider contract."
        ),
        context=(
            "This is the reference implementation for the new capability-oriented "
            "decision layer. It is intentionally deterministic and dependency-free. "
            "Later decision providers, including external services, will be "
            "benchmarked against this baseline. Keep provider identity and action "
            "authority separate: this class supplies a DecisionResult and does not "
            "execute actions."
        ),
        allowed_paths=(
            "core/deterministic_decision_provider.py",
            "tests/test_deterministic_decision_provider.py",
        ),
        protected_paths=(
            "core/decision_provider.py",
            "core/codex_task.py",
            "core/codex_execution_bridge.py",
            "core/codex_cli_transport.py",
            "core/orchestrator.py",
            "core/semantic_audit.py",
            "data/",
            "docs/",
            "AGENTS.md",
            "scripts/",
        ),
        constraints=(
            "Do not modify existing production files.",
            "Do not modify files outside the two allowed paths.",
            "Do not add external dependencies.",
            "Do not integrate Jev or any other provider.",
            "Do not commit or push.",
            "Keep the implementation small and easy to benchmark.",
        ),
        acceptance_criteria=(
            "The implementation satisfies the existing DecisionProvider protocol.",
            "Answers are deterministic and keyed by question_id.",
            "Missing question IDs are rejected.",
            "Returned results are validated against the request before they are returned.",
            "Tests cover boolean, choice and score decisions plus invalid/missing answers.",
            "The focused deterministic-provider test suite passes.",
        ),
        verification_commands=(
            "PYTHONPATH=. pytest -q tests/test_deterministic_decision_provider.py",
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
        default="/tmp/arsa-pisha-codex-deterministic-provider.json",
    )
    args = parser.parse_args()

    if not args.approve:
        parser.error("Pass --approve to authorize the deterministic-provider mission.")

    root = Path(__file__).resolve().parents[1]
    task = build_task(root)
    result = CodexExecutionBridge(
        CodexCliTransport(root=root, trace_path=args.trace_path)
    ).execute(task, human_approved=True)
    print(json.dumps(result.to_dict(), ensure_ascii=False, indent=2, sort_keys=True))

    expected = {
        "core/deterministic_decision_provider.py",
        "tests/test_deterministic_decision_provider.py",
    }
    return 0 if result.status == "completed" and set(result.changed_files) == expected else 2


if __name__ == "__main__":
    raise SystemExit(main())
