# Semantic next phase — post v0.1

This document is a planning baseline for the next development phase. It does not change the v0.1 architecture or its contracts.

## Baseline

The semantic architecture v0.1 is considered closed at the feature baseline with the full test suite green and a clean working tree. Future work should preserve that baseline and avoid parallel semantic paths.

## Phase order

### 1. Real evidence acquisition

Introduce external evidence adapters without placing provider-specific logic in Core.

Required boundary:

```text
external observation
    ↓
evidence adapter
    ↓
canonical EvidenceClaim
    ↓
EvidenceSnapshot
    ↓
existing contracts / evaluators
```

Rules:

- adapters normalize evidence; they do not decide canon validity;
- Core consumes `EvidenceClaim`, never provider-specific objects;
- unsupported, ambiguous, or incomplete evidence remains `UNKNOWN`;
- provider failure must not be converted into `FAIL`.

### 2. Semantic regression between iterations

The loop currently revalidates every candidate. The next phase should explicitly test whether an iteration can regress previously satisfied invariants.

Desired property:

```text
candidate N satisfies invariant X
        ↓
candidate N+1 changes X
        ↓
new validation required
        ↓
no silent preservation assumption
```

A later candidate may improve or regress an invariant, but the result must be attributable to a fresh evaluation rather than inherited implicitly from the previous candidate.

### 3. Audit trace

Add an immutable execution trace that records, at minimum:

- input idea;
- classification decisions;
- contracts selected;
- EvidenceSnapshot identity/content summary;
- candidate iteration number;
- validation result;
- evaluation result;
- final decision or human-review reason.

The trace should be data, not logging side effects, so it can be tested and serialized independently.

### 4. Real end-to-end slice

Once an external adapter exists, validate the complete path:

```text
human idea
  ↓
pipeline
  ↓
compiled prompt
  ↓
external model / execution layer
  ↓
candidate
  ↓
Canon Guard
  ↓
Evidence Snapshot
  ↓
Evaluator
  ↓
loop
  ↓
accept / continue / human review
```

The execution layer remains injected and Core remains model-agnostic.

### 5. Canon coverage audit

Before adding large numbers of invariants, map the current canon into the existing mechanisms:

- deterministic range;
- deterministic categorical/value;
- deterministic structure;
- deterministic relation;
- perceptual evidence;
- stylistic evidence;
- contextual evidence.

Any canon requirement that cannot be expressed cleanly should trigger a design review rather than an ad-hoc mechanism.

## Non-goals for the next phase

Do not:

- create provider-specific logic inside Core;
- add invariant-specific evaluators when an existing mechanism is sufficient;
- infer classifications or contracts silently;
- weaken `UNKNOWN` semantics;
- mutate the canonical knowledge base during evaluation;
- bypass `EvidenceSnapshot` from a loop iteration;
- expand the taxonomy merely to increase test counts.

## Exit criteria

The next phase should not be considered complete until all of the following are demonstrated:

1. real external evidence is normalized into canonical claims;
2. the same EvidenceSnapshot governs every iteration of one execution;
3. semantic regressions between candidates are explicitly observable;
4. an immutable audit trace can reconstruct the decision path;
5. a real end-to-end execution remains provider-agnostic in Core;
6. the complete regression suite remains green.

The v0.1 baseline is the comparison point for all of these changes.
