from pathlib import Path
import unittest

from core.canon_guard import validate_piece
from core.evidence_state import EvidenceClaim, EvidenceState
from core.evaluator import EvaluationReport
from core.evidence_evaluator import evaluate_candidate_with_evidence
from core.loop import Evaluation


ROOT = Path(__file__).resolve().parents[1]


CANDIDATE_V1 = {
    "characters": ["illo", "killo"],
    "elements": [
        {"id": "clavel", "intention": "character_identity"},
        {
            "library": "fauna",
            "id": "mosquito_tigre",
            "very_small": True,
            "intention": "scene_support",
        },
        {
            "id": "black_spots",
            "count": 2,
            "color": "black",
            "intention": "character_identity",
        },
    ],
    "checks": {
        "intention": True,
        "canon": True,
        "coherence": True,
        "reuse_intention": True,
    },
}


class SemanticRegressionTests(unittest.TestCase):
    def test_changed_candidate_cannot_silently_remove_existing_categorical_invariant(self):
        v2 = {
            **CANDIDATE_V1,
            "elements": [
                *CANDIDATE_V1["elements"][:1],
                {
                    "library": "fauna",
                    "id": "mosquito_tigre",
                    "very_small": False,
                    "intention": "scene_support",
                },
                CANDIDATE_V1["elements"][2],
            ],
        }

        validation = validate_piece(v2, __import__("core.loader", fromlist=["load_repository"]).load_repository(ROOT))
        self.assertFalse(validation.valid)
        self.assertIn(
            "CANON_CATEGORICAL_INVARIANT_FAILED",
            {issue.code for issue in validation.issues},
        )

    def test_changed_candidate_preserving_canon_is_eligible_for_normal_evaluation(self):
        v2 = {
            **CANDIDATE_V1,
            "elements": [
                *CANDIDATE_V1["elements"][:1],
                {
                    "library": "fauna",
                    "id": "mosquito_tigre",
                    "very_small": True,
                    "intention": "revised_scene_support",
                },
                CANDIDATE_V1["elements"][2],
            ],
        }

        knowledge = __import__("core.loader", fromlist=["load_repository"]).load_repository(ROOT)
        validation = validate_piece(v2, knowledge)
        report = evaluate_candidate_with_evidence(
            v2,
            validation,
            {
                name: EvidenceClaim(name, EvidenceState.CONFIRMED)
                for name in ("intention", "canon", "coherence", "reuse_intention")
            },
        )

        self.assertEqual(report.evaluation.decision, "accept")

    def test_regression_check_has_no_mutation_side_effects(self):
        before = {
            "characters": list(CANDIDATE_V1["characters"]),
            "elements": [dict(element) for element in CANDIDATE_V1["elements"]],
            "checks": dict(CANDIDATE_V1["checks"]),
        }
        changed = {
            **CANDIDATE_V1,
            "elements": [dict(element) for element in CANDIDATE_V1["elements"]],
        }
        changed["elements"][1]["very_small"] = False

        knowledge = __import__("core.loader", fromlist=["load_repository"]).load_repository(ROOT)
        validate_piece(changed, knowledge)
        self.assertEqual(CANDIDATE_V1, before)


if __name__ == "__main__":
    unittest.main()
