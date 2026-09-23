"""A small provider-neutral source of predeclared decision answers."""

from __future__ import annotations

from typing import Mapping

from core.decision_provider import DecisionRequest, DecisionResult


class DeterministicDecisionProvider:
    """Return configured values for question IDs without executing actions."""

    def __init__(
        self,
        answers: Mapping[str, bool | str | float],
        provider_id: str = "deterministic",
        confidence: float | None = None,
    ) -> None:
        self._answers = dict(answers)
        self._provider_id = provider_id
        self._confidence = confidence

    def decide(self, request: DecisionRequest) -> DecisionResult:
        try:
            value = self._answers[request.question_id]
        except KeyError as exc:
            raise ValueError(f"no deterministic answer for question_id {request.question_id!r}") from exc

        result = DecisionResult(
            question_id=request.question_id,
            kind=request.kind,
            value=value,
            provider_id=self._provider_id,
            confidence=self._confidence,
        )
        result.validate_for(request)
        return result
