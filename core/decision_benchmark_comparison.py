"""Side-by-side comparison helper for provider-neutral decision benchmarks.

The comparison layer preserves each provider's observations independently. It does
not rank providers, select a production provider, route requests, or execute actions.
"""

from __future__ import annotations

import json
from dataclasses import dataclass
from typing import Any, Iterable, Mapping

from core.decision_benchmark import DecisionBenchmarkCase, DecisionBenchmarkReport, run_decision_benchmark
from core.decision_provider import DecisionProvider


@dataclass(frozen=True)
class DecisionBenchmarkParticipant:
    """One named participant and its independent benchmark report."""

    participant_id: str
    report: DecisionBenchmarkReport

    def __post_init__(self) -> None:
        if not isinstance(self.participant_id, str) or not self.participant_id.strip():
            raise ValueError("participant_id must be a non-empty string")
        if not isinstance(self.report, DecisionBenchmarkReport):
            raise TypeError("report must be a DecisionBenchmarkReport")

    def to_dict(self) -> dict[str, Any]:
        return {
            "participant_id": self.participant_id,
            "report": self.report.to_dict(),
        }


@dataclass(frozen=True)
class DecisionBenchmarkComparisonReport:
    """Provider reports preserved side-by-side without a winner or aggregate score."""

    participants: tuple[DecisionBenchmarkParticipant, ...]

    def __post_init__(self) -> None:
        if not self.participants:
            raise ValueError("comparison requires at least one participant")
        participant_ids = tuple(item.participant_id for item in self.participants)
        if len(set(participant_ids)) != len(participant_ids):
            raise ValueError("participant_id values must be unique")
        if any(not isinstance(item, DecisionBenchmarkParticipant) for item in self.participants):
            raise TypeError("participants must contain only DecisionBenchmarkParticipant values")

    def to_dict(self) -> dict[str, Any]:
        return {
            "schema_version": 1,
            "participants": [item.to_dict() for item in self.participants],
        }

    def to_json(self) -> str:
        return json.dumps(
            self.to_dict(),
            sort_keys=True,
            separators=(",", ":"),
            ensure_ascii=False,
            allow_nan=False,
        )


def run_decision_benchmark_comparison(
    providers: Mapping[str, DecisionProvider],
    cases: Iterable[DecisionBenchmarkCase],
) -> DecisionBenchmarkComparisonReport:
    """Run identical benchmark cases for each named provider and retain all observations."""
    if not isinstance(providers, Mapping) or not providers:
        raise ValueError("providers must be a non-empty mapping")

    normalized_providers: list[tuple[str, DecisionProvider]] = []
    for participant_id, provider in providers.items():
        if not isinstance(participant_id, str) or not participant_id.strip():
            raise ValueError("participant_id must be a non-empty string")
        normalized_providers.append((participant_id, provider))

    frozen_cases = tuple(cases)
    if not frozen_cases:
        raise ValueError("cases must contain at least one benchmark case")
    if any(not isinstance(case, DecisionBenchmarkCase) for case in frozen_cases):
        raise TypeError("cases must contain only DecisionBenchmarkCase values")

    return DecisionBenchmarkComparisonReport(
        tuple(
            DecisionBenchmarkParticipant(
                participant_id=participant_id,
                report=run_decision_benchmark(provider, frozen_cases),
            )
            for participant_id, provider in normalized_providers
        )
    )
