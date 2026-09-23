import json
import unittest

from core.decision_provider import (
    DecisionRequest,
    DecisionResult,
    DecisionProvider,
    deserialize_decision_request,
    deserialize_decision_result,
    serialize_decision_request,
    serialize_decision_result,
)


class FakeProvider:
    def decide(self, request):
        if request.kind == "boolean":
            value = True
        elif request.kind == "choice":
            value = request.choices[0]
        else:
            value = 0.75
        return DecisionResult(request.question_id, request.kind, value, "fake", 0.9)


class DecisionProviderTests(unittest.TestCase):
    def test_supports_boolean_choice_and_score_with_provider_protocol(self):
        provider: DecisionProvider = FakeProvider()
        requests = (
            DecisionRequest("q-bool", "boolean", {"ready": True}, "Ready?"),
            DecisionRequest("q-choice", "choice", {}, "Select", ("a", "b")),
            DecisionRequest("q-score", "score", {}, "Rate"),
        )
        results = [provider.decide(request) for request in requests]
        for request, result in zip(requests, results):
            result.validate_for(request)
        self.assertEqual([result.value for result in results], [True, "a", 0.75])

    def test_rejects_invalid_kinds_and_kind_value_mismatch(self):
        with self.assertRaises(ValueError):
            DecisionRequest("q", "route", {}, "Route it")
        with self.assertRaises(ValueError):
            DecisionResult("q", "route", True, "fake")
        with self.assertRaises(ValueError):
            DecisionResult("q", "boolean", "yes", "fake")

    def test_choice_must_be_allowed_and_choice_request_requires_choices(self):
        with self.assertRaises(ValueError):
            DecisionRequest("q", "choice", {}, "Choose")
        request = DecisionRequest("q", "choice", {}, "Choose", ("left", "right"))
        with self.assertRaises(ValueError):
            DecisionResult("q", "choice", "outside", "fake").validate_for(request)
        with self.assertRaises(ValueError):
            DecisionRequest("q", "choice", {}, "Choose", ("left", "left"))

    def test_confidence_is_optional_and_bounded(self):
        self.assertIsNone(DecisionResult("q", "boolean", False, "fake").confidence)
        for confidence in (-0.01, 1.01, float("nan"), float("inf"), True):
            with self.subTest(confidence=confidence), self.assertRaises(ValueError):
                DecisionResult("q", "boolean", False, "fake", confidence)

    def test_request_and_result_serialization_is_deterministic_and_round_trips(self):
        request = DecisionRequest("q", "choice", {"z": 2, "a": [True]}, "Pick", ("x", "y"))
        encoded_request = serialize_decision_request(request)
        self.assertEqual(encoded_request, serialize_decision_request(request))
        self.assertEqual(request, deserialize_decision_request(encoded_request))
        result = DecisionResult("q", "choice", "x", "fake", 0.5, "local")
        encoded_result = serialize_decision_result(result)
        self.assertEqual(encoded_result, serialize_decision_result(result))
        self.assertEqual(result, deserialize_decision_result(encoded_result))
        self.assertEqual(json.loads(encoded_result)["schema_version"], 1)

    def test_serialized_contracts_reject_extra_fields(self):
        request_data = DecisionRequest("q", "boolean", {}, "Ready?").to_dict()
        request_data["extra"] = "no"
        with self.assertRaises(ValueError):
            deserialize_decision_request(json.dumps(request_data))
        result_data = DecisionResult("q", "boolean", True, "fake").to_dict()
        result_data["extra"] = "no"
        with self.assertRaises(ValueError):
            deserialize_decision_result(json.dumps(result_data))


if __name__ == "__main__":
    unittest.main()
