"""Core-owned integration for resolving and executing bounded decisions.

The flow records provider judgments through the existing audit seam. It does
not execute any action represented by a decision.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Callable, Protocol

from core.decision_execution import DecisionExecutionRecord, execute_decision
from core.decision_provider import DecisionProvider, DecisionRequest


class DecisionProviderResolver(Protocol):
    """Resolve a provider for one bounded request."""

    def __call__(self, request: DecisionRequest) -> DecisionProvider: ...


@dataclass(frozen=True)
class DecisionFlowRecord:
    """Small immutable Core record exposing the auditable execution."""

    execution: DecisionExecutionRecord


def run_decision_flow(
    request: DecisionRequest,
    provider_resolver: DecisionProviderResolver | Callable[[DecisionRequest], DecisionProvider],
) -> DecisionFlowRecord:
    """Resolve a provider and execute its judgment through the audit seam."""
    if not isinstance(request, DecisionRequest):
        raise TypeError("request must be a DecisionRequest")
    if not callable(provider_resolver):
        raise TypeError("provider_resolver must be callable")

    provider = provider_resolver(request)
    if not callable(getattr(provider, "decide", None)):
        raise TypeError("provider_resolver must return a DecisionProvider with callable decide()")

    return DecisionFlowRecord(execution=execute_decision(provider, request))
