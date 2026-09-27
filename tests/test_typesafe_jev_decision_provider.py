from types import SimpleNamespace

import pytest

from core.decision_execution import execute_decision
from core.decision_provider import DecisionRequest
from core.typesafe_jev_decision_provider import (
    TypeSafeJevDecisionProvider,
)


class FakeQuestion:
    def __init__(self, **kwargs):
        self.kwargs = kwargs


class FakeClient:
    def __init__(self, response):
        self.response = response
        self.calls = []
        self.closed = False

    def system_one(self, **kwargs):
        self.calls.append(kwargs)
        return self.response

    def close(self):
        self.closed = True


def fake_sdk_types():
    return FakeQuestion, FakeQuestion, FakeQuestion


def test_boolean_probability_is_explicitly_thresholded(monkeypatch):
    monkeypatch.setattr(
        "core.typesafe_jev_decision_provider._load_sdk_question_types",
        fake_sdk_types,
    )
    client = FakeClient(SimpleNamespace(model="jev-test", nouls={"decision": SimpleNamespace(noul=0.73)}))
    provider = TypeSafeJevDecisionProvider(boolean_threshold=0.7, client=client, model="jev-test")

    result = provider.decide(DecisionRequest("q", "boolean", {"x": 1}, "Escalate?"))

    assert result.value is True
    assert result.confidence is None
    assert result.provider_id == "typesafe-jev"
    assert result.model_id == "jev-test"
    assert client.calls[0]["state"] == {"x": 1}
    assert client.calls[0]["model"] == "jev-test"
    assert client.calls[0]["questions"]["decision"].kwargs == {"instructions": "Escalate?"}


def test_choice_maps_allowed_labels_and_provider_confidence(monkeypatch):
    monkeypatch.setattr(
        "core.typesafe_jev_decision_provider._load_sdk_question_types",
        fake_sdk_types,
    )
    client = FakeClient(
        SimpleNamespace(
            model="jev-test",
            choices={"decision": SimpleNamespace(choice="accept", confidence=0.91)},
        )
    )
    provider = TypeSafeJevDecisionProvider(boolean_threshold=0.5, client=client)

    result = provider.decide(
        DecisionRequest("q", "choice", {}, "Route?", ("accept", "human_review", "continue"))
    )

    assert result.value == "accept"
    assert result.confidence == 0.91
    assert client.calls[0]["questions"]["decision"].kwargs == {
        "instructions": "Route?",
        "criteria": {"accept": None, "human_review": None, "continue": None},
    }


def test_score_requires_explicit_rubric_and_maps_score(monkeypatch):
    monkeypatch.setattr(
        "core.typesafe_jev_decision_provider._load_sdk_question_types",
        fake_sdk_types,
    )
    missing_client = FakeClient(SimpleNamespace(model="jev-test", scores={}))
    provider = TypeSafeJevDecisionProvider(boolean_threshold=0.5, client=missing_client)
    with pytest.raises(ValueError, match="score_criteria"):
        provider.decide(DecisionRequest("q", "score", {"x": 1}, "Rate?"))
    assert missing_client.calls == []

    client = FakeClient(
        SimpleNamespace(
            model="jev-test",
            scores={"decision": SimpleNamespace(score=0.75, confidence=0.88)},
        )
    )
    provider = TypeSafeJevDecisionProvider(boolean_threshold=0.5, client=client)
    request = DecisionRequest(
        "q",
        "score",
        {"score_criteria": ["zero", "one", "two"]},
        "Rate?",
    )

    result = provider.decide(request)

    assert result.value == 0.75
    assert result.confidence == 0.88
    assert client.calls[0]["questions"]["decision"].kwargs == {
        "instructions": "Rate?",
        "criteria": ["zero", "one", "two"],
    }


def test_execute_decision_keeps_jev_as_provider_evidence_only(monkeypatch):
    monkeypatch.setattr(
        "core.typesafe_jev_decision_provider._load_sdk_question_types",
        fake_sdk_types,
    )
    client = FakeClient(SimpleNamespace(model="jev-test", nouls={"decision": SimpleNamespace(noul=0.2)}))
    provider = TypeSafeJevDecisionProvider(boolean_threshold=0.5, client=client)

    execution = execute_decision(
        provider,
        DecisionRequest("q", "boolean", {"evidence_state": "unknown"}, "Escalate?"),
    )

    assert execution.result.value is False
    assert execution.result.provider_id == "typesafe-jev"
    assert execution.request.question_id == "q"
    assert execution.request_digest
    assert execution.result_digest


