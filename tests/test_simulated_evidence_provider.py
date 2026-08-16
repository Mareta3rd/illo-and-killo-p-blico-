from pathlib import Path
import unittest

from core.evidence_snapshot import build_evidence_snapshot
from core.evidence_state import EvidenceState
from core.external_evidence_adapter import ExternalEvidenceRecord, normalize_external_evidence
from core.simulated_evidence_provider import build_simulated_provider


ROOT = Path(__file__).resolve().parents[1]


class SimulatedEvidenceProviderTests(unittest.TestCase):
    KEY = "fauna/mosquito_tigre/readable_as_mosquito"

    def _record(self, state: EvidenceState, sources: tuple[str, ...] = ("simulated-vision",)):
        return ExternalEvidenceRecord(
            self.KEY,
            "candidate is visually readable as mosquito",
            state,
            supporting_sources=sources if state is EvidenceState.CONFIRMED else (),
            contradicting_sources=sources if state is EvidenceState.CONTRADICTED else (),
        )

    def test_provider_returns_requested_records_in_request_order(self):
        first = self._record(EvidenceState.CONFIRMED)
        second_key = "fauna/mosquito_tigre/summer_context"
        second = ExternalEvidenceRecord(
            second_key,
            "candidate has summer context",
            EvidenceState.UNKNOWN,
        )
        provider = build_simulated_provider((second, first))
        result = provider.collect((self.KEY, second_key))
        self.assertEqual(tuple(record.claim_key for record in result), (self.KEY, second_key))

    def test_provider_does_not_invent_unrequested_claims(self):
        provider = build_simulated_provider((self._record(EvidenceState.CONFIRMED),))
        self.assertEqual(provider.collect(("fauna/mosquito_tigre/invented",)), ())

    def test_simulated_provider_can_feed_snapshot_without_reinterpreting_state(self):
        record = self._record(EvidenceState.UNKNOWN, ())
        provider = build_simulated_provider((record,))
        records = provider.collect((self.KEY,))
        claims = normalize_external_evidence(records)
        snapshot = build_evidence_snapshot(str(ROOT), claims)
        self.assertEqual(snapshot.get(self.KEY).state, EvidenceState.UNKNOWN)


if __name__ == "__main__":
    unittest.main()
