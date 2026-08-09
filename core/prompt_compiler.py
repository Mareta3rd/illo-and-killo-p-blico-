"""Compile a validated Core result into a deterministic execution prompt.

The compiler does not generate creative content, call external models, mutate
canon, or execute loops. It transforms an already validated pipeline result
into an explicit, auditable task for a later execution layer.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .pipeline import PipelineResult


@dataclass(frozen=True)
class CompiledPrompt:
    """Immutable prompt package ready for a later model/execution layer."""

    route: str
    task: str
    constraints: tuple[str, ...]
    checks: tuple[str, ...]
    context_summary: tuple[str, ...]

    def render(self) -> str:
        """Render the package as plain text without adding creative content."""
        sections = [
            f"ROUTE: {self.route}",
            "TASK:",
            self.task,
            "CONSTRAINTS:",
            *[f"- {item}" for item in self.constraints],
            "CHECKS BEFORE OUTPUT:",
            *[f"- {item}" for item in self.checks],
            "CONTEXT:",
            *[f"- {item}" for item in self.context_summary],
        ]
        return "\n".join(sections)


_ROUTE_TASKS = {
    "character": "Develop the requested character task while preserving canonical identity and invariants.",
    "gag": "Develop the requested gag while preserving canonical characters, established invariants, and explicit intentions.",
    "parody": "Develop the requested parody while adapting the reference to the requested context without copying its setting or identity when the brief requires transformation.",
    "merchandising": "Develop the requested merchandising task while preserving canonical visual identity and production constraints.",
    "3d": "Develop the requested 3D task while preserving canonical identity and declared asset constraints.",
    "general": "Develop the requested task only within the validated scope and repository canon.",
}


_BASE_CONSTRAINTS = (
    "Do not invent or silently alter canon.",
    "Do not add recurring assets without an explicit narrative or comic intention.",
    "Preserve fixed character invariants unless a documented exception is present.",
    "Do not modify repository knowledge as part of execution.",
)

_BASE_CHECKS = (
    "Confirm that the requested route remains the active route.",
    "Confirm that all introduced elements have an explicit intention.",
    "Confirm that fixed character invariants remain satisfied.",
    "If a relevant ambiguity appears, stop and request human review rather than guessing.",
)


def compile_prompt(result: PipelineResult) -> CompiledPrompt:
    """Compile a prompt only from a completed, valid pipeline result.

    A stopped or invalid result is deliberately rejected. The compiler is not
    allowed to repair upstream decisions or infer missing information.
    """
    if result.stopped:
        raise ValueError("Cannot compile a stopped pipeline result.")
    if not result.validation.valid:
        raise ValueError("Cannot compile an invalid pipeline result.")

    data = result.context.knowledge.data
    characters = data.get("characters", {})
    character_names = tuple(sorted(characters.keys()))

    context_summary = (
        f"idea={result.context.idea}",
        f"confidence={result.context.confidence:.2f}",
        f"known_characters={','.join(character_names) if character_names else 'none'}",
        f"repository_sections={','.join(sorted(data.keys()))}",
    )

    task = _ROUTE_TASKS.get(result.context.route, _ROUTE_TASKS["general"])

    return CompiledPrompt(
        route=result.context.route,
        task=task,
        constraints=_BASE_CONSTRAINTS,
        checks=_BASE_CHECKS,
        context_summary=context_summary,
    )
