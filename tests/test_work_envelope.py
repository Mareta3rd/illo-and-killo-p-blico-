import math

import pytest

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


def test_envelope_is_bounded_and_serializable():
    envelope = make_envelope()
    assert envelope.context == {"route": "gag", "version": 1}
    assert envelope.to_dict()["schema_version"] == 1
    assert envelope.to_json() == envelope.to_json()
    assert '"objective":"Review a small proposal"' in envelope.to_json()


@pytest.mark.parametrize(
    "state",
    ["available", "working", "needs_input", "ready_for_review", "blocked", "done"],
)
def test_supported_work_states(state):
    assert make_envelope(state=state).state == state


def test_rejects_unknown_state_autonomy_and_interrupt_policy():
    with pytest.raises(ValueError, match="unsupported work state"):
        make_envelope(state="whatever")
    with pytest.raises(ValueError, match="unsupported autonomy mode"):
        make_envelope(autonomy="unlimited")
    with pytest.raises(ValueError, match="unsupported interrupt policy"):
        make_envelope(interrupt_policy="always_interrupt")


def test_context_is_bounded():
    with pytest.raises(ValueError, match="maximum key count"):
        make_envelope(context={str(index): index for index in range(25)})


def test_lists_are_bounded_and_unique():
    with pytest.raises(ValueError, match="maximum entry count"):
        make_envelope(constraints=tuple(f"item-{i}" for i in range(33)))
    with pytest.raises(ValueError, match="must not contain duplicates"):
        make_envelope(constraints=("same", "same"))


def test_context_rejects_non_json_values_and_non_mapping():
    with pytest.raises(ValueError, match="finite JSON values"):
        make_envelope(context={"bad": math.nan})
    with pytest.raises(TypeError, match="must be a mapping"):
        make_envelope(context=["not", "a", "mapping"])


def test_expected_output_is_optional_but_bounded():
    assert make_envelope(expected_output="").expected_output == ""
    with pytest.raises(TypeError, match="expected_output must be a string"):
        make_envelope(expected_output=None)
    with pytest.raises(ValueError, match="maximum length"):
        make_envelope(expected_output="x" * 2001)


def test_output_is_bounded_and_requires_mapping():
    with pytest.raises(ValueError, match="maximum encoded size"):
        CollaborationUpdate(
            "work-001",
            "ready_for_review",
            "Done.",
            output={"text": "x" * 24_001},
        )
    with pytest.raises(TypeError, match="must be a mapping"):
        CollaborationUpdate(
            "work-001",
            "ready_for_review",
            "Done.",
            output=["not", "a", "mapping"],
        )


def test_update_requires_input_when_status_requests_it():
    with pytest.raises(ValueError, match="requires a needs_input"):
        CollaborationUpdate("work-001", "needs_input", "I need clarification.")


def test_update_forbids_orphan_input():
    with pytest.raises(ValueError, match="only valid with needs_input"):
        CollaborationUpdate(
            "work-001",
            "working",
            "Proceeding.",
            needs_input="No action is required.",
        )


def test_attention_is_reserved_for_actionable_states():
    with pytest.raises(ValueError, match="actionable handoff"):
        CollaborationUpdate(
            "work-001",
            "working",
            "Still working.",
            attention_required=True,
        )


def test_update_validates_against_envelope():
    envelope = make_envelope()
    update = CollaborationUpdate(
        "work-001",
        "ready_for_review",
        "The proposal is ready for review.",
        progress=("reviewed context", "checked constraints"),
        attention_required=True,
        output={"recommendation": "review"},
    )
    update.validate_for(envelope)
    with pytest.raises(ValueError, match="does not match"):
        CollaborationUpdate(
            "other-work",
            "ready_for_review",
            "Wrong envelope.",
            attention_required=True,
        ).validate_for(envelope)


def test_update_serialization_is_deterministic():
    update = CollaborationUpdate(
        "work-001",
        "blocked",
        "Waiting for missing evidence.",
        blockers=("missing evidence",),
        attention_required=True,
    )
    first = update.to_json()
    assert first == update.to_json()
    assert '"attention_required":true' in first
