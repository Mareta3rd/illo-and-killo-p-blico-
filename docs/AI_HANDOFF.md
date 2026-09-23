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
Current repository checkpoint: `0bc3088` (DecisionProvider contract committed and pushed; complete suite verified green at 615/59).

### Verified closure status
The historical-corpus cleanup block is **CLOSED and GREEN**.
The semantic-context block is also **VERIFIED GREEN by the Codespace**, but has not yet been committed as a final closure checkpoint; the branch currently ends at `fe404c2` and the working tree was reported clean by `scripts/close_work_block.sh`.

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

## Current semantic-context block — CLOSED AND GREEN
The planned next target is now being implemented: a **small, deterministic semantic context** for `CompiledPrompt` derived from authoritative current repository data and selected current documentation.

Implementation now present on the branch:
- `core/semantic_context.py` provides a bounded provider-neutral `SemanticContext` representation;
- `core/loader.py` loads the canonical `data/gag_001_claims.json` mapping;
- `core/prompt_compiler.py` attaches the semantic context while preserving the existing `context_summary` compatibility surface;
- `tests/test_prompt_compiler.py` contains focused tests for route relevance, Arsa/Pisha semantics, historical-boundary exclusion, boundedness and determinism;
- `tests/test_loader.py` verifies canonical Gag 001 claims are loaded.

The context is deliberately bounded and route-specific. Character entries are generated from the structured character catalog, including the separate hands/hooves anatomy; relationship entries come from the current relationship catalog; route-relevant decisions, objects, heritage, current gag claims and selected current documentation sections are included only where appropriate. An explicit boundary marks historical material as reference-only and excluded from active canon.

Important verification state:
- The semantic-context implementation was verified green in the Codespace: **546 passed, 49 subtests passed**.
- `bash scripts/close_work_block.sh` completed successfully, with `git diff --check` and working-tree/diff checks clean.
- Final semantic-context checkpoint: `562826c` (`record semantic context verification`).
- This block is closed. Do not reopen or modify it merely to support the next candidate experiment unless a new failing requirement is discovered.

The semantic context must remain deterministic, bounded, route/task-relevant and derived from authoritative sources. It must not invent missing semantics, mutate canonical data, or allow the provider to decide what is canonical.

### Deliberately out of scope for the closed semantic-context block
- new provider integrations;
- live OpenAI work;
- automatic provider fallback;
- new creative-canon changes;
- replacing or reinterpreting the historical corpus.

The next implementation target is **the first auditable real Qwen candidate-generation experiment using the compiled semantic context**.

## Candidate-generation audit scaffold — CONTRACT REPAIR / VERIFICATION PENDING
A preparatory audit layer has now been added on top of the closed semantic-context block.

Implementation now present on the branch:
- `core/candidate_execution_artifact.py` records the exact compiled prompt, its digest, the bounded semantic-context entries, each exact provider request prompt, each returned candidate as canonical JSON, candidate digests, Core evaluation decisions/reasons, final status and stop reason;
- `core/groq_qwen_candidate_transport.py` exposes the exact request-prompt builder used by the transport so the audit record does not duplicate prompt construction logic;
- `scripts/run_groq_qwen_candidate.py` accepts `--candidate-audit-path` and writes the candidate-generation audit after a real run;
- `tests/test_candidate_execution_artifact.py` covers exact-context capture, per-iteration prompt/candidate digests, deterministic round-trip serialization, persistence and tamper/schema rejection.

Architectural boundary:
- the audit artifact is observational only;
- it records what the provider received and returned plus what Core evaluated;
- it does not create, mutate or reinterpret canon or Core decisions;
- evidence remains in the existing evidence artifact/path and candidate audit remains a separate closed record.

Verification state:
- The Codespace complete suite is now **GREEN: 552 passed, 49 subtests passed**.
- `bash scripts/close_work_block.sh` completed successfully; whitespace, working-tree and diff checks were clean.
- The new audit scaffold is therefore verified by the complete regression suite.
- No live Qwen result has yet been generated for this block.
- The earlier bare `pytest -q` failure was an invocation/environment issue: this repository's closure script correctly uses `PYTHONPATH=.`, after which the same complete suite passed.

### First live-run finding and contract repair

The first real Qwen run reached the external provider and Core successfully, then stopped at `human_review` with `canon validation requires human review`. The captured candidate used bare strings in `elements` even though Core's canonical candidate representation uses structured element objects with explicit intentions and optional structured fields.

