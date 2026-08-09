from pathlib import Path
import copy
import unittest

from core.pipeline import run_pipeline


ROOT = Path(__file__).resolve().parents[1]


class PipelineTests(unittest.TestCase):

    VALID_GAG_PROPOSAL = {
        "characters": ["illo", "killo"],
        "elements": [
            {"id": "clavel", "intention": "character_identity"},
        ],
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
        self.assertIn(
            "REUSE_WITHOUT_INTENTION",
            {issue.code for issue in result.validation.issues},
        )

    def test_ambiguous_idea_stops_for_human_review(self):
        result = run_pipeline("", ROOT, self.VALID_GAG_PROPOSAL)

        self.assertTrue(result.stopped)
        self.assertEqual(result.stop_reason, "missing_idea")
        self.assertTrue(result.context.requires_human_review)

    def test_pipeline_does_not_mutate_proposal_or_loaded_knowledge(self):
        proposal = copy.deepcopy(self.VALID_GAG_PROPOSAL)
        before = copy.deepcopy(proposal)

        result = run_pipeline(
            "Crear un gag nuevo de Illo y Killo",
            ROOT,
            proposal,
        )

        self.assertEqual(proposal, before)
        self.assertIn("characters", result.context.knowledge.data)
        self.assertIn("characters", result.context.knowledge.data)


if __name__ == "__main__":
    unittest.main()
