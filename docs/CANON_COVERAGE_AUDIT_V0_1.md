# Canon coverage audit v0.1

This audit maps the invariant taxonomy to the explicit classification currently present in the repository. It is a coverage review, not a new semantic mechanism.

## Result

The current classification matrix is explicit, structurally valid, and fully covers the invariants present in the canonical character/object/fauna/heritage catalogs. Every classified invariant has exactly one family and mechanism, and every evidence-required classification is governed by an evidence contract.

## Family coverage

| Family | Mechanism | Current canonical classification | Status |
|---|---|---:|---|
| quantitative | deterministic_range | not currently represented | READY / NO CURRENT INVARIANT |
| categorical | deterministic_value | present (`fauna/mosquito_tigre/very_small`) | COVERED |
| structural | deterministic_structure | present in `characters` | COVERED |
| relational | deterministic_relation | taxonomy-defined; current classification contains no relational invariant | READY / NO CURRENT INVARIANT |
| perceptual_semantic | evidence_perceptual | present across fauna, objects and heritage | COVERED |
| stylistic_interpretive | evidence_style | present in objects and heritage | COVERED |
| contextual_conditional | evidence_context | present in fauna | COVERED |

## Important interpretation

A family marked `READY / NO CURRENT INVARIANT` is not a defect. It means the architecture already defines the mechanism, but the present canon does not currently contain an invariant classified into that family.

The audit therefore does **not** add synthetic invariants merely to increase coverage numbers.

## Governance rules confirmed

- New invariants must be classified explicitly before use.
- A family/mechanism assignment cannot be inferred silently.
- Deterministic invariants must remain outside the Evidence boundary.
- Evidence-required invariants must have a matching evidence contract.
- `UNKNOWN` remains a first-class outcome and escalates according to the declared mechanism policy.
- A future invariant that cannot be expressed cleanly by an existing family/mechanism requires design review rather than an ad-hoc evaluator.

## Current conclusion

The semantic architecture has a complete mechanism map for the taxonomy currently defined. There are no unresolved classifications in the current repository. The only open coverage items are taxonomy families with no present canonical invariant (`quantitative` and `relational`); they remain intentionally unpopulated until the canon actually requires them.
