import pytest

from core.decision_provider import DecisionProvider, DecisionRequest
from core.deterministic_decision_provider import DeterministicDecisionProvider


def test_returns_deterministic_boolean_choice_and_score_results():
    provider: DecisionProvider = DeterministicDecisionProvider(
        {"q-bool": True, "q-choice": "right", "q-score": 0.75},
        confidence=0.9,
    )
    requests = (
        DecisionRequest("q-bool", "boolean", {}, "Ready?"),
        DecisionRequest("q-choice", "choice", {}, "Choose", ("left", "right")),
        DecisionRequest("q-score", "score", {}, "Rate"),
    )

    results = [provider.decide(request) for request in requests]

    assert [result.value for result in results] == [True, "right", 0.75]
    assert [result.provider_id for result in results] == ["deterministic"] * 3
    assert [result.confidence for result in results] == [0.9] * 3
    for request, result in zip(requests, results):
        result.validate_for(request)
        assert result == provider.decide(request)


def test_rejects_missing_question_id():
    provider = DeterministicDecisionProvider({})
    request = DecisionRequest("missing", "boolean", {}, "Ready?")

    with pytest.raises(ValueError, match="no deterministic answer"):
        provider.decide(request)


@pytest.mark.parametrize(
    ("decision_request", "answer"),
    [
        (DecisionRequest("q", "boolean", {}, "Ready?"), "yes"),
        (DecisionRequest("q", "choice", {}, "Choose", ("a", "b")), "outside"),
        (DecisionRequest("q", "score", {}, "Rate"), float("nan")),
    ],
)
def test_rejects_invalid_answers(decision_request, answer):
    provider = DeterministicDecisionProvider({"q": answer})

    with pytest.raises(ValueError):
        provider.decide(decision_request)
