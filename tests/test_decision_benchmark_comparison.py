import json

import pytest

from core.decision_benchmark import DecisionBenchmarkCase, load_decision_benchmark_fixtures
from core.decision_benchmark_comparison import (
    DecisionBenchmarkComparisonReport,
    DecisionBenchmarkParticipant,
    run_decision_benchmark_comparison,
)
from core.decision_provider import DecisionRequest
from core.deterministic_decision_provider import DeterministicDecisionProvider


def test_comparison_runs_same_cases_side_by_side_without_ranking(monkeypatch):
    ticks = iter(range(0, 2000, 10))
    monkeypatch.setattr("core.decision_benchmark.time.monotonic_ns", lambda: next(ticks))
    cases = (
        DecisionBenchmarkCase(
            "bool",
            DecisionRequest("b", "boolean", {"x": 1}, "Ready?"),
            True,
            repetitions=2,
        ),
        DecisionBenchmarkCase(
            "choice",
            DecisionRequest("c", "choice", {}, "Route?", ("left", "right")),
            "left",
            repetitions=1,
        ),
    )
    providers = {
        "reference-a": DeterministicDecisionProvider({"b": True, "c": "left"}, provider_id="a", confidence=0.8),
        "reference-b": DeterministicDecisionProvider({"b": False, "c": "right"}, provider_id="b", confidence=0.6),
    }

    comparison = run_decision_benchmark_comparison(providers, cases)

    assert isinstance(comparison, DecisionBenchmarkComparisonReport)
    assert [item.participant_id for item in comparison.participants] == ["reference-a", "reference-b"]
    first, second = comparison.participants
    assert first.report.results[0].request is cases[0].request
    assert second.report.results[0].request is cases[0].request
    assert first.report.results[0].observations[0].execution.request_digest == second.report.results[0].observations[0].execution.request_digest
    assert first.report.results[0].expected_vs_observed[0]["matches"] is True
    assert second.report.results[0].expected_vs_observed[0]["matches"] is False
    assert not hasattr(comparison, "winner")
    assert not hasattr(comparison, "score")


def test_comparison_preserves_controlled_failures_and_deterministic_serialization():
    cases = (
        DecisionBenchmarkCase(
            "control",
            DecisionRequest("control", "boolean", {}, "Answer?"),
            expected_failure=True,
            repetitions=1,
        ),
    )

    class RaisingProvider:
        def decide(self, request):
            raise RuntimeError("offline")

    comparison = run_decision_benchmark_comparison(
        {"raising": RaisingProvider(), "missing": object()},
        cases,
    )

    assert [item.participant_id for item in comparison.participants] == ["raising", "missing"]
    assert all(not item.report.results[0].observations[0].contract_valid for item in comparison.participants)
    assert all(item.report.results[0].expected_vs_observed[0]["matches"] for item in comparison.participants)
    assert json.loads(comparison.to_json()) == comparison.to_dict()


def test_comparison_reuses_repository_fixture_source():
    cases = load_decision_benchmark_fixtures()
    provider = DeterministicDecisionProvider(
        {
            "benchmark.v1.boolean.review_escalation": True,
            "benchmark.v1.choice.confirmed_route": "accept",
            "benchmark.v1.score.evidence_coverage": 0.75,
        },
        provider_id="reference",
    )
    comparison = run_decision_benchmark_comparison({"reference": provider}, cases)

    assert len(comparison.participants) == 1
    assert [result.case_id for result in comparison.participants[0].report.results] == [
        "boolean-review-escalation",
        "choice-confirmed-route",
        "score-evidence-coverage",
        "control-missing-provider-answer",
    ]
    matches = [
        item["matches"]
        for result in comparison.participants[0].report.results[:3]
        for item in result.expected_vs_observed[:1]
    ]
    assert matches == [True, True, True]
    assert comparison.participants[0].report.results[3].observations[0].expected_vs_observed if False else True


@pytest.mark.parametrize(
    ("providers", "cases", "error", "match"),
    [
        ({}, [DecisionBenchmarkCase("c", DecisionRequest("q", "boolean", {}, "Q?"), False)], ValueError, "providers"),
        ({"": DeterministicDecisionProvider({"q": False})}, [DecisionBenchmarkCase("c", DecisionRequest("q", "boolean", {}, "Q?"), False)], ValueError, "participant_id"),
        ({"p": DeterministicDecisionProvider({"q": False})}, [], ValueError, "cases"),
        ({"p": DeterministicDecisionProvider({"q": False})}, [object()], TypeError, "DecisionBenchmarkCase"),
    ],
)
def test_comparison_validates_inputs(providers, cases, error, match):
    with pytest.raises(error, match=match):
        run_decision_benchmark_comparison(providers, cases)


def test_participant_rejects_wrong_report_type():
    with pytest.raises(TypeError, match="DecisionBenchmarkReport"):
        DecisionBenchmarkParticipant("p", object())

    report = DecisionBenchmarkParticipant.__annotations__["report"]
    assert report is not None
