# Collaborative Work Envelope

## Purpose

The collaborative layer exists for work that is broader than a bounded decision but narrower than unrestricted autonomous agency.

It defines two provider-neutral structures:

- WorkEnvelope: the complete bounded brief delivered to a collaborator;
- CollaborationUpdate: the bounded status or handoff returned by that collaborator.

This is a protocol contract, not an execution engine.

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

These values describe policy; they do not grant a capability. Execution is intentionally not implemented in this block.

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

The transition logic itself is deliberately not implemented in this block. A later orchestration layer can enforce legal transitions and persistence without modifying the provider-neutral envelope.

## Boundary

A collaborator using this protocol:

- receives bounded context rather than ambient project state;
- can return progress and proposals without becoming Core;
- cannot infer Core authority from a prompt;
- does not execute actions merely because an output mentions them;
- does not silently change canon;
- remains replaceable by another provider or a human.

## Next target

Next block: add a small orchestration seam that accepts a WorkEnvelope, invokes an injected collaboration provider, validates CollaborationUpdate, and returns an auditable handoff record.

No concrete model/runtime or automatic action execution should be added in that block.
