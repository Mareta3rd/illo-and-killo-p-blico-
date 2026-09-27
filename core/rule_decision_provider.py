"""Provider-neutral local rule implementation of the bounded DecisionProvider capability.

Rules are injected by the caller. They may derive a bounded value from request
context, but they never execute actions or redefine Core semantics.
"""

from __future__ import annotations

from collections.abc import Callable, Mapping

from core.decision_provider import DecisionRequest, DecisionResult, DecisionValue


DecisionRule = Callable[[DecisionRequest], DecisionValue]


class RuleDecisionProvider:
    """Evaluate caller-supplied decision rules against DecisionRequest values."""

    def __init__(
        self,
        rules: Mapping[str, DecisionRule],
        *,
        provider_id: str = "rules",
        confidence: float | None = None,
    ) -> None:
        self._rules = dict(rules)
        self._provider_id = provider_id
        self._confidence = confidence

        for question_id, rule in self._rules.items():
            if not isinstance(question_id, str) or not question_id.strip():
                raise ValueError("rule question IDs must be non-empty strings")
            if not callable(rule):
                raise TypeError("rules must contain callable decision rules")

    def decide(self, request: DecisionRequest) -> DecisionResult:
        try:
            rule = self._rules[request.question_id]
        except KeyError as exc:
            raise ValueError(
                f"no rule configured for question_id {request.question_id!r}"
            ) from exc

        value = rule(request)
        result = DecisionResult(
            question_id=request.question_id,
            kind=request.kind,
            value=value,
            provider_id=self._provider_id,
            confidence=self._confidence,
        )
        result.validate_for(request)
        return result
