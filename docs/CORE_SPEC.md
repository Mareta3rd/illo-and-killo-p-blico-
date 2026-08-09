# Core Spec

## Purpose
Define the implementation contract for SinergYa Core v0.1.

## Scope
SinergYa Core v0.1 must support a minimal end-to-end flow from idea to validated prompt-ready output using the existing repository knowledge.

## Must have
- Load repository knowledge from Markdown and YAML.
- Route an idea to the correct development path.
- Build a structured brief.
- Compile a final production prompt.
- Validate the result against canon and production rules.
- Run the test framework.
- Record metrics and decision log entries.
- Allow escalation to human review when a canon-affecting decision is needed.

## Must not have yet
- Full graphical interface.
- Complex multi-user permissions.
- Automatic canon mutation without human approval.
- Unbounded autonomous loops.
- Expansion beyond the first content base and core orchestration.

## Minimal pipeline
1. Idea
2. Route recommendation
3. Brief generation
4. Prompt compilation
5. Validation
6. Tests
7. Metrics update
8. Decision log update if needed

## External dependencies
- GitHub repository content
- YAML data files
- Markdown documentation
- OpenAI model access for reasoning and generation

## Human escalation points
- Canon changes
- New invariants
- New characters
- New collections with strategic impact
- Conflicting routes or unresolved validation failures

## v0.1 success criteria
The system can process a real Illo & Killo idea from entry to a structured validated output without rewriting the canon or losing the project’s rules.
