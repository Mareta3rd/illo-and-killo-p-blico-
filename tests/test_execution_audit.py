from pathlib import Path
import unittest

from core.context import build_context
from core.evidence_snapshot import build_evidence_snapshot
from core.evidence_state import EvidenceClaim, EvidenceState
from core.execution_audit import build_execution_audit, fingerprint_evidence
from core.semantic_audit import SemanticAuditRecord


ROOT = Path(__file__).resolve().parents[1]


class ExecutionAuditTests(unittest.TestCase):
    def setUp(self):
        self.claims = {
            "fauna/mosquito_tigre/readable_as_mosquito": EvidenceClaim(
                "candidate is visually readable as mosquito",
                EvidenceState.CONFIRMED,
                supporting_sources=("simulated-visual-review",),
            )
        }

    def test_execution_audit_captures_context_and_evidence(self):
        context = build_context("Crear una escena veraniega", ROOT)
        snapshot = build_evidence_snapshot(str(ROOT), self.claims)
        record = SemanticAuditRecord(1, "candidate-fp", "accept", "accepted", ())

        audit = build_execution_audit(
            context,
            snapshot,
            (record,),
            final_status="accepted",
            stop_reason=None,
        )

        self.assertEqual(audit.idea, context.idea)
        self.assertEqual(audit.route, getattr(context.route, "value", context.route))
        self.assertEqual(audit.evidence_keys, tuple(sorted(self.claims)))
        self.assertEqual(audit.iterations, (record,))
        self.assertIsNotNone(audit.evidence_digest)

    def test_evidence_fingerprint_is_stable(self):
        first = build_evidence_snapshot(str(ROOT), self.claims)
        second = build_evidence_snapshot(str(ROOT), dict(reversed(list(self.claims.items()))))

        self.assertEqual(fingerprint_evidence(first), fingerprint_evidence(second))

    def test_evidence_change_changes_execution_identity(self):
        confirmed = build_evidence_snapshot(str(ROOT), self.claims)
        contradicted = build_evidence_snapshot(
            str(ROOT),
            {
                "fauna/mosquito_tigre/readable_as_mosquito": EvidenceClaim(
                    "candidate is visually readable as mosquito",
                    EvidenceState.CONTRADICTED,
                    contradicting_sources=("simulated-visual-review",),
                )
            },
        )

        self.assertNotEqual(fingerprint_evidence(confirmed), fingerprint_evidence(contradicted))

    def test_audit_is_immutable_and_preserves_final_decision(self):
        context = build_context("Crear una escena veraniega", ROOT)
        record = SemanticAuditRecord(1, "candidate-fp", "human_review", "unknown evidence", ())
        audit = build_execution_audit(
            context,
            None,
            (record,),
            final_status="human_review",
            stop_reason="evaluation_requires_human_review",
        )

        with self.assertRaises(Exception):
            audit.final_status = "accepted"
        self.assertEqual(audit.final_status, "human_review")
        self.assertEqual(audit.stop_reason, "evaluation_requires_human_review")


if __name__ == "__main__":
    unittest.main()
