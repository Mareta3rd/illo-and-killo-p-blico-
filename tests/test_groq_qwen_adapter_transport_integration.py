import json
import unittest

from core.evidence_state import EvidenceState
from core.groq_qwen_evidence_adapter import GroqQwenEvidenceAdapter
from core.groq_qwen_real_transport import ModelProfile


KEY = "gag/001/composition/illo_primary"


class FakeResponses:
    def __init__(self, response):
        self.response, self.calls = response, []

    def create(self, **kwargs):
        self.calls.append(kwargs)
        return self.response


class FakeClient:
    def __init__(self, response):
        self.responses = FakeResponses(response)


class Response:
    def __init__(self):
        self.output_text = json.dumps({"observations": [{
            "claim_key": KEY,
            "statement": "Illo is the primary visual subject.",
            "verdict": "unknown",
            "supporting_sources": [],
            "contradicting_sources": [],
        }]})


class GroqQwenAdapterTransportIntegrationTests(unittest.TestCase):
    def test_fake_responses_client_reaches_external_record(self):
        client = FakeClient(Response())
        adapter = GroqQwenEvidenceAdapter.from_responses_client(
            client,
            model="qwen/test",
            model_profile=ModelProfile("qwen/test", True, True, True, True),
            image_bytes=b"image",
            mime_type="image/png",
        )
        record = adapter.collect((KEY,))[0]
        self.assertEqual(record.claim_key, KEY)
        self.assertEqual(record.state, EvidenceState.UNKNOWN)
        self.assertFalse(hasattr(adapter, "evaluate"))
        self.assertFalse(hasattr(adapter, "accept"))
        self.assertEqual(client.responses.calls[0]["model"], "qwen/test")


if __name__ == "__main__":
    unittest.main()