The repair now present on the branch:
- strict Qwen schema requires element objects with `id`, `intention`, `library`, `count`, `color`, `very_small` and `role`, using `null` for non-applicable fields;
- the request prompt states that contract explicitly and forbids bare strings;
- the provider parser now mirrors the strict contract instead of accepting partial candidates;
- the schema was kept within the currently documented strict Structured Outputs subset rather than adding unnecessary constraints;
- `docs/SEMANTIC_MODEL.md` now documents the external candidate contract.

The repair is designed to stop malformed provider output at the provider boundary. It does not weaken Core validation or convert human review into acceptance.

Verification of the repair remains **pending**. The first post-repair suite run exposed four test regressions: two parser-error-message expectations and two fake-provider fixtures that still returned the old minimal `{"content": ...}` payload. The parser was adjusted to reject forbidden provider-boundary fields before completeness checks, and the fake client default was updated to emit a complete structured candidate matching the current contract. The fixes are committed in `2e1f09a` and `1f432f5` on `feature/semantic-model`.

The Codespace run that triggered this repair reported **551 passed, 4 failed, 49 subtests passed**; therefore it must not be treated as green yet. The next required action is to pull the latest branch and run the complete suite again before another live Qwen call.

Recommended first live experiment after verification:
- textual-only Qwen candidate run;
- model `qwen/qwen3.8-27b`;
- new gag idea involving Arsa, Pisha and jamón so the compiled semantic context has a concrete relevance signal for the current Gag 001 claim set;
- write both the existing evidence artifact and the new candidate audit to a local temporary/output path;
- inspect the audit before interpreting the generated candidate;
- do not commit generated run artifacts unless deliberately chosen as historical experimental evidence.

Suggested invocation after the test gate returns green:
```bash
python scripts/run_groq_qwen_candidate.py \
  "Crear un gag nuevo de Arsa y Pisha alrededor de un jamón, con un gag principal inmediato, escalada absurda desde una lógica reconocible y ternura entre ambos." \
  --run-id qwen-semantic-context-001 \
  --artifact-path /tmp/qwen-semantic-context-001.evidence.json \
  --candidate-audit-path /tmp/qwen-semantic-context-001.candidate-audit.json
```

Do not treat the resulting model text as canon. The experiment is successful only as evidence about the behavior of the provider-neutral candidate path and the auditability of the compiled semantic context. Any creative candidate remains subject to Core evaluation and human review where required.

## Creative Feedback Layer — IMPLEMENTED / VERIFICATION PENDING
The first real Qwen candidate exposed a broader architectural requirement: a system that only enforces canon can become a deterministic template generator. The project therefore now distinguishes identity reuse from mechanism reuse.

Implementation added:
- data/creative_mechanisms.json stores a deliberately small, authoritative creative-memory record for the current semantic Gag 001 mechanism;
- core/creative_feedback.py produces bounded, non-scoring feedback and high-confidence mechanism-reuse findings;
- core/prompt_compiler.py states explicitly that canon is a boundary, not a template, and that prop substitution is not meaningful novelty;
- core/orchestrator.py uses creative feedback as a soft iteration gate: a high-confidence mechanism reuse requests another candidate rather than accepting the derivative result, while hard canon validation remains separate;
- core/semantic_audit.py records creative findings, guidance and whether another creative pass was requested;
- core/candidate_execution_artifact.py reconstructs the exact iteration prompt including creative guidance so request digests remain auditable;
- docs/CREATIVE_FEEDBACK.md documents the boundary and philosophy;
- focused regression tests were added for feedback detection and iteration guidance.

This layer is deliberately not a second canon system. It does not score taste, mutate candidates, or prescribe a fixed comic recipe. Its current detector is conservative and only requests revision for high-confidence mechanism overlap with explicitly recorded creative memory.

The branch was last confirmed GREEN at **561 passed, 49 subtests passed in 17.81s** on checkpoint `b5aea86`. The Creative Feedback block is now **VERIFIED GREEN**. The first verification run exposed an overly narrow direct-jamón reuse test (560 passed, 1 failed); the detector was corrected to flag direct central-object reuse even when the prose does not contain two action keywords, and the complete suite then passed at 561/561.

The next target is a new Qwen run using the same jamón brief, primarily to observe whether the structured feedback changes the second-pass generation away from noun substitution and toward a genuinely different causal mechanism. Do not modify the Core canon rules merely to force that experiment to pass.

