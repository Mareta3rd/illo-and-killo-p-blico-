import unittest

from core.canonical_salience import CanonicalClaim, CanonicalSalience, NarrativeRole, VisualSalience
from core.gemini_evidence_adapter import GeminiEvidenceAdapter


KEY = "gag/001/composition/illo_primary"


class CanonicalClaimPromptTests(unittest.TestCase):
    def test_collect_claims_sends_statement_and_salience_without_making_decisions(self):
        seen = []

        def request(payload):
            seen.append(payload)
            return object()

        claim = CanonicalClaim(
            key=KEY,
            statement="Illo is the primary visual and narrative subject of the gag.",
            salience=CanonicalSalience(NarrativeRole.PRIMARY, VisualSalience.DOMINANT),
        )
        adapter = GeminiEvidenceAdapter(request=request, parse=lambda payload, keys: ())
        result = adapter.collect_claims((claim,))

        self.assertEqual(result, ())
        self.assertEqual(seen[0]["requested_keys"], (KEY,))
        self.assertIn(claim.statement, seen[0]["prompt"])
        self.assertIn("narrative_role=primary", seen[0]["prompt"])
        self.assertIn("visual_salience=dominant", seen[0]["prompt"])
        self.assertNotIn("accept", seen[0]["prompt"].lower())

    def test_canonical_claim_requires_key_and_statement(self):
        salience = CanonicalSalience(NarrativeRole.PRIMARY, VisualSalience.DOMINANT)
        with self.assertRaises(ValueError):
            CanonicalClaim("", "statement", salience)
        with self.assertRaises(ValueError):
            CanonicalClaim(KEY, "", salience)


if __name__ == "__main__":
    unittest.main()
