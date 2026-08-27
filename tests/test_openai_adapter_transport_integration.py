import json
import unittest

from core.evidence_state import EvidenceState
from core.openai_evidence_adapter import OpenAIEvidenceAdapter


KEY = "gag/001/composition/illo_primary"


class FakeResponses:
    def __init__(self, response):
        self.response = response
        self.calls = []

    def create(self, **kwargs):
        self.calls.append(kwargs)
        return self.response


class FakeClient:
    def __init__(self, response):
        self.responses = FakeResponses(response)


class Response:
    def __init__(self, payload):
        self.output_text = json.dumps(payload)


class OpenAIAdapterTransportIntegrationTests(unittest.TestCase):
    def test_responses_client_reaches_external_record_only(self):
        client = FakeClient(
            Response(
                {
                    "observations": [
                        {
                            "claim_key": KEY,
                            "statement": "Illo is the primary visual subject.",
                            "verdict": "unknown",
                            "supporting_sources": [],
                            "contradicting_sources": [],
                        }
                    ]
                }
            )
        )
        adapter = OpenAIEvidenceAdapter.from_responses_client(
            client,
            model="openai-test",
            image_bytes=b"image",
            mime_type="image/png",
        )

        records = adapter.collect((KEY,))

        self.assertEqual(records[0].claim_key, KEY)
        self.assertEqual(records[0].state, EvidenceState.UNKNOWN)
        self.assertEqual(records[0].supporting_sources, ())
        self.assertFalse(hasattr(adapter, "evaluate"))
        self.assertFalse(hasattr(adapter, "accept"))
        self.assertFalse(hasattr(adapter, "human_review"))


if __name__ == "__main__":
    unittest.main()