"""Minimal composition root for the first real Groq/Qwen candidate execution.

This entrypoint intentionally stays outside Core and does only the required
composition work:

GroqQwenCandidateExecutor -> ApplicationRequest.executor -> run_application()

This first version is textual-only. Future multimodal execution will require a
controlled extension of the executor contract and a separate composition step.
"""

from __future__ import annotations

import argparse
import json
import os
import sys
from pathlib import Path
from typing import Any, Sequence

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from openai import OpenAI

from core.application import ApplicationRequest, run_application
from core.evidence_state import EvidenceState
from core.external_evidence_adapter import ExternalEvidenceRecord
from core.groq_qwen_candidate_executor import GroqQwenCandidateExecutor
from core.groq_qwen_candidate_transport import (
    DEFAULT_GROQ_BASE_URL,
    DEFAULT_GROQ_QWEN_CANDIDATE_MODEL,
)

DEFAULT_REQUESTED_CLAIMS = ("gag/001/composition/arsa_primary",)
DEFAULT_PROPOSAL: dict[str, Any] = {
    "characters": ["arsa", "pisha"],
    "elements": [
        {"id": "clavel", "intention": "character_identity"},
        {"id": "black_spots", "count": 2, "intention": "character_identity"},
    ],
    "checks": {
        "intention": True,
        "canon": True,
        "coherence": True,
        "reuse_intention": True,
    },
}


class StaticEvidenceProvider:
    """Minimal provider for the first real execution path without calling providers."""

    def collect(self, requested_keys: Sequence[str]) -> tuple[ExternalEvidenceRecord, ...]:
        records: list[ExternalEvidenceRecord] = []
        for key in requested_keys:
            records.append(
                ExternalEvidenceRecord(
                    claim_key=str(key),
                    statement=f"Textual execution path accepted for {key}.",
                    state=EvidenceState.CONFIRMED,
                    supporting_sources=("textual-run",),
                    contradicting_sources=(),
                )
            )
        return tuple(records)


def _json_or_path(value: str | None) -> dict[str, Any] | None:
    if value is None or value == "":
        return None
    candidate = value.strip()
    if candidate.startswith("{"):
        return json.loads(candidate)
    proposal_path = Path(candidate)
    if proposal_path.is_file():
        return json.loads(proposal_path.read_text(encoding="utf-8"))
    raise SystemExit(f"Proposal not found or not valid JSON: {value}")


def build_argument_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description=(
            "Run one real Groq/Qwen candidate execution through the existing Core "
            "Application -> run_vertical_slice composition path."
        )
    )
    parser.add_argument("idea", help="Creative brief or idea for the candidate run")
    parser.add_argument("--run-id", required=True, help="Unique run identifier")
    parser.add_argument(
        "--model",
        default=os.environ.get("GROQ_MODEL", DEFAULT_GROQ_QWEN_CANDIDATE_MODEL),
        help="Groq/Qwen model ID. Default: qwen/qwen3.8-27b",
    )
    parser.add_argument(
        "--base-url",
        default=os.environ.get("GROQ_BASE_URL", DEFAULT_GROQ_BASE_URL),
        help="OpenAI-compatible base URL. Default: https://api.groq.com/openai/v1",
    )
    parser.add_argument(
        "--proposal",
        help="Initial candidate proposal as inline JSON or a path to a JSON file.",
    )
    parser.add_argument(
        "--claim-key",
        action="append",
        default=None,
        help="Canonical claim key to include in the provider observation. Can be repeated.",
    )
    parser.add_argument(
        "--artifact-path",
        type=Path,
        help="Optional path for the execution artifact JSON file.",
    )
    parser.add_argument(
        "--image",
        default="textual-run",
        help="Textual-only runner placeholder. Future multimodal runs will use image bytes.",
    )
    return parser


