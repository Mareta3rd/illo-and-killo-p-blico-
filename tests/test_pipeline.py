import copy
import unittest

from core.pipeline import run_pipeline


class PipelineTests(unittest.TestCase):

    KNOWLEDGE = {
        "characters": {
            "killo": {
                "invariants": ["black_spots", "clavel"]
            }
        },
        "objects": {"clavel": {"type": "fixed_invariant"}},
    }

    def test_clear_gag_completes_pipeline(self):
        result = run_pipeline(
            "Crear un gag nuevo de Illo y Killo",
            self.KNOWLEDGE,
        )

        self.assertEqual(result.context.route, "gag")
        self.assertFalse(result.stopped)
        self.assertTrue(result.validation.valid)

    def test_clear_parody_completes_pipeline(self):
        result = run_pipeline(
            "Crear una parodia de Peaky Blinders con Illo y Killo",
            self.KNOWLEDGE,
        )

        self.assertEqual(result.context.route, "parody")
        self.assertFalse(result.stopped)
        self.assertTrue(result.validation.valid)

    def test_ambiguous_idea_stops_for_human_review(self):
        result = run_pipeline("", self.KNOWLEDGE)

        self.assertTrue(result.stopped)
        self.assertEqual(result.stop_reason, "missing_idea")
        self.assertTrue(result.context.requires_human_review)

    def test_pipeline_does_not_mutate_knowledge(self):
        knowledge = copy.deepcopy(self.KNOWLEDGE)
        before = copy.deepcopy(knowledge)

        run_pipeline(
            "Crear un gag nuevo de Illo y Killo",
            knowledge,
        )

        self.assertEqual(knowledge, before)


if __name__ == "__main__":
    unittest.main()
