#!/usr/bin/env python3
"""Rename the ten historical corpus images using reviewed semantic names.

The original numeric generation ID is preserved in every destination filename.
The script is deliberately explicit and fails before making changes when the
expected source files are missing or a destination already exists.

Run without arguments for a dry run; use --apply to perform the renames.
"""

from __future__ import annotations

import argparse
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
CORPUS = ROOT / "history" / "creative-corpus"

RENAMES = {
    "arsa-pisha-origins": {
        "1788957758584.png": "APO-001_pesca-barca_1788957758584.png",
        "1788957758616.png": "APO-002_portada-parodia-sierra-nevada_1788957758616.png",
        "1788957758655.png": "APO-003_guitarra-baile_1788957758655.png",
        "1788957758694.png": "APO-004_vespino-fuga_1788957758694.png",
        "1788957758729.png": "APO-005_jamon-golpe_1788957758729.png",
        "1788957758750.png": "APO-006_guitarra-persecucion_1788957758750.png",
        "1788957758780.png": "APO-007_guitarra-confrontacion_1788957758780.png",
        "1788957758814.png": "APO-008_titulo-personajes-variante_1788957758814.png",
    },
    "illo-and-killo": {
        "1788958159854.png": "KAI-001_espetos-en-barca_1788958159854.png",
        "1788958159883.png": "KAI-002_jamon-mosquito_1788958159883.png",
    },
}


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--apply",
        action="store_true",
        help="perform the renames; otherwise only print the plan",
    )
    args = parser.parse_args()

    operations: list[tuple[Path, Path]] = []

    for folder_name, mapping in RENAMES.items():
        folder = CORPUS / folder_name
        if not folder.is_dir():
            raise SystemExit(f"Missing corpus directory: {folder}")
        for source_name, destination_name in mapping.items():
            source = folder / source_name
            destination = folder / destination_name
            if not source.exists():
                if destination.exists():
                    continue
                raise SystemExit(f"Missing source image: {source}")
            if destination.exists():
                raise SystemExit(f"Destination already exists: {destination}")
            operations.append((source, destination))

    print(f"Historical corpus rename plan: {len(operations)} file(s)")
    for source, destination in operations:
        print(f"  {source.name} -> {destination.name}")

    if not args.apply:
        print("Dry run only. Re-run with --apply to perform the renames.")
        return 0

    for source, destination in operations:
        source.rename(destination)

    print("Rename complete.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
