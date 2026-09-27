import json

import pytest

from core.decision_benchmark import (
    DecisionBenchmarkCase,
    load_decision_benchmark_fixtures,
    run_decision_benchmark,
)
from core.decision_provider import (
    DecisionProviderIncompatibilityError,
    DecisionRequest,
    DecisionResult,
)
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



def test_benchmark_distinguishes_provider_incompatibility_from_other_failures():
    request = DecisionRequest("q", "score", {}, "Rate?")

    class IncompatibleProvider:
        def decide(self, request):
            raise DecisionProviderIncompatibilityError("missing provider mapping")

    class RuntimeFailureProvider:
        def decide(self, request):
            raise RuntimeError("network unavailable")

    incompatible = run_decision_benchmark(
        IncompatibleProvider(), [DecisionBenchmarkCase("gap", request, expected_failure=False, expected_value=0.5)]
    ).results[0].observations[0]
    runtime = run_decision_benchmark(
        RuntimeFailureProvider(), [DecisionBenchmarkCase("failure", request, expected_failure=True)]
    ).results[0].observations[0]

    assert incompatible.status == "provider_incompatibility"
    assert incompatible.contract_valid is False
    assert runtime.status == "execution_failure"


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


def test_repository_v1_fixtures_are_the_benchmark_case_source():
    from pathlib import Path

    fixture_path = Path(__file__).resolve().parents[1] / "data" / "decision_benchmark_fixtures.json"
    fixture_set = json.loads(fixture_path.read_text(encoding="utf-8"))
    cases = load_decision_benchmark_fixtures()

    assert [case.case_id for case in cases] == [item["case_id"] for item in fixture_set["fixtures"]]
    roles = {item["case_id"]: item["benchmark_role"] for item in fixture_set["fixtures"]}
    assert {case_id for case_id, role in roles.items() if role == "objective"} == {
        "boolean-review-escalation", "choice-confirmed-route", "score-evidence-coverage"
    }
    assert {case_id for case_id, role in roles.items() if role == "harness_control"} == {
        "control-missing-provider-answer"
    }
    assert all(not case.expected_failure for case in cases[:3])
    assert cases[3].expected_failure
    assert [case.request.kind for case in cases] == ["boolean", "choice", "score", "boolean"]


def test_fixture_loader_rejects_malformed_entries(tmp_path):
    fixture_path = tmp_path / "fixtures.json"
    from pathlib import Path
    repository_fixture = Path(__file__).resolve().parents[1] / "data" / "decision_benchmark_fixtures.json"
    fixture_set = json.loads(repository_fixture.read_text(encoding="utf-8"))
    del fixture_set["fixtures"][0]["request"]["question"]
    fixture_path.write_text(json.dumps(fixture_set), encoding="utf-8")

    with pytest.raises(ValueError, match="request has invalid fields"):
        load_decision_benchmark_fixtures(fixture_path)
