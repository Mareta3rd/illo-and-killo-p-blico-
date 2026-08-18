from pathlib import Path
import unittest

from core.external_evidence_adapter import ExternalEvidenceRecord
from core.evidence_state import EvidenceState
from core.real_evidence_provider import RealEvidenceProviderAdapter, RealEvidenceProviderError

ROOT = Path(__file__).resolve().parents[1]
KEY = "fauna/mosquito_tigre/readable_as_mosquito"


class RealProviderConformanceTests(unittest.TestCase):
    def _record(self, state=EvidenceState.UNKNOWN):
        return ExternalEvidenceRecord(
            KEY,
            "candidate is visually readable as mosquito",
            state,
            supporting_sources=("real-provider-test",) if state is EvidenceState.CONFIRMED else (),
            contradicting_sources=("real-provider-test",) if state is EvidenceState.CONTRADICTED else (),
        )

    def test_fetch_receives_requested_keys_without_mutation(self):
        seen = []
        requested = [KEY]

        def fetch(keys):
            seen.append(tuple(keys))
            return {"payload": "ok"}

        adapter = RealEvidenceProviderAdapter(fetch=fetch, parse=lambda payload: (self._record(),))
        adapter.collect(requested)

        self.assertEqual(seen, [(KEY,)])
        self.assertEqual(requested, [KEY])

    def test_parser_output_is_passed_through_as_records(self):
        record = self._record(EvidenceState.CONFIRMED)
        adapter = RealEvidenceProviderAdapter(fetch=lambda keys: object(), parse=lambda payload: (record,))

        result = adapter.collect((KEY,))

        self.assertEqual(result, (record,))
        self.assertEqual(result[0].state, EvidenceState.CONFIRMED)
        self.assertEqual(result[0].supporting_sources, ("real-provider-test",))

    def test_fetch_failure_is_translated_to_boundary_error(self):
        def fetch(keys):
            raise TimeoutError("network timeout")

        adapter = RealEvidenceProviderAdapter(fetch=fetch, parse=lambda payload: ())

        with self.assertRaises(RealEvidenceProviderError) as raised:
            adapter.collect((KEY,))
        self.assertEqual(str(raised.exception), "real provider request failed")

    def test_parse_failure_is_translated_to_boundary_error(self):
        adapter = RealEvidenceProviderAdapter(
            fetch=lambda keys: {"payload": "bad"},
            parse=lambda payload: (_ for _ in ()).throw(ValueError("bad payload")),
        )

        with self.assertRaises(RealEvidenceProviderError) as raised:
            adapter.collect((KEY,))
        self.assertEqual(str(raised.exception), "real provider response could not be parsed")

    def test_invalid_parser_record_is_rejected(self):
        adapter = RealEvidenceProviderAdapter(fetch=lambda keys: {}, parse=lambda payload: ({"bad": True},))

        with self.assertRaises(RealEvidenceProviderError) as raised:
            adapter.collect((KEY,))
        self.assertEqual(str(raised.exception), "real provider parser returned an invalid record")

    def test_adapter_does_not_make_core_decisions(self):
        adapter = RealEvidenceProviderAdapter(fetch=lambda keys: {}, parse=lambda payload: (self._record(),))

        self.assertFalse(hasattr(adapter, "evaluate"))
        self.assertFalse(hasattr(adapter, "accept"))
        self.assertFalse(hasattr(adapter, "reject"))


if __name__ == "__main__":
    unittest.main()
