# Semantic Model v1

## Purpose

This document defines the semantic model used by the Illo & Killo Core to distinguish canonical identity, permitted adaptation, contextual variation, recurring elements, required conditions, and evidence states.

The purpose of this model is to prevent two opposite failures:

1. treating every characteristic as an immutable rule;
2. allowing creative variation to silently alter canon.

The model is semantic rather than purely visual. The system must protect meaning and identity, not demand pixel-level reproduction.

---

## 1. Core Principle

The Core must distinguish between:

- what defines canonical identity;
- what may legitimately adapt;
- what may vary freely;
- what may recur without being mandatory;
- what is required only under specific conditions;
- what is contextual;
- what an element is allowed to be used for;
- what can actually be established from available evidence.

The absence of evidence is not evidence of absence.

The inability to confirm a property must not automatically be treated as a violation.

---

# 2. Canonical Property Classes

Canonical properties are divided into three primary levels.

## Level A — Invariant

An invariant is a canonical property whose alteration changes or risks changing the identity or established canon of an element.

An invariant must not be silently changed.

An explicit and documented decision is required to introduce a canonical exception.

Examples:

- Killo has black spots.
- Killo has a clavel.
- Killo has black hands.
- Killo has black hooves.
- Illo has a green scarf.
- Illo has a yellow tuft.
- Illo has a short flame tail.

An invariant protects semantic identity, not literal geometry.

### Important rule

An invariant does not necessarily mean that every attribute associated with it is fixed.

Example:

Killo's canonical property `black_spots` is invariant, while the number of spots may remain variable within an explicitly defined range.

Therefore:

    invariant meaning
        !=
    fixed visual representation

---

## Level B — Adaptable

An adaptable property may be intentionally transformed to fit a context while preserving the underlying identity of the character, object, reference, or element.

Examples include:

- clothing;
- profession;
- historical period;
- contextual props;
- stylistic reinterpretation;
- parody-specific presentation.

Adaptable does not mean unrestricted.

An adaptation is valid only while it remains compatible with the canonical identity and any applicable constraints.

Example:

Killo may wear historical clothing in a period parody.

This does not permit replacing Killo's canonical identifying characteristics.

---

## Level C — Variable

A variable property may change without constituting a canonical alteration, provided it remains within other applicable constraints.

Examples:

- background;
- scene details;
- secondary characters;
- atmosphere;
- typography when not otherwise constrained;
- pose;
- expression;
- number of canonical spots when explicitly defined as variable;
- visual distribution of adaptable features.

Variable does not mean unconstrained.

A variable property may still be subject to:

- collection rules;
- production requirements;
- contextual rules;
- readability requirements;
- stylistic coherence;
- explicit user intent.

---

# 3. Recurring Elements

Recurring is not a fourth canonical level.

A recurring element is an element that may reappear across works because it belongs to the established visual or narrative language of the universe.

Recurrence does not make presence mandatory.

Examples:

- recurring fauna;
- recurring comic props;
- recurring gags;
- recurring secondary details.

A recurring element may be used when it contributes naturally to the piece.

Repeated use must not become mechanical.

## Recurrence Principle

> Recurrence creates an expectation of coherence, not an obligation of presence.

A recurring element should not be inserted into every piece merely because it exists in the repository.

When a recurring asset is introduced, its use may require an explicit narrative, comic, contextual, or stylistic intention according to the applicable rules.

---

# 4. Required

Required is not a canonical property class.

Required describes a condition under which something must be present or satisfied.

Example:

Killo's clavel is an invariant.

When Killo is present in a representation where his identifying features are expected to be represented, the clavel is required unless an explicit documented exception applies.

Therefore:

    invariant
        =
    what is canonically stable

while:

    required
        =
    what must be present when a condition activates the obligation

A character-specific requirement must not be interpreted as a universal requirement for the entire composition.

Example:

If Killo is absent, Killo's clavel is not required.

---

# 5. Contextual

Contextual describes a property or rule whose application depends on circumstances.

Context may include:

- narrative situation;
- parody;
- collection;
- medium;
- production format;
- historical setting;
- scene;
- user intention;
- composition;
- visual scale.

Contextual is therefore a condition of application, not necessarily a fourth property level.

Examples:

- a recurring mosquito associated with summer;
- a shark fin shown only when needed;
- clothing adapted to a historical parody;
- a production constraint requiring a white background;
- a recurring gag used only when it fits naturally.

A contextual rule must state, explicitly or through a well-defined contract, the circumstances in which it applies.

---

# 6. Affordance / Permitted Use

An affordance describes a permitted function, use, or narrative capability of an element.

An affordance is not necessarily an identity invariant.

Examples:

