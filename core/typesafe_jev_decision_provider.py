"""TypeSafe Jev adapter for the provider-neutral DecisionProvider contract.

The TypeSafe SDK is intentionally optional and imported lazily. Core only sees a
DecisionProvider, so Jev remains a replaceable capability rather than a dependency
of the semantic model.
"""

from __future__ import annotations

from collections.abc import Callable, Mapping
from typing import Any, Protocol

from core.decision_provider import DecisionProvider, DecisionRequest, DecisionResult


class _SystemOneClient(Protocol):
    def system_one(self, **kwargs: Any) -> Any: ...


def _load_sdk_question_types() -> tuple[type[Any], type[Any], type[Any]]:
    try:
        from typesafe_sdk import Choice, Noul, Score
    except ImportError as exc:
        raise RuntimeError(
            "TypeSafe Jev support requires the optional 'typesafe-sdk' package"
        ) from exc
    return Noul, Choice, Score


def _default_client_factory(model: str | None) -> _SystemOneClient:
    try:
        from typesafe_sdk import TypeSafeClient
    except ImportError as exc:
        raise RuntimeError(
            "TypeSafe Jev support requires the optional 'typesafe-sdk' package"
        ) from exc
    return TypeSafeClient(model=model) if model is not None else TypeSafeClient()


class TypeSafeJevDecisionProvider:
    """Adapt TypeSafe System One questions to DecisionProvider.

    The boolean threshold is deliberately explicit because Jev's native Noul
    answer is a probability, not a boolean. The adapter does not expose that
    probability as Core confidence; confidence remains reserved for a provider
    field that the native answer actually supplies.
    """

    provider_id = "typesafe-jev"

    def __init__(
        self,
        *,
        boolean_threshold: float,
        model: str | None = None,
        client: _SystemOneClient | None = None,
        client_factory: Callable[[str | None], _SystemOneClient] | None = None,
    ) -> None:
        if isinstance(boolean_threshold, bool) or not isinstance(boolean_threshold, (int, float)):
            raise ValueError("boolean_threshold must be a finite number between 0 and 1")
        if not 0 < boolean_threshold < 1:
            raise ValueError("boolean_threshold must be strictly between 0 and 1")
        if client is not None and client_factory is not None:
            raise ValueError("client and client_factory are mutually exclusive")

        self._boolean_threshold = float(boolean_threshold)
        self._model = model
        self._owns_client = client is None
        factory = _default_client_factory if client_factory is None else client_factory
        self._client = client if client is not None else factory(model)

    def decide(self, request: DecisionRequest) -> DecisionResult:
        Noul, Choice, Score = _load_sdk_question_types()
        question = self._build_question(request, Noul=Noul, Choice=Choice, Score=Score)

        kwargs: dict[str, Any] = {
            "state": request.context,
            "questions": {"decision": question},
        }
        if self._model is not None:
            kwargs["model"] = self._model

        response = self._client.system_one(**kwargs)
        model_id = getattr(response, "model", None)
        if model_id is not None and not isinstance(model_id, str):
            raise ValueError("TypeSafe response model metadata must be a string")

        if request.kind == "boolean":
            try:
                probability = response.nouls["decision"].noul
            except (AttributeError, KeyError, TypeError) as exc:
                raise ValueError("TypeSafe response did not contain a valid Noul answer") from exc
            if isinstance(probability, bool) or not isinstance(probability, (int, float)):
                raise ValueError("TypeSafe Noul answer must be numeric")
            value = float(probability) >= self._boolean_threshold
            confidence = None
        elif request.kind == "choice":
            try:
                answer = response.choices["decision"]
                value = answer.choice
                confidence = answer.confidence
            except (AttributeError, KeyError, TypeError) as exc:
                raise ValueError("TypeSafe response did not contain a valid Choice answer") from exc
        else:
            try:
                answer = response.scores["decision"]
                value = answer.score
                confidence = answer.confidence
            except (AttributeError, KeyError, TypeError) as exc:
                raise ValueError("TypeSafe response did not contain a valid Score answer") from exc

        result = DecisionResult(
            question_id=request.question_id,
            kind=request.kind,
            value=value,
            provider_id=self.provider_id,
            confidence=confidence,
            model_id=model_id,
        )
        result.validate_for(request)
        return result

    @staticmethod
    def _build_question(
        request: DecisionRequest,
        *,
        Noul: type[Any],
        Choice: type[Any],
        Score: type[Any],
    ) -> Any:
        if request.kind == "boolean":
            return Noul(instructions=request.question)

        if request.kind == "choice":
            assert request.choices is not None
            return Choice(
                instructions=request.question,
                criteria={choice: None for choice in request.choices},
            )

        raw_criteria = request.context.get("score_criteria")
        if not isinstance(raw_criteria, (list, tuple)) or not raw_criteria:
            raise ValueError(
                "score decisions require explicit context['score_criteria'] for TypeSafe mapping"
            )
        return Score(
            instructions=request.question,
            criteria=list(raw_criteria),
        )

    def close(self) -> None:
        """Close a client created by this adapter; leave injected clients untouched."""
        if self._owns_client:
            close = getattr(self._client, "close", None)
            if callable(close):
                close()

    def __enter__(self) -> TypeSafeJevDecisionProvider:
        return self

    def __exit__(self, exc_type: Any, exc_value: Any, traceback: Any) -> None:
        self.close()
