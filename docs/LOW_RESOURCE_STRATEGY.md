# Low-resource strategy

## Objective
Make SinergYa Core v0.1 viable without requiring a powerful local computer or a paid coding-agent subscription.

## Principles
- Cloud-first when local hardware is insufficient.
- Free tiers first; paid services only when they create clear value.
- Provider-neutral architecture.
- No API keys or secrets committed to the repository.
- Graceful degradation when an AI provider is unavailable.
- Human review remains available for important decisions.
- The repository remains the source of truth.

## Development layers
1. GitHub repository — knowledge, code, versioning.
2. Browser/cloud development environment — execution without depending on local hardware.
3. Free coding assistance where available.
4. Model adapters — allow different AI providers to perform the same role.
5. GitHub Actions — automated tests and checks.

## Provider abstraction
The Core should not hard-code a single AI provider.

Suggested interface:
- `reason()`
- `generate_brief()`
- `compile_prompt()`
- `evaluate()`
- `extract_learning()`

A provider can implement one or more capabilities.

## Cost control
- Prefer deterministic local code for routing, state, validation, schemas, and data handling.
- Use AI only where reasoning or generation adds value.
- Cache reusable context when possible.
- Keep loops bounded by explicit iteration limits.
- Record model/provider usage in metrics.

## Hardware independence
The Core must be usable from an older browser-capable computer through cloud services. Local GPU or high-end CPU must not be a requirement for v0.1.

## Security
- Never place API keys in Markdown, YAML, source code, commits, or prompts stored in the repository.
- Use environment variables or platform secrets.
- Keep private project knowledge separate from any public demonstration layer.
