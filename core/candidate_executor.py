"""Provider-neutral interface for deterministic candidate generation.

A Candidate Executor produces one complete candidate dict per iteration,
taking context from a compiled prompt and optionally improving from a
previous candidate. It does not:
- validate canon or invariants (Core responsibility)
- make Core decisions (accept/continue/human_review)
- invent or modify evidence
- mutate repository knowledge
- fabricate multimodal data
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Callable, Protocol, runtime_checkable

from .prompt_compiler import CompiledPrompt


Candidate = dict[str, Any]

# Type alias for raw callables (backward compatible with existing code)
CandidateExecutor = Callable[[CompiledPrompt, int, Candidate | None], Candidate]


class CandidateExecutorError(Exception):
    """Base exception for candidate executor failures."""
    pass


class InvalidCandidateError(CandidateExecutorError):
    """Candidate does not match contract (must be dict)."""
    pass


class ProviderCandidateError(CandidateExecutorError):
    """External provider failed or returned unparseable output."""
    pass


@runtime_checkable
class CandidateExecutorProtocol(Protocol):
    """Explicit interface for candidate generation implementations.

    Enables structural typing and clear documentation of contract.
    Implementations receive:
    - prompt: validated CompiledPrompt with task, constraints, checks
    - iteration: current loop iteration (1-indexed)
    - previous: previous candidate (None on first iteration)

    Return value must be:
    - dict (Candidate)
    - not None
    - not containing Core decisions
    - not containing invented evidence
    - ready for validation and Core evaluation
    """

    def execute(
        self,
        prompt: CompiledPrompt,
        iteration: int,
        previous: Candidate | None,
    ) -> Candidate:
        """Execute one candidate generation iteration.

        Args:
            prompt: Compiled and validated task prompt
            iteration: Loop iteration number (1 for first attempt)
            previous: Previous candidate dict or None if first iteration

        Returns:
            Candidate dict ready for Core validation and evaluation

        Raises:
            ProviderCandidateError: If external provider fails
            InvalidCandidateError: If output is malformed
            CandidateExecutorError: For other execution failures
        """
        ...


@dataclass(frozen=True)
class ExecutorConfig:
    """Provider-neutral configuration for a candidate executor."""

    provider: str
    """Provider name (e.g., 'gemini', 'openai', 'simulated')."""

    model: str | None = None
    """Model identifier for real providers."""

    max_retries: int = 0
    """Retries on transient provider errors (not loop iterations)."""

    timeout_seconds: int = 60
    """Request timeout for real providers."""

    extra: dict[str, Any] | None = None
    """Provider-specific configuration dict."""


__all__ = [
    "Candidate",
    "CandidateExecutor",
    "CandidateExecutorError",
    "InvalidCandidateError",
    "ProviderCandidateError",
    "CandidateExecutorProtocol",
    "ExecutorConfig",
]
