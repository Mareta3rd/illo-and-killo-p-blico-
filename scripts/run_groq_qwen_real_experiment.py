"""Run one real multimodal Groq/Qwen evidence experiment."""

from __future__ import annotations

import argparse
import base64
import json
import mimetypes
import os
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from openai import OpenAI

from core.groq_qwen_evidence_adapter import GroqQwenEvidenceAdapter
from core.groq_qwen_real_transport import DEFAULT_GROQ_BASE_URL, DEFAULT_GROQ_QWEN_MODEL


def read_image(path: Path) -> tuple[bytes, str]:
    mime_type, _ = mimetypes.guess_type(path.name)
    if not mime_type or not mime_type.startswith("image/"):
        raise SystemExit(f"Unsupported image type: {path}")
    return path.read_bytes(), mime_type


def build_argument_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Run one real Groq/Qwen evidence experiment")
    parser.add_argument("image_path", type=Path)
    parser.add_argument("claim_key")
    parser.add_argument("--run-id", required=True)
    parser.add_argument("--model", default=os.environ.get("GROQ_MODEL", DEFAULT_GROQ_QWEN_MODEL))
    parser.add_argument("--base-url", default=os.environ.get("GROQ_BASE_URL", DEFAULT_GROQ_BASE_URL))
    return parser


def main() -> int:
    args = build_argument_parser().parse_args()
    api_key = os.environ.get("GROQ_API_KEY")
    if not api_key:
        raise SystemExit("GROQ_API_KEY is required in the environment")
    if not args.image_path.is_file():
        raise SystemExit(f"Image not found: {args.image_path}")

    image_bytes, mime_type = read_image(args.image_path)
    client = OpenAI(api_key=api_key, base_url=args.base_url, max_retries=0)
    adapter = GroqQwenEvidenceAdapter.from_responses_client(
        client,
        model=args.model,
        image_bytes=image_bytes,
        mime_type=mime_type,
    )
    records = adapter.collect((args.claim_key,))

    print(json.dumps({
        "model": args.model,
        "image": str(args.image_path),
        "run_id": args.run_id,
        "records": [
            {
                "claim_key": record.claim_key,
                "state": record.state.value,
                "statement": record.statement,
                "supporting_sources": list(record.supporting_sources),
                "contradicting_sources": list(record.contradicting_sources),
            }
            for record in records
        ],
    }, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())