"""Export exception mining results directly to JSON.

Usage:
    python helpers/anuncios_exception_export.py --root Anuncios --out Anuncios/exception_mining.json
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path

import anuncios_exception_mining as aem


def main() -> None:
    parser = argparse.ArgumentParser(description="Export exception mining rows directly to JSON.")
    parser.add_argument("--root", required=True, help="Corpus root")
    parser.add_argument("--out", required=True, help="Output JSON path")
    args = parser.parse_args()

    rows = []
    for final_path in sorted(Path(args.root).glob("*/*_Final.txt")):
        row = aem.mine_path(final_path)
        if row["issues"]:
            rows.append(row)

    Path(args.out).write_text(json.dumps(rows, ensure_ascii=False, indent=2), encoding="utf-8")


if __name__ == "__main__":
    main()
