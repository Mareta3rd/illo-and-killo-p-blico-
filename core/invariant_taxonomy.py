"""Load and validate the canonical invariant taxonomy and classification registry."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any

import yaml


@dataclass(frozen=True)
class InvariantFamily:
    name: str
    description: str
    mechanism: str
    examples: tuple[str, ...]


@dataclass(frozen=True)
class InvariantMechanism:
    name: str
    mode: str
    requires_evidence: bool
    unknown_action: str


@dataclass(frozen=True)
class InvariantTaxonomy:
    version: str
    families: dict[str, InvariantFamily]
    mechanisms: dict[str, InvariantMechanism]


@dataclass(frozen=True)
class InvariantClassification:
    catalog: str
    entry: str
    invariant: str
    family: str
    mechanism: str
    evidence_required: bool


REQUIRED_MECHANISM_FIELDS = ("mode", "requires_evidence", "unknown_action")
CATALOGS_WITH_INVARIANTS = ("characters", "objects", "fauna", "heritage")


def _load_registry(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as handle:
        value = yaml.safe_load(handle) or {}
    if not isinstance(value, dict):
        raise ValueError(f"Registry at {path} must be a mapping")
    return value


def load_invariant_taxonomy(root: str | Path) -> InvariantTaxonomy:
    """Load the canonical taxonomy and reject malformed contracts."""

    root = Path(root).resolve()
    raw = _load_registry(root / "data" / "invariant_taxonomy.yaml")

    version = raw.get("version")
    if not isinstance(version, str) or not version.strip():
        raise ValueError("Invariant taxonomy version is required")

    raw_families = raw.get("families")
    raw_mechanisms = raw.get("mechanisms")
    if not isinstance(raw_families, dict) or not raw_families:
        raise ValueError("Invariant taxonomy families are required")
    if not isinstance(raw_mechanisms, dict) or not raw_mechanisms:
        raise ValueError("Invariant taxonomy mechanisms are required")

    mechanisms: dict[str, InvariantMechanism] = {}
    for name, value in raw_mechanisms.items():
        if not isinstance(value, dict):
            raise ValueError(f"Mechanism '{name}' must be a mapping")
        missing = [field for field in REQUIRED_MECHANISM_FIELDS if field not in value]
        if missing:
            raise ValueError(f"Mechanism '{name}' missing fields: {', '.join(missing)}")
        if not isinstance(value["mode"], str):
            raise ValueError(f"Mechanism '{name}' has invalid mode")
        if not isinstance(value["requires_evidence"], bool):
            raise ValueError(f"Mechanism '{name}' has invalid requires_evidence")
        if not isinstance(value["unknown_action"], str):
            raise ValueError(f"Mechanism '{name}' has invalid unknown_action")
        mechanisms[name] = InvariantMechanism(
            name=name,
            mode=value["mode"],
            requires_evidence=value["requires_evidence"],
            unknown_action=value["unknown_action"],
        )

    families: dict[str, InvariantFamily] = {}
    for name, value in raw_families.items():
        if not isinstance(value, dict):
            raise ValueError(f"Family '{name}' must be a mapping")
        description = value.get("description")
        mechanism = value.get("mechanism")
        examples = value.get("examples", ())
        if not isinstance(description, str) or not description.strip():
            raise ValueError(f"Family '{name}' needs a description")
        if not isinstance(mechanism, str) or mechanism not in mechanisms:
            raise ValueError(f"Family '{name}' references unknown mechanism '{mechanism}'")
        if not isinstance(examples, list) or not all(isinstance(item, str) and item.strip() for item in examples):
            raise ValueError(f"Family '{name}' examples must be non-empty strings")
        families[name] = InvariantFamily(
            name=name,
            description=description,
            mechanism=mechanism,
            examples=tuple(examples),
        )

    return InvariantTaxonomy(
        version=version,
        families=families,
        mechanisms=mechanisms,
    )


def load_invariant_classification(root: str | Path) -> tuple[InvariantClassification, ...]:
    """Load the explicit invariant classification matrix without inferring entries."""

    root = Path(root).resolve()
    raw = _load_registry(root / "data" / "invariant_classification.yaml")
    version = raw.get("version")
    if not isinstance(version, str) or not version.strip():
        raise ValueError("Invariant classification version is required")

    raw_classification = raw.get("classification")
    if not isinstance(raw_classification, dict) or not raw_classification:
        raise ValueError("Invariant classification mapping is required")

    results: list[InvariantClassification] = []
    for catalog, entries in raw_classification.items():
        if catalog not in CATALOGS_WITH_INVARIANTS:
            raise ValueError(f"Unsupported invariant catalog '{catalog}'")
        if not isinstance(entries, dict):
            raise ValueError(f"Classification catalog '{catalog}' must be a mapping")
        for entry, invariants in entries.items():
            if not isinstance(invariants, dict):
                raise ValueError(f"Classification entry '{catalog}/{entry}' must be a mapping")
            for invariant, spec in invariants.items():
                if not isinstance(spec, dict):
                    raise ValueError(f"Classification '{catalog}/{entry}/{invariant}' must be a mapping")
                family = spec.get("family")
                mechanism = spec.get("mechanism")
                evidence_required = spec.get("evidence_required")
                if not isinstance(family, str) or not family.strip():
                    raise ValueError(f"Classification '{catalog}/{entry}/{invariant}' needs a family")
                if not isinstance(mechanism, str) or not mechanism.strip():
                    raise ValueError(f"Classification '{catalog}/{entry}/{invariant}' needs a mechanism")
                if not isinstance(evidence_required, bool):
                    raise ValueError(f"Classification '{catalog}/{entry}/{invariant}' needs evidence_required")
                results.append(
                    InvariantClassification(
                        catalog=catalog,
                        entry=entry,
                        invariant=invariant,
                        family=family,
                        mechanism=mechanism,
                        evidence_required=evidence_required,
                    )
                )

    if not results:
        raise ValueError("Invariant classification cannot be empty")
    return tuple(results)


def validate_invariant_classification(
    root: str | Path,
    knowledge: dict[str, Any] | None = None,
) -> tuple[str, ...]:
    """Validate that the explicit matrix covers the current canonical invariants exactly."""

    root = Path(root).resolve()
    taxonomy = load_invariant_taxonomy(root)
    classifications = load_invariant_classification(root)
    errors: list[str] = []

    seen: set[tuple[str, str, str]] = set()
    mechanisms = taxonomy.mechanisms
    families = taxonomy.families

    for item in classifications:
        key = (item.catalog, item.entry, item.invariant)
        if key in seen:
            errors.append(f"duplicate classification: {'/'.join(key)}")
            continue
        seen.add(key)

        family = families.get(item.family)
        if family is None:
            errors.append(f"unknown family: {item.family}")
            continue
        if item.mechanism != family.mechanism:
            errors.append(
                f"mechanism mismatch for {'/'.join(key)}: "
                f"family uses {family.mechanism}, classification uses {item.mechanism}"
            )
        mechanism = mechanisms.get(item.mechanism)
        if mechanism is None:
            errors.append(f"unknown mechanism: {item.mechanism}")
        elif mechanism.requires_evidence != item.evidence_required:
            errors.append(
                f"evidence mismatch for {'/'.join(key)}: "
                f"mechanism requires_evidence={mechanism.requires_evidence}, "
                f"classification says {item.evidence_required}"
            )

    if knowledge is None:
        raw = _load_registry(root / "data" / "characters.yaml")
        knowledge = {"characters": raw}
        for catalog in ("objects", "fauna", "heritage"):
            knowledge[catalog] = _load_registry(root / "data" / f"{catalog}.yaml")

    expected: set[tuple[str, str, str]] = set()
    for catalog in CATALOGS_WITH_INVARIANTS:
        entries = knowledge.get(catalog, {})
        if not isinstance(entries, dict):
            errors.append(f"catalog is not a mapping: {catalog}")
            continue
        for entry, value in entries.items():
            if not isinstance(value, dict):
                errors.append(f"catalog entry is not a mapping: {catalog}/{entry}")
                continue
            invariants = value.get("invariants", ())
            if not isinstance(invariants, list):
                errors.append(f"invariants must be a list: {catalog}/{entry}")
                continue
            for invariant in invariants:
                if not isinstance(invariant, str) or not invariant.strip():
                    errors.append(f"invalid invariant name: {catalog}/{entry}")
                    continue
                expected.add((catalog, entry, invariant))

    missing = sorted(expected - seen)
    extra = sorted(seen - expected)
    errors.extend(f"missing classification: {'/'.join(key)}" for key in missing)
    errors.extend(f"extra classification: {'/'.join(key)}" for key in extra)
    return tuple(errors)
