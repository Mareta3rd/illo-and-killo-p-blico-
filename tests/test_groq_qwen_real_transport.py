import base64
import json
import unittest
from unittest.mock import patch

from core.evidence_state import EvidenceState
from core.groq_qwen_real_transport import (
    DEFAULT_GROQ_BASE_URL,
    DEFAULT_GROQ_QWEN_MODEL,
    GROQ_QWEN_MODEL_PROFILES,
    GROQ_QWEN_EVIDENCE_SCHEMA,
    ModelProfile,
    build_groq_qwen_client,
    build_groq_qwen_responses_transport,
    get_groq_qwen_model_profile,
    parse_groq_qwen_structured_evidence,
)
from core.real_evidence_provider import RealEvidenceProviderError


KEY = "fauna/mosquito_tigre/readable_as_mosquito"


class FakeResponses:
    def __init__(self, response=None, error=None):
        self.response, self.error, self.calls = response, error, []

    def create(self, **kwargs):
        self.calls.append(kwargs)
        if self.error:
            raise self.error
        return self.response


class FakeClient:
    def __init__(self, response=None, error=None):
        self.responses = FakeResponses(response, error)


class Response:
    def __init__(self, text):
        self.output_text = text


class RealisticProviderError(Exception):
    def __init__(self, message, status_code, code):
        super().__init__(message)
        self.status_code = status_code
        self.code = code


