import unittest

from core.evidence_state import EvidenceState
from core.external_evidence_adapter import ExternalEvidenceRecord
from core.real_evidence_provider import (
    RealEvidenceProviderAdapter,
    RealEvidenceProviderError,
)


KEY = "fauna/mosquito_tigre/readable_as_mosquito"


class RealEvidenceProviderTests(unittest.TestCase):
    def test_fetch_receives_requested_keys_and_parser_records_pass_through(self):
        seen = []
        record = ExternalEvidenceRecord(
            KEY,
            "candidate is visually readable as mosquito",
            EvidenceState.CONFIRMED,
            supporting_sources=("real-provider",),
        )

        def fetch(keys):
            seen.append(tuple(keys))
            return {"raw": "provider-response"}

        def parse(payload):
            self.assertEqual(payload, {"raw": "provider-response"})
            return (record,)

        adapter = RealEvidenceProviderAdapter(fetch, parse)
        self.assertEqual(adapter.collect((KEY,)), (record,))
        self.assertEqual(seen, [(KEY,)])

    def test_transport_failure_becomes_provider_error(self):
        def fetch(_keys):
            raise TimeoutError("timeout")

        adapter = RealEvidenceProviderAdapter(fetch, lambda payload: ())
        with self.assertRaises(RealEvidenceProviderError) as raised:
            adapter.collect((KEY,))
        self.assertIn("request failed", str(raised.exception))

    def test_parse_failure_becomes_provider_error(self):
        adapter = RealEvidenceProviderAdapter(lambda _keys: {"ok": True}, lambda _payload: 42)
        with self.assertRaises(RealEvidenceProviderError) as raised:
            adapter.collect((KEY,))
        self.assertIn("could not be parsed", str(raised.exception))

    def test_invalid_parser_record_is_rejected_before_core(self):
        adapter = RealEvidenceProviderAdapter(lambda _keys: {}, lambda _payload: (object(),))
        with self.assertRaises(RealEvidenceProviderError):
            adapter.collect((KEY,))

    def test_unknown_state_is_preserved_as_an_explicit_record(self):
        record = ExternalEvidenceRecord(KEY, "observation unavailable", EvidenceState.UNKNOWN)
        adapter = RealEvidenceProviderAdapter(lambda _keys: {}, lambda _payload: (record,))
        self.assertEqual(adapter.collect((KEY,))[0].state, EvidenceState.UNKNOWN)


if __name__ == "__main__":
    unittest.main()
