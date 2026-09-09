# AI HANDOFF — Arsa & Pisha Semantic Model

## Purpose
Build a deterministic semantic/evidence architecture for the **Arsa & Pisha** project. External AI providers are evidence sources or candidate generators only, according to their explicit provider contract; **Core owns canonical claims, evidence contracts, snapshots, evaluation, regression detection, audit, routing, and final decisions**.

## Working principles
- Do not invent facts, files, paths, test results, APIs, or project state.
- Never put API keys/secrets in chat, source code, commits, issues, or tests.
- Fix every failing test before advancing.
- After meaningful integration blocks, run the complete test suite.
- Prefer small, reversible architectural steps and preserve the Core boundary.
- Do not lower the canon quality bar merely to obtain more examples.
- Treat historical Illo & Killo material as reference/inspiration only unless a documented decision explicitly promotes an element into current canon.
- Provider output must never silently become canon or a Core decision.
- Record major technical and artistic decisions here so future sessions do not depend on conversation memory.

## Current branch and checkpoint
Active branch: `feature/semantic-model`.
Current repository checkpoint: `293317daa0d42d47f2d573d0309b34c48c86becb` (`add work-block closure guardrail script`).

The most recent local verification reported before the final test-alignment commit was **541 passed, 49 subtests passed, 1 failed**. The remaining failure was the historical-gag filename assertion; it was aligned with the actual archived path `002_pesca_legacy.md`. The test suite must now be rerun after the Codespace pulls the current branch. Do not record the suite as green until that run actually completes successfully.

The repository currently has **Arsa & Pisha as the active creative canon**. Illo & Killo are historical development material, not current character canon. Earlier Xoxo terminology is historical/intermediate and must not be treated as the active name.

## Current canonical characters
The structured character catalog defines:
- `arsa` / **Arsa**: co-lead; white pelage; yellow-blonde flame-like crest; green scarf; black three-finger hands; black hooves; short flame tail; stylized equine hint; high-energy, impulsive, mischievous, expressive and tender behavioral grammar.
- `pisha` / **Pisha**: co-lead; red pelage; black spots; clavel; short rounded horns; black three-finger hands; black hooves; compact bovine hint; apparently calm, observant, innocent, proud, mischievous, absent-minded and tender behavioral grammar.

Important mature design decisions to preserve:
- Arms/hands and legs/hooves are distinct anatomical systems and must not collapse into the same visual treatment.
- Black three-finger hands and black hooves are deliberate recognition devices, not interchangeable anatomy.
- Animal identity remains suggestive rather than literal; Arsa is not a horse and Pisha is not a bull.
- The visual language is contemporary, high-quality and forward-looking, with a **small, controlled vintage/print-comic soul** where useful. Vintage is a seasoning, not a period imitation: never deliberately old-fashioned or viejuno.
- Anatomical comic markers are contextual and optional; their absence is not a canon failure.

Their relationship is explicitly modeled as inseparable companions with mutual trust, teasing, protection and shared mischief, with situational role switching and tenderness underneath the mischief. Neither is a permanent protagonist or helper.

## Current visual / humor canon
- One primary gag per illustration.
- Immediate first-read visual comprehension.
- Optional second-read surprise, irony, picardía or contextual detail.
- Absurd escalation from recognizable everyday logic.
- Physical, facial and gestural comedy that can work without dialogue.
- Conflict is playful rather than cruel.
- Tenderness remains protected even in acidic, obscene or black humor when context warrants it.
- Remove details that do not improve gag, reading, personality or composition.

Andalusia is layered as: structural/behavioral first, environmental second, ornamental third. Environmental and ornamental references support the gag rather than turning the universe into a tourist postcard.

## Current Gag 001
The current canonical object is the **semantic gag concept**, not the old raster image.

Current claim keys:
- `gag/001/composition/arsa_primary`
- `gag/001/composition/ham_primary`
- `gag/001/characters/pisha_reaction`

`gags/001_jamon.md` documents the current Arsa/Pisha semantic version. The former `gags/images/001_jamon.png` was removed from the active tree because it belongs to the previous visual base. A new current raster can be canonized later through deliberate review.

Gag 002 · Pesca is not current canon and its specification has been moved to historical material.

## Historical creative corpus
Previously developed material supplied during earlier creative work is intentionally preserved as **historical development corpus**, not canon.

Recovered image groups:

