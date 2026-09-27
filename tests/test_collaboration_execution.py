from dataclasses import FrozenInstanceError

import pytest

from core.collaboration_execution import (
    CollaborationExecutionRecord,
    execute_collaboration,
)
from core.work_envelope import CollaborationUpdate, WorkEnvelope


def make_envelope(**overrides):
    data = {
        "envelope_id": "work-001",
        "objective": "Review a small proposal",
        "project": "Arsa & Pisha",
        "context": {"route": "gag", "version": 1},
        "constraints": ("preserve canon", "do not execute actions"),
        "available_tools": ("semantic_context", "benchmark"),
        "prior_work": ("first draft reviewed",),
        "known_failures": ("previous output was vague",),
        "expected_output": "A bounded review with concrete corrections.",
    }
    data.update(overrides)
    return WorkEnvelope(**data)


class RecordingProvider:
    provider_id = "test-collaborator"

    def __init__(self, update):
        self.update = update
        self.calls = 0
        self.received = None

    def collaborate(self, envelope):
        self.calls += 1
        self.received = envelope
        return self.update


def make_update(envelope_id="work-001"):
    return CollaborationUpdate(
        envelope_id,
        "ready_for_review",
        "The bounded review is ready.",
        progress=("checked context", "checked constraints"),
        output={"finding": "make the next step explicit"},
        attention_required=True,
    )


def test_executes_provider_once_and_returns_validated_audit_record():
    envelope = make_envelope()
    provider = RecordingProvider(make_update())

    record = execute_collaboration(provider, envelope)

    assert isinstance(record, CollaborationExecutionRecord)
    assert record.envelope == envelope
    assert record.update == make_update()
    assert record.provider_id == "test-collaborator"
    assert provider.calls == 1
    assert provider.received == envelope
    assert len(record.envelope_digest) == 64
    assert len(record.update_digest) == 64


def test_record_is_immutable_and_serializable():
    record = execute_collaboration(RecordingProvider(make_update()), make_envelope())

    assert record.to_dict()["schema_version"] == 1
    assert record.to_json() == record.to_json()
    assert '"provider_id":"test-collaborator"' in record.to_json()
    with pytest.raises(FrozenInstanceError):
        record.update_digest = "changed"


def test_repeated_execution_has_stable_digests_and_json():
    envelope = make_envelope()
    first = execute_collaboration(RecordingProvider(make_update()), envelope)
    second = execute_collaboration(RecordingProvider(make_update()), envelope)

    assert first.envelope_digest == second.envelope_digest
    assert first.update_digest == second.update_digest
    assert first.to_json() == second.to_json()


def test_rejects_non_envelope_before_provider_invocation():
    provider = RecordingProvider(make_update())

    with pytest.raises(TypeError, match="envelope must be a WorkEnvelope"):
        execute_collaboration(provider, object())

    assert provider.calls == 0


def test_rejects_provider_without_nonempty_provider_id():
    class MissingIdProvider:
        def collaborate(self, envelope):
            return make_update(envelope.envelope_id)

    with pytest.raises(TypeError, match="non-empty provider_id"):
        execute_collaboration(MissingIdProvider(), make_envelope())


def test_rejects_provider_without_callable_collaborate():
    class MissingMethodProvider:
        provider_id = "missing-method"

    with pytest.raises(TypeError, match="callable collaborate"):
        execute_collaboration(MissingMethodProvider(), make_envelope())


def test_rejects_provider_returning_wrong_type():
    class MalformedProvider:
        provider_id = "malformed"

        def collaborate(self, envelope):
            return {"status": "ready_for_review"}

    with pytest.raises(TypeError, match="must return a CollaborationUpdate"):
        execute_collaboration(MalformedProvider(), make_envelope())


def test_rejects_update_for_another_envelope():
    class MismatchedProvider:
        provider_id = "mismatch"

        def collaborate(self, envelope):
            return make_update("other-work")

    with pytest.raises(ValueError, match="does not match the work envelope"):
        execute_collaboration(MismatchedProvider(), make_envelope())
