"""Run a real Gemini evidence experiment for canonical Gag 001 claims.

This runner remains outside the normal Core execution path. It loads the
canonical claim definition, including narrative and visual salience, then
feeds that definition through the real Gemini adapter.
"""

from __future__ import annotations

import argparse
import json
import mimetypes
import os
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from google import genai

from core.canonical_salience import CanonicalClaim, CanonicalSalience, NarrativeRole, VisualSalience
from core.gemini_evidence_adapter import GeminiEvidenceAdapter

CLAIMS_PATH = REPO_ROOT / "data" / "gag_001_claims.json"


def load_claim(claim_key: str) -> CanonicalClaim:
    data = json.loads(CLAIMS_PATH.read_text(encoding="utf-8"))
    item = data.get(claim_key)
    if not isinstance(item, dict):
        raise SystemExit(f"Unknown canonical claim: {claim_key}")
    try:
        return CanonicalClaim(
            key=claim_key,
            statement=item["statement"],
            salience=CanonicalSalience(
                NarrativeRole[item["narrative_role"].upper()],
                VisualSalience[item["visual_salience"].upper()],
            ),
        )
    except (KeyError, TypeError) as exc:
        raise SystemExit(f"Invalid canonical claim definition: {claim_key}") from exc


def main() -> int:
    parser = argparse.ArgumentParser(description="Run a real Gemini experiment for Gag 001")
    parser.add_argument("image", type=Path)
    parser.add_argument("claim_key", choices=(
        "gag/001/composition/illo_primary",
        "gag/001/composition/ham_primary",
        "gag/001/characters/killo_reaction",
    ))
    parser.add_argument("--model", default=os.environ.get("GEMINI_MODEL", "gemini-3.6-flash"))
    args = parser.parse_args()

    if not os.environ.get("GEMINI_API_KEY"):
        raise SystemExit("GEMINI_API_KEY is required in the environment")
    if not args.image.is_file():
        raise SystemExit(f"Image not found: {args.image}")

    mime_type, _ = mimetypes.guess_type(args.image.name)
    if not mime_type or not mime_type.startswith("image/"):
        raise SystemExit(f"Unsupported image type: {args.image}")

    claim = load_claim(args.claim_key)
    adapter = GeminiEvidenceAdapter.from_interactions_client(
        genai.Client(),
        model=args.model,
        image_bytes=args.image.read_bytes(),
        mime_type=mime_type,
    )

    records = tuple(adapter.collect_claims((claim,)))
    print(
        json.dumps(
            {
                "model": args.model,
                "image": str(args.image),
                "claim": {
                    "key": claim.key,
                    "statement": claim.statement,
                    "narrative_role": claim.salience.narrative_role.label,
                    "visual_salience": claim.salience.visual_salience.label,
                },
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
            },
            ensure_ascii=False,
            indent=2,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
