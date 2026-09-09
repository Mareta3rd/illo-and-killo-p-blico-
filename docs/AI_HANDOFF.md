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
Current repository checkpoint: `a222fa0` (`classify historical creative corpus`).

### Verified closure status
The historical-corpus cleanup block is **CLOSED and GREEN**.

Confirmed in the Codespace immediately before closure:
- historical corpus rename/classification completed;
- 10 historical image files are present under the intended `history/creative-corpus/` subdirectories;
- original numeric generation IDs are retained in every semantic filename;
- `git diff --check` passed with no output;
- complete test suite: **542 passed, 49 subtests passed in 19.32s**;
- commit `a222fa0` created and pushed successfully to `origin/feature/semantic-model`;
- `bash scripts/close_work_block.sh` completed successfully and reported checkpoint `a222fa0` with clean working-tree/diff checks.

The ten semantic filenames are:
- `APO-001_pesca-barca_1788957758584.png`
- `APO-002_portada-parodia-sierra-nevada_1788957758616.png`
- `APO-003_guitarra-baile_1788957758655.png`
- `APO-004_vespino-fuga_1788957758694.png`
- `APO-005_jamon-golpe_1788957758729.png`
- `APO-006_guitarra-persecucion_1788957758750.png`
- `APO-007_guitarra-confrontacion_1788957758780.png`
- `APO-008_titulo-personajes-variante_1788957758814.png`
- `KAI-001_espetos-en-barca_1788958159854.png`
- `KAI-002_jamon-mosquito_1788958159883.png`

The repository now has durable work-block guardrails in `docs/WORK_BLOCK_PROTOCOL.md` and `scripts/close_work_block.sh`. The protocol requires a coherent block to be solved, verified, inspected, committed, pushed, handed off, given one next direction, and then stopped. The closure script runs the complete suite, whitespace validation, working-tree/diff inspection and checkpoint reporting; it deliberately does not commit, push or edit the handoff automatically.

## Current creative canon
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

### Arsa & Pisha Origins
Eight historical images. This is the first development stage: it is historically related to the project but is **not an early canonical version of current Arsa & Pisha**. In that stage the characters were a horse and a bull and several later decisions were discarded. Use these images only to study visual/gag mechanisms and evolution.

### Illo & Killo
Two historical images covering an espeto/fishing scene and a jamón/mosquito gag. This is the immediately previous development stage before current Arsa & Pisha. It may supply useful mechanisms and lessons, but it is not current canon.

The historical corpus is documented under `history/creative-corpus/` and is intended for extraction of successful mechanisms, lessons and reusable ideas only after revalidation against current canon. The corpus is now classified semantically while retaining each original generation ID for traceability.

Historical naming/classification rule: classify by **content + gag/mechanism**, not by guessed chronology. The current archive follows that rule through descriptive names such as fishing/pesca, parody-cover, guitar/dance, Vespino/fuga, jamón impact, guitar chase/confrontation, title variants, espeto/fishing and jamón/mosquito.

## Repository cleanup completed
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

Obsolete `model-sheets/illo.md`, `model-sheets/killo.md` and current `gags/002_pesca.md` were removed from active roots. `docs/SESSION_HANDOFF.md` is historical/superseded and points to this file as the durable source of continuity.

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
OpenAI Phase A exists as a provider-specific transport/adapter implementation, but an earlier real connectivity attempt returned `429 insufficient_quota`. Do not treat OpenAI as the next mandatory phase merely because older handoff text says so.

Any future live OpenAI work must verify the current SDK/API surface and model availability before implementation assumptions are made.

## Groq/Qwen
Groq/Qwen is already validated through the provider-neutral evidence path with a real multimodal Qwen 3.8 27B experiment using the earlier Gag 001 image.

The candidate-generation path exists through:
- `core/groq_qwen_candidate_executor.py`
- `core/groq_qwen_candidate_transport.py`
- `scripts/run_groq_qwen_candidate.py`

The default candidate model is `qwen/qwen3.8-27b`, and the transport requires structured outputs for the strict candidate schema. No automatic fallback is allowed.

The candidate transport is intentionally provider-specific and returns a `Candidate`; it must not return Core decisions or evidence-contract decisions. Forbidden fields include `accept`, `decision`, `evidence`, and `claim_key`.

## Current semantic-context gap — NEXT TARGET
The next and only planned implementation target is to build a **small, deterministic semantic context** for `CompiledPrompt` from authoritative current repository data.

The target context should expose, only as relevant to the route/task:
- current Arsa/Pisha identities and protected visual/behavioral invariants;
- the distinction between arms/hands and legs/hooves;
- Arsa/Pisha relationship grammar and dynamic role switching;
- current humor grammar, especially one-gag-per-image, immediate readability, absurd escalation, non-malicious conflict and protected tenderness;
- Andalusian structural/behavioral layer as primary, with environmental/ornamental references only when useful;
- contemporary/vanguard visual finish with a restrained vintage soul, never retro imitation;
- relevant documented decisions and current Gag 001 claims when applicable;
- explicit separation between current canon and historical Illo/Killo/Xoxo material.

The semantic context must be deterministic, bounded, route/task-relevant and derived from authoritative sources. It must not duplicate canon into uncontrolled prompt prose, invent missing semantics, mutate canonical data, or allow the provider to decide what is canonical.

### Deliberately out of scope until this target is closed
- new provider integrations;
- live OpenAI work;
- automatic provider fallback;
- new creative-canon changes;
- replacing or reinterpreting the historical corpus;
- the next real Qwen candidate-generation experiment.

The next session must start by reading this handoff, checking branch/worktree state, and rerunning the relevant verification before implementation. After the semantic-context target is solved and verified, the handoff must be updated again before starting the next experimental phase.

## Continuity rule
If the original ChatGPT conversation becomes unavailable, open a new chat and tell the assistant:

“Work on repository `Mareta3rd/illo-and-killo-p-blico-`, branch `feature/semantic-model`. Read `docs/AI_HANDOFF.md` first. Treat it as the durable project state and continue from its current checkpoint. Arsa & Pisha are current canon; Illo & Killo and earlier Xoxo material are historical only. Verify repository state and tests before changing anything. Do not discard historical creative material: use it as an explicitly non-canonical development corpus for learning and comparison.”

This handoff is the durable continuity document. It must be updated whenever a major architectural, experimental, or canon-level state change is made.