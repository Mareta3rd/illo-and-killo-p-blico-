import unittest

from core.evidence_state import EvidenceState
from core.external_evidence_adapter import ExternalEvidenceRecord
from core.gemini_evidence_adapter import GeminiEvidenceAdapter, build_gemini_transport
from core.real_evidence_provider import RealEvidenceProviderError


KEY = "fauna/mosquito_tigre/readable_as_mosquito"


class GeminiEvidenceAdapterTests(unittest.TestCase):
    def _record(self, state=EvidenceState.UNKNOWN):
        return ExternalEvidenceRecord(
            KEY,
            "candidate is visually readable as mosquito",
            state,
            supporting_sources=("gemini",) if state is EvidenceState.CONFIRMED else (),
            contradicting_sources=("gemini",) if state is EvidenceState.CONTRADICTED else (),
        )

    def test_request_contains_only_requested_canonical_keys(self):
        seen = []

        def request(payload):
            seen.append(payload)
            return object()

        adapter = GeminiEvidenceAdapter(request=request, parse=lambda payload, keys: (self._record(),))
        adapter.collect((KEY,))

        self.assertEqual(seen[0]["requested_keys"], (KEY,))
        self.assertNotIn("accept", seen[0]["prompt"].lower())

    def test_parser_output_preserves_confirmed_state(self):
        record = self._record(EvidenceState.CONFIRMED)
        adapter = GeminiEvidenceAdapter(request=lambda payload: object(), parse=lambda payload, keys: (record,))
        result = adapter.collect((KEY,))
        self.assertEqual(result, (record,))
        self.assertEqual(result[0].state, EvidenceState.CONFIRMED)

    def test_parser_output_preserves_unknown_state(self):
        record = self._record(EvidenceState.UNKNOWN)
        adapter = GeminiEvidenceAdapter(request=lambda payload: object(), parse=lambda payload, keys: (record,))
        result = adapter.collect((KEY,))
        self.assertEqual(result[0].state, EvidenceState.UNKNOWN)

    def test_transport_delegates_model_and_prompt(self):
        seen = []

        def client_generate(**kwargs):
            seen.append(kwargs)
            return {"ok": True}

        request = build_gemini_transport(client_generate, model="gemini-test")
        result = request({"prompt": "hello", "requested_keys": (KEY,)})

        self.assertEqual(result, {"ok": True})
        self.assertEqual(seen, [{"model": "gemini-test", "prompt": "hello"}])

    def test_transport_failure_becomes_boundary_error(self):
        def client_generate(**kwargs):
            raise TimeoutError("timeout")

        request = build_gemini_transport(client_generate, model="gemini-test")
        with self.assertRaises(RealEvidenceProviderError) as raised:
            request({"prompt": "hello", "requested_keys": (KEY,)})
        self.assertEqual(str(raised.exception), "gemini request failed")

    def test_adapter_has_no_core_decision_methods(self):
        adapter = GeminiEvidenceAdapter(request=lambda payload: {}, parse=lambda payload, keys: ())
        self.assertFalse(hasattr(adapter, "evaluate"))
        self.assertFalse(hasattr(adapter, "accept"))
        self.assertFalse(hasattr(adapter, "reject"))


if __name__ == "__main__":
    unittest.main()
