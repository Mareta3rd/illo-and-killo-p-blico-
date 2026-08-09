import copy
import unittest

from core.canon_guard import validate_piece


class CanonGuardTests(unittest.TestCase):

    KNOWLEDGE = {
        "characters": {
            "killo": {
                "invariants": ["black_spots", "clavel"]
            }
        }
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

    def test_killo_with_clavel_is_valid(self):
        proposal = {
            "characters": ["killo"],
            "elements": [
                {"id": "clavel", "intention": "character_identity"}
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
                {"id": "clavel", "intention": "character_identity"}
            ],
        }
        knowledge = copy.deepcopy(self.KNOWLEDGE)
        proposal_before = copy.deepcopy(proposal)
        knowledge_before = copy.deepcopy(knowledge)

        validate_piece(proposal, knowledge)

        self.assertEqual(proposal, proposal_before)
        self.assertEqual(knowledge, knowledge_before)


if __name__ == "__main__":
    unittest.main()
