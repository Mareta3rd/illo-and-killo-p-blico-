# Illo & Killo — Copilot repository guardrails

These instructions apply to Copilot work in this repository.

## Architecture

- External AI providers are evidence sources only.
- Core owns canonical claims, evidence contracts, frozen snapshots, evaluation, routing, audit, regression detection, orchestration, and final decisions.
- Provider-specific behavior belongs behind adapters/transports/gateways.
- Never allow provider verdicts to become Core decisions implicitly.

## Evidence states

`CONFIRMED`, `UNKNOWN`, and `CONTRADICTED` are observations. Preserve them exactly unless an existing Core evaluator explicitly transforms them under its declared policy.

## Canon and claims

- Gag 001 · Jamón is the only currently approved canonical visual gag for this phase.
- Do not promote Gag 002 to canon merely to enlarge the test corpus.
- Do not invent claim aliases or rewrite canonical claim meaning to satisfy an existing validator.
- Canonical claim metadata such as narrative role and visual salience is context, not evidence.

## Testing

- Fix failing tests before advancing.
- Prefer focused tests first, then run:
  `python -m unittest discover -s tests -p "test_*.py"`
- Never delete or weaken a regression test solely to obtain a green suite.
- Diagnose failures from the actual traceback and source contract.

## Security

- Never print, commit, or document provider API keys.
- Use environment secrets for Gemini/OpenAI credentials.
- Do not add secrets to fixtures, examples, logs, or documentation.

## Continuity

Read `docs/AI_HANDOFF.md` and `docs/SESSION_HANDOFF.md` when the task involves project architecture, provider integration, semantic-model continuity, or canon.
