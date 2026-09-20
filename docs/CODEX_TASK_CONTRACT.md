# Codex Task Contract

## Purpose

Codex is an **execution agent** for this architecture. It may inspect, implement, repair,
improve and test the system, including generator components, prompts, adapters, evaluators,
orchestration and tooling. It does not own canon, final creative decisions or Core policy.

The contract exists so a task can be produced by a human, the Core orchestrator, a reviewer,
or another controlled agent and handed to Codex without losing scope, authority or auditability.

## Operating boundary

The intended flow is:

```text
mission
  ↓
CodexTask
  ↓
isolated execution / change set
  ↓
CodexTaskResult
  ↓
tests + diff + review
  ↓
integration decision
```

Codex may change code within `allowed_paths`. It must not modify anything under
`protected_paths`. Allowed and protected scopes are required to be disjoint.

The task contract explicitly records:

- **issuer** — human, Core, orchestrator or reviewer;
- **mode** — analysis, implementation, repair or improvement;
- **objective/context** — the actual problem to solve;
- **allowed_paths** — repository scope where changes are permitted;
- **protected_paths** — scope that the executor must not modify;
- **constraints** — architectural or creative boundaries;
- **acceptance_criteria** — observable completion conditions;
- **verification_commands** — checks the executor is expected to run;
- **base_ref/base_commit** — the repository state from which the work is defined;
- **human_approval_required** — always true for this first contract;
- **authority** — fixed to `execution_only`.

## What this enables

This is deliberately broader than “Codex fixes bugs”. A task may request:

### Generator improvement

For example:

> Analyse recent Qwen candidate failures and improve the candidate-generation
> search mechanism so it explores materially different causal mechanisms instead
> of noun substitution. Preserve the Core boundary and creative freedom.

The protected paths can prevent modification of canon while the allowed scope
includes the generator, prompt compiler and creative-feedback components.

### System improvement

A task can ask Codex to improve the machinery itself:

> Trace where visual-review guidance is lost between multimodal review and the
> next generation. Implement the smallest coherent integration and add
> regression tests.

Again, Core remains the authority; Codex changes the machinery that supports it.

### Diagnostic/audit work

`analysis` mode can be read-only in intent. The acceptance criteria can require
a report and the allowed paths can be empty. This provides a controlled way to
ask Codex to inspect a failure without granting modification authority.

### Repair work

`repair` mode is intended for a bounded failing-test or regression incident.
The task must name the failure and its verification commands rather than giving
Codex an open-ended mandate.

## Protected architectural boundaries

For the current phase, typical protected paths include:

- `data/characters.yaml`
- `docs/CANON_100.md`
- canonical claim definitions unless a human explicitly opens a canon-maintenance task;
- historical corpus classification and files;
- secrets and credential files.

These are examples of protection, not a statement that every future task must
use exactly the same path list. The actual `CodexTask` is the authority for each execution.

The task contract also fixes `authority="execution_only"` and
`human_approval_required=true`. A task result therefore cannot represent an implicit
“Core accepted this change”.

## Result contract

`CodexTaskResult` records:

- task identity and task digest;
- execution status;
- concise summary;
- changed repository files;
- tests actually run;
- blockers;
- optional diff digest.

This matters because **Codex must report what it actually did**, not what the task hoped it would do.

A result of `completed` is not itself an integration decision. The repository still requires
the normal tests, diff inspection, review and work-block closure.

## Current deliberate non-goals

This first contract does **not**:

- call the Codex service from inside the Python Core;
- auto-merge Codex changes;
- grant Codex access to canon authority;
- allow a Codex result to become a Core decision;
- invent a scoring system for implementation quality;
- make the system recursively self-modifying without review.

The contract is the control surface. A concrete execution bridge to the Codex environment
is a later block, after this contract is verified green.

## Canonical implementation

- `core/codex_task.py` — task/result types, validation, deterministic serialization and JSON contracts.
- `tests/test_codex_task.py` — contract and regression tests.
