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


def _gag_files(gags_dir: Path) -> tuple[Path, ...]:
    if not gags_dir.exists():
        return ()

    return tuple(
        sorted(
            path
            for path in gags_dir.iterdir()
            if path.is_file() and path.suffix.lower() == ".md"
        )
    )


def _gag_history(gags_dir: Path) -> tuple[str, ...]:
    return tuple(path.name for path in _gag_files(gags_dir))


def _historical_assets(gags_dir: Path) -> tuple[str, ...]:
    """Detect explicitly named assets in existing gag documentation.

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

    for path in _gag_files(gags_dir):
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
        gag_history=_gag_history(root / "gags"),
        historical_assets=_historical_assets(root / "gags"),
    )
