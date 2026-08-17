from pathlib import Path
import unittest

from core.evidence_adapter import (
    EvidenceProviderFailure,
    adapt_external_observation,
    adapt_provider_call,
    normalize_external_observation,
)
from core.evidence_state import EvidenceState


class EvidenceAdapterTests(unittest.TestCase):
    def test_confirmed_observation_becomes_canonical_claim(self):
        claim = adapt_external_observation({
            "claim": "candidate is visually readable as mosquito",
            "verdict": "confirmed",
            "source": "provider:review-1",
        })
        self.assertEqual(claim.state, EvidenceState.CONFIRMED)
        self.assertEqual(claim.supporting_sources, ("provider:review-1",))

    def test_contradicted_observation_becomes_contradicted_claim(self):
        claim = adapt_external_observation({
            "claim": "candidate is visually readable as mosquito",
            "verdict": "contradicted",
            "source": "provider:review-1",
        })
        self.assertEqual(claim.state, EvidenceState.CONTRADICTED)
        self.assertEqual(claim.contradicting_sources, ("provider:review-1",))

    def test_unknown_observation_remains_unknown(self):
        claim = adapt_external_observation({
            "claim": "candidate is visually readable as mosquito",
            "verdict": "unknown",
            "source": "provider:review-1",
        })
        self.assertEqual(claim.state, EvidenceState.UNKNOWN)

    def test_malformed_observation_is_unknown_not_fail(self):
        claim = adapt_external_observation({"verdict": "confirmed"})
        self.assertEqual(claim.state, EvidenceState.UNKNOWN)

    def test_unsupported_verdict_is_unknown(self):
        claim = adapt_external_observation({
            "claim": "candidate is visually readable as mosquito",
            "verdict": "pass",
            "source": "provider:review-1",
        })
        self.assertEqual(claim.state, EvidenceState.UNKNOWN)

    def test_provider_failure_is_unknown_not_contradicted(self):
        def provider():
            raise EvidenceProviderFailure("provider unavailable")

        claim = adapt_provider_call(provider)
        self.assertEqual(claim.state, EvidenceState.UNKNOWN)
        self.assertEqual(claim.supporting_sources, ())
        self.assertEqual(claim.contradicting_sources, ())

    def test_normalization_is_conservative(self):
        observation = normalize_external_observation({
            "claim": "  readable  ",
            "verdict": "  CONFIRMED ",
            "source": " provider:1 ",
        })
        self.assertEqual(observation.claim, "readable")
        self.assertEqual(observation.verdict, "confirmed")
        self.assertEqual(observation.source, "provider:1")


if __name__ == "__main__":
    unittest.main()
