# Evidence States v1

## Purpose

Evidence states describe what can currently be established about a specific claim from repository evidence.

They do not modify canon, create facts, or infer missing information.

## States

### CONFIRMED

Explicit supporting evidence establishes the claim.

A claim may be confirmed only from evidence that actually supports that claim. Repository presence by itself is not enough to infer every possible use or meaning of an asset.

### CONTRADICTED

Explicit evidence establishes the opposite of the claim.

Contradicted is not the same as "not found". A missing search result cannot produce CONTRADICTED.

### UNKNOWN

The available evidence is insufficient to establish either the claim or its negation.

UNKNOWN is the correct result when evidence is absent, incomplete, ambiguous, or not specific enough to answer the claim.

## Conflict handling

If explicit supporting and contradicting evidence coexist, the system must not silently choose one source. The tri-state resolver raises an evidence conflict so that a higher-level process can route the case to explicit review.

This preserves the distinction between:

- UNKNOWN — insufficient evidence;
- CONTRADICTED — explicit evidence against the claim;
- conflict — explicit evidence on both sides.

Conflict is therefore not collapsed into UNKNOWN or CONTRADICTED.

## Relationship to historical status

Historical evidence may still use the separate statuses defined by `EVIDENCE_SPEC.md`:

- `mentioned`
- `used`
- `uncertain`

Those describe the nature of an historical observation. `CONFIRMED`, `CONTRADICTED`, and `UNKNOWN` describe the state of a particular claim after evidence is assessed.

They must not be treated as interchangeable vocabularies.

## Non-inference rule

The following implication is forbidden:

    no evidence found
        ->
    CONTRADICTED

The correct implication is:

    no sufficient evidence
        ->
    UNKNOWN

This rule is essential because the repository is incomplete evidence about the universe, not a complete record of every possible work.
