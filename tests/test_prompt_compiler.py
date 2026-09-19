from pathlib import Path
import unittest

from core.pipeline import run_pipeline
from core.prompt_compiler import compile_prompt


ROOT = Path(__file__).resolve().parents[1]


class PromptCompilerTests(unittest.TestCase):

    VALID_PROPOSAL = {
        "characters": ["arsa", "pisha"],
        "elements": [
            {"id": "clavel", "intention": "character_identity"},
            {
                "id": "black_spots",
                "count": 2,
                "intention": "character_identity",
            },
        ],
    }

    def test_compiles_valid_parody_result(self):
        result = run_pipeline(
            "Crear una parodia de Peaky Blinders con Arsa y Pisha",
            ROOT,
            self.VALID_PROPOSAL,
        )

        compiled = compile_prompt(result)

        self.assertEqual(compiled.route, "parody")
        self.assertIn("parody", compiled.render())
        self.assertIn("Do not invent or silently alter canon.", compiled.constraints)
        self.assertIn(
            "Confirm that all introduced elements have an explicit intention.",
            compiled.checks,
        )
        self.assertIn(
            "idea=Crear una parodia de Peaky Blinders con Arsa y Pisha",
            compiled.context_summary,
        )
        self.assertTrue(compiled.semantic_context)
        self.assertTrue(any("character=arsa" in item for item in compiled.semantic_context.entries))
        self.assertTrue(any("character=pisha" in item for item in compiled.semantic_context.entries))

    def test_gag_context_is_semantic_and_route_relevant(self):
        result = run_pipeline(
            "Crear un gag de jamón con Arsa y Pisha",
            ROOT,
            self.VALID_PROPOSAL,
        )

        compiled = compile_prompt(result)
        entries = compiled.semantic_context.entries

        self.assertTrue(any("relationship=arsa_pisha" in item for item in entries))
        self.assertTrue(any("claim=gag/001/composition/ham_primary" in item for item in entries))
        self.assertTrue(any("un gag por ilustración" in item.lower() for item in entries))
        self.assertTrue(any("andalu" in item.lower() for item in entries))

    def test_historical_identity_is_not_activated(self):
        result = run_pipeline(
            "Crear un gag nuevo de Arsa y Pisha",
            ROOT,
            self.VALID_PROPOSAL,
        )

        entries = compile_prompt(result).semantic_context.entries
        joined = " ".join(entries).lower()

        self.assertIn("historical_material=reference_only", joined)
        self.assertNotIn("illo", joined)
        self.assertNotIn("killo", joined)
        self.assertNotIn("xoxo", joined)

    def test_semantic_context_is_bounded_and_deterministic(self):
        result = run_pipeline(
            "Crear un gag nuevo de Arsa y Pisha",
            ROOT,
            self.VALID_PROPOSAL,
        )

        first = compile_prompt(result).semantic_context
        second = compile_prompt(result).semantic_context

        self.assertLessEqual(len(first.entries), 32)
        self.assertTrue(all(len(entry) <= 260 for entry in first.entries))
        self.assertEqual(first.entries, second.entries)
        self.assertEqual(
            first.entries[-1],
            "historical_material=reference_only; excluded_from_active_canon",
        )

    def test_compiler_does_not_repair_stopped_result(self):
        result = run_pipeline(
            "Crear un gag nuevo de Pisha",
            ROOT,
            {"characters": ["pisha"], "elements": []},
        )

        with self.assertRaises(ValueError):
            compile_prompt(result)

    def test_render_is_deterministic(self):
        result = run_pipeline(
            "Crear un gag nuevo de Arsa y Pisha",
            ROOT,
            self.VALID_PROPOSAL,
        )

        first = compile_prompt(result).render()
        second = compile_prompt(result).render()

        self.assertEqual(first, second)


if __name__ == "__main__":
    unittest.main()
