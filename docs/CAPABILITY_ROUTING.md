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

- `decision` — bounded judgments such as route, classify, select, score or escalate;
- `generation` — create text, code, image or other artifacts;
- `execution` — modify files, run commands or operate a workspace;
- `perception` — inspect images, documents or other external state;
- `orchestration` — manage sessions, delegation, recovery and long-running work;
- `computer_use` — operate desktop/browser interfaces;
- `evaluation` — verify acceptance, regression, scope and policy compliance.

## DecisionProvider contract

The first concrete capability contract to implement is `DecisionProvider`.

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
Gemini, Qwen or any other provider.

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
