# Canon / Validation Guard

## Purpose

The Canon / Validation Guard checks a proposed piece against the repository's explicit canon and intention rules.

It is a gate, not a generator. It may reject or escalate a proposal, but it must not rewrite the proposal or modify repository knowledge.

## v0.1 checks

1. **Character invariants**
   - Killo's clavel in the ear is mandatory when Killo is present, unless an explicit documented exception is supplied.
   - Canonical character invariants must not be silently removed.

2. **Intentional reuse**
   - Recurring assets such as the mosquito, shark, ham and espeto require an explicit narrative or comedic intention when reused.
   - Repetition alone is insufficient.

3. **Element intention**
   - Every proposed element must have an explainable intention.
   - Missing intention produces a validation issue rather than an invented justification.

4. **Human escalation**
   - A proposal that conflicts with a Level A invariant requires human review.
   - A proposal with unexplained recurring-asset reuse requires human review.

## Non-goals

The guard does not generate images, rewrite prompts, call external models, infer hidden intentions, or mutate canon.

## Contract

Input:

```text
proposal + loaded repository knowledge
```

Output:

```text
ValidationResult
- valid
- requires_human_review
- issues
```
