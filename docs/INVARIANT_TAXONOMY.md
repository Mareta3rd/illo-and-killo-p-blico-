# Invariant Taxonomy

## Purpose
Define a small, explicit taxonomy for canonical invariants before adding automated invariant evaluation to SinergYa Core.

The taxonomy separates **what is canonical** from **how a canonical property can be verified**. It deliberately does not encode catalog metadata such as `name`, `role`, or `affordances` as invariants.

## Primary families

| Family | What it covers | Default mechanism | Typical examples |
| --- | --- | --- | --- |
| `quantitative` | Measurable values, counts, ranges and limits | `deterministic_range` | `count` |
| `categorical` | Discrete canonical values | `deterministic_value` | `color`, `type` |
| `structural` | Required parts, presence and internal construction | `deterministic_structure` | `green_scarf`, `black_hooves` |
| `relational` | Required relationships between parts or elements | `deterministic_relation` | positional or component relationships |
| `perceptual_semantic` | Recognizability and intended visual/semantic reading | `evidence_perceptual` | `readable_as_mosquito`, `recognizable_mass` |
| `stylistic_interpretive` | Canonical aesthetic or reinterpretation constraints | `evidence_style` | `simplified_nasrid_reading`, `fantasy_reference_reading` |
| `contextual_conditional` | Rules that activate under explicit scene/use conditions | `evidence_context` | `summer_context`, `fin_only_when_needed` |

## Why these families

The first four families are normally suitable for deterministic validation. They describe properties that can be represented as explicit values, structure or relationships.

The last three families are deliberately evidence-bound. They describe properties where a raw value comparison is not enough. For example, `readable_as_seagull` is not equivalent to a string match; it is a claim about the resulting representation. The system must therefore use explicit Evidence and preserve the existing tri-state boundary: `CONFIRMED`, `CONTRADICTED`, or `UNKNOWN`.

## Evidence mechanism contract

Every invariant family maps to exactly one primary verification mechanism.

### Deterministic mechanisms

`deterministic_range`, `deterministic_value`, `deterministic_structure`, and `deterministic_relation` may produce a decision directly from canonical data and the candidate representation.

A deterministic contradiction is a validation failure. A missing observation is not acceptance; it becomes `UNKNOWN` and may escalate to human review.

### Evidence-bound mechanisms

`evidence_perceptual`, `evidence_style`, and `evidence_context` must cross the Evidence boundary.

Their evaluation is:

```text
CONFIRMED    -> invariant satisfied
CONTRADICTED -> invariant violated / candidate may continue
UNKNOWN      -> human review
CONFLICT     -> human review
```

There is no implicit shortcut from absent evidence to acceptance.

## Invariant versus metadata

The following remain **metadata or usage policy**, not invariant families:

- `name`
- `role`
- `affordances`
- reuse/recurrence policy
- whether an element is selected for a particular gag
- production intent

For example, `supports_boxing_gag` describes an object's affordance. It can inform composition and intention, but it should not be treated as a visual invariant of the object's identity.

## Conditional invariants

A conditional invariant must make its activating condition explicit. A rule such as `fin_only_when_needed` is not a permanent visual requirement; it is a conditional constraint. The evaluation therefore needs both:

1. evidence that the condition is active; and
2. evidence that the candidate complies with the rule under that condition.

## Migration rule

Existing invariant strings are not reinterpreted automatically.

Before an invariant is passed to an automated invariant evaluator, it must be assigned a primary family and mechanism in the taxonomy registry. Unknown or unclassified invariants remain visible and require human review rather than receiving a guessed family.

## Canonical decision policy

The taxonomy follows the existing Core decision boundary:

```text
canonical rule
     ↓
 family + mechanism
     ↓
 evidence / deterministic check
     ↓
 CONFIRMED | CONTRADICTED | UNKNOWN
     ↓
 accept | continue | human_review
```

The taxonomy is intentionally small. New families should only be added when an existing family cannot express the invariant without creating ambiguous or contradictory semantics.
