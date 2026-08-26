"""Contract tests for Gemini evidence stability at the provider/Core boundary."""

from __future__ import annotations

import unittest

from core.canonical_salience import CanonicalClaim, CanonicalSalience, NarrativeRole, VisualSalience
from core.evidence_state import EvidenceState
from core.external_evidence_adapter import ExternalEvidenceRecord, normalize_external_evidence
from core.gemini_evidence_adapter import GeminiEvidenceAdapter


class GeminiEvidenceStabilityTests(unittest.TestCase):
    CLAIM = CanonicalClaim(
        key="gag/001/illo_primary",
        statement="Illo is the primary visual and narrative subject of the gag.",
        salience=CanonicalSalience(NarrativeRole.PRIMARY, VisualSalience.DOMINANT),
    )

    def _adapter(self, payload):
        calls = []

        def request(value):
            calls.append(value)
            return payload

        return GeminiEvidenceAdapter(request=request), calls

    def test_canonical_claim_key_is_preserved_without_provider_rewrite(self):
        payload = {
            "observations": [
                {
                    "claim_key": self.CLAIM.key,
                    "statement": "Illo is the primary active subject.",
                    "verdict": "confirmed",
                    "supporting_sources": ["image"],
                    "contradicting_sources": [],
                }
            ]
        }
        adapter, _ = self._adapter(payload)

        record = tuple(adapter.collect_claims((self.CLAIM,)))[0]

        self.assertEqual(record.claim_key, self.CLAIM.key)
        self.assertEqual(record.state, EvidenceState.CONFIRMED)
        self.assertEqual(record.supporting_sources, ("image",))

    def test_salience_metadata_is_context_not_evidence(self):
        payload = {
            "observations": [
                {
                    "claim_key": self.CLAIM.key,
                    "statement": "The image does not provide enough evidence to confirm this.",
                    "verdict": "unknown",
                    "supporting_sources": [],
                    "contradicting_sources": [],
                }
            ]
        }
        adapter, calls = self._adapter(payload)

        record = tuple(adapter.collect_claims((self.CLAIM,)))[0]

        self.assertEqual(record.state, EvidenceState.UNKNOWN)
        prompt = calls[0]["prompt"]
        self.assertIn("narrative_role=primary", prompt)
        self.assertIn("visual_salience=dominant", prompt)
        self.assertIn("Do not turn salience metadata into evidence", prompt)

    def test_same_canonical_claim_and_payload_produce_same_record(self):
        payload = {
            "observations": [
                {
                    "claim_key": self.CLAIM.key,
                    "statement": "Illo is the primary active subject.",
                    "verdict": "confirmed",
                    "supporting_sources": ["image"],
                    "contradicting_sources": [],
                }
            ]
        }
        adapter, _ = self._adapter(payload)

        first = tuple(adapter.collect_claims((self.CLAIM,)))[0]
        second = tuple(adapter.collect_claims((self.CLAIM,)))[0]

        self.assertEqual(first, second)

    def test_normalization_keeps_provider_state_out_of_acceptance_decisions(self):
        record = ExternalEvidenceRecord(
            claim_key=self.CLAIM.key,
            statement="Illo is the primary active subject.",
            state=EvidenceState.CONFIRMED,
            supporting_sources=("image",),
        )

        claims = normalize_external_evidence((record,))

        self.assertEqual(claims[record.claim_key].state, EvidenceState.CONFIRMED)
        self.assertEqual(claims[record.claim_key].supporting_sources, ("image",))

        canonical_claim = claims[record.claim_key]
        self.assertNotIn("decision", canonical_claim.__dataclass_fields__)

    def test_contradicted_and_unknown_are_preserved_as_observations(self):
        cases = (
            ("contradicted", EvidenceState.CONTRADICTED, (), ("image",)),
            ("unknown", EvidenceState.UNKNOWN, (), ()),
        )
        for verdict, expected_state, supporting, contradicting in cases:
            with self.subTest(verdict=verdict):
                payload = {
                    "observations": [
                        {
                            "claim_key": self.CLAIM.key,
                            "statement": "Provider observation.",
                            "verdict": verdict,
                            "supporting_sources": supporting,
                            "contradicting_sources": contradicting,
                        }
                    ]
                }
                adapter, _ = self._adapter(payload)
                record = tuple(adapter.collect_claims((self.CLAIM,)))[0]
                self.assertEqual(record.state, expected_state)


if __name__ == "__main__":
    unittest.main()
