"""Provider-neutral creative feedback for iterative candidate generation.

This layer is advisory by design. It detects high-confidence mechanism reuse
from authoritative creative-memory records and produces revision guidance. It
does not define canon, mutate candidates, score aesthetics, or replace Core
validation.
"""

from __future__ import annotations

import json
import re
import unicodedata
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Mapping


@dataclass(frozen=True)
class CreativeFinding:
    """One explicit creative observation derived from candidate + memory."""

    code: str
    message: str
    guidance: str
    revision_required: bool = False


@dataclass(frozen=True)
class CreativeFeedbackReport:
    """Advisory feedback for the next candidate-generation iteration."""

    findings: tuple[CreativeFinding, ...] = ()
    guidance: tuple[str, ...] = ()
    revision_required: bool = False


def _normalise(text: str) -> str:
    text = unicodedata.normalize("NFKD", text)
    text = "".join(char for char in text if not unicodedata.combining(char))
    return text.lower()


def _tokens(text: str) -> set[str]:
    return {token for token in re.findall(r"[a-zA-Z0-9_]+", _normalise(text)) if len(token) >= 3}


def _load_memory(root: str | Path | None = None) -> tuple[dict[str, Any], ...]:
    base = Path(root) if root is not None else Path(__file__).resolve().parents[1]
    path = base / "data" / "creative_mechanisms.json"
    data = json.loads(path.read_text(encoding="utf-8"))
    mechanisms = data.get("mechanisms", ())
    if not isinstance(mechanisms, list):
        raise ValueError("creative mechanism memory must contain a mechanisms array")
    return tuple(item for item in mechanisms if isinstance(item, dict))


def _candidate_object_ids(candidate: Mapping[str, Any]) -> set[str]:
    result: set[str] = set()
    for element in candidate.get("elements", ()):
        if not isinstance(element, dict):
            continue
        element_id = element.get("id")
        role = str(element.get("role") or "").lower()
        intention = str(element.get("intention") or "").lower()
        if not isinstance(element_id, str) or not element_id.strip():
            continue
        combined = role + " " + intention
        if any(marker in combined for marker in ("primary", "central", "target", "comedic_object", "action_center")):
            result.add(element_id.lower())
    return result


def _character_match(candidate: Mapping[str, Any], mechanism: Mapping[str, Any]) -> bool:
    characters = {str(item).lower() for item in candidate.get("characters", ()) if isinstance(item, str)}
    required = {
        str(mechanism.get("primary_character", "")).lower(),
        str(mechanism.get("secondary_character", "")).lower(),
    }
    required.discard("")
    return bool(required) and required.issubset(characters)


def _build_finding(mechanism: Mapping[str, Any], *, object_match: bool, action_overlap: set[str]) -> CreativeFinding | None:
    mechanism_id = str(mechanism.get("id", "unknown"))
    central_object = str(mechanism.get("central_object", "")).lower()
    if len(action_overlap) < 2:
        return None
    if object_match:
        return CreativeFinding(
            code="CREATIVE_MECHANISM_REUSE",
            message="Candidate reuses the known mechanism '%s', including its central object '%s'." % (mechanism_id, central_object),
            guidance="Do not repeat the same causal chain. Keep the characters and canon, but invent a different mechanism for the new gag.",
            revision_required=True,
        )
    return CreativeFinding(
        code="CREATIVE_OBJECT_SUBSTITUTION",
        message="Candidate appears to preserve mechanism '%s' while substituting its central object." % mechanism_id,
        guidance="Do not create novelty by replacing the main prop alone. Change the causal mechanism, escalation or relationship dynamic.",
        revision_required=True,
    )


def build_creative_feedback(candidate: Mapping[str, Any], *, root: str | Path | None = None) -> CreativeFeedbackReport:
    """Produce bounded, non-scoring feedback for one candidate.

    The detector is conservative: it emits revision guidance only for
    high-confidence mechanism overlap with explicitly recorded memory.
    """
    if not isinstance(candidate, Mapping):
        raise TypeError("candidate must be a mapping")

    content_tokens = _tokens(str(candidate.get("content") or ""))
    findings: list[CreativeFinding] = []
    guidance = [
        "Use canon as a boundary, not as a template.",
        "For a genuinely new gag, seek a new causal chain rather than swapping nouns or props.",
        "Búscate la vida: use the available resources to find a coherent, specific solution the corpus has not already shown.",
    ]

    for mechanism in _load_memory(root):
        if not _character_match(candidate, mechanism):
            continue
        action_terms = {
            token
            for term in mechanism.get("action_terms", ())
            if isinstance(term, str)
            for token in _tokens(term)
        }
        action_overlap = content_tokens & action_terms
        if len(action_overlap) < 2:
            continue
        central_object = str(mechanism.get("central_object", "")).lower()
        object_match = central_object in _candidate_object_ids(candidate)
        finding = _build_finding(mechanism, object_match=object_match, action_overlap=action_overlap)
        if finding is not None:
            findings.append(finding)

    return CreativeFeedbackReport(
        findings=tuple(findings),
        guidance=tuple(guidance) + tuple(item.guidance for item in findings),
        revision_required=any(item.revision_required for item in findings),
    )


__all__ = ["CreativeFeedbackReport", "CreativeFinding", "build_creative_feedback"]
