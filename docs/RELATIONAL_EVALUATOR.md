# Relational Evaluator

The relational evaluator provides a deterministic tri-state mechanism for comparing two explicitly declared paths within an observed mapping.

It does not infer missing relationships and does not coerce types.

## Contract

- both paths exist and values have the same exact type and value → `pass`
- both paths exist but values differ → `fail`
- either path is missing, or the observed value is not a mapping → `unknown`

This evaluator is intentionally independent from the canonical taxonomy until a real relational invariant is declared. No current catalog invariant is promoted to relational merely to exercise the mechanism.
