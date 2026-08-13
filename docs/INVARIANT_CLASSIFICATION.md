# Invariant Classification

## Purpose

This document records the primary family and validation mechanism assigned to every invariant currently present in the canonical character, object, fauna, and heritage catalogs.

The classification is deliberately explicit. No invariant may acquire a family or validation mechanism through inference at runtime.

## Families

| Family | Mechanism | Evidence | Typical question |
| --- | --- | --- | --- |
| `quantitative` | `deterministic_range` | No | Is the value within the canonical range? |
| `categorical` | `deterministic_value` | No | Does the observed value match the canonical value/category? |
| `structural` | `deterministic_structure` | No | Is the required structure present and coherent? |
| `relational` | `deterministic_relation` | No | Does the required relation between parts/elements hold? |
| `perceptual_semantic` | `evidence_perceptual` | Yes | Does the representation read as the intended thing? |
| `stylistic_interpretive` | `evidence_style` | Yes | Does the representation preserve the intended stylistic interpretation? |
| `contextual_conditional` | `evidence_context` | Yes | Is the conditional rule active and satisfied? |

## Classification decisions

### Characters

Illo and Killo's current invariants are structural because they describe required body or accessory construction. Killo's spot count is a separate quantitative constraint already expressed in `characters.yaml` and enforced by Canon Guard; the invariant `black_spots` itself remains structural.

### Fauna

`very_small` for the tiger mosquito is treated as categorical at this stage because the catalog supplies a qualitative size class rather than a numeric measurement. `readable_as_*` invariants are perceptual. `summer_context` and `fin_only_when_needed` are contextual conditional rules.

### Objects

`readable_as_*`, `simple_*_reading`, and `chairlift_reading` are perceptual because their success depends on recognizability. `simplified_iconic_form` and `fantasy_reference_reading` are stylistic because they describe a deliberate visual interpretation rather than a directly measurable property. `small_loco_detail` is classified as stylistic pending a more specific formal definition.

### Heritage

`recognizable_silhouette` and `recognizable_mass` are classified as perceptual rather than relational because their correctness depends primarily on recognition of the depicted subject. This resolves an earlier ambiguity in the taxonomy. `simplified_nasrid_reading` and similar explicit reinterpretation statements are stylistic. The remaining reading invariants are perceptual unless their catalog definition later establishes a stronger deterministic contract.

## Boundary rules

A deterministic family must never use Evidence merely as a shortcut for an objectively testable property.

An evidence-bound family must never silently degrade to acceptance when Evidence is absent or `UNKNOWN`.

If a future invariant cannot be classified unambiguously from the taxonomy, the system must stop for human review rather than invent a family or mechanism.

## Status

The current classification is explicit and implementation-ready, but remains a versioned semantic contract. Changes to a family assignment are canon/architecture changes and should be accompanied by tests and a clear rationale.
