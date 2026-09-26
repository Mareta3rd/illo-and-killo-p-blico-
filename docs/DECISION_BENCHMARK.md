# Decision Provider Benchmark Protocol

## Purpose

Compare different implementations of the provider-neutral DecisionProvider contract
without changing the request contract or allowing any provider to execute actions.

The first comparison should use the same DecisionRequest fixtures for every
implementation. The exact v1 comparison set is defined in `docs/DECISION_BENCHMARK_COMPARISON.md`
and sourced from `data/decision_benchmark_fixtures.json`.

## Participants

Initial participants:

- deterministic reference provider;
- a future TypeSafe Jev adapter;
- a future model-based decision provider;
- optional human review as an external reference.

Participants are implementations of the same capability, not competing authorities.

## Measures

Record at least:

- decision correctness against the fixture expectation;
- contract validity;
- choice containment;
- repeatability across identical requests;
- latency;
- operational cost when measurable;
- provider/model identifier;
- confidence when supplied;
- failure or abstention behavior.

Do not collapse these measurements into a single universal score unless a later
project decision explicitly requires one.

## Fixture requirements

A benchmark fixture should:

- have a stable question_id;
- use one of the closed decision kinds;
- provide explicit expected behavior for the benchmark;
- avoid secret data;
- be independent of a particular provider;
- remain small enough to reproduce locally.

Fixtures should cover at least:

1. a boolean decision;
2. a constrained choice decision;
3. a numeric score;
4. a request that should fail or require escalation.

## Authority boundary

A benchmark result is evidence about provider behavior.

It does not:
- change canon;
- authorize an action;
- select the production provider automatically;
- modify Core policy.

Provider selection remains a separate routing/policy decision.

## Adoption rule

A provider enters the adopted set only after:

1. it satisfies the DecisionProvider contract;
2. benchmark behavior is inspected;
3. operational characteristics are acceptable for the intended capability;
4. its integration boundary is explicit and replaceable;
5. the project retains a viable alternative or human-review path where practical.

The benchmark is therefore an engineering instrument, not a leaderboard.
