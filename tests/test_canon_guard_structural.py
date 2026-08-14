import unittest
from pathlib import Path

from core.canon_guard import validate_piece
from core.loader import load_repository


class CanonGuardStructuralTests(unittest.TestCase):
    ROOT = Path(__file__).resolve().parents[1]

    def setUp(self):
        self.knowledge = load_repository(self.ROOT)

    def _illo_element(self, **overrides):
        element = {
            "library": "characters",
            "id": "illo",
            "scarf": {"color": "green"},
            "tuft": {"color": "yellow"},
            "hands": {"color": "black"},
            "feet": {"type": "hoof", "color": "black"},
            "tail": {"type": "flame", "length": "short"},
            "intention": "character_identity",
        }
        for key, value in overrides.items():
            element[key] = value
        return element

    def _killo_element(self, **overrides):
        element = {
            "library": "characters",
            "id": "killo",
            "spots": {"color": "black"},
            "flower": {"type": "clavel"},
            "body": {"shape": "compact_round"},
            "hands": {"color": "black"},
            "feet": {"type": "hoof", "color": "black"},
            "intention": "character_identity",
        }
        for key, value in overrides.items():
            element[key] = value
        return element

    def test_character_structural_invariants_pass_against_real_canon(self):
        result = validate_piece({"elements": [self._illo_element()]}, self.knowledge)
        self.assertTrue(result.valid)

    def test_character_structural_mismatch_fails(self):
        result = validate_piece(
            {"elements": [self._illo_element(scarf={"color": "red"})]},
            self.knowledge,
        )
        self.assertFalse(result.valid)
        self.assertIn(
            "CANON_STRUCTURAL_INVARIANT_FAILED",
            {issue.code for issue in result.issues},
        )
        self.assertFalse(result.requires_human_review)

    def test_character_structural_missing_path_requires_human_review(self):
        element = self._illo_element()
        del element["tail"]
        result = validate_piece({"elements": [element]}, self.knowledge)
        self.assertFalse(result.valid)
        self.assertTrue(result.requires_human_review)
        self.assertIn(
            "CANON_STRUCTURAL_INVARIANT_UNKNOWN",
            {issue.code for issue in result.issues},
        )

    def test_multi_path_structural_invariant_passes(self):
        result = validate_piece({"elements": [self._killo_element()]}, self.knowledge)
        self.assertTrue(result.valid)

    def test_multi_path_structural_mismatch_fails(self):
        result = validate_piece(
            {
                "elements": [
                    self._killo_element(feet={"type": "hoof", "color": "red"})
                ]
            },
            self.knowledge,
        )
        self.assertFalse(result.valid)
        self.assertIn(
            "CANON_STRUCTURAL_INVARIANT_FAILED",
            {issue.code for issue in result.issues},
        )

    def test_unclassified_field_is_not_inferred(self):
        element = self._illo_element()
        element["invented_structure"] = {"color": "purple"}
        result = validate_piece({"elements": [element]}, self.knowledge)
        self.assertTrue(result.valid)


if __name__ == "__main__":
    unittest.main()