def build_application_request(
    idea: str,
    run_id: str,
    model: str,
    *,
    proposal: dict[str, Any] | None = None,
    claim_keys: Sequence[str] | None = None,
    artifact_path: str | Path | None = None,
    image: str = "textual-run",
    base_url: str = DEFAULT_GROQ_BASE_URL,
    client: Any | None = None,
) -> ApplicationRequest:
    if proposal is None:
        proposal = dict(DEFAULT_PROPOSAL)

    if client is None:
        api_key = os.environ.get("GROQ_API_KEY")
        if not api_key:
            raise SystemExit("GROQ_API_KEY is required in the environment")
        client = OpenAI(api_key=api_key, base_url=base_url, max_retries=0)

    executor = GroqQwenCandidateExecutor.from_client(client, model=model)
    request = ApplicationRequest(
        idea=idea,
        root=REPO_ROOT,
        provider=StaticEvidenceProvider(),
        provider_name="groq_qwen_candidate",
        run_id=run_id,
        requested_claims=tuple(claim_keys or DEFAULT_REQUESTED_CLAIMS),
        proposal=proposal,
        executor=executor,
        model=model,
        image=image,
        artifact_path=artifact_path,
        max_iterations=3,
    )
    return request


def _safe_result_summary(result: Any) -> dict[str, Any]:
    core_decision = None
    iteration_count = 0
    stop_reason = result.stop_reason if hasattr(result, "stop_reason") else None

    if getattr(result, "core", None) is not None:
        core = result.core
        if getattr(core, "loop", None) is not None and getattr(core.loop, "iterations", None):
            iteration_count = len(core.loop.iterations)
            core_decision = core.loop.iterations[-1].evaluation.decision
        elif getattr(core, "pipeline", None) is not None and getattr(core.pipeline, "evaluation", None) is not None:
            core_decision = core.pipeline.evaluation.evaluation.decision

    return {
        "model": None,
        "run_id": getattr(result, "run_id", None),
        "stopped": bool(getattr(result, "stopped", False)),
        "stop_reason": stop_reason,
        "core_decision": core_decision,
        "iterations": iteration_count,
        "artifact": bool(getattr(result, "artifact", None) is not None),
        "attention": None,
    }


def main(argv: Sequence[str] | None = None) -> int:
    args = build_argument_parser().parse_args(argv)

    if not args.run_id:
        raise SystemExit("--run-id is required")

    api_key = os.environ.get("GROQ_API_KEY")
    if not api_key:
        raise SystemExit("GROQ_API_KEY is required in the environment")

    try:
        client = OpenAI(api_key=api_key, base_url=args.base_url, max_retries=0)
        proposal = _json_or_path(args.proposal)
        request = build_application_request(
            args.idea,
            args.run_id,
            args.model,
            proposal=proposal,
            claim_keys=tuple(args.claim_key) if args.claim_key else DEFAULT_REQUESTED_CLAIMS,
            artifact_path=args.artifact_path,
            image=args.image,
            base_url=args.base_url,
            client=client,
        )
        result = run_application(request)
    except Exception as exc:
        raise SystemExit(f"Groq Qwen candidate runner failed: {exc}") from exc

    safe_summary = {
        "model": args.model,
        "run_id": args.run_id,
        "stopped": bool(getattr(result, "stopped", False)),
        "stop_reason": getattr(result, "stop_reason", None),
        "core_decision": None,
        "iterations": 0,
        "artifact": bool(getattr(result, "artifact", None) is not None),
        "attention": None,
    }

    if getattr(result, "core", None) is not None:
        core = result.core
        if getattr(core, "loop", None) is not None and getattr(core.loop, "iterations", None):
            safe_summary["iterations"] = len(core.loop.iterations)
            safe_summary["core_decision"] = core.loop.iterations[-1].evaluation.decision
        elif getattr(core, "pipeline", None) is not None and getattr(core.pipeline, "evaluation", None) is not None:
            safe_summary["core_decision"] = core.pipeline.evaluation.evaluation.decision

    print(json.dumps(safe_summary, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())


__all__ = [
    "DEFAULT_PROPOSAL",
    "DEFAULT_REQUESTED_CLAIMS",
    "StaticEvidenceProvider",
    "build_application_request",
    "build_argument_parser",
    "main",
    "_json_or_path",
]
