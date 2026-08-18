import unittest

from core.evidence_provider_registry import EvidenceProviderRegistry
from core.external_evidence_adapter import ExternalEvidenceRecord, normalize_external_evidence
from core.external_evidence_gateway import ExternalEvidenceGateway, collect_external_evidence
from core.evidence_state import EvidenceState


KEY = "fauna/mosquito_tigre/readable_as_mosquito"


class Provider:
    def __init__(self, records):
        self.records = tuple(records)

    def collect(self, requested_keys):
        return tuple(record for key in requested_keys for record in self.records if record.claim_key == key)


class ContractCompatibilityAuditTests(unittest.TestCase):
    def _record(self, state):
        return ExternalEvidenceRecord(
            KEY,
            "candidate is visually readable as mosquito",
            state,
            supporting_sources=("audit",) if state is EvidenceState.CONFIRMED else (),
            contradicting_sources=("audit",) if state is EvidenceState.CONTRADICTED else (),
        )

    def test_registry_resolves_provider_to_gateway_protocol(self):
        provider = Provider((self._record(EvidenceState.CONFIRMED),))
        registry = EvidenceProviderRegistry.empty().register("simulated", provider)
        resolved = registry.resolve("simulated")
        self.assertTrue(callable(resolved.collect))
        self.assertEqual(tuple(r.claim_key for r in resolved.collect((KEY,))), (KEY,))

    def test_external_record_normalizes_to_core_claim_without_semantic_rewrite(self):
        record = self._record(EvidenceState.CONTRADICTED)
        claims = normalize_external_evidence((record,))
        claim = claims[KEY]
        self.assertEqual(claim.state, EvidenceState.CONTRADICTED)
        self.assertEqual(claim.claim, record.statement)
        self.assertEqual(claim.contradicting_sources, record.contradicting_sources)
        self.assertEqual(record.claim_key, KEY)

    def test_gateway_returns_snapshot_from_normalized_claims(self):
        provider = Provider((self._record(EvidenceState.CONFIRMED),))
        result = collect_external_evidence(".", provider, (KEY,))
        self.assertFalse(result.stopped)
        self.assertIsNotNone(result.snapshot)
        self.assertEqual(result.snapshot.get(KEY).state, EvidenceState.CONFIRMED)

    def test_gateway_and_registry_expose_only_provider_boundary(self):
        provider = Provider((self._record(EvidenceState.UNKNOWN),))
        gateway = ExternalEvidenceGateway(".")
        result = gateway.collect(provider, (KEY,))
        self.assertEqual(result.snapshot.get(KEY).state, EvidenceState.UNKNOWN)
        self.assertFalse(hasattr(gateway, "evaluate"))
        self.assertFalse(hasattr(gateway, "accept"))

    def test_missing_and_failure_keep_contracts_explicit(self):
        missing = collect_external_evidence(".", Provider(()), (KEY,))
        self.assertTrue(missing.stopped)
        self.assertEqual(missing.missing_keys, (KEY,))
        self.assertIsNone(missing.snapshot)

        class Failing:
            def collect(self, requested_keys):
                raise RuntimeError("provider failure")

        failed = collect_external_evidence(".", Failing(), (KEY,))
        self.assertTrue(failed.stopped)
        self.assertEqual(failed.missing_keys, (KEY,))
        self.assertIn("external_evidence_provider_failed", failed.stop_reason)


if __name__ == "__main__":
    unittest.main()