- a jamón may support a boxing gag;
- a chorizo may work as bait;
- an object may serve a particular comic function;
- a recurring prop may be used in a defined narrative role.

The existence of an affordance does not require that the affordance be used.

Likewise, failure to use an affordance is not a canon violation.

Therefore:

    identity
        !=
    permitted use

This distinction prevents functional or narrative capabilities from being incorrectly enforced as visual invariants.

---

# 7. Semantic Identity vs Representation

The Core protects semantic identity rather than pixel-level similarity.

A canonical property may have multiple valid visual representations.

Examples:

- a flame tail may be stylized;
- a character may be viewed from different angles;
- perspective may alter apparent proportions;
- a pose may temporarily change the visible silhouette;
- lighting may alter perceived colour;
- a canonical feature may be partially obscured.

A representation is valid when the underlying canonical meaning remains intact.

## Representation Principle

> The Guard protects semantic properties, not pixels.

A visual difference must not automatically be classified as a canon violation.

The system should ask whether the difference constitutes a meaningful contradiction.

---

# 8. Occlusion and Missing Visibility

The absence of a visible feature does not prove that the feature is absent.

Examples:

- a hand hidden behind the body;
- a hoof outside the frame;
- a scarf knot obscured by pose;
- a tail hidden behind another element;
- a canonical spot hidden by composition.

In these situations the correct state may be:

    UNKNOWN

rather than:

    VIOLATION

The system must not infer absence from lack of visibility.

---

# 9. Evidence States

When evaluating a semantic property, the available evidence should be interpreted using three fundamental states.

## CONFIRMED

The available evidence supports the property.

Example:

Killo is explicitly present and the proposal contains a canonical clavel.

Result:

    CONFIRMED

---

## CONTRADICTED

The available evidence explicitly demonstrates that the property has been violated.

Example:

Killo is clearly shown without black spots when black spots are a canonical invariant.

Result:

    CONTRADICTED

---

## UNKNOWN

The available evidence is insufficient to determine whether the property is satisfied or violated.

Examples:

- a canonical feature is completely occluded;
- the representation is too ambiguous;
- the proposal does not contain enough information;
- the visual evidence cannot reliably establish the property.

Result:

    UNKNOWN

UNKNOWN must not be silently converted into FALSE.

When an UNKNOWN state affects a required canonical decision, the appropriate response may be HUMAN_REVIEW.

---

# 10. Validation States

Semantic evaluation should distinguish at least:

    VALID
    VIOLATION
    UNKNOWN
    HUMAN_REVIEW

These states have different meanings.

## VALID

The available evidence supports compatibility with canon.

## VIOLATION

The available evidence demonstrates a contradiction with canon.

## UNKNOWN

There is insufficient evidence for a reliable determination.

## HUMAN_REVIEW

The system cannot safely resolve the situation automatically, or the situation requires an explicit human decision.

The system must not use HUMAN_REVIEW as a generic replacement for reasoning.

---

# 11. Range-Constrained Variables

A variable property may have explicit boundaries.

Example:

Killo's canonical black spots:

    color: black
    count: variable

The current semantic decision establishes:

    minimum count: 2
    maximum count: 8

Therefore:

- 2 black spots is valid;
- 3 black spots is valid;
- 8 black spots is valid;
- 1 black spot violates the defined range;
- 9 black spots violates the defined range.

The number of spots may vary within the range.

However, numerical validity does not automatically guarantee visual adequacy.

---

# 12. Visual Adequacy

Visual adequacy is separate from canonical validity.

A value can be inside a canonical range while still being unsuitable for a particular representation.

Examples:

- eight spots may technically be allowed but visually overcrowded;
- two spots may technically be allowed but become visually dominant if excessively large;
- spots may technically satisfy colour requirements but become unreadable at production scale.

Therefore:

    canonical validity
        !=
    visual adequacy

Visual adequacy may depend on:

- spot size;
- distribution;
- composition;
- output scale;
- medium;
- stylistic treatment;
- intended visual emphasis.

A stylistic or visual intention may justify a particular choice within the allowed canonical space, but intention alone does not override an invariant.

---

# 13. Intention

Intention explains why an element or decision exists in a proposal.

Intention may be:

- narrative;
- comic;
- contextual;
- stylistic;
- compositional;
- production-related.

Intention must not be confused with canon.

A valid intention does not automatically authorize a canon violation.

Example:

A parody may intentionally exaggerate a character.

That does not automatically authorize changing an invariant.

A deliberate canon exception requires an explicit documented decision.

---

# 14. Parody

Parody is an adaptable transformation of an external or cultural reference into the Illo & Killo universe.

