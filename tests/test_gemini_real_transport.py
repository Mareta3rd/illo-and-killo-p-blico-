import base64
import json
import unittest

from core.evidence_state import EvidenceState
from core.external_evidence_adapter import ExternalEvidenceRecord
from core.gemini_real_transport import (
    build_gemini_interactions_transport,
    parse_gemini_structured_evidence,
)
from core.real_evidence_provider import RealEvidenceProviderError


KEY = "fauna/mosquito_tigre/readable_as_mosquito"


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


class GeminiRealTransportTests(unittest.TestCase):
    def _payload(self, verdict="unknown"):
        return {
            "observations": [
                {
                    "claim_key": KEY,
                    "verdict": verdict,
                    "statement": "candidate is visually readable as mosquito",
                    "supporting_sources": ["gemini"] if verdict == "confirmed" else [],
                    "contradicting_sources": ["gemini"] if verdict == "contradicted" else [],
                }
            ]
        }

    def test_parser_builds_unknown_record(self):
        records = parse_gemini_structured_evidence(self._payload(), (KEY,))
        self.assertEqual(records[0].state, EvidenceState.UNKNOWN)
        self.assertEqual(records[0].claim_key, KEY)

    def test_parser_preserves_confirmed_and_contradicted_states(self):
        confirmed = parse_gemini_structured_evidence(self._payload("confirmed"), (KEY,))[0]
        contradicted = parse_gemini_structured_evidence(self._payload("contradicted"), (KEY,))[0]
        self.assertEqual(confirmed.state, EvidenceState.CONFIRMED)
        self.assertEqual(contradicted.state, EvidenceState.CONTRADICTED)

    def test_parser_rejects_missing_claims(self):
        with self.assertRaises(RealEvidenceProviderError):
            parse_gemini_structured_evidence({"observations": []}, (KEY,))

    def test_parser_rejects_unrequested_claim(self):
        payload = self._payload()
        payload["observations"][0]["claim_key"] = "fauna/mosquito_tigre/invented"
        with self.assertRaises(RealEvidenceProviderError):
            parse_gemini_structured_evidence(payload, (KEY,))

    def test_parser_rejects_invalid_state_source_combination(self):
        payload = self._payload("unknown")
        payload["observations"][0]["supporting_sources"] = ["gemini"]
        with self.assertRaises(RealEvidenceProviderError):
            parse_gemini_structured_evidence(payload, (KEY,))

    def test_interactions_transport_sends_image_and_structured_schema(self):
        client = FakeClient(response=Response(json.dumps(self._payload())))
        request = build_gemini_interactions_transport(
            client,
            model="gemini-test",
            image_bytes=b"image-bytes",
            mime_type="image/png",
        )
        text = request({"prompt": "evaluate this claim"})
        call = client.interactions.calls[0]
        self.assertEqual(text, json.dumps(self._payload()))
        self.assertEqual(call["model"], "gemini-test")
        self.assertEqual(call["input"][0]["data"], base64.b64encode(b"image-bytes").decode("utf-8"))
        self.assertEqual(call["input"][0]["mime_type"], "image/png")
        self.assertEqual(call["response_format"]["mime_type"], "application/json")
        self.assertIn("observations", call["response_format"]["schema"]["properties"])

    def test_interactions_failure_is_translated_to_boundary_error(self):
        client = FakeClient(error=TimeoutError("timeout"))
        request = build_gemini_interactions_transport(
            client,
            model="gemini-test",
            image_bytes=b"image-bytes",
            mime_type="image/png",
        )
        with self.assertRaises(RealEvidenceProviderError) as raised:
            request({"prompt": "evaluate this claim"})
        self.assertEqual(str(raised.exception), "gemini interactions request failed")


if __name__ == "__main__":
    unittest.main()
