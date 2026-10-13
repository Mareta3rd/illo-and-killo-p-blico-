# Collaborative Work Envelope

## Purpose

The collaborative layer exists for work that is broader than a bounded decision but narrower than unrestricted autonomous agency.

It defines two provider-neutral structures:

- WorkEnvelope: the complete bounded brief delivered to a collaborator;
- CollaborationUpdate: the bounded status or handoff returned by that collaborator.

This is a protocol contract plus a small orchestration seam; it is not an autonomous execution engine.

## WorkEnvelope

A work envelope answers:

- What are we trying to achieve? objective
- Where does the work belong? project
- What state is the work in? state
- What context is relevant? context
- What must not be violated? constraints
- Which capabilities/tools are available? available_tools
- What has already been done? prior_work
- What is known not to work? known_failures
- What form should the result take? expected_output
- How much autonomy is allowed? autonomy
- When may the collaborator interrupt? interrupt_policy

The contract deliberately keeps these dimensions separate. A collaborator does not infer permission from the objective, and availability of a tool does not itself authorize its use.

### Boundedness

The envelope limits context size, list sizes and individual text sizes. Context must be finite JSON data. Outputs are bounded too. This prevents accidental "send the whole project" behavior and keeps the input/output deterministic and auditable.

### Autonomy modes

- advisory: analysis/proposal only;
- bounded_execution: future mode for explicitly scoped execution;
- human_approval_required: work may prepare changes but a human approval gate remains mandatory.

These values describe policy; they do not grant a capability. The current orchestration seam does not execute tools or actions.

### Interrupt policy

- needs_input_only: surface only questions that block progress;
- state_change_or_input: surface actionable state changes and blocking questions;
- explicit_request_only: do not proactively surface intermediate status.

For Sinergya, state_change_or_input is the intended cooperative default because it avoids continuous chatter while keeping meaningful handoffs visible.

## CollaborationUpdate

A collaboration update answers:

- what happened;
- what remains in progress;
- whether input is needed;
- whether there are blockers;
- whether a bounded output is ready;
- whether human attention is actually required.

attention_required is intentionally constrained: it can only be true for needs_input, ready_for_review, blocked or done.

The protocol therefore distinguishes:

working != needs attention

and:

tool available != tool authorized.

## State model

The permitted states are:

    available -> working -> needs_input / ready_for_review / blocked -> done

The transition logic itself remains a future policy/orchestration concern. The provider-neutral envelope does not mutate its own state.

## Orchestration seam

core/collaboration_execution.py now provides:

- CollaborationProvider: an injected provider contract exposing provider_id and collaborate(envelope);
- execute_collaboration(...): one bounded provider invocation;
- CollaborationExecutionRecord: an immutable handoff record containing the envelope, validated update, provider identifier and deterministic SHA-256 digests of the exact envelope/update JSON.

The seam validates the envelope before invocation, rejects providers without a usable identity or callable collaboration method, requires an actual CollaborationUpdate, and validates that the returned update belongs to the same envelope.

It deliberately does not:

- execute tools or external actions;
- infer authorization from available_tools;
- select a production provider;
- create or modify canon;
- turn a collaborator update into a Core decision.

Verification of this orchestration seam is performed by the repository's complete closure gate. A green checkpoint is required before the next layer is added.

## Boundary

A collaborator using this protocol:

- receives bounded context rather than ambient project state;
- can return progress and proposals without becoming Core;
- cannot infer Core authority from a prompt;
- does not execute actions merely because an output mentions them;
- does not silently change canon;
- remains replaceable by another provider or a human.

## Next target

After the orchestration seam is verified green, add a concrete collaborative provider adapter separately from this protocol. The first candidate can be the local Qwen runtime, but the provider must consume the WorkEnvelope and return a CollaborationUpdate without bypassing Core.

No automatic action execution or provider adoption should be bundled into that adapter block.
