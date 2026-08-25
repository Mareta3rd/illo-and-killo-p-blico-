"""Run one isolated real Gemini evidence experiment.

This script is deliberately outside the normal Core execution path. It requires
GEMINI_API_KEY in the environment and a local image. The result is printed as
canonical ExternalEvidenceRecord data so the experiment can be inspected before
any production integration is attempted.
"""

from __future__ import annotations

import argparse
import json
import mimetypes
import os
from pathlib import Path

from google import genai

from core.gemini_evidence_adapter import GeminiEvidenceAdapter


def main() -> int:
    parser = argparse.ArgumentParser(description="Run one real Gemini evidence experiment")
    parser.add_argument("image", type=Path)
    parser.add_argument("claim_key")
    parser.add_argument("--model", default=os.environ.get("GEMINI_MODEL", "gemini-3.6-flash"))
    args = parser.parse_args()

    if not os.environ.get("GEMINI_API_KEY"):
        raise SystemExit("GEMINI_API_KEY is required in the environment")
    if not args.image.is_file():
        raise SystemExit(f"Image not found: {args.image}")

    mime_type, _ = mimetypes.guess_type(args.image.name)
    if not mime_type or not mime_type.startswith("image/"):
        raise SystemExit(f"Unsupported image type: {args.image}")

    client = genai.Client()
    adapter = GeminiEvidenceAdapter.from_interactions_client(
        client,
        model=args.model,
        image_bytes=args.image.read_bytes(),
        mime_type=mime_type,
    )

    records = tuple(adapter.collect((args.claim_key,)))
    output = {
        "model": args.model,
        "image": str(args.image),
        "records": [
            {
                "claim_key": record.claim_key,
                "statement": record.statement,
                "state": record.state.value,
                "supporting_sources": list(record.supporting_sources),
                "contradicting_sources": list(record.contradicting_sources),
            }
            for record in records
        ],
    }
    print(json.dumps(output, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
