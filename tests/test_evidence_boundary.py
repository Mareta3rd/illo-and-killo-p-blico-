import unittest

from core.evidence_boundary import evaluate_evidence


class EvidenceBoundaryTests(unittest.TestCase):
    def test_confirmed_state_passes(self):
        result = evaluate_evidence("readable_as_mosquito", "pass")
        self.assertEqual(result.decision, "pass")

    def test_contradicted_state_fails(self):
        result = evaluate_evidence("readable_as_mosquito", "fail")
        self.assertEqual(result.decision, "fail")

    def test_unknown_state_remains_unknown(self):
        result = evaluate_evidence("readable_as_mosquito", "unknown")
        self.assertEqual(result.decision, "unknown")

    def test_custom_reasons_are_preserved(self):
        result = evaluate_evidence(
            "readable_as_mosquito",
            "pass",
            confirmed_reason="explicit visual evidence supports the reading",
        )
        self.assertEqual(
            result.reason,
            "explicit visual evidence supports the reading",
        )

    def test_invariant_name_is_preserved(self):
        result = evaluate_evidence("summer_context", "unknown")
        self.assertEqual(result.invariant, "summer_context")

    def test_invalid_state_is_rejected(self):
        with self.assertRaises(ValueError):
            evaluate_evidence("readable_as_mosquito", "maybe")


if __name__ == "__main__":
    unittest.main()
