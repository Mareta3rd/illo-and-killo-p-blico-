"""Run a controlled Gemini prompt-stability experiment for one canonical claim."""

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
CANONICAL_CLAIM_KEYS = (
    "gag/001/composition/illo_primary",
    "gag/001/composition/ham_primary",
    "gag/001/characters/killo_reaction",
)

VARIANTS = (
    "canonical",
    "semantic_rephrase",
    "salience_explicit",
)


def load_claim(claim_key: str) -> CanonicalClaim:
    data = json.loads(CLAIMS_PATH.read_text(encoding="utf-8"))
    item = data.get(claim_key)
    if not isinstance(item, dict):
        raise SystemExit(f"Unknown canonical claim: {claim_key}. Choose one of: {', '.join(CANONICAL_CLAIM_KEYS)}")
    return CanonicalClaim(
        key=claim_key,
        statement=item["statement"],
        salience=CanonicalSalience(
            NarrativeRole[item["narrative_role"].upper()],
            VisualSalience[item["visual_salience"].upper()],
        ),
    )


def variant_prompt(claim: CanonicalClaim, variant: str) -> str:
    """Keep the canonical provider contract fixed; vary only one instruction."""
    base = (
        "Evaluate only the requested canonical evidence claim.\n"
        "Do not turn salience metadata into evidence; it only explains the claim's role.\n"
        "Return one observation for the requested key. Preserve UNKNOWN when the image is insufficient.\n\n"
        f"- {claim.key}: {claim.statement} "
        f"[narrative_role={claim.salience.narrative_role.label}; "
        f"visual_salience={claim.salience.visual_salience.label}]\n\n"
    )

    suffixes = {
        "canonical": "Evaluate only this claim from the image.",
        "semantic_rephrase": "Assess whether the image supports the stated claim without inferring missing evidence.",
        "salience_explicit": (
            "Remember that the salience values above are contextual metadata, not evidence, "
            "and do not use them to determine the verdict."
        ),
    }
    return base + suffixes[variant]


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("image", type=Path)
    parser.add_argument("claim_key", choices=CANONICAL_CLAIM_KEYS)
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
    client = genai.Client()
    results = []

    for variant in VARIANTS:
        prompt = variant_prompt(claim, variant)

        # The runner intentionally overrides only the prompt at the provider
        # boundary; the transport, structured response contract, parser, and
        # Core decision boundary remain unchanged.
        adapter = GeminiEvidenceAdapter.from_interactions_client(
            client,
            model=args.model,
            image_bytes=args.image.read_bytes(),
            mime_type=mime_type,
        )
        original_request = adapter.request
        adapter = GeminiEvidenceAdapter(
            request=lambda payload, _request=original_request, _prompt=prompt: _request({**payload, "prompt": _prompt}),
            parse=adapter.parse,
        )
        record = tuple(adapter.collect_claims((claim,)))[0]
        results.append(
            {
                "variant": variant,
                "claim_key": record.claim_key,
                "state": record.state.value,
                "statement": record.statement,
                "supporting_sources": list(record.supporting_sources),
                "contradicting_sources": list(record.contradicting_sources),
            }
        )

    print(json.dumps({"model": args.model, "image": str(args.image), "results": results}, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
