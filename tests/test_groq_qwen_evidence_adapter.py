import unittest

from core.evidence_state import EvidenceState
from core.groq_qwen_evidence_adapter import GroqQwenEvidenceAdapter
from core.groq_qwen_real_transport import parse_groq_qwen_structured_evidence
from core.real_evidence_provider import RealEvidenceProviderError


KEY = "fauna/mosquito_tigre/readable_as_mosquito"
GAG_KEY = "gag/001/composition/illo_primary"


class GroqQwenEvidenceAdapterTests(unittest.TestCase):
    def item(self, key=KEY, verdict="unknown"):
        return {"claim_key": key, "statement": "evidence statement", "verdict": verdict,
                "supporting_sources": ["image"] if verdict == "confirmed" else [],
                "contradicting_sources": ["image"] if verdict == "contradicted" else []}

    def payload(self, *items):
        return {"observations": list(items)}

    def test_requested_keys_are_not_mutated(self):
        requested = [KEY]
        seen = []
        adapter = GroqQwenEvidenceAdapter(request=lambda payload: (seen.append(payload), self.payload(self.item()))[1])
        adapter.collect(requested)
        self.assertEqual(seen[0]["requested_keys"], (KEY,))
        self.assertEqual(requested, [KEY])

    def test_prompt_requires_image_source_identifier_and_statement_explanation(self):
        seen = []
        adapter = GroqQwenEvidenceAdapter(request=lambda payload: (seen.append(payload), self.payload(self.item()))[1])
        adapter.collect((KEY,))
        prompt = seen[0]["prompt"]
        self.assertIn('supporting_sources to exactly ["image"]', prompt)
        self.assertIn('contradicting_sources to exactly ["image"]', prompt)
        self.assertIn("keep the perceptual explanation in statement", prompt)
        self.assertIn("Source fields are identifiers only", prompt)

    def test_states_and_sources_are_preserved(self):
        for verdict, state in (("confirmed", EvidenceState.CONFIRMED), ("contradicted", EvidenceState.CONTRADICTED), ("unknown", EvidenceState.UNKNOWN)):
            with self.subTest(verdict=verdict):
                record = GroqQwenEvidenceAdapter(request=lambda payload, v=verdict: self.payload(self.item(verdict=v))).collect((KEY,))[0]
                self.assertEqual(record.state, state)

    def test_statement_can_contain_perceptual_explanation(self):
        item = self.item("fauna/mosquito_tigre/readable_as_mosquito", "confirmed") | {
            "statement": "The flying insect has the hallmark physical traits of a mosquito."
        }
        record = GroqQwenEvidenceAdapter(request=lambda payload: self.payload(item)).collect((KEY,))[0]
        self.assertEqual(record.statement, item["statement"])
        self.assertEqual(record.supporting_sources, ("image",))

    def test_gag001_claim_is_preserved_as_four_segments(self):
        item = self.item(GAG_KEY, "confirmed")
        record = GroqQwenEvidenceAdapter(request=lambda payload: self.payload(item)).collect((GAG_KEY,))[0]
        self.assertEqual(record.claim_key, GAG_KEY)

    def test_adapter_returns_no_core_decision(self):
        record = GroqQwenEvidenceAdapter(request=lambda payload: self.payload(self.item())).collect((KEY,))[0]
        self.assertFalse(hasattr(record, "accept"))
        self.assertFalse(hasattr(record, "continue"))
        self.assertFalse(hasattr(record, "human_review"))

    def test_claim_validation_rejects_invalid_payloads(self):
        cases = (
            (self.payload(self.item(verdict="confirmed") | {"supporting_sources": []}), "confirmed"),
            (self.payload(self.item(verdict="confirmed") | {"supporting_sources": ["the image shows a mosquito"]}), "confirmed source explanation"),
            (self.payload(self.item(verdict="contradicted") | {"contradicting_sources": []}), "contradicted"),
            (self.payload(self.item(verdict="contradicted") | {"contradicting_sources": ["the image contradicts the claim"]}), "contradicted source explanation"),
            (self.payload(self.item() | {"supporting_sources": ["image"]}), "unknown"),
            (self.payload(self.item("invented/key")), "unrequested"),
            (self.payload(self.item(), self.item()), "duplicate"),
            (self.payload(self.item(verdict="invalid")), "unsupported"),
            (self.payload(self.item() | {"statement": ""}), "statement"),
            (self.payload(self.item() | {"decision": "accept"}), "Core"),
        )
        for payload, label in cases:
            with self.subTest(label=label):
                with self.assertRaises(RealEvidenceProviderError):
                    parse_groq_qwen_structured_evidence(payload, (KEY,))

    def test_missing_claim_is_rejected(self):
        with self.assertRaises(RealEvidenceProviderError):
            parse_groq_qwen_structured_evidence({"observations": []}, (KEY,))


if __name__ == "__main__":
    unittest.main()