A successful parody should preserve enough structural or semantic identity for the source reference to remain recognizable while becoming part of the Illo & Killo universe.

Parody may adapt:

- titles;
- typography;
- names;
- credits;
- clothing;
- setting;
- props;
- visual language;
- narrative framing;
- comic interpretation.

Parody must not silently rewrite established Illo & Killo canon.

The parody principle is:

    recognizable source structure
        +
    Illo & Killo reinterpretation
        =
    coherent parody

---

# 15. Organic Recurring Gags

Recurring comic details may appear when they contribute naturally to the composition, narrative, or humour.

They should not be forced into every representation.

A recurring gag should preferably satisfy:

- contextual relevance;
- natural visual integration;
- comic or narrative usefulness;
- compatibility with canon;
- proportionality to the rest of the composition.

The system should prefer:

    natural recurrence

over:

    mechanical recurrence

The absence of a recurring gag is not a canon violation.

---

# 16. Explicit Exceptions

A canon exception must be explicit and documented.

The system must not infer an exception merely because:

- a user requested something unusual;
- a parody is being created;
- the result would be funnier;
- a model generated a different interpretation;
- an invariant is inconvenient;
- the evidence is incomplete.

An exception should identify:

- the affected canon element;
- the requested change;
- the reason;
- the scope;
- the authority or decision responsible;
- the resulting canonical status.

Until an exception is documented, the existing canon remains authoritative.

---

# 17. Decision Priority

When semantic rules overlap, the system should use the following priority order:

1. Explicit documented canon decision.
2. Canonical invariants.
3. Explicit contextual or production constraints.
4. Required conditions.
5. Permitted adaptations.
6. Variable properties.
7. Stylistic or compositional preference.

A lower-priority preference must not silently override a higher-priority canonical rule.

---

# 18. No Silent Repair

Validation must not silently repair a proposal.

If a proposal violates canon, the validator should:

- report the violation;
- preserve the original proposal;
- preserve the original knowledge;
- stop or escalate according to the pipeline rules.

The validator must not:

- add missing canonical elements;
- rewrite user intent;
- silently replace forbidden elements;
- alter repository knowledge;
- invent evidence.

Generation and validation remain separate responsibilities.

---

# 19. General Decision Model

For a proposed property:

    proposal
        |
        v
    identify property
        |
        v
    determine semantic class
        |
        v
    determine whether the rule applies
        |
        +---- NO ----------> no violation
        |
        +---- UNKNOWN -----> UNKNOWN / HUMAN_REVIEW
        |
        +---- YES
               |
               v
        evaluate evidence
               |
          +----+----+
          |         |
       supports   contradicts
          |         |
          v         v
        VALID    VIOLATION

The system must never turn insufficient evidence into a fabricated negative fact.

---

# 20. Examples

## Killo — clavel

    invariant:
        clavel

If Killo is present and the clavel is clearly absent:

    VIOLATION

If the relevant ear is completely hidden:

    UNKNOWN

If the clavel is present with an adaptable colour:

    VALID

If the clavel is replaced with another flower:

    VIOLATION

---

## Killo — black spots

    invariant:
        black_spots

    count:
        variable

    allowed range:
        2..8

    colour:
        black

The number may vary within the range.

The exact size and distribution may vary subject to visual adequacy.

A different colour contradicts the canonical property.

---

## Illo — flame tail

    invariant:
        short_flame_tail

A stylized flame tail may be valid.

A tail partially hidden by pose is not evidence of absence.

A clearly long non-flame tail contradicts the canonical property.

---

## Recurring mosquito

The mosquito may recur.

Its recurrence does not make it mandatory.

Its inclusion should have an appropriate intention and remain compatible with the applicable contextual rules.

---

## Jamón as comic prop

The jamón may support a boxing gag.

The ability to support that gag is an affordance.

The gag does not have to occur whenever the jamón appears.

---

# 21. Semantic Model Summary

The model can be summarized as:

    INVARIANT
        what must remain canonically stable

    ADAPTABLE
        what may intentionally transform while preserving identity

    VARIABLE
        what may vary without changing canon

    RECURRENT
        what may return without being mandatory

    REQUIRED
        what must be present when a condition activates the obligation

    CONTEXTUAL
        what depends on circumstances

    AFFORDANCE
        what an element is permitted or able to do

    INTENTION
        why a choice or element is present

    EVIDENCE
        what can actually be established

    UNKNOWN
        insufficient evidence, not falsehood

The Core should protect canon without suppressing legitimate creative variation.

The goal is not maximum rigidity.

The goal is:

    stable identity
        +
    controlled adaptation
        +
    contextual intelligence
        +
    explicit evidence
        +
    human escalation when necessary
