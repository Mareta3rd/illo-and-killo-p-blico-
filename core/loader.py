"""Load the structured and documentary knowledge used by SinergYa Core.

The loader is intentionally deterministic: it reads repository content but does
not interpret, mutate, or invent canon.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any

import yaml


@dataclass(frozen=True)
class RepositoryKnowledge:
    """Repository knowledge loaded without changing its source content."""

    data: dict[str, Any]
    markdown: dict[str, str]


DEFAULT_DATA_FILES = (
    "characters.yaml",
    "decisions.yaml",
    "fauna.yaml",
    "heritage.yaml",
    "metrics.yaml",
    "objects.yaml",
)


def _load_yaml(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as handle:
        value = yaml.safe_load(handle) or {}
    if not isinstance(value, dict):
        raise ValueError(f"Expected a mapping in {path}")
    return value


def _load_markdown_directory(directory: Path) -> dict[str, str]:
    if not directory.exists():
        return {}
    return {
        path.relative_to(directory).as_posix(): path.read_text(encoding="utf-8")
        for path in sorted(directory.rglob("*.md"))
    }


def load_repository(root: str | Path) -> RepositoryKnowledge:
    """Load the v0.1 repository knowledge from *root*.

    Only existing canonical data files and Markdown documentation are read.
    Missing optional data files are ignored; malformed YAML is reported.
    """

    root = Path(root).resolve()
    data_dir = root / "data"
    docs_dir = root / "docs"

    data: dict[str, Any] = {}
    for filename in DEFAULT_DATA_FILES:
        path = data_dir / filename
        if path.exists():
            data[path.stem] = _load_yaml(path)

    return RepositoryKnowledge(
        data=data,
        markdown=_load_markdown_directory(docs_dir),
    )
