import base64
import json
import unittest

from core.gemini_visual_reviewer import (
    GeminiVisualReviewer,
    GeminiVisualReviewError,
    build_gemini_visual_review_prompt,
    build_gemini_visual_review_transport,
    parse_gemini_visual_critique,
)
from core.visual_critique import VISUAL_DIMENSIONS, VisualCritiqueReport


class FakeInteractions:
    def __init__(self, response=None, error=None):
        self.response = response
        self.error = error
        self.calls = []

    def create(self, **kwargs):
        self.calls.append(kwargs)
        if self.error:
            raise self.error
        return self.response


class FakeClient:
    def __init__(self, response=None, error=None):
        self.interactions = FakeInteractions(response=response, error=error)


class Response:
    def __init__(self, text):
        self.output_text = text


class GeminiVisualReviewerTests(unittest.TestCase):
    def _payload(self):
        return {
            "findings": [
                {
                    "dimension": dimension,
                    "state": "observed",
                    "observation": f"{dimension} observation",
                    "evidence": f"visible evidence for {dimension}",
                    "confidence": "high",
                    "guidance": f"guidance for {dimension}",
                }
                for dimension in VISUAL_DIMENSIONS
            ]
        }

    def test_parser_returns_closed_report_with_all_dimensions(self):
        report = parse_gemini_visual_critique(self._payload())
        self.assertIsInstance(report, VisualCritiqueReport)
        self.assertEqual(
            [finding.dimension for finding in report.findings],
            list(VISUAL_DIMENSIONS),
        )

    def test_parser_rejects_incomplete_dimension_coverage(self):
        payload = self._payload()
        payload["findings"] = payload["findings"][:-1]
        with self.assertRaises(GeminiVisualReviewError):
            parse_gemini_visual_critique(payload)

    def test_parser_rejects_malformed_findings(self):
        payload = self._payload()
        payload["findings"][0]["confidence"] = "certain"
        with self.assertRaises(GeminiVisualReviewError):
            parse_gemini_visual_critique(payload)

    def test_prompt_requires_observation_not_scoring(self):
        prompt = build_gemini_visual_review_prompt(
            "Arsa is white with a yellow crest and green scarf.",
        )
        self.assertIn("Do not assign a numeric score", prompt)
        self.assertIn("Do not decide canon", prompt)
        self.assertIn("For every requested dimension, return exactly one finding", prompt)
        for dimension in VISUAL_DIMENSIONS:
            self.assertIn(dimension, prompt)

    def test_reviewer_returns_report_without_core_decision_methods(self):
        reviewer = GeminiVisualReviewer(
            request=lambda payload: json.dumps(self._payload())
        )
        report = reviewer.review(review_context="controlled Arsa & Pisha image")
        self.assertIsInstance(report, VisualCritiqueReport)
        self.assertFalse(hasattr(reviewer, "accept"))
        self.assertFalse(hasattr(reviewer, "reject"))
        self.assertFalse(hasattr(reviewer, "evaluate"))

    def test_prompt_payload_preserves_requested_dimensions(self):
        seen = []

        def request(payload):
            seen.append(payload)
            return json.dumps(self._payload())

        reviewer = GeminiVisualReviewer(request=request)
        reviewer.review(review_context="controlled visual review")
        self.assertEqual(seen[0]["requested_dimensions"], VISUAL_DIMENSIONS)
        self.assertIn("character_fidelity", seen[0]["prompt"])

    def test_interactions_transport_sends_image_and_structured_schema(self):
        client = FakeClient(response=Response(json.dumps(self._payload())))
        request = build_gemini_visual_review_transport(
            client,
            model="gemini-test",
            image_bytes=b"image-bytes",
            mime_type="image/png",
        )
        text = request({"prompt": "review this image"})
        call = client.interactions.calls[0]
        self.assertEqual(text, json.dumps(self._payload()))
        self.assertEqual(call["model"], "gemini-test")
        self.assertEqual(
            call["input"][0]["data"],
            base64.b64encode(b"image-bytes").decode("utf-8"),
        )
        self.assertEqual(call["input"][0]["mime_type"], "image/png")
        self.assertEqual(call["response_format"]["mime_type"], "application/json")
        self.assertIn(
            "findings",
            call["response_format"]["schema"]["properties"],
        )

    def test_interactions_failure_is_translated_to_boundary_error(self):
        client = FakeClient(error=TimeoutError("timeout"))
        request = build_gemini_visual_review_transport(
            client,
            model="gemini-test",
            image_bytes=b"image-bytes",
            mime_type="image/png",
        )
        with self.assertRaises(GeminiVisualReviewError) as raised:
            request({"prompt": "review this image"})
        self.assertEqual(
            str(raised.exception),
            "gemini visual review request failed",
        )

    def test_empty_review_context_is_rejected(self):
        with self.assertRaises(ValueError):
            build_gemini_visual_review_prompt("")


if __name__ == "__main__":
    unittest.main()
