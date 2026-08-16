import unittest
from pathlib import Path

from core.evidence_state import EvidenceState
from core.external_evidence_adapter import ExternalEvidenceRecord
from core.simulated_evidence_provider import SimulatedEvidenceProvider

ROOT = Path(__file__).resolve().parents[1]


class SimulatedEvidenceProviderTests(unittest.TestCase):
    def test_provider_emits_records_without_core_decision(self):
        provider = SimulatedEvidenceProvider(
            (
                ExternalEvidenceRecord(
                    "fauna",
                    "mosquito_tigre",
                    "readable_as_mosquito",
                    "candidate is visually readable as mosquito",
                    "confirmed",
                    ("simulated-vision",),
                ),
            )
        )
        records = provider.collect()
        self.assertEqual(len(records), 1)
        self.assertEqual(records[0].status, "confirmed")

    def test_provider_normalizes_to_evidence_claims(self):
        provider = SimulatedEvidenceProvider(
            (
                ExternalEvidenceRecord(
                    "fauna",
                    "mosquito_tigre",
                    "readable_as_mosquito",
                    "candidate is visually readable as mosquito",
                    "confirmed",
                    ("simulated-vision",),
                ),
            )
        )
        claims = provider.collect_claims()
        key = "fauna/mosquito_tigre/readable_as_mosquito"
        self.assertIn(key, claims)
        self.assertEqual(claims[key].state, EvidenceState.CONFIRMED)

    def test_unknown_state_survives_provider_boundary(self):
        provider = SimulatedEvidenceProvider(
            (
                ExternalEvidenceRecord(
                    "fauna",
                    "mosquito_tigre",
                    "summer_context",
                    "candidate is appropriate for summer context",
                    "unknown",
                    (),
                ),
            )
        )
        claims = provider.collect_claims()
        key = "fauna/mosquito_tigre/summer_context"
        self.assertEqual(claims[key].state, EvidenceState.UNKNOWN)


if __name__ == "__main__":
    unittest.main()
