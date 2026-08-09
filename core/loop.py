"""Deterministic loop engine for bounded, auditable Core iterations.

The loop is deliberately model-agnostic. It orchestrates an executor and an
evaluator, but it does not generate creative content itself, call external
models, or decide canon questions. Those responsibilities belong to later
layers. Every iteration is recorded and the loop has explicit terminal states.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Callable, Generic, Literal, TypeVar


CandidateT = TypeVar("CandidateT")

LoopDecision = Literal["continue", "accept", "human_review"]
LoopStatus = Literal["accepted", "human_review", "max_iterations"]


@dataclass(frozen=True)
class Evaluation:
    """Decision returned by the evaluator after one candidate is produced."""

    decision: LoopDecision
    reason: str


@dataclass(frozen=True)
class IterationRecord(Generic[CandidateT]):
    """Immutable audit record for one loop iteration."""

    iteration: int
    candidate: CandidateT
    evaluation: Evaluation


@dataclass(frozen=True)
class LoopResult(Generic[CandidateT]):
    """Final bounded result with the complete iteration history."""

    status: LoopStatus
    candidate: CandidateT | None
    iterations: tuple[IterationRecord[CandidateT], ...]


Executor = Callable[[int, CandidateT | None], CandidateT]
Evaluator = Callable[[CandidateT, int], Evaluation]


def run_loop(
    executor: Executor[CandidateT],
    evaluator: Evaluator[CandidateT],
    *,
    max_iterations: int = 3,
    initial_candidate: CandidateT | None = None,
) -> LoopResult[CandidateT]:
    """Run a bounded executor/evaluator loop.

    The evaluator controls whether to accept, continue, or request human
    review. A hard iteration limit always exists, so the loop cannot continue
    indefinitely. Invalid configuration is rejected before execution starts.
    """
    if max_iterations < 1:
        raise ValueError("max_iterations must be at least 1")

    history: list[IterationRecord[CandidateT]] = []
    previous = initial_candidate

    for iteration in range(1, max_iterations + 1):
        candidate = executor(iteration, previous)
        evaluation = evaluator(candidate, iteration)
        record = IterationRecord(
            iteration=iteration,
            candidate=candidate,
            evaluation=evaluation,
        )
        history.append(record)

        if evaluation.decision == "accept":
            return LoopResult("accepted", candidate, tuple(history))

        if evaluation.decision == "human_review":
            return LoopResult("human_review", candidate, tuple(history))

        if evaluation.decision != "continue":
            raise ValueError(f"Unknown loop decision: {evaluation.decision!r}")

        previous = candidate

    return LoopResult("max_iterations", history[-1].candidate, tuple(history))
