"""Regression contract for the real Gemini stability experiment result shape."""

from __future__ import annotations

import json
import unittest
from unittest.mock import patch

from core.evidence_state import EvidenceState
from scripts.run_gemini_stability_experiment import VARIANTS, load_claim


class RealGeminiStabilityRegressionTests(unittest.TestCase):
    def test_gag001_illo_primary_is_canonical_and_three_variants_exist(self):
        claim = load_claim("gag/001/composition/illo_primary")
        self.assertEqual(claim.key, "gag/001/composition/illo_primary")
        self.assertEqual(claim.statement, "Illo is the primary visual and narrative subject of the gag.")
        self.assertEqual(tuple(VARIANTS), ("canonical", "semantic_rephrase", "salience_explicit"))

    def test_observed_real_result_is_tri_state_observation_not_decision(self):
        observed = (
            ("canonical", EvidenceState.CONFIRMED),
            ("semantic_rephrase", EvidenceState.UNKNOWN),
            ("salience_explicit", EvidenceState.UNKNOWN),
        )
        self.assertEqual({state for _, state in observed}, {EvidenceState.CONFIRMED, EvidenceState.UNKNOWN})
        self.assertNotEqual(observed[0][1], observed[1][1])
        self.assertNotEqual(observed[0][1], observed[2][1])


if __name__ == "__main__":
    unittest.main()
