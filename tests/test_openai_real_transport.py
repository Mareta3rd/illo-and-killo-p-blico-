import base64
import json
import unittest

from core.evidence_state import EvidenceState
from core.openai_real_transport import (
    OPENAI_EVIDENCE_SCHEMA,
    build_openai_responses_transport,
    parse_openai_structured_evidence,
)
from core.real_evidence_provider import RealEvidenceProviderError


KEY = "fauna/mosquito_tigre/readable_as_mosquito"


class FakeResponses:
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
        self.responses = FakeResponses(response=response, error=error)


class Response:
    def __init__(self, text):
        self.output_text = text


class OpenAIRealTransportTests(unittest.TestCase):
    def _payload(self, verdict="unknown"):
        return {
            "observations": [
                {
                    "claim_key": KEY,
                    "statement": "candidate is visually readable as mosquito",
                    "verdict": verdict,
                    "supporting_sources": ["image"] if verdict == "confirmed" else [],
                    "contradicting_sources": ["image"] if verdict == "contradicted" else [],
                }
            ]
        }

    def test_request_contains_text_and_image_with_model(self):
        client = FakeClient(Response(json.dumps(self._payload())))
        request = build_openai_responses_transport(
            client, model="openai-test", image_bytes=b"image-bytes", mime_type="image/png"
        )

        request({"prompt": "evaluate this claim"})
        call = client.responses.calls[0]
        content = call["input"][0]["content"]

        self.assertEqual(call["model"], "openai-test")
        self.assertEqual(content[0], {"type": "input_text", "text": "evaluate this claim"})
        self.assertEqual(content[1]["type"], "input_image")
        self.assertEqual(
            content[1]["image_url"],
            "data:image/png;base64," + base64.b64encode(b"image-bytes").decode("ascii"),
        )

    def test_request_contains_strict_schema_with_required_fields(self):
        client = FakeClient(Response(json.dumps(self._payload())))
        request = build_openai_responses_transport(
            client, model="openai-test", image_bytes=b"image", mime_type="image/jpeg"
        )

        request({"prompt": "evaluate"})
        schema_config = client.responses.calls[0]["text"]["format"]
        item_schema = OPENAI_EVIDENCE_SCHEMA["properties"]["observations"]["items"]

        self.assertEqual(schema_config["type"], "json_schema")
        self.assertTrue(schema_config["strict"])
        self.assertEqual(schema_config["schema"], OPENAI_EVIDENCE_SCHEMA)
        self.assertFalse(OPENAI_EVIDENCE_SCHEMA["additionalProperties"])
        self.assertFalse(item_schema["additionalProperties"])
        self.assertEqual(
            item_schema["required"],
            ["claim_key", "statement", "verdict", "supporting_sources", "contradicting_sources"],
        )

    def test_output_text_is_returned_for_parser(self):
        expected = json.dumps(self._payload())
        client = FakeClient(Response(expected))
        request = build_openai_responses_transport(
            client, model="openai-test", image_bytes=b"image", mime_type="image/png"
        )

        self.assertEqual(request({"prompt": "evaluate"}), expected)

    def test_transport_error_becomes_boundary_error(self):
        client = FakeClient(error=TimeoutError("timeout"))
        request = build_openai_responses_transport(
            client, model="openai-test", image_bytes=b"image", mime_type="image/png"
        )

        with self.assertRaisesRegex(RealEvidenceProviderError, "openai responses request failed"):
            request({"prompt": "evaluate"})

    def test_parser_preserves_all_supported_states(self):
        for verdict, state in (("confirmed", EvidenceState.CONFIRMED), ("contradicted", EvidenceState.CONTRADICTED), ("unknown", EvidenceState.UNKNOWN)):
            with self.subTest(verdict=verdict):
                record = parse_openai_structured_evidence(self._payload(verdict), (KEY,))[0]
                self.assertEqual(record.state, state)


if __name__ == "__main__":
    unittest.main()