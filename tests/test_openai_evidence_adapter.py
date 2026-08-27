import unittest

from core.evidence_state import EvidenceState
from core.openai_evidence_adapter import OpenAIEvidenceAdapter
from core.openai_real_transport import parse_openai_structured_evidence
from core.real_evidence_provider import RealEvidenceProviderError


KEY = "fauna/mosquito_tigre/readable_as_mosquito"
GAG_KEY = "gag/001/composition/illo_primary"


class OpenAIEvidenceAdapterTests(unittest.TestCase):
    def _item(self, claim_key=KEY, verdict="unknown"):
        return {
            "claim_key": claim_key,
            "statement": "candidate is visually readable as mosquito",
            "verdict": verdict,
            "supporting_sources": ["image"] if verdict == "confirmed" else [],
            "contradicting_sources": ["image"] if verdict == "contradicted" else [],
        }

    def _payload(self, *items):
        return {"observations": list(items)}

    def test_requested_keys_are_passed_without_mutation(self):
        requested = [KEY]
        seen = []

        def request(payload):
            seen.append(payload)
            return self._payload(self._item())

        OpenAIEvidenceAdapter(request=request).collect(requested)

        self.assertEqual(seen[0]["requested_keys"], (KEY,))
        self.assertEqual(requested, [KEY])
        self.assertNotIn("accept", seen[0]["prompt"].lower())

    def test_valid_confirmed_contradicted_and_unknown_records(self):
        for verdict, state in (("confirmed", EvidenceState.CONFIRMED), ("contradicted", EvidenceState.CONTRADICTED), ("unknown", EvidenceState.UNKNOWN)):
            with self.subTest(verdict=verdict):
                adapter = OpenAIEvidenceAdapter(
                    request=lambda payload, verdict=verdict: self._payload(self._item(verdict=verdict))
                )
                record = adapter.collect((KEY,))[0]
                self.assertEqual(record.state, state)

    def test_gag001_four_segment_claim_is_preserved_literally(self):
        item = self._item(GAG_KEY)
        item["statement"] = "Illo is the primary visual subject."
        item["verdict"] = "confirmed"
        item["supporting_sources"] = ["image"]

        record = OpenAIEvidenceAdapter(
            request=lambda payload: self._payload(item)
        ).collect((GAG_KEY,))[0]

        self.assertEqual(record.claim_key, GAG_KEY)

    def test_adapter_never_returns_core_decisions(self):
        record = OpenAIEvidenceAdapter(
            request=lambda payload: self._payload(self._item())
        ).collect((KEY,))[0]
        self.assertFalse(hasattr(record, "accept"))
        self.assertFalse(hasattr(record, "continue"))
        self.assertFalse(hasattr(record, "human_review"))

    def test_malformed_and_forbidden_responses_are_rejected(self):
        cases = (
            (self._payload(), "missing observations"),
            (self._payload(self._item(verdict="confirmed") | {"supporting_sources": []}), "confirmed"),
            (self._payload(self._item(verdict="contradicted") | {"contradicting_sources": []}), "contradicted"),
            (self._payload(self._item() | {"supporting_sources": ["image"]}), "unknown"),
            (self._payload(self._item("invented/key")), "unrequested"),
            (self._payload(self._item(), self._item()), "duplicate"),
            (self._payload(self._item(verdict="invalid")), "unsupported"),
            (self._payload(self._item() | {"statement": ""}), "statement"),
            (self._payload(self._item() | {"decision": "accept"}), "Core decision"),
        )
        for payload, message in cases:
            with self.subTest(message=message):
                with self.assertRaises(RealEvidenceProviderError):
                    parse_openai_structured_evidence(payload, (KEY,))

    def test_adapter_wraps_unexpected_transport_or_parser_errors(self):
        adapter = OpenAIEvidenceAdapter(request=lambda payload: (_ for _ in ()).throw(ValueError("bad")))
        with self.assertRaisesRegex(RealEvidenceProviderError, "openai evidence adapter failed"):
            adapter.collect((KEY,))


if __name__ == "__main__":
    unittest.main()