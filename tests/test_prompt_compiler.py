from pathlib import Path
import unittest

from core.pipeline import run_pipeline
from core.prompt_compiler import compile_prompt


ROOT = Path(__file__).resolve().parents[1]


class PromptCompilerTests(unittest.TestCase):

    VALID_PROPOSAL = {
        "characters": ["illo", "killo"],
        "elements": [
            {"id": "clavel", "intention": "character_identity"},
        ],
    }

    def test_compiles_valid_parody_result(self):
        result = run_pipeline(
            "Crear una parodia de Peaky Blinders con Illo y Killo",
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
            "idea=Crear una parodia de Peaky Blinders con Illo y Killo",
            compiled.context_summary,
        )

    def test_compiler_does_not_repair_stopped_result(self):
        result = run_pipeline(
            "Crear un gag nuevo de Killo",
            ROOT,
            {"characters": ["killo"], "elements": []},
        )

        with self.assertRaises(ValueError):
            compile_prompt(result)

    def test_render_is_deterministic(self):
        result = run_pipeline(
            "Crear un gag nuevo de Illo y Killo",
            ROOT,
            self.VALID_PROPOSAL,
        )

        first = compile_prompt(result).render()
        second = compile_prompt(result).render()

        self.assertEqual(first, second)


if __name__ == "__main__":
    unittest.main()
