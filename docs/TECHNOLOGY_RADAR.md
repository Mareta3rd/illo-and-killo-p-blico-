# Technology Radar & Capability Strategy

## Purpose

The project must evolve as AI capabilities change without replacing its architectural identity every time a new model, agent runtime, decision model or computer-use product appears.

The durable rule is:

> Keep the Core stable; make capabilities and providers replaceable.

The radar is therefore a technical observation and adoption layer, not canon and not a product wishlist.

## Capability lifecycle

```
OBSERVE → INVESTIGATE → PROTOTYPE → BENCHMARK → ADOPT → MAINTAIN / DEPRECATE
```

A technology can remain in OBSERVE indefinitely. Adoption requires evidence against the project's own tasks.

## Stable architectural concepts

The project should reason about capabilities, not brands.

Examples:

- `decision` — bounded typed judgment, routing, selection, filtering or review escalation;
- `generation` — text, code, image or other artifact creation;
- `execution` — editing files, running commands, operating a workspace;
- `perception` — visual/document/environment observation;
- `orchestration` — sessions, delegation, recovery, context management and scheduling;
- `tooling` — MCP, APIs, connectors and programmatic tools;
- `computer_use` — direct interaction with desktop/browser applications;
- `evaluation` — regression, quality, safety, scope and acceptance checks.

A provider may implement several capabilities, but Core depends on the capability contract rather than the provider identity.

## Capability record

Every watched or adopted capability should be describable with:

- `id`
- `capability`
- `provider`
- `product_or_runtime`
- `status`
- `integration` (local / API / desktop / managed cloud / hybrid)
- `cost_model`
- `latency_character`
- `strengths`
- `limitations`
- `dependencies`
- `security_boundary`
- `replaceable_by`
- `last_reviewed`
- `evidence`

The record describes a capability candidate; it does not grant authority to use it.

## Current radar — September 2026

### ADOPTED / VERIFIED

#### Codex CLI execution
- Capability: execution
- Provider: OpenAI
- Product/runtime: Codex CLI `codex exec`
- Integration: local CLI
- Status: **adopted in the project**
- Evidence: first real read-only smoke completed; first write-enabled smoke completed with a one-file scope and no production changes.
- Architectural role: concrete `CodexTransport` implementation behind `CodexExecutionBridge`.

The project deliberately keeps the transport provider-neutral. A future execution provider can implement the same transport contract.

### EVALUATE / HIGH PRIORITY

#### OpenAI Agents API
- Capability: orchestration + execution + tooling
- Provider: OpenAI
- Product/runtime: Agents API
- Integration: managed API
- Status: **evaluate**
- Current documented status: **public beta**. OpenAI manages sessions, orchestration, context compaction and recovery; agents can use tools and MCP servers and run in OpenAI-hosted sandboxes or a connected compatible sandbox.
- Architectural opportunity: a possible managed runtime for the same execution/task concepts already expressed locally in this repository.
- Architectural rule: do not replace `CodexTask` / Core with provider objects. Build an adapter if and only if a benchmark proves it useful.

Source:
https://openai.com/index/introducing-the-agents-api/
https://developers.openai.com/api/docs/guides/agents-api/overview

#### TypeSafe Jev / System One
- Capability: decision
- Provider: TypeSafe AI
- Product/runtime: Jev / System One
- Integration: API
- Status: **deferred — keep adapter ready**
- Intended role: fast, structured, bounded judgments such as routing, classification, selection, scoring or escalation.
- Architectural opportunity: the useful decision semantics are already represented by the provider-neutral `DecisionProvider` contract and the internal `RuleDecisionProvider`.
- Current project state: the Jev adapter remains ready for future paid/API access, but no budget is allocated to activate it now.
- Important boundary: Jev, when eventually tested, will provide evidence for the decision capability; ordinary project code decides whether and how to act.

Source:
https://typesafe.ai/blog/introducing-system-one-models-and-jev
https://www.typesafeai.org/jev
https://www.typesafeai.org/guides/jev-api-quickstart

#### Claude / Cowork computer use
- Capability: computer_use + execution
- Provider: Anthropic
- Product/runtime: Claude / Cowork
- Integration: desktop application
- Status: **evaluate when suitable desktop hardware is available**
- Current documented status: Cowork and chat are being unified into one Claude experience. Claude can use connectors first, then browser tools, then direct screen interaction when enabled; computer use is currently beta for Pro/Max on supported desktop platforms.
- Architectural opportunity: a second execution environment for desktop workflows where API-level tools are insufficient.
- Boundary: computer-use agents remain executors/observers; project policy and acceptance remain external.

Source:
https://claude.com/blog/cowork-is-now-claude
https://support.claude.com/en/articles/14128542

### Current technology refresh — September 27, 2026

