# Core Spec

## Purpose
Define the implementation contract for SinergYa Core v0.1.

## Scope
SinergYa Core v0.1 must support a minimal end-to-end flow from idea to validated prompt-ready output using the existing repository knowledge and explicit Evidence.

## Must have
- Load repository knowledge from Markdown and YAML.
- Route an idea to the correct development path.
- Build a structured brief.
- Compile a final production prompt.
- Validate the result against canon and production rules.
- Evaluate explicit Evidence before execution.
- Revalidate every loop candidate against canon and the same Evidence boundary.
- Run the test framework.
- Record metrics and decision log entries.
- Allow escalation to human review when a canon-affecting or evidence-conflicting decision is needed.

## Must not have yet
- Full graphical interface.
- Complex multi-user permissions.
- Automatic canon mutation without human approval.
- Unbounded autonomous loops.
- Expansion beyond the first content base and core orchestration.

## Minimal pipeline
1. Idea
2. Repository knowledge
3. Route recommendation
4. Brief generation
5. Canon validation
6. Evidence evaluation
7. Prompt compilation
8. Bounded execution loop
9. Candidate revalidation and Evidence evaluation on every iteration
10. Tests
11. Metrics update
12. Decision log update if needed

## Evidence boundary
The end-to-end orchestrator must receive explicit Evidence claims. Evidence is not optional at the final execution boundary.

Evidence may produce `CONFIRMED`, `CONTRADICTED`, or `UNKNOWN`. Missing or conflicting evidence must remain visible and may escalate to `HUMAN_REVIEW`; the system must not silently bypass the Evidence boundary in order to execute a candidate.

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
- Unknown or conflicting Evidence at the execution boundary

## v0.1 success criteria
The system can process a real Illo & Killo idea from entry to a structured validated output without rewriting the canon, bypassing the Evidence boundary, or losing the project’s rules.