### Subsequent live-run observation: Groq OTPM boundary
The next Qwen run did not reach candidate generation. Groq rejected the request before execution because the requested expected output exceeded the observed on-demand Output Tokens Per Minute limit: 1000, with the request estimated at 1047. The provider returned HTTP 429 rate_limit_exceeded. This is a transport-budget issue, not a candidate-quality or Core-validation failure.

The transport has now been changed to request `max_tokens=900` for qwen/qwen3.8-27b, with a regression test protecting that ceiling.
The transport-budget/motif block is now also **VERIFIED GREEN: 562 passed, 49 subtests passed in 29.24s**, with clean whitespace and working-tree checks at checkpoint `6f95779`.

## Visual Critique Layer — GEMINI REVIEWER IMPLEMENTED / VERIFICATION PENDING
A provider-neutral visual critique contract is now paired with a concrete Gemini multimodal reviewer adapter:
- core/visual_critique.py defines closed observations for character fidelity, gag readability, composition hierarchy, motion/pose, style coherence, cultural integration and production fit;
- observations use state (observed/uncertain/not_applicable) and independent confidence (high/medium/low), with no aesthetic score;
- core/gemini_visual_reviewer.py builds the Gemini image+text request, constructs the review prompt, parses structured findings, and requires complete coverage of the requested dimensions;
- tests/test_visual_critique.py covers the provider-neutral contract;
- tests/test_gemini_visual_reviewer.py covers prompt construction, strict dimension coverage, malformed responses, image transport, and provider-boundary failures;
- docs/VISUAL_CRITIQUE.md documents the architecture and boundary.

The reviewer is deliberately observational only. It returns VisualCritiqueReport values and has no Core decision methods. The next step after a green verification is one real controlled image review, then wiring selected high-confidence observations into the existing creative-feedback loop without turning the reviewer into a scoring or canon system.

The purpose is to let the future system say not merely whether an image obeys canon, but what it concretely observes about character treatment, gag readability, movement, hierarchy, style coherence, Andalusian integration and production suitability, while leaving taste and canon decisions in their proper layers.

The first Codespace verification failed during test collection because `core/visual_critique.py` contained a malformed module docstring. No tests executed. The complete header was subsequently corrected in `9300805`. The branch now also contains the first Gemini reviewer adapter and its tests. The first closure run exposed a transport-builder bug (`None` instead of the request callable); `cee61d8` adds the missing `return request`. Complete closure is still the required verification gate before the visual block can be marked green.

### Recurrent Andalusian ambient motifs
Experience from SinergYa product design is now recorded as soft environmental guidance: a simple Andalusian streetlamp, a small pot with carnations, and a present-but-not-dominant bougainvillea are recurring optional motifs. They are not canon invariants and should never appear together by default; selection depends on context, composition and gag.

### Naming
Arsa remains the canonical code identifier for now. Arza is a naming candidate that currently has stronger artistic resonance for the user, but no repository-wide rename has been authorized yet.

## Codex Task Contract — VERIFIED GREEN

A first controlled executor boundary is implemented for using Codex as a governed work agent rather than a Core authority.

Implementation now present:
- `core/codex_task.py` defines `CodexTask` and `CodexTaskResult` with closed deterministic JSON serialization;
- task modes cover `analysis`, `implementation`, `repair` and `improvement`;
- each task records issuer, objective/context, allowed paths, protected paths, constraints, acceptance criteria, verification commands, base ref/commit, fixed `execution_only` authority and mandatory human approval;
- `validate_codex_task_result()` verifies task identity, digest, protected-path exclusion, allowed-scope containment and the read-only nature of analysis tasks;
- `tests/test_codex_task.py` covers round-tripping, closed schemas, authority protection and execution-scope enforcement;
- `docs/CODEX_TASK_CONTRACT.md` documents the executor boundary;
- `digital_ricard` is a recognised controlled issuer, while retaining the same execution-only authority and mandatory human approval.

Verification:
- complete suite: **601 passed, 54 subtests passed in 16.60s**;
- `bash scripts/close_work_block.sh` completed successfully;
- checkpoint: `20c9e68`;
- whitespace, working-tree and diff checks were clean.

## Creative Direction — SUBVERSIÓN ELEGANTE / MAGNETISMO PUNK

A recent artistic direction has been explicitly recognised as an important part of the Arsa & Pisha identity and must be documented as a compositional/behavioral grammar rather than as a requirement to sexualise the characters.

