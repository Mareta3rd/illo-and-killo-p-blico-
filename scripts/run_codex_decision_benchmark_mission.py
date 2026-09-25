#!/usr/bin/env python3
"""Run the bounded DecisionProvider benchmark implementation mission."""

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
        task_id="codex-live-decision-benchmark-001",
        issuer="digital_ricard",
        mode="implementation",
        objective=(
            "Implement the smallest reusable local benchmark harness for the existing "
            "provider-neutral DecisionProvider capability. Modify only "
            "core/decision_benchmark.py and tests/test_decision_benchmark.py. The harness "
            "must define provider-neutral benchmark fixtures covering boolean, constrained "
            "choice, numeric score, and provider failure/invalid-result behavior; execute "
            "each fixture through the existing decision execution boundary; record "
            "contract validity, expected-vs-observed value, repeatability, latency, "
            "provider/model identifiers, confidence, and failure/abstention information; "
            "and produce deterministic serializable benchmark results. The harness must "
            "not select a production provider, execute actions, mutate canon, or collapse "
            "all measurements into a universal score."
        ),
        context=(
            "The repository already has DecisionProvider, DeterministicDecisionProvider, "
            "DecisionExecutionRecord, Core decision flow, Application integration, and a "
            "verified end-to-end exercise. The benchmark protocol is documented in "
            "docs/DECISION_BENCHMARK.md. This mission turns that protocol into a small "
            "local engineering instrument using only the deterministic provider as the "
            "initial participant. Future Jev, model-based and human implementations must "
            "be able to participate through the same provider contract without changing "
            "the harness."
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
            "Do not alter any existing DecisionProvider or decision execution contract.",
            "Do not integrate Jev, an LLM, an external service, or any network dependency.",
            "Do not add external dependencies.",
            "Reuse execute_decision() for provider execution and validation.",
            "Keep benchmark fixtures provider-neutral and small.",
            "Do not execute any action represented by a decision.",
            "Do not choose or recommend a production provider.",
            "Do not collapse measurements into a single quality score.",
            "Do not commit or push.",
        ),
        acceptance_criteria=(
            "A reusable benchmark case structure can express boolean, choice, score, and failure/invalid-result cases.",
            "The harness executes valid cases through execute_decision() and records the resulting DecisionExecutionRecord metadata needed by the benchmark protocol.",
            "Expected-vs-observed value is explicit rather than inferred into a universal score.",
            "Repeatability is checked for repeated identical requests.",
            "Latency is measured with a monotonic clock and recorded as a raw measurement.",
            "Provider/model identifier and confidence are retained when supplied.",
            "Provider failures or malformed results are recorded as benchmark outcomes rather than silently converted to success.",
            "Results serialize deterministically to JSON-compatible state.",
            "Focused tests cover all fixture categories, repeatability, latency recording, failure handling, and deterministic serialization.",
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
        default="/tmp/arsa-pisha-codex-decision-benchmark.json",
    )
    args = parser.parse_args()

    if not args.approve:
        parser.error("Pass --approve to authorize the DecisionProvider benchmark mission.")

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
