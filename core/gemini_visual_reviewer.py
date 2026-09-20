"""Gemini-backed multimodal visual reviewer.

This module owns only provider-specific transport, prompt construction, and
response normalization. The provider proposes observations; the Core-owned
visual critique contract remains the canonical boundary.
"""

from __future__ import annotations

import base64
import json
from dataclasses import dataclass
from typing import Any, Callable, Mapping, Sequence

from .visual_critique import (
    VISUAL_DIMENSIONS,
    VisualCritiqueReport,
    build_visual_critique,
)


class GeminiVisualReviewError(RuntimeError):
    """Operational or contract failure while using Gemini as visual reviewer."""


def parse_gemini_visual_critique(
    payload: Any,
    requested_dimensions: Sequence[str] = VISUAL_DIMENSIONS,
) -> VisualCritiqueReport:
    """Parse a Gemini structured visual review and require full dimension coverage."""
    if isinstance(payload, str):
        try:
            data = json.loads(payload)
        except json.JSONDecodeError as exc:
            raise GeminiVisualReviewError(
                "gemini visual review response was not valid JSON"
            ) from exc
    elif isinstance(payload, Mapping):
        data = payload
    else:
        raise GeminiVisualReviewError(
            "gemini visual review response has an invalid payload type"
        )

    findings = data.get("findings")
    if not isinstance(findings, list):
        raise GeminiVisualReviewError(
            "gemini visual review response missing findings"
        )

    requested = tuple(requested_dimensions)
    try:
        report = build_visual_critique(findings)
    except (TypeError, ValueError) as exc:
        raise GeminiVisualReviewError(
            "gemini visual review contained invalid findings"
        ) from exc

    dimensions = tuple(item.dimension for item in report.findings)
    if set(dimensions) != set(requested):
        raise GeminiVisualReviewError(
            "gemini visual review does not cover all requested dimensions"
        )

    if len(dimensions) != len(requested):
        raise GeminiVisualReviewError(
            "gemini visual review contains an invalid number of dimensions"
        )

    return report


def build_gemini_visual_review_prompt(
    review_context: str,
    requested_dimensions: Sequence[str] = VISUAL_DIMENSIONS,
) -> str:
    """Build the provider prompt without embedding Core policy."""
    dimensions = tuple(requested_dimensions)
    if not review_context.strip():
        raise ValueError("review_context must not be empty")
    if not dimensions:
        raise ValueError("requested_dimensions must not be empty")
    unknown = set(dimensions) - set(VISUAL_DIMENSIONS)
    if unknown:
        raise ValueError(
            "unsupported visual dimensions: " + ",".join(sorted(unknown))
        )

    lines = [
        "Act as a multimodal visual reviewer for a generated Arsa & Pisha artifact.",
        "Review only what is visible in the supplied image plus the review context below.",
        "Do not generate a replacement image.",
        "Do not assign a numeric score or an overall aesthetic verdict.",
        "Do not decide canon. Report observations, visible evidence, confidence, and practical guidance.",
        "For every requested dimension, return exactly one finding.",
        "Use state='observed' only when the point is directly visible,",
        "state='uncertain' when the image is ambiguous, and",
        "state='not_applicable' only when the dimension genuinely does not apply.",
        "Confidence is independent of state and must be high, medium, or low.",
        "",
        "Review context:",
        review_context.strip(),
        "",
        "Requested dimensions:",
    ]
    lines.extend(f"- {dimension}" for dimension in dimensions)
    lines.extend(
        [
            "",
            "Each finding must contain exactly these fields:",
            "dimension, state, observation, evidence, confidence, guidance.",
            "Keep observation and evidence concrete and tied to visible features.",
            "Guidance may suggest the kind of next pass that would clarify or improve the issue,",
            "but must not prescribe a complete gag or silently rewrite canon.",
        ]
    )
    return "\n".join(lines)


def build_gemini_visual_review_transport(
    client: Any,
    *,
    model: str,
    image_bytes: bytes,
    mime_type: str,
) -> Callable[[dict[str, Any]], Any]:
    """Build an injected Gemini Interactions API request function."""
    def request(payload: dict[str, Any]) -> Any:
        """Send one image-review request through the injected Gemini client."""
        try:
            interaction = client.interactions.create(
                model=model,
                input=[
                    {
                        "type": "image",
                        "data": base64.b64encode(image_bytes).decode("utf-8"),
                        "mime_type": mime_type,
                    },
                    {"type": "text", "text": payload["prompt"]},
                ],
                response_format={
                    "type": "text",
                    "mime_type": "application/json",
                    "schema": {
                        "type": "object",
                        "properties": {
                            "findings": {
                                "type": "array",
                                "items": {
                                    "type": "object",
                                    "properties": {
                                        "dimension": {
                                            "type": "string",
                                            "enum": list(VISUAL_DIMENSIONS),
                                        },
                                        "state": {
                                            "type": "string",
                                            "enum": [
                                                "observed",
                                                "uncertain",
                                                "not_applicable",
                                            ],
                                        },
                                        "observation": {"type": "string"},
                                        "evidence": {"type": "string"},
                                        "confidence": {
                                            "type": "string",
                                            "enum": ["high", "medium", "low"],
                                        },
                                        "guidance": {"type": "string"},
                                    },
                                    "required": [
                                        "dimension",
                                        "state",
                                        "observation",
                                        "evidence",
                                        "confidence",
                                        "guidance",
                                    ],
                                },
                            }
                        },
                        "required": ["findings"],
                    },
                },
            )
        except Exception as exc:
            raise GeminiVisualReviewError(
                "gemini visual review request failed"
            ) from exc

        text = getattr(interaction, "output_text", None)
        if not isinstance(text, str) or not text.strip():
            raise GeminiVisualReviewError(
                "gemini visual review response contained no structured text"
            )
        return text

    return request


@dataclass(frozen=True)
class GeminiVisualReviewer:
    """Provider adapter that returns only a VisualCritiqueReport."""

    request: Callable[[dict[str, Any]], Any]
    parse: Callable[
        [Any, Sequence[str]], VisualCritiqueReport
    ] = parse_gemini_visual_critique

    def review(
        self,
        *,
        review_context: str,
        requested_dimensions: Sequence[str] = VISUAL_DIMENSIONS,
    ) -> VisualCritiqueReport:
        """Review one already-supplied image without making Core decisions."""
        dimensions = tuple(requested_dimensions)
        prompt = build_gemini_visual_review_prompt(
            review_context,
            dimensions,
        )
        try:
            payload = self.request({"prompt": prompt, "requested_dimensions": dimensions})
            return self.parse(payload, dimensions)
        except GeminiVisualReviewError:
            raise
        except Exception as exc:
            raise GeminiVisualReviewError(
                "gemini visual reviewer failed"
            ) from exc

    @classmethod
    def from_interactions_client(
        cls,
        client: Any,
        *,
        model: str,
        image_bytes: bytes,
        mime_type: str,
    ) -> "GeminiVisualReviewer":
        """Build the reviewer around the existing Gemini Interactions transport."""
        return cls(
            request=build_gemini_visual_review_transport(
                client,
                model=model,
                image_bytes=image_bytes,
                mime_type=mime_type,
            )
        )


__all__ = [
    "GeminiVisualReviewer",
    "GeminiVisualReviewError",
    "build_gemini_visual_review_prompt",
    "build_gemini_visual_review_transport",
    "parse_gemini_visual_critique",
]
