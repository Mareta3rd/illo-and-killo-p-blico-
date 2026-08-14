from pathlib import Path
import unittest

from core.evidence_state import EvidenceClaim, EvidenceState
from core.pipeline import run_pipeline


ROOT = Path(__file__).resolve().parents[1]


class PipelineCanonicalEvidenceTests(unittest.TestCase):
    PROPOSAL = {
        "characters": ["illo", "killo"],
        "elements": [
            {"id": "clavel", "intention": "character_identity"},
            {"id": "black_spots", "count": 2, "intention": "character_identity"},
        ],
    }

    def test_canonical_perceptual_claim_completes_pipeline_with_legacy_checks(self):
        claims = {
            "fauna/mosquito_tigre/readable_as_mosquito": EvidenceClaim(
                "candidate is visually readable as mosquito",
                EvidenceState.CONFIRMED,
                supporting_sources=("visual-review-1",),
            ),
            "intention": EvidenceClaim("intention", EvidenceState.CONFIRMED),
            "canon": EvidenceClaim("canon", EvidenceState.CONFIRMED),
            "coherence": EvidenceClaim("coherence", EvidenceState.CONFIRMED),
            "reuse_intention": EvidenceClaim("reuse", EvidenceState.CONFIRMED),
        }
        result = run_pipeline(
            "Crear un gag nuevo de Illo y Killo",
            ROOT,
            self.PROPOSAL,
            claims,
        )
        self.assertFalse(result.stopped)
        self.assertIsNotNone(result.evaluation)
        self.assertEqual(result.evaluation.evaluation.decision, "accept")

    def test_canonical_claim_can_coexist_with_incomplete_legacy_checks(self):
        claims = {
            "fauna/mosquito_tigre/readable_as_mosquito": EvidenceClaim(
                "candidate is visually readable as mosquito",
                EvidenceState.CONFIRMED,
                supporting_sources=("visual-review-1",),
            ),
            "intention": EvidenceClaim("intention", EvidenceState.CONFIRMED),
        }
        result = run_pipeline(
            "Crear un gag nuevo de Illo y Killo",
            ROOT,
            self.PROPOSAL,
            claims,
        )
        self.assertTrue(result.stopped)
        self.assertEqual(
            result.stop_reason,
            "evaluation_requires_human_review",
        )

    def test_invalid_canonical_invariant_stops_for_human_review(self):
        claims = {
            "fauna/gaviota/invented_invariant": EvidenceClaim(
                "invented",
                EvidenceState.CONFIRMED,
                supporting_sources=("source",),
            )
        }
        result = run_pipeline(
            "Crear un gag nuevo de Illo y Killo",
            ROOT,
            self.PROPOSAL,
            claims,
        )
        self.assertTrue(result.stopped)
        self.assertEqual(
            result.stop_reason,
            "evidence_contract_requires_human_review",
        )

    def test_deterministic_invariant_cannot_be_routed_as_canonical_evidence(self):
        claims = {
            "characters/killo/clavel": EvidenceClaim(
                "wrong route",
                EvidenceState.CONFIRMED,
                supporting_sources=("source",),
            )
        }
        result = run_pipeline(
            "Crear un gag nuevo de Illo y Killo",
            ROOT,
            self.PROPOSAL,
            claims,
        )
        self.assertTrue(result.stopped)
        self.assertEqual(
            result.stop_reason,
            "evidence_contract_requires_human_review",
        )