def test_client_lifecycle_does_not_close_injected_clients():
    injected = FakeClient(SimpleNamespace(model="jev-test", nouls={"decision": SimpleNamespace(noul=0.5)}))
    provider = TypeSafeJevDecisionProvider(boolean_threshold=0.5, client=injected)
    provider.close()
    assert injected.closed is False


def test_client_factory_creates_owned_client_and_close_is_called():
    client = FakeClient(SimpleNamespace(model="jev-test", nouls={"decision": SimpleNamespace(noul=0.5)}))
    seen = []

    def factory(model):
        seen.append(model)
        return client

    provider = TypeSafeJevDecisionProvider(
        boolean_threshold=0.5,
        model="jev-test",
        client_factory=factory,
    )
    provider.close()

    assert seen == ["jev-test"]
    assert client.closed is True


@pytest.mark.parametrize("threshold", [0, 1, -0.1, 1.1, float("nan"), float("inf")])
def test_boolean_threshold_must_be_strictly_bounded(threshold):
    with pytest.raises(ValueError, match="boolean_threshold"):
        TypeSafeJevDecisionProvider(boolean_threshold=threshold, client=FakeClient(SimpleNamespace()))


def test_client_and_factory_are_mutually_exclusive():
    with pytest.raises(ValueError, match="mutually exclusive"):
        TypeSafeJevDecisionProvider(
            boolean_threshold=0.5,
            client=FakeClient(SimpleNamespace()),
            client_factory=lambda model: FakeClient(SimpleNamespace()),
        )


@pytest.mark.parametrize("probability", [-0.1, 1.1, float("nan"), float("inf")])
def test_boolean_provider_probability_must_be_valid(monkeypatch, probability):
    monkeypatch.setattr(
        "core.typesafe_jev_decision_provider._load_sdk_question_types",
        fake_sdk_types,
    )
    client = FakeClient(SimpleNamespace(model="jev-test", nouls={"decision": SimpleNamespace(noul=probability)}))
    provider = TypeSafeJevDecisionProvider(boolean_threshold=0.5, client=client)

    with pytest.raises(ValueError, match="finite probability"):
        provider.decide(DecisionRequest("q", "boolean", {}, "Escalate?"))


def test_choice_outside_allowed_set_is_rejected_by_core(monkeypatch):
    monkeypatch.setattr(
        "core.typesafe_jev_decision_provider._load_sdk_question_types",
        fake_sdk_types,
    )
    client = FakeClient(
        SimpleNamespace(
            model="jev-test",
            choices={"decision": SimpleNamespace(choice="not-allowed", confidence=0.9)},
        )
    )
    provider = TypeSafeJevDecisionProvider(boolean_threshold=0.5, client=client)

    with pytest.raises(ValueError, match="allowed choices"):
        provider.decide(DecisionRequest("q", "choice", {}, "Route?", ("accept", "continue")))


@pytest.mark.parametrize("model", ["", "   "])
def test_model_must_be_non_empty_when_supplied(model):
    with pytest.raises(ValueError, match="model"):
        TypeSafeJevDecisionProvider(boolean_threshold=0.5, model=model, client=FakeClient(SimpleNamespace()))


def test_client_must_expose_system_one():
    with pytest.raises(TypeError, match="system_one"):
        TypeSafeJevDecisionProvider(boolean_threshold=0.5, client=object())


def test_jev_choice_cardinality_limit_is_enforced(monkeypatch):
    monkeypatch.setattr(
        "core.typesafe_jev_decision_provider._load_sdk_question_types",
        fake_sdk_types,
    )
    client = FakeClient(SimpleNamespace())
    provider = TypeSafeJevDecisionProvider(boolean_threshold=0.5, client=client)
    choices = tuple(f"option-{index}" for index in range(256))

    with pytest.raises(ValueError, match="255 choices"):
        provider.decide(DecisionRequest("q", "choice", {}, "Route?", choices))
    assert client.calls == []
