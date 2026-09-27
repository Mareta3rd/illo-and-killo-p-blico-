from types import SimpleNamespace

import pytest

from core.decision_provider import DecisionRequest
from core.local_structured_decision_provider import LocalStructuredDecisionProvider, build_decision_prompt


class FakeCompletions:
    def __init__(self, content):
        self.content = content
        self.calls = []

    def create(self, **kwargs):
        self.calls.append(kwargs)
        return SimpleNamespace(choices=[SimpleNamespace(message=SimpleNamespace(content=self.content))])


class FakeClient:
    def __init__(self, content):
        self.chat = SimpleNamespace(completions=FakeCompletions(content))


def test_boolean_request_maps_through_structured_output():
    client = FakeClient('{"value": true, "confidence": null}')
    provider = LocalStructuredDecisionProvider(client, model="qwen3.8-27b")
    result = provider.decide(DecisionRequest("q", "boolean", {"evidence_state": "unknown"}, "Escalate?"))
    assert result.value is True
    assert result.provider_id == "local-llm"
    assert result.model_id == "qwen3.8-27b"
    assert result.confidence is None
    call = client.chat.completions.calls[0]
    assert call["model"] == "qwen3.8-27b"
    assert call["temperature"] == 0.0
    assert call["response_format"]["type"] == "json_schema"
    assert call["response_format"]["json_schema"]["schema"]["properties"]["value"] == {"type": "boolean"}


def test_choice_request_uses_request_choices_as_schema_enum():
    client = FakeClient('{"value": "accept", "confidence": 0.91}')
    provider = LocalStructuredDecisionProvider(client, model="local-qwen")
    request = DecisionRequest("route", "choice", {"evidence_state": "confirmed"}, "Which route?", ("accept", "human_review", "continue"))
    result = provider.decide(request)
    assert result.value == "accept"
    assert result.confidence == 0.91
    schema = client.chat.completions.calls[0]["response_format"]["json_schema"]["schema"]
    assert schema["properties"]["value"]["enum"] == ["accept", "human_review", "continue"]


def test_score_request_is_numeric_and_core_validates_result():
    client = FakeClient('{"value": 0.75, "confidence": 0.82}')
    provider = LocalStructuredDecisionProvider(client, model="local-qwen")
    result = provider.decide(DecisionRequest("coverage", "score", {"covered": 3, "required": 4}, "Coverage?"))
    assert result.value == 0.75
    assert result.confidence == 0.82


def test_invalid_choice_is_rejected_at_core_boundary():
    client = FakeClient('{"value": "not-allowed", "confidence": null}')
    provider = LocalStructuredDecisionProvider(client, model="local-qwen")
    with pytest.raises(ValueError, match="allowed choices"):
        provider.decide(DecisionRequest("route", "choice", {}, "Which route?", ("accept", "human_review")))


def test_malformed_payload_is_rejected():
    client = FakeClient('{"value": true}')
    provider = LocalStructuredDecisionProvider(client, model="local-qwen")
    with pytest.raises(ValueError, match="invalid decision object"):
        provider.decide(DecisionRequest("q", "boolean", {}, "Continue?"))


def test_invalid_confidence_is_rejected():
    client = FakeClient('{"value": true, "confidence": 1.5}')
    provider = LocalStructuredDecisionProvider(client, model="local-qwen")
    with pytest.raises(ValueError, match="confidence must be between"):
        provider.decide(DecisionRequest("q", "boolean", {}, "Continue?"))


def test_prompt_is_deterministic_and_contains_bounded_request_state():
    request = DecisionRequest("q", "boolean", {"z": 2, "a": 1}, "Should we continue?")
    assert build_decision_prompt(request) == build_decision_prompt(request)
    prompt = build_decision_prompt(request)
    assert '"question_id": "q"' in prompt
    assert '"kind": "boolean"' in prompt
    assert '"a": 1' in prompt
    assert '"z": 2' in prompt


@pytest.mark.parametrize("client,model,error", [(None, "m", "client must expose"), (FakeClient('{"value": true, "confidence": null}'), "", "model")])
def test_constructor_preconditions(client, model, error):
    with pytest.raises((TypeError, ValueError), match=error):
        LocalStructuredDecisionProvider(client, model=model)


def test_temperature_must_be_non_negative_finite_number():
    with pytest.raises(ValueError, match="non-negative"):
        LocalStructuredDecisionProvider(FakeClient('{"value": true, "confidence": null}'), model="m", temperature=-1)