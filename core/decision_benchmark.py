"""Small local benchmark harness for provider-neutral decision requests.

Benchmark observations are evidence about a provider. They do not authorize
actions or make provider-selection decisions.
"""

from __future__ import annotations

import json
import math
import time
from dataclasses import dataclass
from typing import Any, Iterable

from core.decision_execution import DecisionExecutionRecord, execute_decision
from core.decision_provider import DecisionProvider, DecisionRequest


@dataclass(frozen=True)
class DecisionBenchmarkCase:
    case_id: str
    request: DecisionRequest
    expected_value: bool | str | float | None = None
    expected_failure: bool = False
    repetitions: int = 2

    def __post_init__(self) -> None:
        if not isinstance(self.case_id, str) or not self.case_id.strip():
            raise ValueError("case_id must be a non-empty string")
        if not isinstance(self.request, DecisionRequest):
            raise TypeError("request must be a DecisionRequest")
        if isinstance(self.repetitions, bool) or not isinstance(self.repetitions, int) or self.repetitions < 1:
            raise ValueError("repetitions must be a positive integer")
        if self.expected_failure and self.expected_value is not None:
            raise ValueError("failure cases cannot specify expected_value")
        if not self.expected_failure and self.expected_value is None:
            raise ValueError("successful cases require expected_value")

    def to_dict(self) -> dict[str, Any]:
        return {
            "case_id": self.case_id,
            "request": self.request.to_dict(),
            "expected_value": self.expected_value,
            "expected_failure": self.expected_failure,
            "repetitions": self.repetitions,
        }


@dataclass(frozen=True)
class DecisionBenchmarkObservation:
    contract_valid: bool
    observed_value: bool | str | float | None
    provider_id: str | None
    model_id: str | None
    confidence: float | None
    latency_ns: int
    failure_type: str | None = None
    failure_message: str | None = None
    abstained: bool = False
    execution: DecisionExecutionRecord | None = None

    def to_dict(self) -> dict[str, Any]:
        return {
            "contract_valid": self.contract_valid,
            "observed_value": self.observed_value,
            "provider_id": self.provider_id,
            "model_id": self.model_id,
            "confidence": self.confidence,
            "latency_ns": self.latency_ns,
            "failure_type": self.failure_type,
            "failure_message": self.failure_message,
            "abstained": self.abstained,
            "request_digest": self.execution.request_digest if self.execution else None,
            "result_digest": self.execution.result_digest if self.execution else None,
        }


@dataclass(frozen=True)
class DecisionBenchmarkResult:
    case_id: str
    request: DecisionRequest
    expected_value: bool | str | float | None
    expected_failure: bool
    observations: tuple[DecisionBenchmarkObservation, ...]
    expected_vs_observed: tuple[dict[str, Any], ...]
    repeatable: bool

    def to_dict(self) -> dict[str, Any]:
        return {
            "case_id": self.case_id,
            "request": self.request.to_dict(),
            "expected_value": self.expected_value,
            "expected_failure": self.expected_failure,
            "observations": [item.to_dict() for item in self.observations],
            "expected_vs_observed": [dict(item) for item in self.expected_vs_observed],
            "repeatable": self.repeatable,
        }


@dataclass(frozen=True)
class DecisionBenchmarkReport:
    results: tuple[DecisionBenchmarkResult, ...]

    def to_dict(self) -> dict[str, Any]:
        return {"schema_version": 1, "results": [result.to_dict() for result in self.results]}

    def to_json(self) -> str:
        return json.dumps(self.to_dict(), sort_keys=True, separators=(",", ":"), ensure_ascii=False, allow_nan=False)


def run_decision_benchmark(
    provider: DecisionProvider, cases: Iterable[DecisionBenchmarkCase]
) -> DecisionBenchmarkReport:
    """Execute each case repeatedly through the existing validation boundary."""
    results: list[DecisionBenchmarkResult] = []
    for case in cases:
        observations: list[DecisionBenchmarkObservation] = []
        for _ in range(case.repetitions):
            started = time.monotonic_ns()
            raw_result: Any = None

            class CapturingProvider:
                def decide(self, request: DecisionRequest) -> Any:
                    nonlocal raw_result
                    raw_result = provider.decide(request)
                    return raw_result

            try:
                execution = execute_decision(CapturingProvider(), case.request)
            except Exception as exc:
                elapsed = time.monotonic_ns() - started
                text = str(exc)
                provider_id = getattr(raw_result, "provider_id", None)
                model_id = getattr(raw_result, "model_id", None)
                confidence = getattr(raw_result, "confidence", None)
                observed = getattr(raw_result, "value", None)
                if isinstance(observed, float) and not math.isfinite(observed):
                    observed = None
                if isinstance(confidence, float) and not math.isfinite(confidence):
                    confidence = None
                observations.append(DecisionBenchmarkObservation(
                    contract_valid=False,
                    observed_value=observed if isinstance(observed, (bool, str, int, float)) else None,
                    provider_id=provider_id if isinstance(provider_id, str) else None,
                    model_id=model_id if isinstance(model_id, str) else None,
                    confidence=confidence if isinstance(confidence, (int, float)) and not isinstance(confidence, bool) else None,
                    latency_ns=elapsed,
                    failure_type=type(exc).__name__, failure_message=text,
                    abstained="abstain" in text.lower() or "escalat" in text.lower(),
                ))
            else:
                elapsed = time.monotonic_ns() - started
                result = execution.result
                observations.append(DecisionBenchmarkObservation(
                    contract_valid=True, observed_value=result.value,
                    provider_id=result.provider_id, model_id=result.model_id,
                    confidence=result.confidence, latency_ns=elapsed, execution=execution,
                ))
        comparisons = tuple({
            "expected": None if case.expected_failure else case.expected_value,
            "observed": observation.observed_value,
            "expected_failure": case.expected_failure,
            "observed_failure": not observation.contract_valid,
            "matches": (not observation.contract_valid) if case.expected_failure else (
                observation.contract_valid and observation.observed_value == case.expected_value
            ),
        } for observation in observations)
        signatures = tuple(
            (item.contract_valid, item.observed_value, item.provider_id, item.model_id,
             item.confidence, item.failure_type, item.failure_message)
            for item in observations
        )
        results.append(DecisionBenchmarkResult(
            case_id=case.case_id, request=case.request,
            expected_value=case.expected_value, expected_failure=case.expected_failure,
            observations=tuple(observations), expected_vs_observed=comparisons,
            repeatable=len(set(signatures)) <= 1,
        ))
    return DecisionBenchmarkReport(tuple(results))
