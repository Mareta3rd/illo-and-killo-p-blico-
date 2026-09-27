"""Run the fixed provider-neutral decision benchmark against a local OpenAI-compatible model server."""

from __future__ import annotations

import argparse
import json
import os
from typing import Sequence

from openai import OpenAI

from core.decision_benchmark import load_decision_benchmark_fixtures, run_decision_benchmark
from core.local_structured_decision_provider import LocalStructuredDecisionProvider


def build_argument_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--base-url", default=os.environ.get("LOCAL_LLM_BASE_URL", "http://127.0.0.1:8080/v1"))
    parser.add_argument("--model", default=os.environ.get("LOCAL_LLM_MODEL", "Qwen3.8-27B-GGUF:Q4_K_M"))
    parser.add_argument("--provider-id", default="local-qwen")
    parser.add_argument("--api-key", default=os.environ.get("LOCAL_LLM_API_KEY", "none"))
    parser.add_argument("--include-control", action="store_true")
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    args = build_argument_parser().parse_args(argv)
    cases = load_decision_benchmark_fixtures()
    if not args.include_control:
        cases = tuple(case for case in cases if not case.expected_failure)
    client = OpenAI(api_key=args.api_key, base_url=args.base_url, max_retries=0)
    provider = LocalStructuredDecisionProvider(client, model=args.model, provider_id=args.provider_id, temperature=0.0)
    report = run_decision_benchmark(provider, cases)
    print(json.dumps(report.to_dict(), ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())