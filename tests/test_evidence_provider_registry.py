import unittest

from core.evidence_provider_registry import EvidenceProviderRegistry
from core.external_evidence_adapter import ExternalEvidenceRecord
from core.evidence_state import EvidenceState


class StubProvider:
    def __init__(self, marker):
        self.marker = marker

    def collect(self, requested_keys):
        return ()


class EvidenceProviderRegistryTests(unittest.TestCase):
    def test_empty_registry_has_no_names(self):
        registry = EvidenceProviderRegistry.empty()
        self.assertEqual(registry.names(), ())

    def test_register_returns_new_registry(self):
        original = EvidenceProviderRegistry.empty()
        provider = StubProvider("one")
        updated = original.register("simulated", provider)
        self.assertEqual(original.names(), ())
        self.assertEqual(updated.names(), ("simulated",))
        self.assertIs(updated.resolve("simulated"), provider)

    def test_registry_rejects_duplicate_name(self):
        provider = StubProvider("one")
        registry = EvidenceProviderRegistry.empty().register("simulated", provider)
        with self.assertRaises(ValueError):
            registry.register("simulated", StubProvider("two"))

    def test_unknown_provider_is_explicit(self):
        registry = EvidenceProviderRegistry.empty()
        with self.assertRaises(KeyError) as raised:
            registry.resolve("missing")
        self.assertIn("Unknown evidence provider", str(raised.exception))

    def test_provider_mapping_is_not_mutable(self):
        provider = StubProvider("one")
        registry = EvidenceProviderRegistry.empty().register("simulated", provider)
        with self.assertRaises(TypeError):
            registry.providers["other"] = StubProvider("two")

    def test_invalid_provider_is_rejected(self):
        registry = EvidenceProviderRegistry.empty()
        with self.assertRaises(TypeError):
            registry.register("broken", object())


if __name__ == "__main__":
    unittest.main()
