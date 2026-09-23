from dataclasses import FrozenInstanceError

import pytest

from core.decision_execution import DecisionExecutionRecord
from core.decision_flow import DecisionFlowRecord, run_decision_flow
from core.decision_provider import DecisionRequest, DecisionResult
from core.deterministic_decision_provider import DeterministicDecisionProvider


def test_resolves_injected_provider_and_exposes_execution_record():
    request = DecisionRequest("q-ready", "boolean", {"source": "test"}, "Ready?")
    provider = DeterministicDecisionProvider({"q-ready": True}, confidence=0.9)
    resolved = []

    def resolver(received_request):
        resolved.append(received_request)
        return provider

    flow_record = run_decision_flow(request, resolver)

    assert isinstance(flow_record, DecisionFlowRecord)
    assert isinstance(flow_record.execution, DecisionExecutionRecord)
    assert resolved == [request]
    assert flow_record.execution.request == request
    assert flow_record.execution.result == DecisionResult(
        "q-ready", "boolean", True, "deterministic", 0.9
    )


def test_flow_record_is_immutable():
    request = DecisionRequest("q-ready", "boolean", {}, "Ready?")
    record = run_decision_flow(
        request, lambda _: DeterministicDecisionProvider({"q-ready": True})
    )

    with pytest.raises(FrozenInstanceError):
        record.execution = record.execution


def test_rejects_resolver_result_without_callable_decide():
    request = DecisionRequest("q-ready", "boolean", {}, "Ready?")

    with pytest.raises(TypeError, match="return a DecisionProvider"):
        run_decision_flow(request, lambda _: object())


def test_provider_result_validation_errors_propagate_from_execution_seam():
    request = DecisionRequest("q-ready", "boolean", {}, "Ready?")

    class WrongTypeProvider:
        def decide(self, request):
            return {"value": True}

    with pytest.raises(TypeError, match="must return a DecisionResult"):
        run_decision_flow(request, lambda _: WrongTypeProvider())

    class MismatchedProvider:
        def decide(self, request):
            return DecisionResult("another-question", "boolean", True, "fake")

    with pytest.raises(ValueError, match="does not match request"):
        run_decision_flow(request, lambda _: MismatchedProvider())


def test_repeated_deterministic_flow_has_stable_nested_digests():
    request = DecisionRequest("q-score", "score", {"limit": 1}, "Rate")
    provider = DeterministicDecisionProvider({"q-score": 0.75})

    first = run_decision_flow(request, lambda _: provider).execution
    second = run_decision_flow(request, lambda _: provider).execution

    assert first.request_digest == second.request_digest
    assert first.result_digest == second.result_digest
