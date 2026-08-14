import unittest

from core.canon_guard import validate_piece


class CanonGuardCategoricalTests(unittest.TestCase):
    def test_known_fauna_categorical_invariant_passes(self):
        proposal = {
            "elements": [
                {
                    "library": "fauna",
                    "id": "mosquito_tigre",
                    "very_small": True,
                    "intention": "scene_support",
                }
            ]
        }

        result = validate_piece(proposal, {"characters": {}, "fauna": {}})

        self.assertTrue(result.valid)

    def test_known_fauna_categorical_invariant_fails(self):
        proposal = {
            "elements": [
                {
                    "library": "fauna",
                    "id": "mosquito_tigre",
                    "very_small": False,
                    "intention": "scene_support",
                }
            ]
        }

        result = validate_piece(proposal, {"characters": {}, "fauna": {}})

        self.assertFalse(result.valid)
        self.assertIn(
            "CANON_CATEGORICAL_INVARIANT_FAILED",
            {issue.code for issue in result.issues},
        )

    def test_missing_fauna_observation_requires_human_review(self):
        proposal = {
            "elements": [
                {
                    "library": "fauna",
                    "id": "mosquito_tigre",
                    "intention": "scene_support",
                }
            ]
        }

        result = validate_piece(proposal, {"characters": {}, "fauna": {}})

        self.assertFalse(result.valid)
        self.assertTrue(result.requires_human_review)
        self.assertIn(
            "CANON_CATEGORICAL_INVARIANT_UNKNOWN",
            {issue.code for issue in result.issues},
        )

    def test_unclassified_or_unconstrained_field_is_not_inferred(self):
        proposal = {
            "elements": [
                {
                    "library": "fauna",
                    "id": "mosquito_tigre",
                    "invented_property": True,
                    "intention": "scene_support",
                }
            ]
        }

        result = validate_piece(proposal, {"characters": {}, "fauna": {}})

        self.assertTrue(result.valid)


if __name__ == "__main__":
    unittest.main()