Core idea:
- polished, friendly and commercially approachable surface;
- underneath, a controlled punk attitude: confidence, insolence, asymmetry, self-awareness and refusal to look timid or generic;
- visual magnetism may come from pose, body language, gaze, silhouette, crop, diagonals, gesture and compositional tension;
- suggestive or cheeky energy can exist without explicit sexual content;
- the effect should often reveal itself on a second read rather than announce itself immediately;
- provocative energy must remain compatible with tenderness, humour and the inseparable Arsa/Pisha relationship.

This is not a fixed gag recipe, score or mandatory visual motif. It is a search direction for generators, reviewers and human art direction. The desired balance is disciplined enough to preserve identity but open enough to allow invention.

Practical vocabulary:
- contrapposto and deliberate weight shifts;
- asymmetrical shoulders/hips and compact dynamic silhouettes;
- direct or knowingly cheeky gaze when context supports it;
- bold crops, diagonals and negative space;
- occasional rebellious line gestures or controlled deformation in the drawing;
- acid/high-contrast accents used selectively against otherwise friendly presentation;
- visual subversion hidden beneath an accessible product surface.

Important boundary: examples involving sexualised commercial imagery, adult-coded presentation or infantilisation should not be copied as content. Only the abstract visual observations that are useful to the project are retained: attention capture, pose magnetism, rhythm, gaze, silhouette, confidence and layered readability.

Creative test implication:
The previous shield-of-Andalusia gag experiment was understood as conceptually coherent but visually too restrained. Future experiments should test stronger attitude/composition before escalating explicitness.

## Ricard Digital — ARCHITECTURAL ENTRY POINT ESTABLISHED

`docs/DIGITAL_RICARD.md` establishes Ricard Digital as a provider-neutral human-facing coordination role. The current ChatGPT interaction can implement this role, but Core remains independent of any single model or interface.

Ricard Digital can interpret human intent, preserve continuity, coordinate specialised agents and formulate bounded Codex work. It cannot silently promote provider output to canon, grant Core authority to an executor, bypass protected scopes or remove human approval.

This is an architectural door for future implementations rather than a persistent autonomous runtime. Future interfaces/providers may implement the same role without changing Core.

## Codex Live Smoke — HISTORICAL ENVIRONMENT BLOCK

The live execution path was initially blocked because the Codespace did not yet have the `codex` executable installed. This section is historical: the executable was subsequently installed and authenticated, and the real smoke reached Codex CLI. The current blocker is documented in the newer `Codex CLI Live Smoke — ARGUMENT COMPATIBILITY FIX READY` section below.
- `AGENTS.md` provides project-level instructions that current Codex tooling loads from the repository root;
- `scripts/run_codex_smoke_test.py` builds a task from the current branch and HEAD and requires an explicit `--approve` flag;
- the smoke task is `analysis` mode, has no writable paths, and returns failure if repository files change;
- missing executable and timeout conditions now return structured failed task results instead of raw subprocess exceptions.
- missing executable and timeout conditions now return structured failed task results instead of raw subprocess exceptions.

Verification state: the preparation block is GREEN at **607 passed, 54 subtests passed in 16.60s** on checkpoint `bdcd16d`; the live smoke remains blocked only by missing local Codex installation. The setup-helper/docs additions are pending the next complete-suite closure.

After the next green closure, install/authenticate the Codex CLI in the Codespace, verify it with `bash scripts/check_codex_environment.sh`, and then rerun:
```bash
PYTHONPATH=. python scripts/run_codex_smoke_test.py --approve
```

## Codex CLI Transport — VERIFIED GREEN

The first concrete Codex transport now exists outside Core:
- `core/codex_cli_transport.py` invokes `codex exec` non-interactively;
- analysis tasks use a read-only sandbox; implementation/repair/improvement tasks use workspace-write;
- repository branch, base commit and clean working tree are checked before execution;
- JSONL events, final agent message, observed verification commands, changed files and a diff digest are translated into `CodexTaskResult`;
- `tests/test_codex_cli_transport.py` covers prompt construction, JSONL parsing, verification extraction and CLI invocation wiring;
- `docs/CODEX_CLI_TRANSPORT.md` documents the provider boundary.

Verification:
- complete suite: **606 passed, 54 subtests passed in 17.84s**;
- checkpoint: `9293764`;
- the initial transport tests exposed only fixture defects: a missing `CodexTask` import and an overlapping allowed/protected scope. Both were fixed without weakening the authority/scope contract.

Historical status at that stage: the transport had not yet been exercised against the live Codex installation.

