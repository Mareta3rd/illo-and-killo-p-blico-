from pathlib import Path
import copy
import unittest

from core.canon_guard import ValidationResult
from core.evidence_state import EvidenceClaim, EvidenceState
from core.pipeline import run_pipeline


ROOT = Path(__file__).resolve().parents[1]


class PipelineTests(unittest.TestCase):

    VALID_GAG_PROPOSAL = {
        "characters": ["illo", "killo"],
        "elements": [
            {"id": "clavel", "intention": "character_identity"},
        ],
    }

    COMPLETE_EVIDENCE = {
        "intention": EvidenceClaim("intention", EvidenceState.CONFIRMED),
        "canon": EvidenceClaim("canon", EvidenceState.CONFIRMED),
        "coherence": EvidenceClaim("coherence", EvidenceState.CONFIRMED),
        "reuse_intention": EvidenceClaim("reuse", EvidenceState.CONFIRMED),
    }

    def test_clear_gag_completes_pipeline(self):
        result = run_pipeline(
            "Crear un gag nuevo de Illo y Killo",
            ROOT,
            self.VALID_GAG_PROPOSAL,
        )

        self.assertEqual(result.context.route, "gag")
        self.assertFalse(result.stopped)
        self.assertTrue(result.validation.valid)
        self.assertIsNotNone(result.compiled_prompt)
        self.assertEqual(result.compiled_prompt.route, "gag")
        self.assertIn("ROUTE: gag", result.compiled_prompt.render())
        self.assertIn("characters", result.context.knowledge.data)

    def test_clear_parody_completes_pipeline(self):
        result = run_pipeline(
            "Crear una parodia de Peaky Blinders con Illo y Killo",
            ROOT,
            self.VALID_GAG_PROPOSAL,
        )

        self.assertEqual(result.context.route, "parody")
        self.assertFalse(result.stopped)
        self.assertTrue(result.validation.valid)
        self.assertIsNotNone(result.compiled_prompt)
        self.assertEqual(result.compiled_prompt.route, "parody")

    def test_killo_without_clavel_stops_pipeline(self):
        proposal = {
            "characters": ["killo"],
            "elements": [],
        }

        result = run_pipeline(
            "Crear un gag nuevo de Killo",
            ROOT,
            proposal,
        )

        self.assertTrue(result.stopped)
        self.assertEqual(result.stop_reason, "canon_requires_human_review")
        self.assertFalse(result.context.requires_human_review)
        self.assertIsNone(result.compiled_prompt)
        self.assertIn(
            "CANON_KILLO_CLAVEL_MISSING",
            {issue.code for issue in result.validation.issues},
        )

    def test_recurring_asset_without_intention_stops_pipeline(self):
        proposal = {
            "characters": ["illo", "killo"],
            "elements": [
                {"id": "clavel", "intention": "character_identity"},
                {"id": "mosquito"},
            ],
        }

        result = run_pipeline(
            "Crear un gag nuevo de Illo y Killo",
            ROOT,
            proposal,
        )

        self.assertTrue(result.stopped)
        self.assertEqual(result.stop_reason, "canon_requires_human_review")
        self.assertIsNone(result.compiled_prompt)
        self.assertIn(
            "REUSE_WITHOUT_INTENTION",
            {issue.code for issue in result.validation.issues},
        )

    def test_ambiguous_idea_stops_for_human_review(self):
        result = run_pipeline("", ROOT, self.VALID_GAG_PROPOSAL)

        self.assertTrue(result.stopped)
        self.assertEqual(result.stop_reason, "missing_idea")
        self.assertTrue(result.context.requires_human_review)
        self.assertIsNone(result.compiled_prompt)

    def test_pipeline_does_not_mutate_proposal_or_loaded_knowledge(self):
        proposal = copy.deepcopy(self.VALID_GAG_PROPOSAL)
        before = copy.deepcopy(proposal)

        result = run_pipeline(
            "Crear un gag nuevo de Illo y Killo",
            ROOT,
            proposal,
        )

        self.assertEqual(proposal, before)
        self.assertIsNotNone(result.compiled_prompt)
        self.assertIn("characters", result.context.knowledge.data)

    def test_evidence_can_complete_real_pipeline(self):
        result = run_pipeline(
            "Crear un gag nuevo de Illo y Killo",
            ROOT,
            self.VALID_GAG_PROPOSAL,
            self.COMPLETE_EVIDENCE,
        )

        self.assertFalse(result.stopped)
        self.assertIsNotNone(result.evaluation)
        self.assertEqual(result.evaluation.evaluation.decision, "accept")
        self.assertIsNotNone(result.compiled_prompt)

    def test_unknown_evidence_stops_real_pipeline_for_review(self):
        claims = dict(self.COMPLETE_EVIDENCE)
        claims["coherence"] = EvidenceClaim("coherence", EvidenceState.UNKNOWN)

        result = run_pipeline(
            "Crear un gag nuevo de Illo y Killo",
            ROOT,
            self.VALID_GAG_PROPOSAL,
            claims,
        )

        self.assertTrue(result.stopped)
        self.assertEqual(result.stop_reason, "evaluation_requires_human_review")
        self.assertIsNotNone(result.evaluation)
        self.assertIsNone(result.compiled_prompt)

    def test_contradicted_evidence_stops_real_pipeline_for_continuation(self):
        claims = dict(self.COMPLETE_EVIDENCE)
        claims["reuse_intention"] = EvidenceClaim(
            "reuse",
            EvidenceState.CONTRADICTED,
            contradicting_sources=("canon/example.md",),
        )

        result = run_pipeline(
            "Crear un gag nuevo de Illo y Killo",
            ROOT,
            self.VALID_GAG_PROPOSAL,
            claims,
        )

        self.assertTrue(result.stopped)
        self.assertEqual(result.stop_reason, "evaluation_requires_continuation")
        self.assertIsNotNone(result.evaluation)
        self.assertIsNone(result.compiled_prompt)


if __name__ == "__main__":
    unittest.main()
