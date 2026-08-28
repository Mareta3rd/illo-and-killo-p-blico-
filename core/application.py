"""Provider-neutral application entrypoint for one complete Core execution."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any

from .evidence_snapshot import EvidenceSnapshot
from .execution_artifact import (
    ExecutionArtifact,
    build_execution_artifact,
    write_execution_artifact,
)
from .external_evidence_adapter import ExternalEvidenceProvider
from .orchestrator import Executor, VerticalSliceResult, run_vertical_slice
from .provider_evidence_observation import (
    ProviderEvidenceObservation,
    collect_provider_observation,
)


@dataclass(frozen=True)
class ApplicationRequest:
    idea: str
    root: str | Path
    provider: ExternalEvidenceProvider
    provider_name: str
    run_id: str
    requested_claims: tuple[str, ...]
    proposal: dict[str, Any]
    executor: Executor
    model: str
    image: str
    artifact_path: str | Path | None = None
    max_iterations: int = 3


@dataclass(frozen=True)
class ApplicationResult:
    run_id: str
    observation: ProviderEvidenceObservation | None
    snapshot: EvidenceSnapshot | None
    core: VerticalSliceResult | None
    artifact: ExecutionArtifact | None
    artifact_error: str | None
    stopped: bool
    stop_reason: str | None


def run_application(request: ApplicationRequest) -> ApplicationResult:
    """Collect evidence once, run the existing Core slice once, and persist optionally."""
    _validate_request(request)

    try:
        observation, collected_snapshot = collect_provider_observation(
            str(request.root),
            request.provider,
            request.provider_name,
            request.run_id,
            request.requested_claims,
        )
    except Exception as exc:
        return ApplicationResult(
            run_id=request.run_id,
            observation=None,
            snapshot=None,
            core=None,
            artifact=None,
            artifact_error=None,
            stopped=True,
            stop_reason=f"external_evidence_provider_failed: {exc}",
        )

    core = run_vertical_slice(
        request.idea,
        request.root,
        request.executor,
        evidence_claims=collected_snapshot.claims,
        initial_candidate=request.proposal,
        max_iterations=request.max_iterations,
    )
    snapshot = core.pipeline.evidence_snapshot or collected_snapshot
    artifact = None
    artifact_error = None
    if request.artifact_path is not None:
        artifact = build_execution_artifact(
            observation,
            snapshot,
            model=request.model,
            image=request.image,
            core_decision=_core_decision(core),
        )
        try:
            write_execution_artifact(request.artifact_path, artifact)
        except OSError as exc:
            artifact = None
            artifact_error = f"unable to write execution artifact: {exc}"

    return ApplicationResult(
        run_id=request.run_id,
        observation=observation,
        snapshot=snapshot,
        core=core,
        artifact=artifact,
        artifact_error=artifact_error,
        stopped=core.stopped,
        stop_reason=core.stop_reason,
    )


def _core_decision(core: VerticalSliceResult) -> str | None:
    if core.loop is not None and core.loop.iterations:
        return core.loop.iterations[-1].evaluation.decision
    if core.pipeline.evaluation is not None:
        return core.pipeline.evaluation.evaluation.decision
    return None


def _validate_request(request: ApplicationRequest) -> None:
    if not isinstance(request, ApplicationRequest):
        raise TypeError("request must be an ApplicationRequest")
    if not isinstance(request.idea, str) or not request.idea.strip():
        raise ValueError("idea is required")
    if not isinstance(request.provider_name, str) or not request.provider_name.strip():
        raise ValueError("provider_name is required")
    if not isinstance(request.run_id, str) or not request.run_id.strip():
        raise ValueError("run_id is required")
    if not isinstance(request.requested_claims, tuple) or not request.requested_claims:
        raise ValueError("requested_claims must be a non-empty tuple")
    if not all(isinstance(claim, str) and claim.strip() for claim in request.requested_claims):
        raise ValueError("requested_claims must contain non-empty strings")
    if not isinstance(request.proposal, dict):
        raise TypeError("proposal must be a dictionary")
    if not isinstance(request.model, str) or not request.model.strip():
        raise ValueError("model is required")
    if not isinstance(request.image, str) or not request.image.strip():
        raise ValueError("image is required")
    if request.max_iterations < 1:
        raise ValueError("max_iterations must be at least 1")


__all__ = ["ApplicationRequest", "ApplicationResult", "run_application"]