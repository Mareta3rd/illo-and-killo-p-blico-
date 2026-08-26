# AI HANDOFF — Illo & Killo Semantic Model

## Purpose
Build a deterministic semantic/evidence architecture for the Illo & Killo project. External AI providers are evidence sources only; the Core owns canonical claims, evidence contracts, snapshots, evaluation, regression detection, audit, routing, and final decisions.

## Working principles
- Do not invent facts, files, paths, test results, APIs, or project state.
- Never put API keys/secrets in chat, source code, commits, issues, or tests.
- Fix every failing test before advancing.
- After meaningful integration blocks, run the complete unittest suite.
- Prefer small, reversible architectural steps and preserve the Core boundary.
- Do not lower the canon quality bar merely to obtain more examples.

## Current branch and checkpoint
Active branch: `feature/semantic-model`.
Latest full-suite result actually confirmed in the current session: **387 tests, OK**.
The Gemini end-to-end milestone is complete.

## Architecture validated
The project now has tested boundaries for:

provider
→ ExternalEvidenceRecord
→ ProviderEvidenceObservation
→ EvidenceSnapshot
→ Core pipeline/evaluator
→ decision

Earlier gateway/registry/orchestrator, regression, semantic-audit, and execution-audit layers remain part of the validated architecture.

## Gemini — first real provider
Gemini is the first real external evidence provider and has been exercised end-to-end from the Codespace.

Validated components include:
- `core/gemini_evidence_adapter.py`
- `core/gemini_real_transport.py`
- `core/provider_evidence_observation.py`
- `scripts/run_gag001_gemini_experiment.py`
- Gemini adapter/transport/integration/conformance tests
- provider observation/snapshot/pipeline tests

Real environment validation:
- `google-genai` is installed and imports successfully.
- `GEMINI_API_KEY` is supplied as a GitHub Codespaces secret; it is not stored in the repository or chat.
- `genai.Client()` initializes successfully.
- `gemini-3.6-flash` produced a real `GEMINI_REAL_OK` response during connectivity validation.

## Gemini end-to-end milestone
A real run was completed with:
- image: `gags/images/001_jamon.png`
- provider: `gemini`
- model: `gemini-3.6-flash`
- run id: `real-gag001-mosquito-20260826-01`
- invariant: `fauna/mosquito_tigre/readable_as_mosquito`

Observed result:
- `CONFIRMED`
- `supporting_sources=["image"]`
- contract evaluation: `pass`
- final Core decision: `accept`

The provider returned evidence only. `accept` was produced by the Core after the evidence crossed the snapshot boundary and the candidate contained its required explicit Core checks.

A separate real Gag 001 composition run validated that `gag/001/composition/illo_primary` can be preserved as a canonical claim without inventing a three-segment contract evaluation.

An earlier real run where Gemini returned `CONFIRMED` without supporting sources was rejected by the parser. The interaction contract was then strengthened so the provider explicitly supplies `image` when the image is the evidence source.

## Canon decision
Only one image/gag is currently accepted as canonical visual material: **Gag 001 · Jamón**.

The second existing gag image is not canonical because it has unresolved character, execution, and composition problems. Do not promote it merely to enlarge the corpus.

Keep `CANON` separate from any future `TEST CORPUS` of positive, negative, ambiguous, or synthetic images.

## Claim taxonomy boundary
Canonical Gag 001 claims such as `gag/001/composition/illo_primary` are not the same thing as registered three-segment evidence-contract invariants such as `catalog/entry/invariant`.

Do not rewrite, alias, or relax claims simply to fit the registered invariant taxonomy. Canonical gag claims may cross the snapshot boundary while remaining without contractual evaluation until a deliberate human decision establishes that relationship.

## Custom Copilot agent
Repository custom agent:
`.github/agents/semantic-boundary-engineer.agent.md`

Repository-wide Copilot guardrails:
`.github/copilot-instructions.md`

The custom agent is the local execution/development counterpart to the architectural reasoning in the main project conversation. It can inspect files, edit code, run tests, and iterate in the Codespace, but it must stop rather than invent semantics when an architectural decision is ambiguous.

## Next phase — OpenAI as second provider
The next provider must implement the same provider boundary used by Gemini.

Target architecture:

OpenAI transport
→ OpenAI provider adapter
→ ExternalEvidenceRecord
→ ProviderEvidenceObservation
→ EvidenceSnapshot
→ existing Core pipeline/evaluator

Do not create a parallel OpenAI-specific Core path.

Initial OpenAI phase should be staged:
1. Verify the current OpenAI SDK/API surface and model availability in the live environment before coding against assumptions.
2. Build a provider-specific transport/parser contract with injected/fake transport.
3. Add conformance tests proving the adapter emits only `ExternalEvidenceRecord` and never Core decisions.
4. Reuse the existing observation/snapshot/pipeline composition; do not duplicate it.
5. Validate real connectivity with an environment secret, never source code or chat.
6. Run one real perceptual invariant experiment.
7. Run one real end-to-end Core decision experiment.
8. Run the full suite after every meaningful integration block.

OpenAI model identifiers, SDK methods, endpoints, authentication, and response schemas must be verified against the live environment when implementation starts. Do not assume a model name or endpoint from memory.

## Next session starting point
Read this file first. Then inspect the current branch and confirm the full suite before changing anything.

The architectural target is not merely “call OpenAI”; it is to prove that a second independent provider can enter through the same evidence contract without changing Core semantics. Gemini remains the reference implementation for that conformance work.

## Conversation continuity
If the original ChatGPT conversation becomes unavailable or visually resets, open a new chat and tell the assistant:
“Work on repository `Mareta3rd/illo-and-killo-p-blico-`, branch `feature/semantic-model`. Read `docs/AI_HANDOFF.md` first. Treat it as the durable project state and continue from its current checkpoint. Do not assume anything not supported by the repository or this document.”

This handoff file is intentionally the durable source of project continuity so progress does not depend on one chat thread.
