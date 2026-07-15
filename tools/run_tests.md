# Run tests

## Objective
Execute the system tests against a piece, prompt, workflow, or data set and return a structured result.

## Inputs
- target_type
- target_name
- target_content
- related_assets
- destination
- support

## Steps
1. Load the relevant tests from `docs/TESTS.md`.
2. Select the tests that apply to the target.
3. Evaluate the target against each test.
4. Assign a result to each test.
5. Summarize risks, blockers, and strengths.
6. Return the overall status and recommended next action.

## Output
- overall_status
- per_test_results
- strengths
- weaknesses
- blockers
- next_action

## Rule
The runner must not modify canon; it only evaluates against it.
