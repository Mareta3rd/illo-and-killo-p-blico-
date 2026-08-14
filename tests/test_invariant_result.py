import unittest

from core.categorical_evaluator import CategoricalEvaluation
from core.invariant_evaluator import InvariantEvaluation
from core.relational_evaluator import RelationalEvaluation
from core.structural_evaluator import StructuralEvaluation
from core.invariant_result import InvariantDecision


class InvariantResultContractTests(unittest.TestCase):

    def test_deterministic_evaluators_share_one_result_type(self):
        self.assertIs(CategoricalEvaluation, InvariantEvaluation)
        self.assertIs(StructuralEvaluation, InvariantEvaluation)
        self.assertIs(RelationalEvaluation, InvariantEvaluation)

    def test_shared_decision_contract_is_tri_state(self):
        self.assertEqual(InvariantDecision.__args__, ("pass", "fail", "unknown"))

    def test_result_is_immutable_and_auditable(self):
        result = InvariantEvaluation("example", "pass", "explicit test reason")

        self.assertEqual(result.invariant, "example")
        self.assertEqual(result.decision, "pass")
        self.assertEqual(result.reason, "explicit test reason")

        with self.assertRaises(AttributeError):
            result.decision = "fail"


if __name__ == "__main__":
    unittest.main()