Recent releases reinforce the strategy of treating model capabilities as replaceable
resources rather than architectural dependencies. Anthropic announced Claude Opus 5.5
on September 22 with stronger coding, agentic and professional-work positioning; OpenAI's
September release notes describe GPT-6 Astra improvements in coding, research, computer
use and complex multi-step work, while ChatGPT Images 2.5 added sharper generation and
more precise editing. These are technology observations, not adoption decisions.

Open and Chinese model ecosystems are also worth watching for zero-API-cost paths. DeepSeek
V4.1-Flash has native multimodal understanding and the vendor says it is expanding open-
source inference support; GLM-5.3 is published as open weights with local-serving paths;
Kimi K3 is described by Moonshot as an open model with native vision and long context.
These models are not assumed to be free to run: local deployment moves cost from API billing
to hardware/compute, and hosted APIs may still be paid.

## PROTOTYPE / ZERO-API EXPERIMENT

### Local Qwen3.8-27B decision provider
- Capability: decision
- Provider/model: Qwen3.8-27B
- Integration target: local GGUF through an OpenAI-compatible llama.cpp server
- Status: prototype / not adopted
- Reason for selection: Qwen3.8-27B is published as an open-weight 27B native multimodal model, and a public GGUF distribution supports local inference. llama.cpp exposes JSON Schema-constrained output on its server interface, which maps cleanly to the bounded DecisionProvider contract.
- Current project implementation: core/local_structured_decision_provider.py and scripts/run_local_decision_benchmark.py.
- Constraint: local inference is not automatically free; hardware, storage and runtime resources still have a cost.
- Evidence sources checked 27 September 2026:
  - https://github.com/AlibabaCloud-Official/Qwen3.8-27B
  - https://huggingface.co/ggml-org/Qwen3.8-27B-GGUF
  - https://github.com/ggml-org/llama.cpp

This candidate is deliberately evaluated at the provider boundary. Its measured project
quality, latency, repeatability and hardware feasibility remain unknown until the local
benchmark is executed in the runtime environment.
## WATCH

#### Zero-cost / low-cost decision-provider candidates
- **Internal rules** — already available as `decision.rules`; use as the local/no-service path for objective rules.
- **DeepSeek** — watch for a future `DecisionProvider` adapter; V4.1-Flash currently supports native multimodal input and the vendor documents open-source inference work alongside paid API access.
- **GLM** — watch open-weight releases and local-serving options; GLM-5.3 is distributed with model downloads and local serving instructions.
- **Kimi** — watch K3 and later open-model releases for a future provider adapter.
- **Qwen and other open-weight ecosystems** — keep as generic provider slots; do not couple Core to any single vendor.

No candidate is treated as free merely because its weights are public. The preferred zero-budget
path is local/open-weight inference when hardware permits, existing no-cost product access when
permitted, and paid APIs only as optional experiments.

#### ChatGPT Work
- Capability: orchestration + long-running work
- Provider: OpenAI
- Integration: managed product
- Status: **watch / evaluate through actual account access**
- Use as a reference for how end-user long-running agent work may evolve, not as a dependency of Core. Review actual account availability before planning a project integration.

#### Claude Code / multi-agent workflows
- Capability: execution + delegation
- Provider: Anthropic
- Status: **watch**
- Useful as a second implementation/runtime ecosystem for comparison with Codex.

## Anti-obsolescence rules

1. Core contracts are capability-oriented, not provider-oriented.
2. Provider adapters may be replaced without changing canonical data or Core decisions.
3. A new product does not enter the architecture merely because it is newer.
4. Every adoption claim must be backed by a concrete experiment, test or documented integration.
5. Preserve a fallback path when practical: deterministic rule, alternate provider, or human review.
6. Track lifecycle events such as model retirement, API beta changes and pricing changes.
7. Prefer small adapters over provider-shaped abstractions in Core.

## Current strategic direction

The architecture is moving toward four separable planes:

```
INTENT
  ↓
DECISION PLANE
  ↓
CAPABILITY ROUTING
  ↓
EXECUTION / GENERATION / PERCEPTION
  ↓
CORE VALIDATION + AUDIT
```

A decision system may recommend a capability or provider, but the final authorization still belongs to the project contracts, scopes, tests and human approval policy where required.

## First research experiments

1. Implement the deterministic `DecisionProvider` baseline and benchmark it on stable fixtures.
2. Evaluate Jev as a drop-in `DecisionProvider` only after the baseline is green; keep vendor claims separate from project measurements.
3. Compare OpenAI Agents API with the existing `CodexTask` + `CodexExecutionBridge` lifecycle for one bounded task.
4. Compare Claude computer-use execution only after the new Windows machine is available.
5. Record model/product retirement notices in this radar instead of hard-coding assumptions into Core.

## Review cadence

Review this radar when:
- a major model/runtime is released;
- an existing model is retired;
- a new execution surface appears;
- a new provider demonstrates a materially different capability;
- a current dependency becomes unavailable or uneconomic;
- a project experiment produces evidence that changes an adoption decision.

The radar is not a promise to adopt every new technology. Its purpose is to ensure that the architecture has a safe place for useful new capabilities.
