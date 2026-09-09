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
Current repository checkpoint: `9c424a9`.
Latest full-suite result confirmed in the current working session: **542 passed, 49 subtests passed**.

The repository currently has **Arsa & Pisha as the active creative canon**. Illo & Killo are historical development material, not current character canon. Earlier Xoxo terminology is also historical/intermediate and must not be treated as the active name.

## Current canonical characters
The structured character catalog defines:
- `arsa` / **Arsa**: co-lead; white pelage; yellow-blonde flame-like crest; green scarf; black three-finger hands; black hooves; short flame tail; stylized equine hint; high-energy, impulsive, mischievous, expressive and tender behavioral grammar.
- `pisha` / **Pisha**: co-lead; red pelage; black spots; clavel; short rounded horns; black three-finger hands; black hooves; compact bovine hint; apparently calm, observant, innocent, proud, mischievous, absent-minded and tender behavioral grammar.

Important mature design decisions to preserve:
- Arms/hands and legs/hooves are distinct anatomical systems and must not collapse into the same visual treatment.
- Black three-finger hands and black hooves are deliberate recognition devices, not interchangeable anatomy.
- The characters are stylized and deliberately non-realistic; animal identity remains suggestive rather than literal.
- The visual language is contemporary and high-quality, with a **small, controlled vintage/print-comic soul** where useful. Vintage is a seasoning, not a period imitation: the target remains modern, contemporary and forward-looking, never deliberately old-fashioned.
- Anatomical comic markers are contextual and optional; their absence is not a canon failure.

Their relationship is explicitly modeled as inseparable companions with mutual trust, teasing, protection and shared mischief, with situational role switching and tenderness underneath the mischief. Neither is a permanent protagonist or helper.

## Current visual / humor canon
The canonical universe is defined as contemporary, Andalusian in attitude and behavior rather than tourist decoration, playful, irreverent but affectionate, exportable and visually legible.

Core humor rules include:
- one primary gag per illustration;
- immediate first-read visual comprehension;
- optional second-read surprise, irony, picardía or contextual detail;
- absurd escalation from recognizable everyday logic;
- physical, facial and gestural comedy that can work without dialogue;
- conflict that is playful rather than cruel;
- tenderness remains protected even in acidic, obscene or black humor when context warrants it;
- economy: remove details that do not improve gag, reading, personality or composition.

Andalusia is layered as: structural/behavioral first, environmental second, ornamental third. Environmental and ornamental references must support the gag rather than turn the universe into a tourist postcard.

## Canon Gag 001
The accepted canonical visual material remains **Gag 001 · Jamón**.

Its current semantic claim keys are:
- `gag/001/composition/arsa_primary`
- `gag/001/composition/ham_primary`
- `gag/001/characters/pisha_reaction`

Old Illo/Killo or Xoxo naming in historical material must not be used as the active interpretation of these claims.

## Historical creative corpus
Previously developed material supplied during earlier creative work is intentionally preserved as **historical development corpus**, not canon.

The currently recovered corpus consists of two small image groups:

### Arsa & Pisha Origins
Eight historical images covering early gag/composition experiments including fishing/sea, parody-cover treatment, guitar/dance, motorbike/action, jamón impact, title/identity exploration, guitar confrontation and title variants. These are useful for studying evolution of composition, timing, silhouettes, expressions, typography and early character treatment.

### Killo & Illo
Two historical images covering an espeto/fishing scene and a jamón/mosquito gag. These are especially useful for studying earlier Andalusian environmental recognition, secondary-detail jokes, composition and gag density.

These images are **not** current reference sheets and do not override `data/characters.yaml`, current model sheets, current palette, current humor rules or canonical gag claims. Historical anatomy, proportions, names, typography, palette details, props and exact designs must not be reintroduced automatically.

A repository manifest has been added at `history/creative-corpus/MANIFEST.md`. The binary image files themselves are prepared in an external transfer package because the available repository write interface is text-only; they still need to be copied into the corresponding `history/creative-corpus/` directories from the prepared package.

The corpus may be mined for successful mechanisms, learned lessons and reusable ideas only after revalidation against current canon.

## Validated architecture
The project has tested boundaries for:

`provider → ExternalEvidenceRecord → ProviderEvidenceObservation → EvidenceSnapshot → contractual evaluation when applicable → Core pipeline/evaluator → Core decision`

Earlier gateway/registry/orchestrator, regression, semantic-audit and execution-audit layers remain part of the validated architecture.

## Gemini
Gemini is a validated external evidence provider. Its provider-specific transport and adapter enter through the common observation/snapshot path.

Previously validated live configuration included a real Gemini run against `gags/images/001_jamon.png`, with evidence entering Core and a final Core decision of `accept`. The provider supplied evidence; Core supplied the decision.

The Gemini stability/composition tests and experiment scripts are aligned with the current Arsa-based Gag 001 claim keys.

## OpenAI
OpenAI Phase A exists as a provider-specific transport/adapter implementation, but its earlier real connectivity attempt returned `429 insufficient_quota`. Do not treat OpenAI as the next mandatory phase merely because older handoff text says so.

Any future live OpenAI work must verify the current SDK/API surface and model availability before implementation assumptions are made.

## Groq/Qwen
Groq/Qwen is already validated through the provider-neutral evidence path with a real multimodal Qwen 3.8 27B experiment using `gags/images/001_jamon.png`.

The candidate-generation path also exists through:
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

## Next implementation sequence
1. Complete incorporation of the prepared historical image package into `history/creative-corpus/` in the Codespace.
2. Inspect the existing Core knowledge-loading path and identify the authoritative structured sources already available to `PipelineContext`.
3. Extend `CompiledPrompt` with a deterministic semantic-context representation or an equivalent provider-neutral structure.
4. Build that context from authoritative current data, with route/task relevance and bounded size.
5. Add focused tests proving that Arsa/Pisha semantics are present and historical Illo/Killo/Xoxo content is not treated as active identity.
6. Keep the Groq/Qwen transport unchanged except where the new compiled representation requires a deliberate rendering adjustment.
7. Run the complete suite.
8. Only then perform the next real Qwen candidate-generation experiment, recording the actual prompt/context and candidate so the result is auditable.

## Documentation discipline
`docs/BIBLIA_2_0.md` is the canonical narrative reference for the current universe and explicitly distinguishes historical Illo & Killo material from Arsa & Pisha canon.

`README.md`, `docs/HUMOR.md`, and `docs/PALETA.md` are current-facing documents and describe Arsa & Pisha. Historical references should remain only where their historical status is explicit and useful.

Do not blindly mass-replace `Illo`, `Killo`, or `Xoxo`: historical archives and tests can legitimately retain legacy terminology when they are explicitly preserving historical material. Conversely, any current-facing canon, prompt context or real experiment must use Arsa & Pisha.

## Continuity rule
If the original ChatGPT conversation becomes unavailable, open a new chat and tell the assistant:

“Work on repository `Mareta3rd/illo-and-killo-p-blico-`, branch `feature/semantic-model`. Read `docs/AI_HANDOFF.md` first. Treat it as the durable project state and continue from its current checkpoint. Arsa & Pisha are current canon; Illo & Killo and earlier Xoxo material are historical only. Verify repository state and tests before changing anything. Do not discard historical creative material: use it as an explicitly non-canonical development corpus for learning and comparison.”

This handoff is the durable continuity document. It must be updated whenever a major architectural, experimental, or canon-level state change is made.
