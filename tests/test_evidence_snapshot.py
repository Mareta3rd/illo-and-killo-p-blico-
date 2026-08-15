from pathlib import Path
import unittest

from core.evidence_snapshot import build_evidence_snapshot
from core.evidence_state import EvidenceClaim, EvidenceState


ROOT = str(Path(__file__).resolve().parents[1])


class EvidenceSnapshotTests(unittest.TestCase):
    def test_canonical_claims_are_validated_once(self):
        claims = {
            "fauna/mosquito_tigre/readable_as_mosquito": EvidenceClaim(
                "candidate is visually readable as mosquito",
                EvidenceState.CONFIRMED,
                supporting_sources=("visual-review-1",),
            )
        }
        snapshot = build_evidence_snapshot(ROOT, claims)
        self.assertEqual(len(snapshot), 1)
        self.assertEqual(len(snapshot.canonical_evaluations), 1)
        self.assertEqual(snapshot.canonical_evaluations[0].evaluation.decision, "pass")

    def test_legacy_claims_are_preserved(self):
        claims = {"intention": EvidenceClaim("intention", EvidenceState.CONFIRMED)}
        snapshot = build_evidence_snapshot(ROOT, claims)
        self.assertEqual(snapshot.get("intention"), claims["intention"])
        self.assertEqual(len(snapshot.canonical_evaluations), 0)

    def test_snapshot_is_deterministically_ordered(self):
        claims = {
            "coherence": EvidenceClaim("coherence", EvidenceState.CONFIRMED),
            "canon": EvidenceClaim("canon", EvidenceState.CONFIRMED),
        }
        snapshot = build_evidence_snapshot(ROOT, claims)
        self.assertEqual(tuple(snapshot.claims), ("canon", "coherence"))

    def test_claim_mapping_is_read_only(self):
        snapshot = build_evidence_snapshot(
            ROOT,
            {"intention": EvidenceClaim("intention", EvidenceState.CONFIRMED)},
        )
        with self.assertRaises(TypeError):
            snapshot.claims["new"] = EvidenceClaim("new", EvidenceState.CONFIRMED)

    def test_invalid_canonical_claim_is_rejected_during_snapshot_creation(self):
        claims = {
            "fauna/gaviota/invented": EvidenceClaim(
                "invented",
                EvidenceState.CONFIRMED,
                supporting_sources=("source",),
            )
        }
        with self.assertRaises(KeyError):
            build_evidence_snapshot(ROOT, claims)


if __name__ == "__main__":
    unittest.main()
