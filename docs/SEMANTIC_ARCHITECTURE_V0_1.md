# SinergYa Core v0.1 — Semantic Architecture

## Purpose

This document freezes the semantic architecture established on `feature/semantic-model` at the v0.1 boundary. It describes contracts and execution boundaries, not implementation details.

## Canonical flow

```text
Repository knowledge
        ↓
Invariant taxonomy
        ↓
Invariant classification
        ↓
Dispatcher
        ↓
┌───────────────────────────────┐
│ deterministic evaluator       │
│ OR                            │
│ evidence contract             │
│      ↓                        │
│ EvidenceClaim                 │
│      ↓                        │
│ Evidence Boundary             │
└───────────────────────────────┘
        ↓
EvidenceSnapshot (when Evidence participates)
        ↓
Candidate validation
        ↓
Evaluation
        ↓
Bounded loop / Orchestrator
        ↓
Human review when required
```

## Architectural invariants

1. Every canonical invariant belongs to an explicit classification.
2. Classification never infers a missing invariant, family, or mechanism.
3. A classification mechanism and its family mechanism must agree.
4. `evidence_required` must agree with the declared mechanism.
5. Every evidence-required invariant has exactly one Evidence contract.
6. Evidence contracts require explicit support and route `unknown` to human review.
7. Deterministic invariants cannot enter the Evidence execution boundary.
8. Canonical Evidence is validated before execution and represented by an immutable `EvidenceSnapshot`.
9. Loop iterations reuse the same evidence snapshot; they do not reinterpret raw claims.
10. Missing or unknown evidence is never silently coerced into failure or success.
11. Candidate state and repository knowledge remain non-mutating inputs to evaluation.
12. The Core remains model-agnostic: external generation is injected through the execution boundary.

## Result semantics

Deterministic invariant evaluation uses a shared tri-state result contract:

```text
pass
fail
unknown
```

Evidence adds an epistemic boundary around that same decision surface:

```text
CONFIRMED     → pass
CONTRADICTED  → fail
UNKNOWN       → unknown / human review according to contract
```

The system does not treat absence of evidence as contradiction.

## Evidence contract responsibilities

An Evidence contract declares:

- canonical invariant identity;
- semantic family;
- evidence mechanism;
- canonical claim text;
- explicit-support policy;
- contradiction policy;
- action for unresolved evidence.

The contract does not itself establish truth. It defines what evidence evaluation is permitted and how unresolved evidence is handled.

## Snapshot responsibility

`EvidenceSnapshot` is the execution-time boundary for explicit claims. It freezes the claims accepted for one operation, validates canonical claims once, and supplies the same evidence context to every loop iteration.

This prevents evidence semantics from drifting between candidate iterations.

## Governance boundary

Governance tests verify the structural properties above. They are intended to fail when a future change introduces an execution path that bypasses classification, contracts, the Evidence boundary, or snapshot semantics.

## v0.1 closure criterion

The semantic model is considered closed for v0.1 when:

- taxonomy and classification are explicit and validated;
- deterministic evaluators share one result contract;
- Evidence has a declarative contract layer;
- canonical Evidence is routed and snapshotted;
- pipeline and orchestrator consume the governed Evidence path;
- governance tests remain green;
- the complete test suite remains green.

Future work should extend this architecture rather than introduce parallel semantic paths.
