# Local collaborative provider

## Purpose

This adapter is the first concrete provider for the provider-neutral collaborative
protocol. It is designed for a local OpenAI-compatible runtime such as the llama.cpp
server used by the Qwen local prototype.

The adapter is deliberately separate from the orchestration seam:

    WorkEnvelope
        -> LocalStructuredCollaborationProvider
        -> CollaborationUpdate
        -> execute_collaboration()
        -> CollaborationExecutionRecord

## Contract

The provider:

- consumes exactly one bounded WorkEnvelope;
- builds a deterministic prompt containing the bounded envelope, prior work and known failures;
- requests a strict structured CollaborationUpdate;
- validates the returned object through the existing CollaborationUpdate contract;
- exposes provider and model identity for inspection;
- never executes tools or actions;
- never changes canon;
- never emits Core decisions.

The provider-specific structured output contains collaboration state plus a bounded
output object with answer, rationale, proposals and questions. This gives a local
model room to produce concrete work without making the provider-specific response
shape part of Core canon.

## Why this differs from the earlier narrow Qwen experiment

The earlier local decision adapter was intentionally narrow: it asked for a single
boolean, choice or score. That is appropriate for DecisionProvider but insufficient
for cooperative creative work.

This adapter instead gives the model the complete WorkEnvelope boundary, including
context, constraints, prior work and known failures. The prompt explicitly tells the
model to use those together and to avoid generic output.

This is still bounded. More context is not implied by the provider. The model receives
only what Core places in the envelope.

## Runtime

The adapter requires an injected OpenAI-compatible client. No concrete runtime or SDK
is imported by the provider itself.

The first live target remains the local Qwen3.8-27B runtime. Actual live inference belongs
in a later experiment after the adapter passes the repository closure gate.

## Safety boundary

available_tools describes metadata only. It does not grant permission.

The adapter returns a CollaborationUpdate. Core remains responsible for any later
evaluation, human handoff, routing decision or action authorization.

## Next experiment

After the complete suite is green, run one real local collaboration using a deliberately
constructed WorkEnvelope with:
- a concrete objective;
- selected current semantic context;
- prior failed or vague output;
- explicit expected output;
- no implied tool execution.

Capture the resulting CollaborationExecutionRecord and inspect the output for specificity,
context use, non-intrusiveness and compliance with the envelope before considering any
further provider changes.
