# SinergYa Core — Loader + Router Integration

## Purpose
Define the first integration boundary between repository knowledge and deterministic routing.

## Contract
The integration layer receives an idea and repository knowledge, then returns a routing decision plus the minimum contextual information required by later stages.

It must:
- use the existing `loader` as the source of repository knowledge;
- use the existing deterministic `router` for route selection;
- preserve the distinction between facts, decisions, and intent;
- never modify canon or source data;
- expose human-review requirements rather than silently resolving ambiguity;
- remain deterministic in v0.1.

## Flow

```text
idea
  ↓
RepositoryKnowledge (loader)
  ↓
route_idea (router)
  ↓
CoreContext
  ├── idea
  ├── route
  ├── confidence
  ├── requires_human_review
  └── knowledge
```

## Output model

`CoreContext` should provide:

- `idea`: original user idea, preserved verbatim;
- `route`: selected workflow route;
- `confidence`: deterministic routing confidence;
- `requires_human_review`: explicit escalation flag;
- `knowledge`: loaded repository knowledge.

## Non-goals for v0.1

The integration layer does not:

- generate creative content;
- rewrite the idea;
- alter YAML or Markdown sources;
- validate canon compliance;
- invoke external AI providers;
- execute loops;
- compile prompts.

Those responsibilities belong to later layers.

## Invariants

1. Loading knowledge must be side-effect free.
2. Routing must be deterministic for the same input and repository state.
3. The original idea must remain recoverable without transformation.
4. Ambiguity must be visible through `requires_human_review`.
5. No integration step may silently change canon.

## Acceptance criteria

The first implementation is complete when tests demonstrate that:

- a clear gag routes to `gag`;
- a clear parody routes to `parody`;
- an ambiguous/empty idea requires human review;
- the resulting context contains loaded repository knowledge;
- source files remain unchanged after execution.
