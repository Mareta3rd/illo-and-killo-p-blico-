# Illo & Killo — Copilot repository guardrails

These instructions apply to Copilot work in this repository.

## Start here

- For architecture, provider integration, semantic-model continuity, or canon, read [`docs/AI_HANDOFF.md`](../docs/AI_HANDOFF.md) and [`docs/SESSION_HANDOFF.md`](../docs/SESSION_HANDOFF.md) before changing files.
- Use [`docs/INDEX.md`](../docs/INDEX.md) to find the authoritative document for creative, canon, pipeline, and validation rules; link to those documents instead of copying their contents into code or instructions.
- For semantic/evidence changes, use [`docs/SEMANTIC_ARCHITECTURE_V0_1.md`](../docs/SEMANTIC_ARCHITECTURE_V0_1.md), [`docs/EVIDENCE_SPEC.md`](../docs/EVIDENCE_SPEC.md), and [`docs/EVIDENCE_STATES.md`](../docs/EVIDENCE_STATES.md) as the contracts; use [`docs/CORE_SPEC.md`](../docs/CORE_SPEC.md) for Core ownership.
- For creative or canon changes, consult [`docs/CANON_100.md`](../docs/CANON_100.md), [`docs/BIBLIA_2_0.md`](../docs/BIBLIA_2_0.md), and the relevant document listed by the index.
- The repository custom agent [`semantic-boundary-engineer`](agents/semantic-boundary-engineer.agent.md) is the focused workflow for semantic/evidence implementation.

## Architecture

- External AI providers are evidence sources only.
- Core owns canonical claims, evidence contracts, frozen snapshots, evaluation, routing, audit, regression detection, orchestration, and final decisions.
- Provider-specific behavior belongs behind adapters/transports/gateways.
- Never allow provider verdicts to become Core decisions implicitly.
- The provider-neutral composition is `ExternalEvidenceRecord -> ProviderEvidenceObservation -> EvidenceSnapshot -> Core pipeline/evaluator`; reuse it for every provider.
- Canonical claims and registered evidence-contract invariants are distinct. Do not invent aliases, relax contracts, or force a canonical claim into an unrelated invariant taxonomy.

## Evidence states

`CONFIRMED`, `UNKNOWN`, and `CONTRADICTED` are observations. Preserve them exactly unless an existing Core evaluator explicitly transforms them under its declared policy.

## Canon and claims

- Gag 001 · Jamón is the only currently approved canonical visual gag for this phase.
- Do not promote Gag 002 to canon merely to enlarge the test corpus.
- Do not invent claim aliases or rewrite canonical claim meaning to satisfy an existing validator.
- Canonical claim metadata such as narrative role and visual salience is context, not evidence.

## Testing

- Fix failing tests before advancing.
- Prefer the narrowest relevant `tests/test_*.py` module first, then run the full suite after a meaningful integration block:
  `python -m unittest discover -s tests -p "test_*.py"`
- Use injected or fake transports and conformance tests before any real-provider experiment. Real-provider checks require the relevant environment secret and must be reported separately from automated tests.
- Do not claim a test or real-provider experiment passed unless it was actually executed; report the exact command and result.
- Never delete or weaken a regression test solely to obtain a green suite.
- Diagnose failures from the actual traceback and source contract.

## Change discipline

- Inspect `git status --short --branch` before editing and preserve unrelated user changes.
- Keep changes within the requested ownership boundary; do not stage, commit, push, or alter unrelated files unless explicitly requested.
- Prefer small, reversible changes. When a provider is involved, first use an injected/fake transport and conformance tests before any live call.
- Provider integrations must enter through the existing evidence path; never create a provider-specific Core decision path.
- Verify SDK methods, model identifiers, endpoints, and response schemas in the live environment before relying on provider-specific assumptions.

## Useful commands

- Full regression suite: `python -m unittest discover -s tests -p "test_*.py"`
- Inspect tracked scope: `git status --short --branch` and `git diff --check`
- Real provider experiments require the corresponding environment secret; never print or persist credentials.

## Security

- Never print, commit, or document provider API keys.
- Use environment secrets for Gemini/OpenAI credentials.
- Do not add secrets to fixtures, examples, logs, or documentation.

## Continuity

- The durable architecture and current checkpoint live in [`docs/AI_HANDOFF.md`](../docs/AI_HANDOFF.md); session-specific continuation is in [`docs/SESSION_HANDOFF.md`](../docs/SESSION_HANDOFF.md).
- Keep `CANON` separate from any test corpus. Gag 001 is the only approved canonical visual gag for this phase.
- Before beginning a new session, confirm the active branch and current tests; treat handoff test counts and provider results as historical until re-verified.
