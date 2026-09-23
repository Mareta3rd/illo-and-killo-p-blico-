# Deterministic Decision Provider

## Purpose

The deterministic provider is the reference implementation for the
provider-neutral DecisionProvider capability.

It exists for three reasons:

1. provide a dependency-free implementation against which future providers can be tested;
2. establish the simplest possible decision path before adding external decision services;
3. make capability benchmarks reproducible.

## Contract

The implementation must consume the existing DecisionRequest and return a
validated DecisionResult.

It should not:
- modify the DecisionProvider contract;
- execute tools or actions;
- know about Jev, OpenAI, Anthropic, Gemini or Qwen;
- make routing decisions about which provider to use.

## Initial model

The first reference implementation may use a predeclared answer map keyed by
question_id.

That is intentionally simple. It gives us a deterministic baseline for:
- result correctness;
- serialization;
- latency;
- repeatability;
- failure behavior.

More sophisticated rule engines can be evaluated later without changing the
DecisionProvider interface.

## Benchmark role

A future benchmark can submit the same DecisionRequest fixtures to:
- deterministic provider;
- Jev provider;
- model-based decision provider;
- human review.

The benchmark compares the decision outputs and operational characteristics
without allowing any participant to execute the selected action.
