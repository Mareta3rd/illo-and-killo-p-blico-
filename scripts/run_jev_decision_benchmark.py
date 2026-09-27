#!/usr/bin/env python3
"""Run the fixed provider-neutral decision benchmark against TypeSafe Jev."""

from __future__ import annotations

import argparse
from pathlib import Path

from core.decision_benchmark import load_decision_benchmark_fixtures, run_decision_benchmark
from core.typesafe_jev_decision_provider import TypeSafeJevDecisionProvider


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--boolean-threshold",
        type=float,
        required=True,
        help="Explicit Jev Noul probability threshold used to produce Core booleans.",
    )
    parser.add_argument("--model", default=None, help="Optional TypeSafe model name/alias.")
    parser.add_argument(
        "--include-harness-controls",
        action="store_true",
        help="Also execute harness-control fixtures; these are not provider-quality cases.",
    )
    parser.add_argument("--output", type=Path, default=None, help="Optional JSON output path.")
    args = parser.parse_args()

    cases = load_decision_benchmark_fixtures()
    if not args.include_harness_controls:
        cases = tuple(case for case in cases if not case.expected_failure)
    with TypeSafeJevDecisionProvider(
        boolean_threshold=args.boolean_threshold,
        model=args.model,
    ) as provider:
        report = run_decision_benchmark(provider, cases)

    rendered = report.to_json()
    if args.output is None:
        print(rendered)
    else:
        args.output.write_text(rendered + "\n", encoding="utf-8")

    all_match = all(
        comparison["matches"]
        for result in report.results
        for comparison in result.expected_vs_observed
    )
    has_incompatibility = any(
        observation.status == "provider_incompatibility"
        for result in report.results
        for observation in result.observations
    )
    if all_match:
        return 0
    if has_incompatibility:
        return 3
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
