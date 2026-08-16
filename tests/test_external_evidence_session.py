from pathlib import Path
import unittest

from core.evidence_state import EvidenceState
from core.external_evidence_adapter import ExternalEvidenceRecord
from core.external_evidence_session import collect_external_evidence
from core.simulated_evidence_provider import build_simulated_provider

ROOT = Path(__file__).resolve().parents[1]
KEY = "fauna/mosquito_tigre/readable_as_mosquito"


class ExternalEvidenceSessionTests(unittest.TestCase):
    def test_confirmed_external_evidence_reaches_snapshot(self):
        provider = build_simulated_provider([
            ExternalEvidenceRecord(
                KEY,
                "candidate is visually readable as mosquito",
                EvidenceState.CONFIRMED,
                supporting_sources=("vision-review-1",),
            )
        ])
        session = collect_external_evidence(str(ROOT), provider, [KEY])
        self.assertEqual(session.requested_keys, (KEY,))
        self.assertEqual(session.snapshot.get(KEY).state, EvidenceState.CONFIRMED)
        self.assertEqual(session.snapshot.canonical_evaluations[0].evaluation.decision, "pass")

    def test_contradicted_external_evidence_reaches_snapshot(self):
        provider = build_simulated_provider([
            ExternalEvidenceRecord(
                KEY,
                "candidate is visually readable as mosquito",
                EvidenceState.CONTRADICTED,
                contradicting_sources=("vision-review-2",),
            )
        ])
        session = collect_external_evidence(str(ROOT), provider, [KEY])
        self.assertEqual(session.snapshot.get(KEY).state, EvidenceState.CONTRADICTED)
        self.assertEqual(session.snapshot.canonical_evaluations[0].evaluation.decision, "fail")

    def test_unknown_external_evidence_remains_unknown(self):
        provider = build_simulated_provider([
            ExternalEvidenceRecord(
                KEY,
                "candidate cannot be established as mosquito from available evidence",
                EvidenceState.UNKNOWN,
            )
        ])
        session = collect_external_evidence(str(ROOT), provider, [KEY])
        self.assertEqual(session.snapshot.get(KEY).state, EvidenceState.UNKNOWN)
        self.assertEqual(session.snapshot.canonical_evaluations[0].evaluation.decision, "unknown")

    def test_unrequested_provider_records_do_not_enter_snapshot(self):
        provider = build_simulated_provider([
            ExternalEvidenceRecord(
                KEY,
                "candidate is visually readable as mosquito",
                EvidenceState.CONFIRMED,
                supporting_sources=("vision-review-1",),
            )
        ])
        other_key = "fauna/mosquito_tigre/summer_context"
        session = collect_external_evidence(str(ROOT), provider, [other_key])
        self.assertEqual(len(session.snapshot), 0)

    def test_duplicate_requested_keys_are_rejected(self):
        provider = build_simulated_provider([])
        with self.assertRaises(ValueError):
            collect_external_evidence(str(ROOT), provider, [KEY, KEY])


if __name__ == "__main__":
    unittest.main()
