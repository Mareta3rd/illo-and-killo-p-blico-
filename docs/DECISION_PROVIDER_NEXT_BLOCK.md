# Decision Provider Next Block

## Status

The green checkpoint on `feature/semantic-model` remains untouched at commit `762b7e5`.

This auxiliary branch, `assistant/benchmark-comparison-prep`, contains an isolated
benchmark-comparison helper and focused tests. They are intentionally not merged into
the green branch until the Codespace runs the full closure gate.

## Comparison helper

Implemented in:

- `core/decision_benchmark_comparison.py`
- `tests/test_decision_benchmark_comparison.py`

The helper accepts a mapping of participant IDs to `DecisionProvider` implementations,
materializes the benchmark cases once, runs the identical cases for each participant,
and preserves each `DecisionBenchmarkReport` independently.

The comparison layer explicitly does not:

- rank participants;
- calculate an aggregate score;
- select a production provider;
- route a request;
- execute an action.

Participant identity is kept separate from the provider/model metadata returned inside
`DecisionResult`.

## Jev compatibility findings

TypeSafe's official launch material describes Jev as a System One model for fast,
structured decisions, with typed outputs rather than generated strings. TypeSafe
reports 70--500 ms end-to-end response times and $0.042 per million input tokens;
these are vendor-published figures and should be treated as such until independently
measured in our environment.

The official Python SDK exposes three relevant primitives:

- Noul: probability of a yes/true answer;
- Choice: selected option, confidence and per-option probabilities;
- Score: probability-weighted average of ordered rubric levels, confidence and
  per-level probabilities.

The official SDK therefore maps conceptually well to the existing `boolean`,
`choice`, and `score` decision kinds, but the mapping is not completely mechanical.

### Adapter rules to preserve the Core boundary

1. The adapter must receive a `DecisionRequest` and return only `DecisionResult`.
2. `choice` maps directly to the selected allowed label and confidence.
3. `score` maps directly only when the request carries an explicit ordered rubric.
   The adapter must not invent score criteria.
4. `boolean` requires an explicit adapter threshold policy because Jev's native Noul
   output is a probability rather than a boolean. The threshold must be visible and
   tested; it must not be silently embedded in Core.
5. Jev's Noul probability should not be mislabeled as provider-supplied confidence.
   The current contract may leave `confidence` unset for boolean results unless a
   separate, explicitly named derived-confidence policy is introduced.
6. The adapter should use an injected client seam. Importing the optional TypeSafe SDK
   should remain lazy/provider-specific so the provider-neutral Core package does not
   acquire a hard runtime dependency merely by importing the adapter module.
7. Live API credentials must remain environment-only. No key belongs in fixtures,
   tests, source, commits, or handoff notes.

## Recommended execution order

First, run the focused comparison/adapter tests and then the complete closure script on this
auxiliary branch.

Second, build a fake-client Jev adapter test surface with no network access. Verify
contract mapping, choice containment, score handling, boolean threshold behavior,
provider/model metadata, and error propagation through `execute_decision()`.

Third, only after the adapter is green, run a real Jev benchmark with the repository's
fixed v1 objective fixtures. The runner excludes the harness-control case by default;
that case is a robustness control, not a provider-quality assertion. Any semantic
incompatibility, such as the fixed score fixture lacking an explicit rubric, should be
recorded as a contract gap rather than hidden through provider-specific fixture rewrites.

Fourth, measure Jev in the same environment used for the other providers. Record
latency, repeatability, contract validity, expected-vs-observed behavior and any
available cost/usage metadata separately. Do not create a universal provider score.

## Current external verification

TypeSafe's official launch announcement is dated 15 September 2026. Its public Python
SDK repository is active; the latest tagged release visible on GitHub is v0.7.1 dated
21 September 2026. The service status page currently reports the API operational, while
also showing resolved incidents earlier in September. These operational facts can
change and must be rechecked before a live run.

The project should therefore treat Jev as a now-verifiable external provider, not as
an unverified future concept, while still keeping the provider replaceable.

## Open contract question before full digestion

Jev exposes richer probabilistic information than the current DecisionResult retains:
the current adapter keeps the selected boolean/choice/score and provider-supplied
confidence where available, but it deliberately does not add provider-specific
probability distributions to Core.

This is intentional for the first compatibility step. A later architectural block may
consider an optional provider-neutral distribution/evidence field if several decision
providers expose useful calibrated distributions. That change should be justified by
multiple capability requirements, not by Jev alone.

Until then, the adapter is a projection into the existing contract, not a claim that
the full Jev capability has been absorbed.

### Noul confidence nuance

The current Python SDK source models NoulAnswer with the `noul` probability field and
does not expose a separate Noul confidence field, while TypeSafe's public product
material describes confidence as part of System One outputs. The adapter therefore
leaves Core confidence unset for boolean Noul decisions rather than inventing a
derived value. This should be rechecked against a live response before any contract
extension is considered.
