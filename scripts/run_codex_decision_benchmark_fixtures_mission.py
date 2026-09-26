#!/usr/bin/env python3
"""Run the bounded DecisionProvider benchmark-fixture integration mission."""

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
        task_id="codex-live-decision-benchmark-fixtures-001",
        issuer="digital_ricard",
        mode="implementation",
        objective=(
            "Integrate the new provider-neutral decision benchmark v1 fixture set into "
            "the existing local benchmark harness. Modify only "
            "core/decision_benchmark.py and tests/test_decision_benchmark.py. Add the "
            "smallest reusable loader needed to read data/decision_benchmark_fixtures.json "
            "into DecisionBenchmarkCase objects while preserving the existing run "
            "contract and provider neutrality. Tests must exercise the repository fixture "
            "source, verify all four v1 fixture roles, and retain the existing benchmark "
            "coverage for repeatability, latency, metadata, failure handling and "
            "deterministic serialization."
        ),
        context=(
            "The DecisionProvider contract, deterministic reference provider, execution "
            "seam and benchmark harness are already verified. The repository now defines "
            "an exact provider-neutral v1 comparison fixture set in "
            "data/decision_benchmark_fixtures.json and documents its execution rules in "
            "docs/DECISION_BENCHMARK_COMPARISON.md. The fixture set must become the "
            "single reusable source for benchmark cases so future providers cannot drift "
            "from provider-neutral inputs."
        ),
        allowed_paths=(
            "core/decision_benchmark.py",
            "tests/test_decision_benchmark.py",
        ),
        protected_paths=(
            "core/decision_provider.py",
            "core/deterministic_decision_provider.py",
            "core/decision_execution.py",
            "core/decision_flow.py",
            "core/application.py",
            "core/orchestrator.py",
            "core/execution_audit.py",
            "core/router.py",
            "core/context.py",
            "core/pipeline.py",
            "core/semantic_audit.py",
            "core/codex_task.py",
            "core/codex_execution_bridge.py",
            "core/codex_cli_transport.py",
            "data/",
            "docs/",
            "scripts/",
            "AGENTS.md",
        ),
        constraints=(
            "Do not modify files outside the two allowed paths.",
            "Do not modify data/decision_benchmark_fixtures.json.",
            "Do not alter any existing DecisionProvider or execute_decision() contract.",
            "Do not integrate Jev, an LLM, an external service, or any network dependency.",
            "Do not add external dependencies.",
            "Preserve the existing run_decision_benchmark() behavior for callers.",
            "Keep the fixture loader provider-neutral and deterministic.",
            "Do not select a production provider or execute any action.",
            "Do not add a universal benchmark score.",
            "Do not commit or push.",
        ),
        acceptance_criteria=(
            "A reusable loader can convert data/decision_benchmark_fixtures.json into "
            "DecisionBenchmarkCase objects without provider-specific logic.",
            "The loader validates the fixture-set structure sufficiently to reject malformed "
            "fixture entries instead of silently creating partial cases.",
            "Tests load the repository v1 fixture set as the source of truth and verify the "
            "three objective fixtures plus the harness-control failure fixture.",
            "Existing benchmark tests continue to cover boolean, choice, score, failure, "
            "repeatability, latency, metadata and deterministic JSON serialization.",
            "Focused verification passes with PYTHONPATH=. pytest -q tests/test_decision_benchmark.py.",
        ),
        verification_commands=(
            "PYTHONPATH=. pytest -q tests/test_decision_benchmark.py",
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
        default="/tmp/arsa-pisha-codex-decision-benchmark-fixtures.json",
    )
    args = parser.parse_args()

    if not args.approve:
        parser.error("Pass --approve to authorize the benchmark-fixture integration mission.")

    root = Path(__file__).resolve().parents[1]
    task = build_task(root)
    result = CodexExecutionBridge(
        CodexCliTransport(root=root, trace_path=args.trace_path)
    ).execute(task, human_approved=True)
    print(json.dumps(result.to_dict(), ensure_ascii=False, indent=2, sort_keys=True))

    expected = {
        "core/decision_benchmark.py",
        "tests/test_decision_benchmark.py",
    }
    return 0 if result.status == "completed" and set(result.changed_files) == expected else 2


if __name__ == "__main__":
    raise SystemExit(main())
