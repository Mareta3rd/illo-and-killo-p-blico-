"""Provider-neutral visual critique contract for generated creative artifacts.""

The critique layer does not generate images, score taste, or decide canon. It
normalizes observations from a future multimodal reviewer into auditable
dimensions that Core and a creative feedback layer can consume.

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Mapping


VISUAL_DIMENSIONS = (
    "character_fidelity",
    "gag_readability",
    "composition_hierarchy",
    "motion_and_pose",
    "style_coherence",
    "cultural_integration",
    "production_fit",
)

OBSERVATION_STATES = {"observed", "uncertain", "not_applicable"}
CONFIDENCE_LEVELS = {"high", "medium", "low"}


@dataclass(frozen=True)
class VisualFinding:
    """One provider-neutral observation about a visual candidate."""

    dimension: str
    state: str
    observation: str
    evidence: str
    confidence: str
    guidance: str = ""


@dataclass(frozen=True)
class VisualCritiqueReport:
    """Closed, non-scoring visual critique for one candidate."""

    findings: tuple[VisualFinding, ...]

    def by_dimension(self) -> dict[str, VisualFinding]:
        """Return one finding per dimension in deterministic order."""
        return {finding.dimension: finding for finding in self.findings}


def build_visual_critique(
    findings: list[Mapping[str, Any]] | tuple[Mapping[str, Any], ...],
) -> VisualCritiqueReport:
    """Normalize externally observed visual findings without interpreting them."""
    if not isinstance(findings, (list, tuple)):
        raise TypeError("findings must be a list or tuple")

    normalized: list[VisualFinding] = []
    seen: set[str] = set()
    for index, raw in enumerate(findings):
        if not isinstance(raw, Mapping):
            raise ValueError(f"visual finding {index} must be an object")
        required = {"dimension", "state", "observation", "evidence", "confidence"}
        missing = required - set(raw)
        unknown = set(raw) - required - {"guidance"}
        if missing or unknown:
            detail = []
            if missing:
                detail.append("missing=" + ",".join(sorted(missing)))
            if unknown:
                detail.append("unknown=" + ",".join(sorted(unknown)))
            raise ValueError(
                f"visual finding {index} has invalid fields ({'; '.join(detail)})"
            )

        dimension = raw["dimension"]
        state = raw["state"]
        confidence = raw["confidence"]
        if dimension not in VISUAL_DIMENSIONS:
            raise ValueError(f"unsupported visual dimension: {dimension}")
        if dimension in seen:
            raise ValueError(f"duplicate visual dimension: {dimension}")
        if state not in OBSERVATION_STATES:
            raise ValueError(f"unsupported visual observation state: {state}")
        if confidence not in CONFIDENCE_LEVELS:
            raise ValueError(f"unsupported visual confidence: {confidence}")

        for key in ("observation", "evidence", "guidance"):
            value = raw.get(key, "")
            if not isinstance(value, str):
                raise ValueError(f"visual finding {index} '{key}' must be a string")

        normalized.append(
            VisualFinding(
                dimension=dimension,
                state=state,
                observation=raw["observation"],
                evidence=raw["evidence"],
                confidence=confidence,
                guidance=raw.get("guidance", ""),
            )
        )
        seen.add(dimension)

    normalized.sort(key=lambda finding: VISUAL_DIMENSIONS.index(finding.dimension))
    return VisualCritiqueReport(findings=tuple(normalized))


def visual_critique_contract() -> dict[str, Any]:
    """Return a provider-neutral schema suitable for a future multimodal reviewer."""
    return {
        "type": "object",
        "additionalProperties": False,
        "properties": {
            "findings": {
                "type": "array",
                "items": {
                    "type": "object",
                    "additionalProperties": False,
                    "properties": {
                        "dimension": {"type": "string", "enum": list(VISUAL_DIMENSIONS)},
                        "state": {"type": "string", "enum": sorted(OBSERVATION_STATES)},
                        "observation": {"type": "string"},
                        "evidence": {"type": "string"},
                        "confidence": {"type": "string", "enum": sorted(CONFIDENCE_LEVELS)},
                        "guidance": {"type": "string"},
                    },
                    "required": ["dimension", "state", "observation", "evidence", "confidence", "guidance"],
                },
            },
        },
        "required": ["findings"],
    }


__all__ = [
    "CONFIDENCE_LEVELS",
    "OBSERVATION_STATES",
    "VISUAL_DIMENSIONS",
    "VisualCritiqueReport",
    "VisualFinding",
    "build_visual_critique",
    "visual_critique_contract",
]