class GroqQwenRealTransportTests(unittest.TestCase):
    def payload(self, verdict="unknown"):
        return {"observations": [{
            "claim_key": KEY,
            "statement": "candidate is visually readable as mosquito",
            "verdict": verdict,
            "supporting_sources": ["image"] if verdict == "confirmed" else [],
            "contradicting_sources": ["image"] if verdict == "contradicted" else [],
        }]}

    def transport(self, response=None, error=None, model=DEFAULT_GROQ_QWEN_MODEL):
        return FakeClient(response, error), build_groq_qwen_responses_transport(
            FakeClient(response, error), model=model, image_bytes=b"image", mime_type="image/png"
        )

    def test_client_factory_uses_configurable_base_url(self):
        with patch("openai.OpenAI") as openai_client:
            build_groq_qwen_client(base_url="https://example.test/v1")
        openai_client.assert_called_once_with(api_key=None, base_url="https://example.test/v1")

    def test_defaults_are_groq_endpoint_and_qwen_model(self):
        self.assertEqual(DEFAULT_GROQ_QWEN_MODEL, "qwen/qwen3.8-27b")
        self.assertEqual(DEFAULT_GROQ_BASE_URL, "https://api.groq.com/openai/v1")

    def test_model_profiles_declare_structured_output_capability(self):
        self.assertTrue(get_groq_qwen_model_profile("qwen/qwen3.8-27b").structured_outputs)
        self.assertFalse(get_groq_qwen_model_profile("qwen/qwen3.6-27b").structured_outputs)
        self.assertEqual(set(GROQ_QWEN_MODEL_PROFILES), {"qwen/qwen3.6-27b", "qwen/qwen3.8-27b"})

    def test_model_selection_is_explicit(self):
        client = FakeClient(Response(json.dumps(self.payload())))
        request = build_groq_qwen_responses_transport(
            client, model="qwen/qwen3.8-27b", image_bytes=b"x", mime_type="image/png"
        )
        request({"prompt": "evaluate"})
        self.assertEqual(client.responses.calls[0]["model"], "qwen/qwen3.8-27b")

    def test_qwen36_is_rejected_without_structured_outputs(self):
        with self.assertRaisesRegex(RealEvidenceProviderError, "structured_outputs"):
            build_groq_qwen_responses_transport(
                FakeClient(), model="qwen/qwen3.6-27b", image_bytes=b"x", mime_type="image/png"
            )

    def test_no_fallback_to_json_object_mode(self):
        client = FakeClient()
        with self.assertRaises(RealEvidenceProviderError):
            build_groq_qwen_responses_transport(
                client, model="qwen/qwen3.6-27b", image_bytes=b"x", mime_type="image/png"
            )
        self.assertEqual(client.responses.calls, [])

    def test_custom_profile_can_be_selected_for_fake_transport(self):
        profile = ModelProfile("qwen/test", True, True, True, True)
        client = FakeClient(Response(json.dumps(self.payload())))
        build_groq_qwen_responses_transport(
            client,
            model="qwen/test",
            model_profile=profile,
            image_bytes=b"x",
            mime_type="image/png",
        )({"prompt": "evaluate"})

    def test_request_contains_model_text_image_and_base64_mime(self):
        client = FakeClient(Response(json.dumps(self.payload())))
        request = build_groq_qwen_responses_transport(
            client,
            model="qwen/test",
            model_profile=ModelProfile("qwen/test", True, True, True, True),
            image_bytes=b"image-bytes",
            mime_type="image/jpeg",
        )
        request({"prompt": "evaluate"})
        call = client.responses.calls[0]
        content = call["input"][0]["content"]
        self.assertEqual(call["model"], "qwen/test")
        self.assertEqual(content[0], {"type": "input_text", "text": "evaluate"})
        self.assertEqual(content[1]["type"], "input_image")
        self.assertEqual(content[1]["image_url"], "data:image/jpeg;base64," + base64.b64encode(b"image-bytes").decode("ascii"))

    def test_request_contains_strict_closed_schema(self):
        client = FakeClient(Response(json.dumps(self.payload())))
        build_groq_qwen_responses_transport(client, image_bytes=b"x", mime_type="image/png")({"prompt": "evaluate"})
        schema = client.responses.calls[0]["text"]["format"]
        item = GROQ_QWEN_EVIDENCE_SCHEMA["properties"]["observations"]["items"]
        self.assertEqual(schema["type"], "json_schema")
        self.assertTrue(schema["strict"])
        self.assertFalse(GROQ_QWEN_EVIDENCE_SCHEMA["additionalProperties"])
        self.assertFalse(item["additionalProperties"])
        self.assertEqual(schema["schema"], GROQ_QWEN_EVIDENCE_SCHEMA)

    def test_output_text_is_returned(self):
        expected = json.dumps(self.payload())
        client = FakeClient(Response(expected))
        request = build_groq_qwen_responses_transport(client, image_bytes=b"x", mime_type="image/png")
        self.assertEqual(request({"prompt": "evaluate"}), expected)

    def test_transport_error_is_boundary_error(self):
        client = FakeClient(error=TimeoutError("timeout"))
        request = build_groq_qwen_responses_transport(client, image_bytes=b"x", mime_type="image/png")
        with self.assertRaisesRegex(RealEvidenceProviderError, "groq qwen responses request failed"):
            request({"prompt": "evaluate"})

    def test_transport_error_preserves_safe_provider_details(self):
        original = RealisticProviderError(
            "invalid request; Authorization: Bearer secret-token api_key=secret-key",
            400,
            "invalid_request_error",
        )
        client = FakeClient(error=original)
        request = build_groq_qwen_responses_transport(client, image_bytes=b"x", mime_type="image/png")

        with self.assertRaises(RealEvidenceProviderError) as raised:
            request({"prompt": "evaluate"})

        error = raised.exception
        self.assertIs(error.__cause__, original)
        self.assertIn("RealisticProviderError", str(error))
        self.assertIn("status_code=400", str(error))
        self.assertIn("code=invalid_request_error", str(error))
        self.assertNotIn("secret-token", str(error))
        self.assertNotIn("secret-key", str(error))

    def test_parser_preserves_states(self):
        for verdict, state in (("confirmed", EvidenceState.CONFIRMED), ("contradicted", EvidenceState.CONTRADICTED), ("unknown", EvidenceState.UNKNOWN)):
            with self.subTest(verdict=verdict):
                self.assertEqual(parse_groq_qwen_structured_evidence(self.payload(verdict), (KEY,))[0].state, state)


if __name__ == "__main__":
    unittest.main()