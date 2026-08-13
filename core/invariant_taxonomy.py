"""Load and validate the canonical invariant taxonomy registry."""

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


REQUIRED_MECHANISM_FIELDS = ("mode", "requires_evidence", "unknown_action")


def _load_registry(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as handle:
        value = yaml.safe_load(handle) or {}
    if not isinstance(value, dict):
        raise ValueError("Invariant taxonomy must be a mapping")
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