### Arsa & Pisha Origins
Eight historical images. This is the first development stage: it is historically related to the project but is **not an early canonical version of current Arsa & Pisha**. In that stage the characters were a horse and a bull and several later decisions were discarded. Use these images only to study visual/gag mechanisms and evolution.

### Illo & Killo
Two historical images covering an espeto/fishing scene and a jamón/mosquito gag. This is the immediately previous development stage before current Arsa & Pisha. It may supply useful mechanisms and lessons, but it is not current canon.

The historical corpus is documented under `history/creative-corpus/` and is intended for extraction of successful mechanisms, lessons and reusable ideas only after revalidation against current canon. The image filenames currently preserve their numeric generation IDs; semantic filenames may be introduced after image-by-image classification, while retaining the generation ID in the filename for traceability.

Historical naming/classification rule: classify by **content + gag/mechanism**, not by guessed chronology. Examples of useful semantic categories include fishing/pesca, jamón, fiesta, Vespino/fuga/action, parody-cover, guitar/dance/confrontation, and other distinct gag mechanisms discovered during review. Do not assign a title solely from a filename or memory when the image itself has not been checked.

## Repository cleanup completed in the current block
Current-facing roots have been evolved to Arsa & Pisha, including:
- `model-sheets/arsa.md`
- `model-sheets/pisha.md`
- `prompts/maestro.md`
- `prompts/gag.md`
- `prompts/model-sheet.md`
- `docs/CANON_100.md`
- `docs/SEMANTIC_MODEL.md`
- `docs/INDEX.md`
- `.github/agents/semantic-boundary-engineer.agent.md`

Obsolete `model-sheets/illo.md`, `model-sheets/killo.md` and current `gags/002_pesca.md` were removed from active roots. `docs/SESSION_HANDOFF.md` is now explicitly historical/superseded and points to this file as the durable source of continuity.

The GitHub repository slug itself still contains the historical name because renaming the remote repository is a separate GitHub administration action; do not rename or recreate the repository implicitly during development.

## Validated architecture
The project has tested boundaries for:

`provider → ExternalEvidenceRecord → ProviderEvidenceObservation → EvidenceSnapshot → contractual evaluation when applicable → Core pipeline/evaluator → Core decision`

Earlier gateway/registry/orchestrator, regression, semantic-audit and execution-audit layers remain part of the validated architecture.

## Gemini
Gemini is a validated external evidence provider. Its provider-specific transport and adapter enter through the common observation/snapshot path.

Previously validated live configuration included real runs against the earlier Gag 001 image, with evidence entering Core and a final Core decision of `accept`. Those experiments remain historical evidence of the provider integration; the old image is no longer the current canonical raster.

Gemini stability/composition tests and experiment scripts use the current Arsa-based claim keys.

## OpenAI
OpenAI Phase A exists as a provider-specific transport/adapter implementation, but its earlier real connectivity attempt returned `429 insufficient_quota`. Do not treat OpenAI as the next mandatory phase merely because older handoff text says so.

Any future live OpenAI work must verify the current SDK/API surface and model availability before implementation assumptions are made.

## Groq/Qwen
Groq/Qwen is already validated through the provider-neutral evidence path with a real multimodal Qwen 3.8 27B experiment using the earlier Gag 001 image.

The candidate-generation path exists through:
- `core/groq_qwen_candidate_executor.py`
- `core/groq_qwen_candidate_transport.py`
- `scripts/run_groq_qwen_candidate.py`

The default candidate model is `qwen/qwen3.8-27b`, and the transport requires structured outputs for the strict candidate schema. No automatic fallback is allowed.

The candidate transport is intentionally provider-specific and returns a `Candidate`; it must not return Core decisions or evidence-contract decisions. Forbidden fields include `accept`, `decision`, `evidence`, and `claim_key`.

## Current semantic-context gap
The current `CompiledPrompt` is structurally correct but semantically sparse. Its `context_summary` currently contains mainly:
- the idea,
- confidence,
- known character keys,
- repository section names.

That is not enough for a creative candidate generator to reliably express the current universe. The next architectural task is therefore to build a **small, deterministic semantic context** from existing canonical repository data rather than dumping the entire repository or duplicating canon into ad hoc prompt text.

