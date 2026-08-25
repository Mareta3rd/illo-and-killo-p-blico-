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
`339 tests in 7.235s — OK`

The latest committed semantic-model checkpoint is the real-Gemini experiment contract commit on `feature/semantic-model`.

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
- `google-genai` installed successfully (`2.19.0` was installed at the time of verification).
- `from google import genai` works.
- `GEMINI_API_KEY` is supplied through a GitHub Codespaces secret named `GEMINI_API_KEY`.
- The key is not stored in the repository or chat.
- `genai.Client(api_key=key)` initializes successfully.
- A real request returned `GEMINI_REAL_OK`.

Important: do not disclose or log the key. Do not replace the Codespaces secret with the literal key in any committed file.

## Gemini model note
A first connectivity test using `gemini-2.5-flash` returned 404 because that model is no longer available to new users. The same real connectivity test succeeded with `gemini-3.6-flash`, returning `GEMINI_REAL_OK`.

Model identifiers should therefore be treated as configuration and verified against the currently available Gemini API rather than assumed from memory.

## Canon decision
Only one image/gag is currently accepted as canonical for this phase: **Gag 001 · Jamón**.

The repository has `gags/001_jamon.md`, whose official hierarchy is Illo → jamón → reacción de Killo.

The second existing gag image is not currently acceptable as canon because it has known character, execution, and composition defects. Do not force it into canon merely to obtain a second example.

A distinction is intentional:
- CANON = approved project material.
- TEST CORPUS = additional positive/negative/ambiguous images used to test evidence behavior; these do not need to be canon.

## Current local image situation
The Codespace screenshot showed an uploaded local file under `gags/images` named:
`001_jamon.png.png`
with untracked (`U`) status.

The earlier attempt to locate repository-tracked image files with `find` returned no results because images were not yet tracked in the repository.

The attached image used for the experiment is the Gag 001 artwork (Illo hitting the ham, Killo reacting, with a mosquito as a secondary decorative element).

Do not assume the double extension is intended. Before running the real image experiment, rename the local file to a clean canonical filename such as:
`gags/images/001_jamon.png`
Then verify with:
`ls -lh gags/images/001_jamon.png`

Do not commit the image until we deliberately decide that this image is the canonical asset and confirm repository asset policy.

## First real perceptual experiment
Initial experiment idea was `fauna/mosquito_tigre/readable_as_mosquito`, but this should be reconsidered before execution because the mosquito is a secondary element of Gag 001 and the image is primarily a composition test.

A cleaner first experiment may use claims derived directly from Gag 001’s canonical specification, for example:
- Illo is present and is the primary character/subject.
- The ham is present and is the central action object.
- Killo is present and reacts to the action.

A mosquito-related claim can be tested later as a deliberately secondary/ambiguous case.

Do not change Core semantics to accommodate a surprising Gemini answer. First record and analyze the real provider output.

## Immediate next step
1. Fix the local filename `001_jamon.png.png` → `001_jamon.png`.
2. Decide the first Gag 001 invariant/claim to test against the real image.
3. Run the real Gemini experiment from the Codespace using the existing script:
   `python scripts/run_gemini_real_experiment.py <image> <claim_key>`
4. Capture the full provider output and resulting `ExternalEvidenceRecord`.
5. Analyze whether Gemini’s result is usable, ambiguous, contradictory, or incomplete.
6. Only then decide whether code, contracts, prompt wording, or provider-specific parsing needs adjustment.

## Conversation continuity
If the original ChatGPT conversation becomes unavailable or visually resets, open a new chat and tell the assistant:
"Work on repository `Mareta3rd/illo-and-killo-p-blico-`, branch `feature/semantic-model`. Read `docs/AI_HANDOFF.md` first. Treat it as the durable project state and continue from its Immediate next step. Do not assume anything not supported by the repository or this document."

This handoff file is intentionally the durable source of project continuity so progress does not depend on one chat thread.
