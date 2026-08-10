"""Translate tri-state Evidence claims into explicit evaluator checks.

The adapter is deliberately narrow: Evidence remains read-only and owns
claim state; the evaluator remains responsible for deciding what to do with
those checks. No repository knowledge is changed or inferred here.
"""

from __future__ import annotations

from typing import Mapping, Any

from .evidence_state import EvidenceClaim, EvidenceState


_DECISIONS = {
    EvidenceState.CONFIRMED: "pass",
    EvidenceState.CONTRADICTED: "fail",
    EvidenceState.UNKNOWN: "unknown",
}


def claims_to_checks(
    claims: Mapping[str, EvidenceClaim],
) -> dict[str, dict[str, Any]]:
    """Convert explicit Evidence claims into evaluator-compatible checks.

    The mapping is loss-minimising: the evaluator decision is derived from
    the tri-state evidence, while the original claim state and sources remain
    available for audit.
    """

    checks: dict[str, dict[str, Any]] = {}
    for name, claim in claims.items():
        if not isinstance(claim, EvidenceClaim):
            raise TypeError(f"Evidence claim for '{name}' is not an EvidenceClaim")

        checks[str(name)] = {
            "decision": _DECISIONS[claim.state],
            "reason": f"evidence state: {claim.state.value}",
            "claim": claim.claim,
            "supporting_sources": claim.supporting_sources,
            "contradicting_sources": claim.contradicting_sources,
        }

    return checks
