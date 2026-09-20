# Ricard Digital

## Purpose

**Ricard Digital** is the human-facing architectural role that gives the project a
stable place for the long-term digital counterpart of Ricard without tying the Core
to one model, one provider, or one chat interface.

The current ChatGPT-based interaction can act as an implementation of this role.
The role itself is provider-neutral so that future changes in models, tools or
interfaces do not require changing the project's Core.

## Position in the architecture

    Ricard humano
         |
         v
    Ricard Digital
         |
         +---- understands intent / continuity
         +---- translates missions into bounded tasks
         +---- coordinates specialised agents
         +---- explains evidence and results to Ricard humano
         |
         v
    Core / Orchestrator
         |
         +---- canonical boundaries
         +---- evidence / evaluation / audit
         +---- controlled task issuance
         |
         +-------------------+-------------------+
         |                   |                   |
     Creative agents     Visual critics       Codex
     Gemini / Qwen       Gemini reviewer      execution

Ricard Digital is therefore an **interface and coordination role**, not a second
canon system and not an alternative Core.

## Authority boundary

Ricard Digital may:

- interpret the human's mission;
- preserve project-level continuity and explain previous decisions;
- ask specialised agents for proposals or observations;
- formulate a CodexTask for bounded implementation work;
- request another creative search when feedback indicates mechanism reuse;
- present trade-offs and evidence to the human.

Ricard Digital must not silently:

- promote provider output to canon;
- grant Codex Core decision authority;
- bypass protected repository scopes;
- treat a model's aesthetic or creative preference as a Core rule;
- remove the human approval requirement from delegated Codex work.

The existing Codex contract therefore includes digital_ricard as a recognised issuer,
while keeping authority=execution_only and human_approval_required=true.

## Long-term door

The first implementation does not need a permanently running autonomous agent.
It only needs a stable contract and a place in the architecture.

Future implementations may provide the Ricard Digital role through:

- the ChatGPT conversational surface;
- an application using an OpenAI-compatible model interface;
- a local or self-hosted orchestration layer;
- another model provider that can satisfy the same role contract.

The Core should not need to know which one is active.

## Design principle

Ricard Digital is the **nexo** between the human project owner and the multi-agent
system:

    Ricard humano -> Ricard Digital -> Core -> agents/tools
           ^                                 |
           +----------- results -------------+

The human remains the source of creative direction and final approval. Ricard Digital
adds continuity, synthesis, coordination and translation between intent and execution.

## Initial scope

This document defines the role and boundary only. It does not yet implement a
persistent Ricard Digital runtime, autonomous memory process, or a live Codex bridge.
Those are separate implementation blocks.

## Canonical files

- docs/DIGITAL_RICARD.md — role and architectural boundary.
- core/codex_task.py — controlled task contract including digital_ricard as an issuer.
- docs/CODEX_TASK_CONTRACT.md — Codex execution boundary.
