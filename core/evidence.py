"""Repository evidence layer for SinergYa Core.

Evidence collects observable repository facts without generating,
repairing, or interpreting creative candidates.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any

import yaml


@dataclass(frozen=True)
class Evidence:
    """Immutable snapshot of repository evidence."""

    canonical_invariants: dict[str, tuple[str, ...]]
    gag_history: tuple[str, ...]
    historical_assets: tuple[str, ...]


def _load_yaml(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as handle:
        data = yaml.safe_load(handle) or {}

    if not isinstance(data, dict):
        raise ValueError(f"Expected mapping in {path}")

    return data


def _canonical_invariants(
    data: dict[str, Any],
) -> dict[str, tuple[str, ...]]:
    result: dict[str, tuple[str, ...]] = {}

    for character_id, character in data.items():
        if not isinstance(character, dict):
            continue

        invariants = character.get("invariants", [])

        if isinstance(invariants, list):
            result[str(character_id)] = tuple(
                str(item) for item in invariants
            )

    return result


def _gag_files(directory: Path) -> tuple[Path, ...]:
    if not directory.exists():
        return ()

    return tuple(
        sorted(
            path
            for path in directory.rglob("*.md")
            if path.is_file()
        )
    )


def _gag_history(root: Path) -> tuple[str, ...]:
    """Collect active and historical gag documentation without changing status.

    The returned names are repository-history evidence only. A gag appearing
    here is not thereby promoted to current canon.
    """

    files = list(_gag_files(root / "gags"))
    files.extend(_gag_files(root / "history" / "gags"))
    return tuple(sorted({path.name for path in files}))


def _historical_assets(root: Path) -> tuple[str, ...]:
    """Detect explicitly named assets in current and historical gag text.

    This is historical evidence only. It does not promote an asset
    to canon and does not infer that the asset should be reused.
    """

    known_assets = (
        "jamón",
        "chorizo",
        "guindilla",
        "tiburón",
        "espeto",
        "mosquito tigre",
    )

    found: set[str] = set()

    gag_paths = list(_gag_files(root / "gags"))
    gag_paths.extend(_gag_files(root / "history" / "gags"))

    for path in gag_paths:
        text = path.read_text(encoding="utf-8").lower()

        for asset in known_assets:
            if asset in text:
                found.add(asset)

    return tuple(sorted(found))


def build_evidence(root: Path) -> Evidence:
    """Build a read-only evidence snapshot from repository knowledge."""

    characters = _load_yaml(root / "data" / "characters.yaml")

    return Evidence(
        canonical_invariants=_canonical_invariants(characters),
        gag_history=_gag_history(root),
        historical_assets=_historical_assets(root),
    )
