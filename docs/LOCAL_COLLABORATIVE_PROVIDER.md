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

The bounded collaboration runner defaults to the smaller `qwen3-4b` model ID and
accepts `LOCAL_QWEN_MODEL` or `--model` when a local server exposes a different name.
It does not install a runtime or download a model. Actual inference is optional and
should only use a model already available through the explicitly started local server.

## Safety boundary

available_tools describes metadata only. It does not grant permission.

The adapter returns a CollaborationUpdate. Core remains responsible for any later
evaluation, human handoff, routing decision or action authorization.

## Verifying a result

Use the optional GitHub Actions job for the pinned Qwen3-4B CPU experiment. Review the
resulting CollaborationExecutionRecord against the original brief saved as
`envelope.context.requested_idea`. A valid record demonstrates that the response fits
the protocol. Review creative adherence separately, including whether the requested
object drives the gag and whether the comic mechanism differs from Gag 001.
The first cloud result and its limitations are recorded in [AI_HANDOFF.md](AI_HANDOFF.md).
