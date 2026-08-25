# Session Handoff — semantic-model

## Repository state
- Repository: `Mareta3rd/illo-and-killo-p-blico-`
- Active branch: `feature/semantic-model`
- Latest confirmed full suite: **339 tests, OK**.
- The semantic-model work must continue from the current branch; do not assume `main` contains the latest work.

## Architecture already completed
The project has validated boundaries for:
- evidence evaluation and perceptual evidence
- candidate end-to-end orchestration
- semantic regression detection
- orchestrator semantic audit
- execution audit / immutable evidence fingerprints
- external evidence adapter + frozen snapshots
- simulated provider end-to-end path
- external evidence gateway
- provider registry
- real provider adapter/conformance contracts
- contract compatibility audit

## Gemini integration status
Gemini is now the first real external provider.

Implemented:
- `core/gemini_evidence_adapter.py`
- `core/gemini_real_transport.py`
- `scripts/run_gemini_real_experiment.py`
- Gemini unit/integration/conformance tests
- real experiment contract tests

Important compatibility detail:
- `GeminiEvidenceAdapter.from_interactions_client(...)` exists and uses the concrete Interactions transport.
- `build_gemini_transport(...)` remains available because older adapter tests import it.

## Real Gemini environment
In the Codespace:
- `google-genai` is installed (`2.19.0` in the current environment).
- `from google import genai` works.
- `GEMINI_API_KEY` is configured as a GitHub Codespaces secret and reaches the environment.
- `genai.Client()` initializes successfully.
- A real connectivity call succeeded with model `gemini-3.6-flash` and returned `GEMINI_REAL_OK`.
- Do **not** put the API key in chat, source, commits, or documentation.

The earlier `gemini-2.5-flash` call returned 404 because that model was no longer available to new users; `gemini-3.6-flash` is the currently validated working model in this environment.

## Canon decision
Only **Gag 001 · Jamón** is currently accepted as canonical visual material.
- `gags/001_jamon.md` is the canonical specification.
- Gag 002 is **not canonical** and should not be used as canonical evidence because it has unresolved character, execution, and composition problems.
- Do not force creation of a second canonical gag just to enlarge the test set.
- Distinguish `canon` from a future synthetic/negative/ambiguous test corpus.

The canonical Gag 001 specification defines the visual hierarchy as **Illo → jamón → reaction of Killo**.

## Current local Codespace image situation
The user uploaded the Gag 001 image to the chat and manually placed it in the Codespace under `gags/images/`.
The VS Code screenshot shows the local untracked filename as:
- `gags/images/001_jamon.png.png`

This appears to be a double-extension naming mistake. The intended path is:
- `gags/images/001_jamon.png`

The user has not yet committed the image. The `find` command returned no image files before the manual upload because the file is currently untracked/local.

## Immediate next step
1. Rename the local image safely:
   `mv gags/images/001_jamon.png.png gags/images/001_jamon.png`
2. Verify:
   `ls -lh gags/images/001_jamon.png`
3. Run the real Gemini experiment using the canonical Gag 001 image.
4. Use a conservative first perceptual claim; do **not** contaminate the prompt with the expected answer.
5. Treat the resulting Gemini output as external evidence, not as a Core decision.
6. Analyze the first real `ExternalEvidenceRecord` before changing Core behavior.

## First experiment context
Earlier the planned claim was:
`fauna/mosquito_tigre/readable_as_mosquito`

However, before executing it, reconsider whether this is the best first invariant because the mosquito is only a secondary visual element in Gag 001. The canonical Gag 001 hierarchy may make these first claims more appropriate:
- `gag/001/composition/illo_is_primary_subject`
- `gag/001/composition/ham_is_secondary_subject`
- `gag/001/characters/illo_present`
- `gag/001/characters/killo_present`

Do not silently change the canonical model; decide the first claim deliberately.

## Working principles
- Do not invent test results, file paths, API behavior, or repository state.
- When a test fails, fix it before advancing.
- After a new block, run its focused tests and then the complete suite.
- Prefer architectural cleanliness and explicit contracts over rushing toward more features.
- Keep real provider credentials outside the repository.
- The next conversation can resume from this file plus the repository state; this file is the durable project handoff.