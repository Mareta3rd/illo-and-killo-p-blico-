import copy
import unittest

from core.canon_guard import validate_piece


class CanonGuardTests(unittest.TestCase):

    KNOWLEDGE = {
        "characters": {
            "killo": {
                "invariants": ["black_spots", "clavel"],
                "body": {
                    "spots": {
                        "color": "black",
                        "count": {
                            "type": "variable",
                            "min": 2,
                            "max": 8,
                        },
                    },
                },
            },
        },
        "objects": {
            "botijo": {
                "name": "Botijo",
                "role": "everyday_prop",
                "invariants": ["simplified_iconic_form"],
            },
        },
    }

    def test_killo_requires_clavel(self):
        proposal = {
            "characters": ["killo"],
            "elements": [
                {"id": "suit", "intention": "parody"}
            ],
        }

        result = validate_piece(proposal, self.KNOWLEDGE)

        self.assertFalse(result.valid)
        self.assertTrue(result.requires_human_review)
        self.assertIn(
            "CANON_KILLO_CLAVEL_MISSING",
            {issue.code for issue in result.issues},
        )

    def test_killo_requires_black_spots(self):
        proposal = {
            "characters": ["killo"],
            "elements": [
                {"id": "clavel", "intention": "character_identity"},
            ],
        }

        result = validate_piece(proposal, self.KNOWLEDGE)

        self.assertFalse(result.valid)
        self.assertTrue(result.requires_human_review)
        self.assertIn(
            "CANON_KILLO_SPOTS_MISSING",
            {issue.code for issue in result.issues},
        )

    def test_killo_with_clavel_is_valid(self):
        proposal = {
            "characters": ["killo"],
            "elements": [
                {"id": "clavel", "intention": "character_identity"},
                {
                    "id": "black_spots",
                    "count": 4,
                    "intention": "character_identity",
                },
            ],
        }

        result = validate_piece(proposal, self.KNOWLEDGE)

        self.assertTrue(result.valid)
        self.assertFalse(result.requires_human_review)

    def test_recurring_asset_requires_intention(self):
        proposal = {
            "characters": ["illo", "killo"],
            "elements": [
                {"id": "clavel", "intention": "character_identity"},
                {
                    "id": "black_spots",
                    "count": 4,
                    "intention": "character_identity",
                },
                {"id": "mosquito"},
            ],
        }

        result = validate_piece(proposal, self.KNOWLEDGE)

        self.assertFalse(result.valid)
        self.assertTrue(result.requires_human_review)
        self.assertIn(
            "REUSE_WITHOUT_INTENTION",
            {issue.code for issue in result.issues},
        )

    def test_intention_allows_recurring_asset(self):
        proposal = {
            "characters": ["illo", "killo"],
            "elements": [
                {"id": "clavel", "intention": "character_identity"},
                {
                    "id": "black_spots",
                    "count": 4,
                    "intention": "character_identity",
                },
                {"id": "mosquito", "intention": "main_gag"},
            ],
        }

        result = validate_piece(proposal, self.KNOWLEDGE)

        self.assertTrue(result.valid)
        self.assertFalse(result.requires_human_review)

    def test_guard_does_not_mutate_inputs(self):
        proposal = {
            "characters": ["killo"],
            "elements": [
                {"id": "clavel", "intention": "character_identity"},
                {
                    "id": "black_spots",
                    "count": 4,
                    "intention": "character_identity",
                },
            ],
        }
        knowledge = copy.deepcopy(self.KNOWLEDGE)
        proposal_before = copy.deepcopy(proposal)
        knowledge_before = copy.deepcopy(knowledge)

        validate_piece(proposal, knowledge)

        self.assertEqual(proposal, proposal_before)
        self.assertEqual(knowledge, knowledge_before)

    def test_killo_spots_minimum_is_valid(self):
        proposal = {
            "characters": ["killo"],
            "elements": [
                {"id": "clavel", "intention": "character_identity"},
                {
                    "id": "black_spots",
                    "count": 2,
                    "intention": "character_identity",
                },
            ],
        }

        result = validate_piece(proposal, self.KNOWLEDGE)

        self.assertTrue(result.valid)
        self.assertFalse(result.requires_human_review)

    def test_killo_spots_maximum_is_valid(self):
        proposal = {
            "characters": ["killo"],
            "elements": [
                {"id": "clavel", "intention": "character_identity"},
                {
                    "id": "black_spots",
                    "count": 8,
                    "intention": "character_identity",
                },
            ],
        }

        result = validate_piece(proposal, self.KNOWLEDGE)

        self.assertTrue(result.valid)
        self.assertFalse(result.requires_human_review)

    def test_killo_spots_below_range_is_violation(self):
        proposal = {
            "characters": ["killo"],
            "elements": [
                {"id": "clavel", "intention": "character_identity"},
                {
                    "id": "black_spots",
                    "count": 1,
                    "intention": "character_identity",
                },
            ],
        }

        result = validate_piece(proposal, self.KNOWLEDGE)

        self.assertFalse(result.valid)
        self.assertIn(
            "CANON_KILLO_SPOTS_OUT_OF_RANGE",
            {issue.code for issue in result.issues},
        )

    def test_killo_spots_above_range_is_violation(self):
        proposal = {
            "characters": ["killo"],
            "elements": [
                {"id": "clavel", "intention": "character_identity"},
                {
                    "id": "black_spots",
                    "count": 9,
                    "intention": "character_identity",
                },
            ],
        }

        result = validate_piece(proposal, self.KNOWLEDGE)

        self.assertFalse(result.valid)
        self.assertIn(
            "CANON_KILLO_SPOTS_OUT_OF_RANGE",
            {issue.code for issue in result.issues},
        )

    def test_killo_spots_wrong_color_is_violation(self):
        proposal = {
            "characters": ["killo"],
            "elements": [
                {"id": "clavel", "intention": "character_identity"},
                {
                    "id": "black_spots",
                    "color": "red",
                    "count": 4,
                    "intention": "character_identity",
                },
            ],
        }

        result = validate_piece(proposal, self.KNOWLEDGE)

        self.assertFalse(result.valid)
        self.assertIn(
            "CANON_KILLO_SPOTS_COLOR_INVALID",
            {issue.code for issue in result.issues},
        )

    def test_known_library_reference_is_valid(self):
        proposal = {
            "elements": [
                {
                    "library": "objects",
                    "id": "botijo",
                    "intention": "scene_support",
                },
            ],
        }

        result = validate_piece(proposal, self.KNOWLEDGE)

        self.assertTrue(result.valid)

    def test_unknown_library_reference_requires_human_review(self):
        proposal = {
            "elements": [
                {
                    "library": "objects",
                    "id": "unknown_object",
                    "intention": "scene_support",
                },
            ],
        }

        result = validate_piece(proposal, self.KNOWLEDGE)

        self.assertFalse(result.valid)
        self.assertTrue(result.requires_human_review)
        self.assertIn(
            "LIBRARY_ENTRY_NOT_FOUND",
            {issue.code for issue in result.issues},
        )


if __name__ == "__main__":
    unittest.main()
