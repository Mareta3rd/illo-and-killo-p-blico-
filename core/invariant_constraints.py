"""Load deterministic constraints for classified invariants."""

from __future__ import annotations

from pathlib import Path
from typing import Any

import yaml


def load_categorical_constraint(
    root: str | Path,
    catalog: str,
    entry: str,
    invariant: str,
) -> Any | None:
    """Return the declared categorical expected value, without inference."""
    root = Path(root).resolve()
    path = root / "data" / "invariant_constraints.yaml"
    with path.open("r", encoding="utf-8") as handle:
        raw = yaml.safe_load(handle) or {}

    if not isinstance(raw, dict):
        return None
    categorical = raw.get("categorical")
    if not isinstance(categorical, dict):
        return None
    catalog_data = categorical.get(catalog)
    if not isinstance(catalog_data, dict):
        return None
    entry_data = catalog_data.get(entry)
    if not isinstance(entry_data, dict):
        return None
    invariant_data = entry_data.get(invariant)
    if not isinstance(invariant_data, dict) or "expected" not in invariant_data:
        return None
    return invariant_data["expected"]