The target context should make available, as relevant to the route/task:
- current character identities and protected visual/behavioral invariants;
- the distinction between arms/hands and legs/hooves;
- Arsa/Pisha relationship grammar and dynamic role switching;
- current humor grammar, especially one-gag-per-image, immediate visual readability, absurd escalation, non-malicious conflict and protected tenderness;
- Andalusian structural/behavioral layer as primary, with environmental/or ornamental references only when useful;
- mature visual-language guidance: contemporary/vanguard finish with a restrained vintage soul, never a retro costume;
- relevant documented decisions and current Gag 001 claim information when the task concerns that gag;
- explicit separation between current canon and historical Illo/Killo/Xoxo material.

The compiler remains a transformation layer. It must not invent missing semantics, mutate canon, or let the provider decide which material is canonical.

## Work-block closure protocol
Every meaningful block should end in the same deterministic sequence:

1. **Solve** the declared problem completely enough to have a coherent architectural state.
2. **Verify** with focused tests and then the complete suite for integration work.
3. **Inspect** the working tree and ensure no accidental files, generated artifacts or secrets have slipped in.
4. **Save** the work with a descriptive commit and push the active branch when the block is ready to preserve.
5. **Record** the new checkpoint, test result, decisions, unresolved gaps and exact next step in this handoff.
6. **Mark direction**: state one next implementation target, and explicitly state what is out of scope until that target is closed.
7. **Stop** at a stable checkpoint rather than starting an unrelated improvement merely because the session is still open.

A block is not considered closed while a failing test, undocumented architectural change, unresolved canon ambiguity, or unrecorded next direction remains.

The repository now includes `docs/WORK_BLOCK_PROTOCOL.md` and `scripts/close_work_block.sh` as practical guardrails for this cycle. The script runs the complete suite, `git diff --check`, working-tree/diff inspection and reports the current checkpoint; it intentionally does **not** commit, push or edit the handoff automatically, because those operations still require an explicit judgment about what is being saved.

A new session should begin by reading this handoff, checking the branch/worktree and rerunning the relevant verification before making changes. The conversation is context; this file is the durable state.

## Next implementation sequence
1. Pull the current `feature/semantic-model` branch into the Codespace and run `PYTHONPATH=. pytest -q`.
2. Once the suite is green, verify active-root references no longer point to the removed legacy Gag 001 raster; historical experiment scripts may explicitly reference archived material when that is their purpose.
3. Finish reviewing any remaining current-facing Illo/Killo/Xoxo references; preserve only those that are explicitly historical.
4. Verify the 10-image historical corpus in `history/creative-corpus/` and classify/rename it semantically while retaining each original generation ID.
5. Extend `CompiledPrompt` with a deterministic semantic-context representation or equivalent provider-neutral structure.
6. Build that context from authoritative current data, with route/task relevance and bounded size.
7. Add focused tests proving Arsa/Pisha semantics are present and historical identity is not activated by the context builder.
8. Keep the Groq/Qwen transport unchanged unless the new compiled representation requires a deliberate rendering adjustment.
9. Run the complete suite after the cleanup and context changes.
10. Only then perform the next real Qwen candidate-generation experiment, recording the actual prompt/context and candidate so the result is auditable.
11. Update this handoff again at the end of that block.

## Documentation discipline
`docs/BIBLIA_2_0.md` is the canonical narrative reference for the current universe and explicitly distinguishes historical Illo & Killo material from Arsa & Pisha canon.

`README.md`, `docs/HUMOR.md`, `docs/PALETA.md`, `docs/CANON_100.md`, `docs/SEMANTIC_MODEL.md`, the model sheets and prompts are current-facing and must describe Arsa & Pisha.

Do not blindly mass-replace `Illo`, `Killo`, or `Xoxo`: historical archives can legitimately retain legacy terminology when their historical status is explicit and useful. Conversely, any current-facing canon, prompt context or real current experiment must use Arsa & Pisha.

## Continuity rule
If the original ChatGPT conversation becomes unavailable, open a new chat and tell the assistant:

“Work on repository `Mareta3rd/illo-and-killo-p-blico-`, branch `feature/semantic-model`. Read `docs/AI_HANDOFF.md` first. Treat it as the durable project state and continue from its current checkpoint. Arsa & Pisha are current canon; Illo & Killo and earlier Xoxo material are historical only. Verify repository state and tests before changing anything. Do not discard historical creative material: use it as an explicitly non-canonical development corpus for learning and comparison.”

This handoff is the durable continuity document. It must be updated whenever a major architectural, experimental, or canon-level state change is made.
