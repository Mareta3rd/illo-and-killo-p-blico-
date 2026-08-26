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

## Current branch
`feature/semantic-model`

## Current checkpoint
Global test suite last confirmed green:
`367 tests — OK`

## Architecture already built and tested
The project now contains and tests the following boundary chain:

provider
→ ExternalEvidenceRecord
→ adapter
→ gateway
→ EvidenceSnapshot
→ evaluator
→ regression detector
→ orchestrator
→ semantic/execution audit

Provider-specific work completed for Gemini:
- `core/gemini_evidence_adapter.py`
- `core/gemini_real_transport.py`
- `scripts/run_gemini_real_experiment.py`
- Gemini adapter/transport/integration tests
- Real experiment contract tests

The adapter is deliberately outside Core decision logic. Gemini output must normalize into canonical `ExternalEvidenceRecord`; the Core does not accept provider-specific decisions.

## Gemini real access status
Gemini access from the Codespace is genuinely working.

Verified in the Codespace:
- `google-genai` installed successfully (`2.19.0` at the time of verification).
- `from google import genai` works.
- `GEMINI_API_KEY` is supplied through a GitHub Codespaces secret named `GEMINI_API_KEY`.
- The key is not stored in the repository or chat.
- `genai.Client()` initializes successfully.
- A real request returned `GEMINI_REAL_OK`.
- `gemini-3.6-flash` is the currently validated working model in this environment.

Important: do not disclose or log the key. Do not replace the Codespaces secret with the literal key in any committed file.

## Canon decision
Only one image/gag is currently accepted as canonical for this phase: **Gag 001 · Jamón**.

The repository has `gags/001_jamon.md`, whose official hierarchy is Illo → jamón → reacción de Killo.

The second existing gag image is not currently acceptable as canon because it has known character, execution, and composition defects. Do not force it into canon merely to obtain a second example.

A distinction is intentional:
- CANON = approved project material.
- TEST CORPUS = additional positive/negative/ambiguous images used to test evidence behavior; these do not need to be canon.

## Provider-observation architecture
Real provider variability is preserved before Core aggregation via:
- `core/provider_evidence_observation.py`
- `ProviderEvidenceObservation(provider, run_id, records)`

A provider observation can cross the snapshot boundary without turning provider metadata into Core claims. Canonical Gag 001 claims such as `gag/001/composition/illo_primary` must not be rewritten merely to fit the three-segment catalog/entry/invariant contract used by the registered evidence taxonomy.

## Custom Copilot agent
A repository-level custom agent has been added at:
`.github/agents/semantic-boundary-engineer.md`

Purpose: execute and verify semantic-boundary engineering work in the Codespace, with strict rules around canon, provider isolation, evidence states, snapshots, contracts, credentials, focused tests, and full-suite regression checks.

Repository-wide Copilot guardrails are also in:
`.github/copilot-instructions.md`

The custom agent is intended as the local execution/development counterpart to the architectural reasoning done in the main project conversation. It can inspect files, edit code, run tests, and iterate in the Codespace; it must stop rather than invent semantics when an architectural decision is ambiguous.

## Conversation continuity
If the original ChatGPT conversation becomes unavailable or visually resets, open a new chat and tell the assistant:
"Work on repository `Mareta3rd/illo-and-killo-p-blico-`, branch `feature/semantic-model`. Read `docs/AI_HANDOFF.md` first. Treat it as the durable project state and continue from its current checkpoint. Do not assume anything not supported by the repository or this document."

This handoff file is intentionally the durable source of project continuity so progress does not depend on one chat thread.
