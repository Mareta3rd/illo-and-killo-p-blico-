from pathlib import Path
import unittest

from core.evidence_snapshot import build_evidence_snapshot
from core.evidence_state import EvidenceState
from core.external_evidence_adapter import (
    ExternalEvidenceRecord,
    normalize_external_evidence,
    normalize_external_observations,
)

ROOT = Path(__file__).resolve().parents[1]


class ExternalEvidenceAdapterTests(unittest.TestCase):
    def test_confirmed_record_becomes_core_claim(self):
        claims = normalize_external_evidence(
            [
                ExternalEvidenceRecord(
                    "fauna/mosquito_tigre/readable_as_mosquito",
                    "candidate is visually readable as mosquito",
                    EvidenceState.CONFIRMED,
                    supporting_sources=("review-1",),
                )
            ]
        )
        self.assertEqual(claims["fauna/mosquito_tigre/readable_as_mosquito"].state, EvidenceState.CONFIRMED)

    def test_unknown_record_is_preserved_without_inference(self):
        claims = normalize_external_evidence(
            [
                ExternalEvidenceRecord(
                    "fauna/mosquito_tigre/summer_context",
                    "seasonal context cannot be established",
                    EvidenceState.UNKNOWN,
                )
            ]
        )
        self.assertEqual(claims["fauna/mosquito_tigre/summer_context"].state, EvidenceState.UNKNOWN)

    def test_duplicate_claim_keys_are_rejected(self):
        record = ExternalEvidenceRecord(
            "fauna/mosquito_tigre/readable_as_mosquito",
            "duplicate",
            EvidenceState.UNKNOWN,
        )
        with self.assertRaises(ValueError):
            normalize_external_evidence([record, record])

    def test_noncanonical_claim_key_is_rejected(self):
        with self.assertRaises(ValueError):
            normalize_external_evidence(
                [ExternalEvidenceRecord("readable_as_mosquito", "claim", EvidenceState.UNKNOWN)]
            )

    def test_empty_statement_is_rejected(self):
        with self.assertRaises(ValueError):
            normalize_external_evidence(
                [ExternalEvidenceRecord("fauna/mosquito_tigre/readable_as_mosquito", "", EvidenceState.UNKNOWN)]
            )

    def test_non_string_sources_are_rejected(self):
        record = ExternalEvidenceRecord(
            "fauna/mosquito_tigre/readable_as_mosquito",
            "claim",
            EvidenceState.CONFIRMED,
            supporting_sources=("review-1", 2),
        )
        with self.assertRaises(TypeError):
            normalize_external_evidence([record])

    def test_normalized_claims_are_deterministically_ordered(self):
        records = [
            ExternalEvidenceRecord("fauna/mosquito_tigre/summer_context", "b", EvidenceState.UNKNOWN),
            ExternalEvidenceRecord("fauna/mosquito_tigre/readable_as_mosquito", "a", EvidenceState.UNKNOWN),
        ]
        claims = normalize_external_evidence(records)
        self.assertEqual(list(claims), [
            "fauna/mosquito_tigre/readable_as_mosquito",
            "fauna/mosquito_tigre/summer_context",
        ])

    def test_normalized_external_claim_enters_existing_snapshot_boundary(self):
        claims = normalize_external_evidence(
            [
                ExternalEvidenceRecord(
                    "fauna/mosquito_tigre/readable_as_mosquito",
                    "candidate is visually readable as mosquito",
                    EvidenceState.CONFIRMED,
                    supporting_sources=("review-1",),
                )
            ]
        )
        snapshot = build_evidence_snapshot(str(ROOT), claims)
        self.assertEqual(len(snapshot), 1)
        self.assertEqual(snapshot.get("fauna/mosquito_tigre/readable_as_mosquito").state, EvidenceState.CONFIRMED)

    def test_generic_observation_normalization_preserves_gag_claim_identity(self):
        claims = normalize_external_observations(
            [
                ExternalEvidenceRecord(
                    "gag/001/composition/illo_primary",
                    "Illo is the primary visual and narrative subject of the gag.",
                    EvidenceState.CONFIRMED,
                    supporting_sources=("image",),
                )
            ]
        )
        self.assertEqual(list(claims), ["gag/001/composition/illo_primary"])
        self.assertEqual(claims["gag/001/composition/illo_primary"].state, EvidenceState.CONFIRMED)

    def test_registered_invariant_normalization_remains_strict(self):
        with self.assertRaises(ValueError):
            normalize_external_evidence(
                [
                    ExternalEvidenceRecord(
                        "gag/001/composition/illo_primary",
                        "Illo is the primary visual and narrative subject of the gag.",
                        EvidenceState.CONFIRMED,
                        supporting_sources=("image",),
                    )
                ]
            )


if __name__ == "__main__":
    unittest.main()
