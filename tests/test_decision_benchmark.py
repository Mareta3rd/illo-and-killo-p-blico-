import json

import pytest

from core.decision_benchmark import DecisionBenchmarkCase, run_decision_benchmark
from core.decision_provider import DecisionRequest, DecisionResult
from core.deterministic_decision_provider import DeterministicDecisionProvider


def test_boolean_choice_score_record_values_metadata_and_latency(monkeypatch):
    ticks = iter(range(100, 1000, 10))
    monkeypatch.setattr("core.decision_benchmark.time.monotonic_ns", lambda: next(ticks))
    cases = (
        DecisionBenchmarkCase("bool", DecisionRequest("b", "boolean", {}, "Ready?"), True),
        DecisionBenchmarkCase("choice", DecisionRequest("c", "choice", {}, "Route?", ("left", "right")), "left"),
        DecisionBenchmarkCase("score", DecisionRequest("s", "score", {}, "Score?"), 0.75),
    )
    provider = DeterministicDecisionProvider(
        {"b": True, "c": "left", "s": 0.75}, provider_id="reference", confidence=0.8
    )

    report = run_decision_benchmark(provider, cases)

    assert [item.case_id for item in report.results] == ["bool", "choice", "score"]
    for result, expected in zip(report.results, (True, "left", 0.75)):
        assert result.observations[0].contract_valid
        assert result.expected_vs_observed[0]["expected"] == expected
        assert result.expected_vs_observed[0]["observed"] == expected
        assert result.expected_vs_observed[0]["matches"]
        assert result.observations[0].provider_id == "reference"
        assert result.observations[0].confidence == 0.8
        assert result.observations[0].latency_ns == 10


@pytest.mark.parametrize("provider", [
    type("RaisingProvider", (), {"decide": lambda self, request: (_ for _ in ()).throw(RuntimeError("offline"))})(),
    type("InvalidProvider", (), {"decide": lambda self, request: {"value": True}})(),
    type("MismatchedProvider", (), {"decide": lambda self, request: DecisionResult("other", "boolean", True, "bad")})(),
])
def test_expected_failure_and_malformed_results_are_recorded(provider):
    request = DecisionRequest("fail", "boolean", {}, "Can answer?")
    report = run_decision_benchmark(provider, [DecisionBenchmarkCase("failure", request, expected_failure=True)])

    result = report.results[0]
    assert all(not observation.contract_valid for observation in result.observations)
    assert result.expected_vs_observed[0]["observed_failure"]
    assert result.expected_vs_observed[0]["matches"]
    assert result.observations[0].failure_type


def test_repeatability_and_deterministic_json_compatible_serialization(monkeypatch):
    ticks = iter((0, 7, 10, 17))
    monkeypatch.setattr("core.decision_benchmark.time.monotonic_ns", lambda: next(ticks))
    request = DecisionRequest("q", "boolean", {"x": 1}, "Continue?")
    provider = DeterministicDecisionProvider({"q": False}, provider_id="local", confidence=0.5)
    report = run_decision_benchmark(provider, [DecisionBenchmarkCase("repeat", request, False)])

    assert report.results[0].repeatable
    state = report.to_dict()
    assert json.loads(report.to_json()) == state
    assert report.to_json() == report.to_json()
    assert [o.latency_ns for o in report.results[0].observations] == [7, 7]


def test_unexpected_failure_is_not_reported_as_success():
    request = DecisionRequest("q", "boolean", {}, "Continue?")
    report = run_decision_benchmark(object(), [DecisionBenchmarkCase("bad", request, True, repetitions=1)])

    observation = report.results[0].observations[0]
    assert not observation.contract_valid
    assert report.results[0].expected_vs_observed[0]["matches"] is False

