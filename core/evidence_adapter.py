"""Translate tri-state Evidence claims into explicit evaluator checks.

The adapter is deliberately narrow: Evidence remains read-only and owns
claim state; the evaluator remains responsible for deciding what to do with
those checks. No repository knowledge is changed or inferred here.
"""

from __future__ import annotations

from typing import Any, Mapping

from .evidence_boundary import evaluate_evidence_claim
from .evidence_state import EvidenceClaim


def claims_to_checks(
    claims: Mapping[str, EvidenceClaim],
) -> dict[str, dict[str, Any]]:
    """Convert explicit Evidence claims into evaluator-compatible checks.

    The mapping is loss-minimising: the shared evidence boundary determines
    the evaluator decision, while the original claim state and sources remain
    available for audit.
    """

    checks: dict[str, dict[str, Any]] = {}
    for name, claim in claims.items():
        if not isinstance(claim, EvidenceClaim):
            raise TypeError(f"Evidence claim for '{name}' is not an EvidenceClaim")

        evaluation = evaluate_evidence_claim(claim)
        checks[str(name)] = {
            "decision": evaluation.decision,
            "reason": evaluation.reason,
            "claim": claim.claim,
            "supporting_sources": claim.supporting_sources,
            "contradicting_sources": claim.contradicting_sources,
        }

    return checks