## Codex CLI Live Smoke — ARGUMENT COMPATIBILITY FIX READY

The first live smoke reached the installed Codex CLI sufficiently to expose a real CLI parser incompatibility. Authentication and the installed executable are working; the failure occurs before any model execution because the installed "codex exec" path rejects both "--ask-for-approval never" and "-a never" when those options are placed after the "exec" subcommand.

The transport has now been corrected to remove the approval flag entirely. This is deliberate, not another flag-order experiment:
- `codex exec` is the non-interactive execution mode used by this transport;
- the project-level explicit human-approval gate remains in `CodexExecutionBridge`, before the provider transport is called;
- the concrete CLI transport controls execution autonomy with the explicit `--sandbox` mode selected from the task mode;
- analysis remains `read-only`; implementation/repair/improvement remains `workspace-write`;
- the exact command invocation test was updated to protect this contract.

The observed live error is preserved as historical diagnostic evidence. Upstream Codex CLI issue reports also document the same rejection of `--ask-for-approval` / `-a` after `exec`, so the previous authentication hypothesis is closed.

Repository state before this correction:
- checkpoint after pulling the previous compatibility patch: `bae971a`;
- complete closure suite: **608 passed, 54 subtests passed in 18.23s**;
- live smoke result: **failed at CLI argument parsing, no repository files changed, exit code 2**.

New verification required after pulling this correction:
```bash
git pull --ff-only origin feature/semantic-model
bash scripts/close_work_block.sh
PYTHONPATH=. python scripts/run_codex_smoke_test.py --approve
```

Do not reintroduce `-a` or `--ask-for-approval` into the post-`exec` argv unless the installed CLI contract changes and is verified directly. The next target after a green live smoke remains a tightly bounded `workspace-write` implementation mission through the same task contract and bridge.

## Codex CLI Live Smoke — VERIFIED GREEN

The first real live smoke test through `Ricard Digital → CodexTask → CodexExecutionBridge → CodexCliTransport → codex exec` is now **GREEN**.

Verified in the user's Codespace after pulling checkpoint `c0cd915`:
- complete closure suite: **608 passed, 54 subtests passed in 38.16s**;
- live smoke status: **completed**;
- blockers: none;
- changed files: none;
- diff digest: none;
- Codex reported that `AGENTS.md` and the required handoff/documentation were loaded;
- the task remained read-only and the repository stayed clean.

This closes the previous CLI-parser blocker. The corrected transport no longer emits `-a` or `--ask-for-approval` after `codex exec`; execution autonomy is bounded by the task mode's `--sandbox`, while project-level human approval remains enforced by `CodexExecutionBridge`.

The smoke's own observations confirm the intended architecture: Ricard Digital formulates bounded work, the bridge gates and validates execution, the concrete transport invokes Codex, and Core retains canon/evidence/evaluation/final authority.

## Codex First Write-Enabled Smoke — VERIFIED GREEN

The first successful read-only live Codex smoke has now been followed by the first successful write-enabled execution through the full governed path.

Verified in the user's Codespace after pulling the preparation checkpoint:
- complete closure suite: **608 passed, 54 subtests passed in 19.61s**;
- live implementation-smoke status: **completed**;
- blockers: none;
- changed files: exactly `tests/test_codex_cli_transport.py`;
- diff digest: `0da20614231d317c618b896e4109f473ee27df406d5f50788b965908b78daeed`;
- Codex reported the focused timeout regression test was added;
- focused verification: **8 passed**;
- no production files were changed.

The execution boundary therefore worked in both directions:

The smoke result is the runtime source of truth for this block. The GitHub file view may continue to show the pre-execution tree until the user's local Codespace mutation is intentionally committed and pushed; no generated or unreviewed local change is assumed canonical here.

- the bridge required explicit human approval before transport execution;
- implementation mode selected `--sandbox workspace-write`;
- the task scope restricted the mutation to one test file;
- the returned `CodexTaskResult` reported exactly that allowed mutation;
- the runner rejected any scope outside the single allowed path;
- Codex was instructed not to commit or push, and no commit/push occurred during the run.

This is the first real evidence that Codex can act as a governed execution agent rather than merely an analysis endpoint. The Core authority boundary remains unchanged: Codex did not decide canon, evidence, evaluation or final project policy.

### Immediate human review gate

Before this write-enabled block is closed, inspect the actual diff in the Codespace:

```bash
git diff -- tests/test_codex_cli_transport.py
git status --short
```

