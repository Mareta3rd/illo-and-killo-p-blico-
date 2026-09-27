from core.decision_benchmark import load_decision_benchmark_fixtures, run_decision_benchmark
from core.decision_provider import DecisionRequest
from core.rule_decision_provider import RuleDecisionProvider


def test_rule_provider_can_reproduce_v1_objective_cases_without_external_service():
    cases = load_decision_benchmark_fixtures()[:3]
    provider = RuleDecisionProvider(
        {
            "benchmark.v1.boolean.review_escalation": lambda request: request.context["human_review_required"],
            "benchmark.v1.choice.confirmed_route": lambda request: (
                "accept" if request.context["evidence_state"] == "confirmed" else "human_review"
            ),
            "benchmark.v1.score.evidence_coverage": lambda request: (
                request.context["covered_dimensions"] / request.context["required_dimensions"]
            ),
        }
    )

    report = run_decision_benchmark(provider, cases)

    assert all(
        comparison["matches"]
        for result in report.results
        for comparison in result.expected_vs_observed
    )
    assert all(
        observation.provider_id == "rules"
        for result in report.results
        for observation in result.observations
    )
    assert all(result.repeatable for result in report.results)


def test_rule_provider_runs_only_the_requested_rule():
    calls = []

    def rule(request):
        calls.append(request.question_id)
        return request.context["answer"]

    provider = RuleDecisionProvider({"q": rule})
    result = provider.decide(DecisionRequest("q", "boolean", {"answer": True}, "Continue?"))

    assert result.value is True
    assert calls == ["q"]


def test_rule_provider_rejects_missing_rules_and_invalid_rule_values():
    import pytest

    provider = RuleDecisionProvider({"q": lambda request: "not-a-boolean"})
    with pytest.raises(ValueError, match="boolean decisions require"):
        provider.decide(DecisionRequest("q", "boolean", {}, "Continue?"))

    with pytest.raises(ValueError, match="no rule configured"):
        provider.decide(DecisionRequest("missing", "boolean", {}, "Continue?"))


def test_rule_provider_rejects_non_callable_rules():
    import pytest

    with pytest.raises(TypeError, match="callable decision rules"):
        RuleDecisionProvider({"q": True})
