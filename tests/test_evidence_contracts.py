import unittest
from pathlib import Path

from core.evidence_contracts import load_evidence_contracts, validate_evidence_contracts

ROOT = Path(__file__).resolve().parents[1]


class EvidenceContractTests(unittest.TestCase):
    def test_real_contracts_load(self):
        contracts = load_evidence_contracts(ROOT)
        self.assertGreater(len(contracts), 0)

    def test_contracts_cover_exactly_evidence_required_invariants(self):
        self.assertEqual(validate_evidence_contracts(ROOT), ())

    def test_contract_matches_declared_mechanism(self):
        contracts = load_evidence_contracts(ROOT)
        mosquito = next(
            item for item in contracts
            if item.catalog == "fauna"
            and item.entry == "mosquito_tigre"
            and item.invariant == "readable_as_mosquito"
        )
        self.assertEqual(mosquito.family, "perceptual_semantic")
        self.assertEqual(mosquito.mechanism, "evidence_perceptual")

    def test_every_contract_requires_explicit_support(self):
        contracts = load_evidence_contracts(ROOT)
        self.assertTrue(all(item.policy.explicit_support_required for item in contracts))

    def test_every_contract_routes_unknown_to_human_review(self):
        contracts = load_evidence_contracts(ROOT)
        self.assertTrue(all(item.policy.unknown_action == "human_review" for item in contracts))

    def test_contract_loader_does_not_mutate_source(self):
        before = (ROOT / "data" / "evidence_contracts.yaml").read_text(encoding="utf-8")
        load_evidence_contracts(ROOT)
        after = (ROOT / "data" / "evidence_contracts.yaml").read_text(encoding="utf-8")
        self.assertEqual(before, after)


if __name__ == "__main__":
    unittest.main()
