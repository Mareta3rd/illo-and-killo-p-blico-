from types import SimpleNamespace

import pytest

from core.local_collaboration_provider import (
    LocalStructuredCollaborationProvider,
    build_collaboration_prompt,
)
from core.work_envelope import CollaborationUpdate, WorkEnvelope


class FakeCompletions:
    def __init__(self, content):
        self.content = content
        self.calls = []

    def create(self, **kwargs):
        self.calls.append(kwargs)
        message = SimpleNamespace(content=self.content)
        return SimpleNamespace(choices=[SimpleNamespace(message=message)])


class FakeClient:
    def __init__(self, content):
        self.completions = FakeCompletions(content)
        self.chat = SimpleNamespace(completions=self.completions)


def make_envelope():
    return WorkEnvelope(
        envelope_id="work-001",
        objective="Review a small proposal",
        project="Arsa & Pisha",
        context={
            "canon_boundary": "current Arsa/Pisha canon",
            "route": "gag",
        },
        constraints=("preserve canon", "do not execute actions"),
        available_tools=("semantic_context", "benchmark"),
        prior_work=("first draft reviewed",),
        known_failures=("previous output was vague",),
        expected_output="A concrete review with corrections and next steps.",
    )


def valid_payload(**overrides):
    payload = {
        "status": "ready_for_review",
        "summary": "The review is ready with concrete corrections.",
        "progress": ["checked the supplied context", "cross-checked known failures"],
        "needs_input": None,
        "blockers": [],
        "output": {
            "answer": "The proposal needs a clearer next action.",
            "rationale": "The previous draft was vague at the handoff boundary.",
            "proposals": ["Rewrite the final step as one explicit action."],
            "questions": [],
        },
        "attention_required": True,
    }
    payload.update(overrides)
    return payload


def test_build_prompt_is_deterministic_and_uses_bounded_work():
    envelope = make_envelope()

    first = build_collaboration_prompt(envelope)

    assert first == build_collaboration_prompt(envelope)
    assert "previous output was vague" in first
    assert "available_tools" in first
    assert "do not call, execute or imply authorization" in first
    assert envelope.to_json() in first


def test_collaborates_with_structured_output_and_returns_valid_update():
    client = FakeClient(json.dumps(valid_payload()))
    provider = LocalStructuredCollaborationProvider(client, model="qwen3.8-27b")
    envelope = make_envelope()

    update = provider.collaborate(envelope)

    assert isinstance(update, CollaborationUpdate)
    assert update.envelope_id == "work-001"
    assert update.status == "ready_for_review"
    assert update.attention_required is True
    assert update.output["proposals"] == [
        "Rewrite the final step as one explicit action."
    ]

    request = client.completions.calls[0]
    assert request["model"] == "qwen3.8-27b"
    assert request["temperature"] == 0.0
    assert request["response_format"]["type"] == "json_schema"
    assert request["response_format"]["json_schema"]["strict"] is True


def test_provider_exposes_identity_for_the_orchestration_seam():
    provider = LocalStructuredCollaborationProvider(
        FakeClient(json.dumps(valid_payload())),
        model="qwen3.8-27b",
    )

    assert provider.provider_id == "local-qwen-collaboration"
    assert provider.model_id == "qwen3.8-27b"


@pytest.mark.parametrize(
    "payload",
    [
        {**valid_payload(), "status": "invalid"},
        {**valid_payload(), "attention_required": "yes"},
        {**valid_payload(), "output": {"answer": "only"}},
        {**valid_payload(), "unexpected": True},
    ],
)
def test_rejects_malformed_payloads(payload):
    provider = LocalStructuredCollaborationProvider(
        FakeClient(json.dumps(payload)),
        model="qwen3.8-27b",
    )

    with pytest.raises((ValueError, TypeError)):
        provider.collaborate(make_envelope())


def test_rejects_invalid_transport_response():
    class MissingChoices:
        choices = []

    class Completions:
        def create(self, **kwargs):
            return MissingChoices()

    client = SimpleNamespace(chat=SimpleNamespace(completions=Completions()))
    provider = LocalStructuredCollaborationProvider(client, model="qwen3.8-27b")

    with pytest.raises(ValueError, match="no choices"):
        provider.collaborate(make_envelope())


def test_rejects_invalid_json_response():
    provider = LocalStructuredCollaborationProvider(
        FakeClient("not-json"),
        model="qwen3.8-27b",
    )

    with pytest.raises(ValueError, match="invalid JSON"):
        provider.collaborate(make_envelope())


def test_provider_rejects_non_envelope():
    provider = LocalStructuredCollaborationProvider(
        FakeClient(json.dumps(valid_payload())),
        model="qwen3.8-27b",
    )

    with pytest.raises(TypeError, match="envelope must be a WorkEnvelope"):
        provider.collaborate(object())
