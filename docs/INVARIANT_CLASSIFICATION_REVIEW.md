# Invariant Classification Review

## Purpose

Review the current invariant-to-family classification before implementation of invariant-specific evaluators.

## Classification contract

Every canonical invariant must have exactly one primary family, one mechanism, and an explicit `evidence_required` flag.

## Review principles

- Deterministic families are used only when the property can be established from structured canonical data without interpretive judgment.
- Evidence-bound families are used when validation depends on perception, stylistic interpretation, or activation of a context-dependent rule.
- `UNKNOWN` never becomes acceptance implicitly.
- Catalog metadata such as `name`, `role`, and `affordances` is not treated as an invariant.
- Classification should describe how a property is proven, not merely what the property sounds like.

## Borderline cases

### recognizable_silhouette

Classification: `perceptual_semantic`.

Reason: the property is about whether the representation is recognisable as the canonical referent. Although silhouette is structurally influenced, the acceptance criterion is perceptual rather than a deterministic structural relation.

### simplified_nasrid_reading

Classification: `stylistic_interpretive`.

Reason: the property concerns a stylistic translation of Nasrid visual language. It cannot be reduced to a fixed set of objective fields without losing the intended interpretation.

### chairlift_reading

Classification: `perceptual_semantic`.

Reason: a viewer must be able to recognise the object as a chairlift. The underlying geometry can vary while the intended reading remains stable.

### simplified_iconic_form

Classification: `structural`.

Reason: in the current catalog this invariant is a canonical construction constraint: the object must retain a simplified but coherent iconic structure. It is treated as deterministic only at the structural contract level; perceptual escalation remains available when a representation cannot establish compliance.

## Implementation consequence

The taxonomy and classification files remain the source of classification truth. Specific invariant evaluators must consume these contracts rather than hard-code family-specific behavior into unrelated modules.

## Next step

Introduce the first invariant evaluators for deterministic families, beginning with quantitative and categorical properties. Evidence-bound families should be connected only after their evidence contracts are explicit.
