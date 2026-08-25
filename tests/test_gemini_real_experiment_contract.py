import unittest

from core.evidence_state import EvidenceState
from core.external_evidence_adapter import ExternalEvidenceRecord
from core.gemini_real_transport import parse_gemini_structured_evidence
from core.real_evidence_provider import RealEvidenceProviderError

KEY = "fauna/mosquito_tigre/readable_as_mosquito"


class GeminiRealExperimentContractTests(unittest.TestCase):
    def test_real_result_can_be_normalized_into_canonical_evidence(self):
        payload = {
            "observations": [
                {
                    "claim_key": KEY,
                    "verdict": "unknown",
                    "statement": "The image does not provide enough evidence for a reliable species-level identification.",
                    "supporting_sources": [],
                    "contradicting_sources": [],
                }
            ]
        }
        records = parse_gemini_structured_evidence(payload, (KEY,))
        self.assertEqual(len(records), 1)
        self.assertIsInstance(records[0], ExternalEvidenceRecord)
        self.assertEqual(records[0].state, EvidenceState.UNKNOWN)
        self.assertEqual(records[0].claim_key, KEY)

    def test_real_experiment_rejects_unusable_provider_output(self):
        payload = {
            "observations": [
                {
                    "claim_key": KEY,
                    "verdict": "confirmed",
                    "statement": "Looks like a mosquito.",
                    "supporting_sources": [],
                    "contradicting_sources": [],
                }
            ]
        }
        with self.assertRaises(RealEvidenceProviderError):
            parse_gemini_structured_evidence(payload, (KEY,))


if __name__ == "__main__":
    unittest.main()
