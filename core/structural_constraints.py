"""Load deterministic structural constraints without inference."""

from __future__ import annotations

from pathlib import Path
from typing import Any

import yaml


def load_structural_constraint(
    root: str | Path,
    catalog: str,
    entry: str,
    invariant: str,
) -> tuple[tuple[str, ...], tuple[tuple[tuple[str, ...], Any], ...]] | None:
    """Return required paths and expected path/value pairs for one invariant."""
    root = Path(root).resolve()
    path = root / "data" / "structural_constraints.yaml"
    with path.open("r", encoding="utf-8") as handle:
        raw = yaml.safe_load(handle) or {}

    if not isinstance(raw, dict):
        return None
    structural = raw.get("structural")
    if not isinstance(structural, dict):
        return None
    catalog_data = structural.get(catalog)
    if not isinstance(catalog_data, dict):
        return None
    entry_data = catalog_data.get(entry)
    if not isinstance(entry_data, dict):
        return None
    invariant_data = entry_data.get(invariant)
    if not isinstance(invariant_data, dict):
        return None

    required_paths_raw = invariant_data.get("required_paths", [])
    expected_raw = invariant_data.get("expected", [])
    required_paths: list[tuple[str, ...]] = []
    expected: list[tuple[tuple[str, ...], Any]] = []

    if required_paths_raw is None:
        required_paths_raw = []
    if expected_raw is None:
        expected_raw = []

    if not isinstance(required_paths_raw, list) or not isinstance(expected_raw, list):
        return None

    for item in required_paths_raw:
        if not isinstance(item, list) or not all(isinstance(part, str) for part in item):
            return None
        required_paths.append(tuple(item))

    for item in expected_raw:
        if not isinstance(item, dict):
            return None
        item_path = item.get("path")
        if not isinstance(item_path, list) or not all(isinstance(part, str) for part in item_path):
            return None
        if "value" not in item:
            return None
        expected.append((tuple(item_path), item["value"]))

    if not required_paths and not expected:
        return None

    return tuple(required_paths), tuple(expected)
