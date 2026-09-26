# Decision Provider Comparison Contract

## Purpose

Define the exact provider-neutral comparison surface that future DecisionProvider
implementations must satisfy.

The comparison layer is evidence about provider behavior. It is not a leaderboard,
a production routing policy, or an authority layer.

## Fixed v1 fixture set

The repository source of truth is:

`data/decision_benchmark_fixtures.json`

Fixture set identifier: `decision-benchmark-v1`.

The set contains three objective contract-level cases and one harness-control case:

| Case | Kind | Expected result | Role |
| --- | --- | --- | --- |
| `boolean-review-escalation` | boolean | `true` | objective |
| `choice-confirmed-route` | choice | `accept` | objective |
| `score-evidence-coverage` | score | `0.75` | objective |
| `control-missing-provider-answer` | boolean | expected controlled failure | harness_control |

The first three are intentionally small, reproducible and objectively answerable
from their supplied context. Their expected values test the decision contract;
they are not a claim that a provider has one universal notion of quality.

The fourth fixture exists to verify that malformed/unconfigured provider behavior
is recorded as failure rather than silently converted into success. It is a
harness robustness control, not a provider-quality case.

## Same-input rule

Every participating provider receives the same `DecisionRequest` serialized from
the fixture set.

A provider-specific adapter may translate that request into its native transport,
but it must not alter the fixture's semantic content, expected answer, choices or
benchmark role.

Provider-specific prompts, schemas and transport details remain outside the Core
benchmark contract.

## Execution contract

For each fixture and provider:

1. execute through the existing `execute_decision()` validation seam;
2. run the configured number of identical repetitions;
3. preserve raw latency for each observation;
4. preserve provider/model identifiers and confidence when supplied;
5. distinguish contract-invalid output, expected failure, unexpected failure,
   abstention and ordinary wrong answers;
6. record expected-vs-observed results per case;
7. retain request/result digests whenever a valid `DecisionExecutionRecord` exists.

A provider must not execute the action represented by a decision during the
benchmark.

## Comparison dimensions

The comparison record is deliberately multidimensional:

- contract validity;
- expected-vs-observed value;
- repeatability;
- latency;
- provider/model metadata;
- confidence;
- failure and abstention behavior;
- execution digests for validated results.

No aggregate score is defined here.

A later analysis may report each dimension separately, but it must not collapse
them into a single provider ranking unless a separate project decision explicitly
creates such a metric.

## Fixture stability

The v1 fixture set is versioned by identifier rather than edited silently.

A semantic change to a fixture should create a new fixture-set identifier. Provider
adapters must not maintain private copies of the benchmark expectations.

## Future judgment set

The v1 set is deliberately objective and small. A future subjective/judgment
benchmark requires a separately documented gold-label procedure, including how
human reviewers establish expected outcomes and how disagreement is represented.

That future work is outside the current comparison-preparation block.

## Adoption boundary

Passing the comparison contract does not select a provider for production.

Production adoption remains a separate architectural decision that must consider
the intended capability, operational characteristics, integration boundary,
security constraints and the availability of a deterministic, alternate-provider
or human-review path where practical.
