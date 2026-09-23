from dataclasses import FrozenInstanceError

import pytest

from core.decision_provider import DecisionRequest, DecisionResult
from core.decision_execution import DecisionExecutionRecord, execute_decision
from core.deterministic_decision_provider import DeterministicDecisionProvider


def test_executes_valid_deterministic_decision_and_returns_immutable_record():
    request = DecisionRequest("q-ready", "boolean", {"source": "test"}, "Ready?")
    provider = DeterministicDecisionProvider({"q-ready": True}, confidence=0.9)

    record = execute_decision(provider, request)

    assert isinstance(record, DecisionExecutionRecord)
    assert record.request == request
    assert record.result == DecisionResult("q-ready", "boolean", True, "deterministic", 0.9)
    assert len(record.request_digest) == 64
    assert len(record.result_digest) == 64
    with pytest.raises(FrozenInstanceError):
        record.result_digest = "changed"


def test_rejects_provider_returning_wrong_type():
    class MalformedProvider:
        def decide(self, request):
            return {"question_id": request.question_id, "value": True}

    request = DecisionRequest("q-ready", "boolean", {}, "Ready?")
    with pytest.raises(TypeError, match="must return a DecisionResult"):
        execute_decision(MalformedProvider(), request)


@pytest.mark.parametrize(
    "result",
    [
        DecisionResult("another-question", "boolean", True, "fake"),
        DecisionResult("q-choice", "choice", "not-allowed", "fake"),
    ],
)
def test_rejects_result_that_does_not_validate_for_request(result):
    class MismatchedProvider:
        def decide(self, request):
            return result

    request = (
        DecisionRequest("q-choice", "choice", {}, "Choose", ("a", "b"))
        if result.kind == "choice"
        else DecisionRequest("q-ready", "boolean", {}, "Ready?")
    )
    with pytest.raises(ValueError):
        execute_decision(MismatchedProvider(), request)


def test_repeated_deterministic_execution_has_stable_digests():
    request = DecisionRequest("q-score", "score", {"limit": 1}, "Rate")
    provider = DeterministicDecisionProvider({"q-score": 0.75})

    first = execute_decision(provider, request)
    second = execute_decision(provider, request)

    assert first.request_digest == second.request_digest
    assert first.result_digest == second.result_digest
