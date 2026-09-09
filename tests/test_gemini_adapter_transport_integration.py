import base64
import json
import unittest

from core.evidence_state import EvidenceState
from core.gemini_evidence_adapter import GeminiEvidenceAdapter
from core.evidence_snapshot import EvidenceSnapshot
from core.real_evidence_provider import RealEvidenceProviderError
from scripts.run_gag001_gemini_experiment import collect_gag001_observation, load_claim

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


class ErrorClient:
    class Interactions:
        def create(self, **kwargs):
            raise TimeoutError("timeout")

    def __init__(self):
        self.interactions = self.Interactions()


def payload(verdict="confirmed", claim_key=KEY):
    return {
        "observations": [
            {
                "claim_key": claim_key,
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

    def test_interactions_schema_requires_all_evidence_fields(self):
        client = FakeClient(Response(json.dumps(payload())))
        adapter = GeminiEvidenceAdapter.from_interactions_client(
            client,
            model="gemini-test",
            image_bytes=b"image",
            mime_type="image/png",
        )
        adapter.collect((KEY,))
        required = client.interactions.calls[0]["response_format"]["schema"]["properties"]["observations"]["items"]["required"]
        self.assertEqual(
            required,
            ["claim_key", "verdict", "statement", "supporting_sources", "contradicting_sources"],
        )

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

    def test_gag001_gemini_adapter_reaches_observation_and_snapshot(self):
        claim = load_claim("gag/001/composition/arsa_primary")
        client = FakeClient(Response(json.dumps(payload("unknown", claim.key))))
        observation, snapshot = collect_gag001_observation(
            client,
            model="gemini-test",
            image_bytes=b"image",
            mime_type="image/png",
            claim=claim,
            run_id="run-gag001-test",
        )
        self.assertEqual(observation.provider, "gemini")
        self.assertEqual(observation.run_id, "run-gag001-test")
        self.assertIsInstance(snapshot, EvidenceSnapshot)
        self.assertEqual(observation.records[0].claim_key, claim.key)
        self.assertEqual(snapshot.get(claim.key).state, EvidenceState.UNKNOWN)
        self.assertEqual(snapshot.get(claim.key).supporting_sources, ())
        self.assertEqual(snapshot.canonical_evaluations, ())

    def test_gag001_gemini_provider_error_does_not_create_partial_snapshot(self):
        client = ErrorClient()
        claim = load_claim("gag/001/composition/arsa_primary")
        with self.assertRaises(RealEvidenceProviderError):
            collect_gag001_observation(
                client,
                model="gemini-test",
                image_bytes=b"image",
                mime_type="image/png",
                claim=claim,
                run_id="run-gag001-error",
            )

    def test_gag001_gemini_states_and_sources_reach_snapshot_unchanged(self):
        claim = load_claim("gag/001/composition/arsa_primary")
        cases = (
            ("confirmed", EvidenceState.CONFIRMED, ("gemini",), ()),
            ("unknown", EvidenceState.UNKNOWN, (), ()),
            ("contradicted", EvidenceState.CONTRADICTED, (), ("gemini",)),
        )
        for verdict, state, supporting, contradicting in cases:
            with self.subTest(verdict=verdict):
                client = FakeClient(Response(json.dumps(payload(verdict, claim.key))))
                observation, snapshot = collect_gag001_observation(
                    client,
                    model="gemini-test",
                    image_bytes=b"image",
                    mime_type="image/png",
                    claim=claim,
                    run_id=f"run-gag001-{verdict}",
                )
                record = observation.records[0]
                observed = snapshot.get(claim.key)
                self.assertEqual(record.state, state)
                self.assertEqual(observed.state, state)
                self.assertEqual(observed.supporting_sources, supporting)
                self.assertEqual(observed.contradicting_sources, contradicting)


if __name__ == "__main__":
    unittest.main()
