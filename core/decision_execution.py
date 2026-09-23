"""Auditable execution seam for bounded decision providers.

This module records a provider judgment; it never performs the action described
or implied by a decision.
"""

from __future__ import annotations

import hashlib
from dataclasses import dataclass

from core.decision_provider import (
    DecisionProvider,
    DecisionRequest,
    DecisionResult,
    serialize_decision_request,
    serialize_decision_result,
)


def _digest(serialized: str) -> str:
    return hashlib.sha256(serialized.encode("utf-8")).hexdigest()


@dataclass(frozen=True)
class DecisionExecutionRecord:
    """Immutable evidence of one validated provider decision."""

    request: DecisionRequest
    result: DecisionResult
    request_digest: str
    result_digest: str


def execute_decision(provider: DecisionProvider, request: DecisionRequest) -> DecisionExecutionRecord:
    """Ask an injected provider for a decision and record its validated result."""
    if not isinstance(request, DecisionRequest):
        raise TypeError("request must be a DecisionRequest")

    result = provider.decide(request)
    if not isinstance(result, DecisionResult):
        raise TypeError("provider must return a DecisionResult")
    result.validate_for(request)

    return DecisionExecutionRecord(
        request=request,
        result=result,
        request_digest=_digest(serialize_decision_request(request)),
        result_digest=_digest(serialize_decision_result(result)),
    )
