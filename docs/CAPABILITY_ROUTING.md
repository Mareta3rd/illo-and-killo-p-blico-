# Capability Routing Contract

## Purpose

The project is evolving from a provider-centric architecture toward a
capability-centric architecture.

The system should ask:

> What kind of capability is required?

before asking:

> Which provider or product should perform it?

This keeps Core stable while allowing providers and runtimes to change.

## Initial capability classes

- decision — bounded judgments such as route, classify, select, score or escalate;
- generation — create text, code, image or other artifacts;
- execution — modify files, run commands or operate a workspace;
- perception — inspect images, documents or other external state;
- orchestration — manage sessions, delegation, recovery and long-running work;
- computer_use — operate desktop/browser interfaces;
- evaluation — verify acceptance, regression, scope and policy compliance.

## Collaborative work protocol

The collaborative layer sits above individual provider capabilities and below Core authority.

It uses a bounded WorkEnvelope to define one unit of work and a CollaborationUpdate to communicate progress or a handoff without requiring continuous human intervention.

The protocol keeps three things distinct:

- context is information, not permission;
- available tools are capability metadata, not authorization;
- a collaborator's proposed output is not a Core decision or executed action.

See docs/COLLABORATIVE_WORK_ENVELOPE.md for the contract and boundaries.

## Local collaborative provider prototype

The first concrete implementation of the collaborative capability is
`collaboration.qwen_local`.

It consumes a bounded `WorkEnvelope` and returns a validated
`CollaborationUpdate` through an injected OpenAI-compatible local runtime.
The orchestration seam records the provider identifier, optional model identifier,
the exact envelope/update digests and the validated handoff.

This capability is registered as `prototype`, not adopted. The first live target
is Qwen3.8-27B in the same local runtime family as the DecisionProvider prototype.
Actual quality, latency and hardware feasibility remain empirical questions.

The capability remains replaceable: the routing layer must reason about
`collaboration`, not about Qwen as a special case.

## DecisionProvider contract

The first concrete capability contract to implement is DecisionProvider.

A decision request should contain:
- a stable question identifier;
- a bounded decision kind;
- structured state/context;
- the question to answer;
- optional allowed choices.

A decision result should contain:
- the question identifier;
- the decision kind;
- the typed result value;
- an uncertainty/confidence value when available;
- the provider identifier;
- an optional model/runtime identifier.

The provider only supplies the judgment. It never executes the resulting action.

## Why this boundary exists

A fast decision model such as Jev may eventually answer a routing question, while
a deterministic rule or human may answer the same contract. The calling system
must not care which one supplied the result.

The first implementation therefore must not import Jev, OpenAI, Anthropic,
Gemini, Qwen or any other provider. The machine-readable registry in
data/capabilities.json is descriptive metadata and is validated independently by
core/capability_registry.py without selecting a provider.

## Safety and determinism

- Requests and results use closed, deterministic serializable structures.
- Confidence is informational and must not silently become authorization.
- The contract must not contain Core decisions, canon mutations or tool execution.
- Provider names are metadata, not routing logic.
- A future router may choose among DecisionProviders, but that router is a
  separate concern from the provider contract.

## First provider-neutral test target

A minimal implementation should prove:
1. boolean, choice and score decisions can be represented;
2. malformed decision kinds are rejected;
3. choice results remain inside the request's allowed choices;
4. confidence is bounded when present;
5. serialization is deterministic;
6. a fake provider can implement the protocol without any external dependency.

This is deliberately small. It establishes the seam first; real Jev integration
comes only after the seam is green.

## Capability digestion

The project does not seek permanent dependence on a provider. External systems are
tested as implementations of capabilities that should remain expressible without the
provider's brand.

The lifecycle is:

OBSERVE -> INVESTIGATE -> PROTOTYPE -> BENCHMARK -> ADOPT -> MAINTAIN / DEPRECATE

A provider is architecturally digested only when the useful behavior can be retained
behind the capability contract and Core can continue operating with another
implementation after the external dependency is removed.

For decision capability this currently means:

- Core owns DecisionRequest, DecisionResult, validation, audit and action authority.
- A provider adapter owns native request/response translation and provider-specific
  policies such as probability thresholds or score rubrics.
- Benchmarking produces evidence but does not select a provider.
- The provider can be removed without changing the semantic model.

TypeSafe Jev is currently an experimental implementation of the decision capability.
The adapter work is isolated on an auxiliary branch and remains unevaluated until the
normal test/closure gate passes.
