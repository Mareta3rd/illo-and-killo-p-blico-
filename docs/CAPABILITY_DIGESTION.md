# Capability Digestion Model

## Purpose

The project treats external AI systems as temporary implementations of capabilities,
not as architectural authorities.

The durable object is the capability contract. A provider is one way of supplying
that capability. An adapter translates between the provider's native interface and
the internal contract. Evidence from experiments determines whether a capability is
useful enough to retain.

This keeps the system replaceable: a provider can disappear, change pricing, change
models, or be superseded without changing the semantic/core contract.

## Four layers

### Capability

A provider-neutral ability that Core can request.

Examples:

- bounded boolean judgement;
- bounded choice;
- bounded score;
- candidate generation;
- evidence extraction;
- audit capture;
- benchmark execution.

A capability should have a small, explicit input/output contract.

### Provider

An implementation that supplies one capability.

Examples may be:

- a deterministic local implementation;
- a TypeSafe Jev implementation;
- a model-based implementation;
- a future local model;
- a human-review process.

A provider is never allowed to redefine Core semantics simply because its native API
uses different concepts.

### Adapter

A replaceable translation layer.

The adapter is responsible for:

- mapping provider-native inputs to the capability contract;
- mapping provider-native outputs back to the capability contract;
- rejecting mappings that require invented semantics;
- keeping provider-specific dependencies and lifecycle out of Core.

Thresholds, rubrics and other translation policies belong here when the provider-native
representation does not match the internal representation.

### Evidence

An observation of how an implementation behaves.

Benchmark observations, latency, repeatability, contract failures, confidence and
provider metadata are evidence. They do not automatically become production policy.

## Digestion rule

An external system is considered architecturally digested only when the project can
describe the useful capability without naming the original provider.

Example:

TypeSafe Jev -> probabilistic bounded decision capability -> DecisionProvider

The middle layer is the durable abstraction.

The provider can then be replaced by another implementation against the same capability
without rewriting the semantic pipeline.

## Current digestion state

The deterministic decision provider is already fully internalized as a reference
implementation.

The benchmark fixture loader and comparison harness are internalized engineering
infrastructure.

The TypeSafe Jev adapter is currently an experimental provider implementation on an
auxiliary branch. It has not yet been accepted into the green feature branch.

Current Jev-specific findings:

- boolean decisions need an explicit probability threshold;
- choice decisions map naturally to the existing constrained-choice contract;
- score decisions need an explicit ordered rubric; the adapter must reject a score
  request that lacks one;
- Jev-native probability must not be silently relabeled as Core confidence;
- the TypeSafe SDK should remain optional and lazily imported.

## Retirement test

A useful test of abstraction maturity is:

Remove the external provider package and credentials. Can Core still import, validate,
benchmark, audit and execute its own contracts using another provider?

The intended answer is yes.

External providers should therefore accumulate evidence and adapters, not architectural
dependence.