If the diff is exactly the focused timeout regression described by the smoke result, the change may be committed and pushed as a normal repository change. The Codex runner itself does not commit or push.

### Technology Evolution Layer — VERIFIED PREPARATION

The technology-evolution layer is now part of the repository architecture.

Added:
- `docs/TECHNOLOGY_RADAR.md` defines capability-oriented lifecycle management:
  OBSERVE → INVESTIGATE → PROTOTYPE → BENCHMARK → ADOPT → MAINTAIN / DEPRECATE.
- `data/capabilities.json` records current capability candidates and verified
  execution infrastructure.
- `docs/CAPABILITY_ROUTING.md` defines the provider-neutral decision seam.
- `docs/DETERMINISTIC_DECISION_PROVIDER.md` defines the reference baseline
  for future decision-provider comparisons.
- `scripts/run_codex_decision_provider_mission.py` and
  `scripts/run_codex_deterministic_provider_mission.py` provide bounded,
  human-approved Codex implementation missions for these seams.

The first DecisionProvider contract has now been implemented by Codex, reviewed
in the Codespace, verified with the complete suite and committed/pushed.

Verified:
- complete suite: **615 passed, 59 subtests passed in 18.50s**;
- focused DecisionProvider suite: **6 passed, 5 subtests passed**;
- whitespace checks on both new untracked files were clean before commit;
- committed checkpoint: `0bc3088`;
- no external decision provider has been integrated yet.

The architectural principle is explicit: **capabilities are stable contracts;
providers are replaceable implementations**. Codex, Jev, Claude, OpenAI
Agents API, Gemini, Qwen and future systems are therefore evaluated at the
capability boundary rather than embedded into Core.

### Next explicit target

Implement the deterministic reference DecisionProvider through the already
validated Codex execution bridge.

The mission is deliberately limited to:
- `core/deterministic_decision_provider.py`
- `tests/test_deterministic_decision_provider.py`

It must remain dependency-free, must not alter the existing DecisionProvider
contract, must not integrate Jev or any cloud API, and must return only
DecisionResult values rather than executing actions.

After the normal closure gate, run:

```bash
git pull --ff-only origin feature/semantic-model
bash scripts/close_work_block.sh
PYTHONPATH=. python scripts/run_codex_deterministic_provider_mission.py --approve
```

Inspect the implementation and focused tests before committing. Then run the
complete suite and close the block.


## Next explicit target

Do not jump directly to a broad autonomous coding task. The next useful experiment is a **bounded production-code mission** with one small allowed production file, at least one protected Core/canon path, explicit acceptance criteria and verification commands, and the same bridge/transport path. That will test whether the authority and scope contract remains effective when Codex is permitted to modify real implementation code.

## Codex Execution Bridge — VERIFIED GREEN

The first runtime bridge is implemented:
- `core/codex_execution_bridge.py` provides a provider-neutral `CodexTransport` protocol and `CodexExecutionBridge`;
- `docs/CODEX_EXECUTION_BRIDGE.md` defines the bridge boundary;
- `tests/test_codex_execution_bridge.py` covers approval gating, transport invocation, malformed results, digest mismatch and scope violations.

Bridge behavior:
- no human approval → return `blocked` without invoking the transport;
- approved task → call the transport;
- returned result must be a `CodexTaskResult` matching task identity/digest and staying inside allowed scope;
- the bridge does not know how a concrete Codex environment is invoked.

Verification:
- complete suite: **601 passed, 54 subtests passed in 16.60s**;
- checkpoint: `20c9e68`;
- bridge and task authority changes are green together.

### Explicit next target

The original first-smoke target is superseded by the live CLI parser finding documented above. The current next step is to pull the transport correction, run the complete closure suite, and rerun the read-only smoke. Once that is green, proceed to a tightly bounded `workspace-write` implementation mission through the existing `CodexTask` + `CodexExecutionBridge` path.

## Continuity rule
If the original ChatGPT conversation becomes unavailable, open a new chat and tell the assistant:

“Work on repository `Mareta3rd/illo-and-killo-p-blico-`, branch `feature/semantic-model`. Read `docs/AI_HANDOFF.md` first. Treat it as the durable project state and continue from its current checkpoint. Arsa & Pisha are current canon; Illo & Killo and earlier Xoxo material are historical only. Verify repository state and tests before changing anything. Do not discard historical creative material: use it as an explicitly non-canonical development corpus for learning and comparison.”

This handoff is the durable continuity document. It must be updated whenever a major architectural, experimental, or canon-level state change is made.