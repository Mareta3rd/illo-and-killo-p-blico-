from pathlib import Path
import unittest

from core.evidence_state import EvidenceClaim, EvidenceState
from core.external_evidence_adapter import ExternalEvidenceRecord, normalize_external_evidence
from core.simulated_evidence_provider import build_simulated_provider
from core.orchestrator import run_vertical_slice


ROOT = Path(__file__).resolve().parents[1]
KEY = "fauna/mosquito_tigre/readable_as_mosquito"

LEGACY_EVIDENCE = {
    "intention": EvidenceClaim("intention", EvidenceState.CONFIRMED),
    "canon": EvidenceClaim("canon", EvidenceState.CONFIRMED),
    "coherence": EvidenceClaim("coherence", EvidenceState.CONFIRMED),
    "reuse_intention": EvidenceClaim("reuse", EvidenceState.CONFIRMED),
}

CANDIDATE = {
    "characters": ["illo", "killo"],
    "elements": [
        {
            "library": "objects",
            "id": "clavel",
            "intention": "character_identity",
        },
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
}


class CandidateEndToEndTests(unittest.TestCase):
    def _claims(self, state: EvidenceState):
        record = ExternalEvidenceRecord(
            claim_key=KEY,
            statement="candidate is visually readable as mosquito",
            state=state,
            supporting_sources=("simulated-visual-review",)
            if state is EvidenceState.CONFIRMED
            else (),
            contradicting_sources=("simulated-visual-review",)
            if state is EvidenceState.CONTRADICTED
            else (),
        )
        provider = build_simulated_provider((record,))
        canonical = normalize_external_evidence(provider.collect((KEY,)))
        return {**LEGACY_EVIDENCE, **canonical}

    def test_complete_candidate_with_confirmed_external_evidence_is_accepted(self):
        calls = []

        def executor(prompt, iteration, previous):
            calls.append((iteration, previous))
            return dict(CANDIDATE)

        result = run_vertical_slice(
            "Crear una escena de verano con Illo, Killo y un mosquito tigre",
            ROOT,
            executor,
            evidence_claims=self._claims(EvidenceState.CONFIRMED),
            initial_candidate=CANDIDATE,
        )

        self.assertFalse(result.stopped)
        self.assertIsNotNone(result.loop)
        self.assertEqual(result.loop.status, "accepted")
        self.assertEqual(len(result.loop.iterations), 1)
        self.assertEqual(calls[0][0], 1)

    def test_complete_candidate_with_contradicted_external_evidence_is_blocked(self):
        def executor(prompt, iteration, previous):
            raise AssertionError("executor must not run when evidence contradicts candidate")

        result = run_vertical_slice(
            "Crear una escena de verano con Illo, Killo y un mosquito tigre",
            ROOT,
            executor,
            evidence_claims=self._claims(EvidenceState.CONTRADICTED),
            initial_candidate=CANDIDATE,
        )

        self.assertTrue(result.stopped)
        self.assertIsNone(result.loop)
        self.assertEqual(result.stop_reason, "evaluation_requires_continuation")

    def test_complete_candidate_with_unknown_external_evidence_requires_review(self):
        def executor(prompt, iteration, previous):
            raise AssertionError("executor must not run while perceptual evidence is unknown")

        result = run_vertical_slice(
            "Crear una escena de verano con Illo, Killo y un mosquito tigre",
            ROOT,
            executor,
            evidence_claims=self._claims(EvidenceState.UNKNOWN),
            initial_candidate=CANDIDATE,
        )

        self.assertTrue(result.stopped)
        self.assertIsNone(result.loop)
        self.assertEqual(result.stop_reason, "evaluation_requires_human_review")


if __name__ == "__main__":
    unittest.main()
