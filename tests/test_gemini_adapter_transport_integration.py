import base64
import json
import unittest

from core.evidence_state import EvidenceState
from core.gemini_evidence_adapter import GeminiEvidenceAdapter

KEY = "fauna/mosquito_tigre/readable_as_mosquito"


class Response:
    def __init__(self, text):
        self.output_text = text


class FakeInteractions:
    def __init__(self, response):
        self.response = response
        self.calls = []

    def create(self, **kwargs):
        self.calls.append(kwargs)
        return self.response


class FakeClient:
    def __init__(self, response):
        self.interactions = FakeInteractions(response)


def payload(verdict="confirmed"):
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


class GeminiAdapterTransportIntegrationTests(unittest.TestCase):
    def test_interactions_client_is_connected_to_canonical_adapter(self):
        client = FakeClient(Response(json.dumps(payload("confirmed"))))
        adapter = GeminiEvidenceAdapter.from_interactions_client(
            client,
            model="gemini-test",
            image_bytes=b"image",
            mime_type="image/png",
        )

        records = adapter.collect((KEY,))

        self.assertEqual(len(records), 1)
        self.assertEqual(records[0].claim_key, KEY)
        self.assertEqual(records[0].state, EvidenceState.CONFIRMED)
        self.assertEqual(client.interactions.calls[0]["model"], "gemini-test")

    def test_interactions_transport_preserves_unknown(self):
        client = FakeClient(Response(json.dumps(payload("unknown"))))
        adapter = GeminiEvidenceAdapter.from_interactions_client(
            client,
            model="gemini-test",
            image_bytes=b"image",
            mime_type="image/png",
        )

        record = adapter.collect((KEY,))[0]

        self.assertEqual(record.state, EvidenceState.UNKNOWN)
        self.assertEqual(record.supporting_sources, ())
        self.assertEqual(record.contradicting_sources, ())

    def test_interactions_payload_contains_image_and_requested_claim(self):
        client = FakeClient(Response(json.dumps(payload())))
        adapter = GeminiEvidenceAdapter.from_interactions_client(
            client,
            model="gemini-test",
            image_bytes=b"image-bytes",
            mime_type="image/jpeg",
        )

        adapter.collect((KEY,))
        call = client.interactions.calls[0]

        self.assertEqual(call["input"][0]["data"], base64.b64encode(b"image-bytes").decode("utf-8"))
        self.assertEqual(call["input"][0]["mime_type"], "image/jpeg")
        self.assertIn(KEY, call["input"][1]["text"])

    def test_adapter_does_not_evaluate_or_accept(self):
        client = FakeClient(Response(json.dumps(payload())))
        adapter = GeminiEvidenceAdapter.from_interactions_client(
            client,
            model="gemini-test",
            image_bytes=b"image",
            mime_type="image/png",
        )
        self.assertFalse(hasattr(adapter, "evaluate"))
        self.assertFalse(hasattr(adapter, "accept"))


if __name__ == "__main__":
    unittest.main()
