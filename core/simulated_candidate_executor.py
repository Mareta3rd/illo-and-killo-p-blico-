"""Deterministic in-memory candidate executor for boundary tests.

SimulatedCandidateExecutor returns pre-declared candidates without
calling external providers or generators. It respects iteration count,
previous candidate, and prompt but does not create new content.
"""

from __future__ import annotations

import copy
from dataclasses import dataclass
from typing import Any, Sequence

from .candidate_executor import (
    Candidate,
    CandidateExecutorProtocol,
    InvalidCandidateError,
    ProviderCandidateError,
)
from .prompt_compiler import CompiledPrompt


@dataclass(frozen=True)
class SimulatedCandidateExecutor:
    """Return pre-declared candidates in sequence without provider calls."""

    candidates: tuple[Candidate, ...]
    """Sequence of candidates indexed by iteration (0=iteration 1, etc)."""

    def execute(
        self,
        prompt: CompiledPrompt,
        iteration: int,
        previous: Candidate | None,
    ) -> Candidate:
        """Return the next candidate from the predetermined sequence.

        Args:
            prompt: CompiledPrompt (stored for audit, not modified)
            iteration: Loop iteration (1-indexed)
            previous: Previous candidate (stored for audit, not used)

        Returns:
            Candidate dict from the pre-declared sequence (defensive copy)

        Raises:
            InvalidCandidateError: If sequence exhausted or index invalid
            ProviderCandidateError: If candidate value is invalid type
        """
        if iteration < 1 or iteration > len(self.candidates):
            raise InvalidCandidateError(
                f"simulated executor: iteration {iteration} out of range "
                f"[1, {len(self.candidates)}]"
            )

        candidate = self.candidates[iteration - 1]
        if not isinstance(candidate, dict):
            raise ProviderCandidateError(
                f"simulated executor: candidate at iteration {iteration} "
                f"is not a dict (got {type(candidate).__name__})"
            )

        # Return a deep defensive copy to prevent mutation of stored candidates
        return copy.deepcopy(candidate)

    # Support callable interface for backward compatibility
    def __call__(
        self,
        prompt: CompiledPrompt,
        iteration: int,
        previous: Candidate | None,
    ) -> Candidate:
        """Make executor callable like Executor type alias."""
        return self.execute(prompt, iteration, previous)


def build_simulated_executor(
    candidates: Sequence[Candidate],
) -> SimulatedCandidateExecutor:
    """Build a deterministic executor from a sequence of candidates.

    Args:
        candidates: Sequence of candidate dicts to return in iteration order

    Returns:
        SimulatedCandidateExecutor ready for run_vertical_slice

    Raises:
        TypeError: If any item is not a dict
        ValueError: If candidates sequence is empty
    """
    if not candidates:
        raise ValueError("simulated executor requires at least one candidate")

    normalized: list[Candidate] = []
    for i, candidate in enumerate(candidates):
        if not isinstance(candidate, dict):
            raise TypeError(
                f"simulated executor: candidate {i} is not a dict "
                f"(got {type(candidate).__name__})"
            )
        normalized.append(copy.deepcopy(candidate))  # defensive deep copy

    return SimulatedCandidateExecutor(tuple(normalized))


__all__ = ["SimulatedCandidateExecutor", "build_simulated_executor"]
