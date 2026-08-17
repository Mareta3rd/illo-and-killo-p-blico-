from pathlib import Path
import unittest

from core.evidence_state import EvidenceState
from core.external_evidence_adapter import ExternalEvidenceRecord, normalize_external_evidence
from core.evidence_snapshot import build_evidence_snapshot
from core.simulated_evidence_provider import build_simulated_provider


ROOT = Path(__file__).resolve().parents[1]
KEY = "fauna/mosquito_tigre/readable_as_mosquito"


class RealisticPerceptualEvidenceTests(unittest.TestCase):
    def _run_case(self, state: EvidenceState):
        record = ExternalEvidenceRecord(
            claim_key=KEY,
            statement="candidate is visually readable as mosquito",
            state=state,
            supporting_sources=("simulated-visual-review",) if state is EvidenceState.CONFIRMED else (),
            contradicting_sources=("simulated-visual-review",) if state is EvidenceState.CONTRADICTED else (),
        )
        provider = build_simulated_provider((record,))
        records = provider.collect((KEY,))
        claims = normalize_external_evidence(records)
        return build_evidence_snapshot(str(ROOT), claims)

    def test_confirmed_perceptual_case_reaches_pass(self):
        snapshot = self._run_case(EvidenceState.CONFIRMED)
        self.assertEqual(len(snapshot.canonical_evaluations), 1)
        evaluation = snapshot.canonical_evaluations[0]
        self.assertEqual(evaluation.mechanism, "evidence_perceptual")
        self.assertEqual(evaluation.evaluation.decision, "pass")

    def test_contradicted_perceptual_case_reaches_fail(self):
        snapshot = self._run_case(EvidenceState.CONTRADICTED)
        evaluation = snapshot.canonical_evaluations[0]
        self.assertEqual(evaluation.evaluation.decision, "fail")

    def test_unknown_perceptual_case_remains_unknown(self):
        snapshot = self._run_case(EvidenceState.UNKNOWN)
        evaluation = snapshot.canonical_evaluations[0]
        self.assertEqual(evaluation.evaluation.decision, "unknown")


if __name__ == "__main__":
    unittest.main()
