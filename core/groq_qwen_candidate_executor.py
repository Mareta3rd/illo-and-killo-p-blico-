"""Groq/Qwen-specific candidate executor implementation.

Follows provider-neutral contract: accepts CompiledPrompt + iteration + previous,
returns Candidate dict ready for Core validation and evaluation.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Callable

from .candidate_executor import (
    Candidate,
    CandidateExecutorError,
    CandidateExecutorProtocol,
    InvalidCandidateError,
    ProviderCandidateError,
)
from .groq_qwen_candidate_transport import (
    DEFAULT_GROQ_QWEN_CANDIDATE_MODEL,
    build_groq_qwen_candidate_client,
    build_groq_qwen_responses_transport,
    parse_groq_qwen_candidate,
)
from .prompt_compiler import CompiledPrompt


@dataclass(frozen=True)
class GroqQwenCandidateExecutor:
    """Groq/Qwen implementation of candidate generation via structured output.

    Wraps a transport function (provider-specific) and exposes the provider-neutral
    CandidateExecutorProtocol interface. Does not modify CompledPrompt, iteration,
    or previous candidate—passes them through to transport unchanged.
    """

    transport: Callable[[CompiledPrompt, int, Candidate | None], Candidate]
    """Provider-specific request/response function."""

    def execute(
        self,
        prompt: CompiledPrompt,
        iteration: int,
        previous: Candidate | None,
    ) -> Candidate:
        """Execute one candidate generation iteration via Groq/Qwen.

        Args:
            prompt: Compiled prompt (passed to transport unchanged)
            iteration: Loop iteration number (1-indexed)
            previous: Previous candidate dict or None

        Returns:
            Candidate dict from Groq/Qwen structured output

        Raises:
            ProviderCandidateError: If Groq/Qwen request fails
            InvalidCandidateError: If response is malformed or validation fails
            CandidateExecutorError: For other failures
        """
        if not isinstance(iteration, int) or iteration < 1:
            raise CandidateExecutorError(
                f"groq qwen candidate executor: iteration must be positive int (got {iteration})"
            )

        if previous is not None and not isinstance(previous, dict):
            raise CandidateExecutorError(
                f"groq qwen candidate executor: previous must be dict or None (got {type(previous).__name__})"
            )

        try:
            candidate = self.transport(prompt, iteration, previous)
        except (ProviderCandidateError, InvalidCandidateError):
            raise
        except Exception as exc:
            raise CandidateExecutorError(
                f"groq qwen candidate executor: unexpected error: {type(exc).__name__}"
            ) from exc

        if not isinstance(candidate, dict):
            raise InvalidCandidateError(
                f"groq qwen candidate executor: transport returned non-dict (got {type(candidate).__name__})"
            )

        return candidate

    @classmethod
    def from_client(
        cls,
        client: Any,
        *,
        model: str = DEFAULT_GROQ_QWEN_CANDIDATE_MODEL,
    ) -> "GroqQwenCandidateExecutor":
        """Build a Groq/Qwen candidate executor from an OpenAI-compatible client.

        Args:
            client: Configured OpenAI client (see build_groq_qwen_candidate_client)
            model: Model ID (must support structured outputs, default qwen3.8-27b)

        Returns:
            Executor ready for injection into run_vertical_slice()
        """
        transport = build_groq_qwen_responses_transport(client, model=model)
        return cls(transport=transport)

    def __call__(
        self,
        prompt: CompiledPrompt,
        iteration: int,
        previous: Candidate | None,
    ) -> Candidate:
        """Allow direct callable usage (backward compatible with Executor type alias)."""
        return self.execute(prompt, iteration, previous)


__all__ = ["GroqQwenCandidateExecutor"]
