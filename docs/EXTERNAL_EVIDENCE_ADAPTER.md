# External Evidence Adapter — Phase 2

The Phase 2 boundary between external systems and Core is deliberately narrow.

```text
external provider / human review / vision system
                 ↓
      ExternalEvidenceRecord
                 ↓
      normalize_external_evidence
                 ↓
            EvidenceClaim
                 ↓
          EvidenceSnapshot
                 ↓
              Core
```

## Contract

An external source may provide only an explicit canonical claim key, a statement, an evidence state, and optional source references.

The adapter does **not** infer truth from text, score confidence, classify an image, or apply canon rules. Those responsibilities remain inside Core's existing taxonomy, contracts, Evidence Boundary, snapshot, and evaluation pipeline.

`CONFIRMED`, `CONTRADICTED`, and `UNKNOWN` are preserved exactly. A missing source list is not converted into a positive or negative decision.

Canonical keys use:

```text
catalog/entry/invariant
```

Duplicate keys, malformed keys, empty statements, invalid states, and malformed source references are rejected before entering the Core boundary.

## Provider independence

Core depends on the `ExternalEvidenceProvider` protocol rather than a concrete vendor. A future adapter for a vision model, human-review UI, local service, or remote API can implement `collect()` and then feed normalized records into the same Core boundary.

The provider is therefore replaceable without changing the semantic model.

## Phase 2 scope

This first step intentionally stops before connecting a real vendor. It establishes the stable ingress contract and proves that external observations can enter the existing EvidenceSnapshot without creating a parallel semantic path.
