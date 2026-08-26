# OpenAI Provider Phase — Implementation Brief

## Objective
Add OpenAI as the second real external evidence provider without creating a second Core path.

The target is conformance, not feature duplication:

OpenAI transport
→ provider adapter
→ ExternalEvidenceRecord
→ ProviderEvidenceObservation
→ EvidenceSnapshot
→ existing Core pipeline/evaluator
→ Core decision

## Non-negotiable boundaries
- OpenAI is an external evidence source, never a Core authority.
- The adapter may translate provider-specific transport/response shapes into `ExternalEvidenceRecord` only.
- `CONFIRMED`, `UNKNOWN`, and `CONTRADICTED` remain observations until the Core evaluates them.
- `provider`, `run_id`, model, prompt variant, and transport metadata stay outside `snapshot.claims`.
- Do not relax the existing three-segment evidence-contract taxonomy.
- Do not rewrite Gag 001 four-segment canonical claims into three-segment invariants.
- Do not add OpenAI-specific branches to `pipeline.py` or `evidence_evaluator.py`.
- Credentials must come from environment/Codespaces secrets and must never be committed or printed.

## Current reference implementation
Gemini is the reference provider. Its successful real path demonstrated:

real provider
→ `ExternalEvidenceRecord`
→ `ProviderEvidenceObservation`
→ `EvidenceSnapshot`
→ contractual evaluation where applicable
→ Core decision

Reuse the existing provider-neutral composition rather than cloning Gemini architecture.

## Phase A — contract and fake transport
Before using network access:
1. Inspect the current project provider protocol and registry/gateway contracts.
2. Verify the current OpenAI SDK/API surface and available model identifiers in the live environment from authoritative documentation or the installed SDK.
3. Introduce only the provider-specific transport/parser boundary.
4. Use an injected/fake transport in tests.
5. Define the structured provider response contract needed by the adapter.

Minimum response semantics:
- requested claim key;
- provider verdict mapping to `CONFIRMED` / `CONTRADICTED` / `UNKNOWN`;
- non-empty statement;
- support sources for confirmed evidence;
- contradiction sources for contradicted evidence;
- empty support/contradiction sources for unknown evidence.

Malformed responses must fail explicitly. Do not infer missing evidence.

## Phase B — adapter conformance
Add tests proving:
- requested keys are passed through without mutation;
- adapter output is `ExternalEvidenceRecord` only;
- no Core decision vocabulary is accepted as provider output;
- duplicate/unrequested/missing claims are rejected;
- invalid source combinations are rejected;
- provider failures become explicit boundary errors;
- adapter does not evaluate canon or candidate quality.

## Phase C — provider-neutral integration
Use the existing composition:

`collect_provider_observation(...)`
→ `snapshot_from_provider_observation(...)`
→ `run_provider_evidence_pipeline(...)`

Do not add an OpenAI-specific observation or snapshot layer.

Test both claim classes:
- contractual three-segment invariant, e.g. `fauna/mosquito_tigre/readable_as_mosquito`;
- Gag 001 canonical four-segment claim, e.g. `gag/001/composition/illo_primary`.

The latter must remain a claim without an invented contractual evaluation.

## Phase D — real OpenAI connectivity
Only after focused and full suites are green:
1. configure the OpenAI credential through Codespaces secret/environment;
2. verify client initialization;
3. run one minimal text connectivity check first;
4. then run one structured/image evidence request against the real adapter;
5. preserve the exact provider observation.

Do not retry automatically to obtain a preferred verdict.

## Phase E — real Core end-to-end
Run one real contractual invariant through:

OpenAI real
→ adapter
→ observation
→ snapshot
→ contractual evaluation
→ Core decision

Expected architecture is identical to Gemini. The provider must not return `accept`, `continue`, or `human_review` as its decision vocabulary.

## Exit criteria
OpenAI phase is considered operational when:
- provider conformance tests are green;
- provider-neutral integration tests are green;
- real connectivity is verified;
- a real perceptual invariant produces a valid evidence record;
- a real evidence record crosses the snapshot boundary;
- at least one real end-to-end Core decision is produced by the Core;
- complete unittest suite remains green;
- no OpenAI-specific Core branch exists.

## First implementation instruction
Start by inspecting the repository's existing provider protocol/registry and the current installed OpenAI tooling. Do not create an adapter until the live SDK/API surface has been verified. Prefer the smallest provider-specific change that satisfies the existing conformance contract.
