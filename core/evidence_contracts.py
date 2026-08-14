"""Load and validate declarative contracts for evidence-backed invariants."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any

import yaml


@dataclass(frozen=True)
class EvidencePolicy:
    explicit_support_required: bool
    contradiction_allowed: bool
    unknown_action: str


@dataclass(frozen=True)
class EvidenceContract:
    catalog: str
    entry: str
    invariant: str
    family: str
    mechanism: str
    claim: str
    policy: EvidencePolicy


def _load(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as handle:
        value = yaml.safe_load(handle) or {}
    if not isinstance(value, dict):
        raise ValueError(f"Evidence contracts at {path} must be a mapping")
    return value


def load_evidence_contracts(root: str | Path) -> tuple[EvidenceContract, ...]:
    root = Path(root).resolve()
    raw = _load(root / "data" / "evidence_contracts.yaml")
    version = raw.get("version")
    if not isinstance(version, str) or not version.strip():
        raise ValueError("Evidence contract version is required")

    contracts = raw.get("contracts")
    if not isinstance(contracts, dict):
        raise ValueError("Evidence contracts mapping is required")

    results: list[EvidenceContract] = []
    for catalog, entries in contracts.items():
        if not isinstance(entries, dict):
            raise ValueError(f"Contract catalog '{catalog}' must be a mapping")
        for entry, invariants in entries.items():
            if not isinstance(invariants, dict):
                raise ValueError(f"Contract entry '{catalog}/{entry}' must be a mapping")
            for invariant, spec in invariants.items():
                if not isinstance(spec, dict):
                    raise ValueError(f"Contract '{catalog}/{entry}/{invariant}' must be a mapping")
                family = spec.get("family")
                mechanism = spec.get("mechanism")
                claim = spec.get("claim")
                policy = spec.get("evidence_policy")
                if not all(isinstance(value, str) and value.strip() for value in (family, mechanism, claim)):
                    raise ValueError(f"Contract '{catalog}/{entry}/{invariant}' needs family, mechanism and claim")
                if not isinstance(policy, dict):
                    raise ValueError(f"Contract '{catalog}/{entry}/{invariant}' needs evidence_policy")
                explicit = policy.get("explicit_support_required")
                contradiction = policy.get("contradiction_allowed")
                unknown_action = policy.get("unknown_action")
                if not isinstance(explicit, bool) or not isinstance(contradiction, bool):
                    raise ValueError(f"Contract '{catalog}/{entry}/{invariant}' has invalid evidence_policy booleans")
                if not isinstance(unknown_action, str) or not unknown_action.strip():
                    raise ValueError(f"Contract '{catalog}/{entry}/{invariant}' has invalid unknown_action")
                results.append(
                    EvidenceContract(
                        catalog=catalog,
                        entry=entry,
                        invariant=invariant,
                        family=family,
                        mechanism=mechanism,
                        claim=claim,
                        policy=EvidencePolicy(explicit, contradiction, unknown_action),
                    )
                )

    if not results:
        raise ValueError("Evidence contracts cannot be empty")
    return tuple(results)


def validate_evidence_contracts(
    root: str | Path,
    classifications: tuple[Any, ...] | None = None,
) -> tuple[str, ...]:
    """Validate exact coverage of evidence-required classifications."""
    from .invariant_taxonomy import load_invariant_classification

    root = Path(root).resolve()
    if classifications is None:
        classifications = load_invariant_classification(root)
    contracts = load_evidence_contracts(root)
    errors: list[str] = []

    expected = {
        (item.catalog, item.entry, item.invariant): item
        for item in classifications
        if item.evidence_required
    }
    seen: dict[tuple[str, str, str], EvidenceContract] = {}

    for contract in contracts:
        key = (contract.catalog, contract.entry, contract.invariant)
        if key in seen:
            errors.append(f"duplicate evidence contract: {'/'.join(key)}")
            continue
        seen[key] = contract
        item = expected.get(key)
        if item is None:
            errors.append(f"extra evidence contract: {'/'.join(key)}")
            continue
        if contract.family != item.family:
            errors.append(f"family mismatch for {'/'.join(key)}")
        if contract.mechanism != item.mechanism:
            errors.append(f"mechanism mismatch for {'/'.join(key)}")
        if contract.policy.unknown_action != "human_review":
            errors.append(f"unknown_action must be human_review: {'/'.join(key)}")
        if not contract.policy.explicit_support_required:
            errors.append(f"explicit support is required: {'/'.join(key)}")

    for key in sorted(expected.keys() - seen.keys()):
        errors.append(f"missing evidence contract: {'/'.join(key)}")

    return tuple(errors)
