"""Build a corpus-wide matrix of hybrid funnel pairs and editorial risk.

Usage:
    python helpers/anuncios_hybrid_matrix.py --root Anuncios
"""

from __future__ import annotations

import argparse
import json
from collections import Counter, defaultdict
from pathlib import Path

import anuncios_reference_policy as arp


DEFAULT_MATRIX_PATH = Path(__file__).resolve().parents[1] / "Anuncios" / "hybrid_matrix.json"


def classify_pair_risk(
    *,
    count: int,
    follow_closely_count: int,
    use_with_review_count: int,
    aggressive_count: int,
    low_conf_count: int,
) -> str:
    if count == 0:
        return "unknown"

    follow_ratio = follow_closely_count / count
    review_ratio = use_with_review_count / count
    aggressive_ratio = aggressive_count / count
    low_ratio = low_conf_count / count

    if low_ratio >= 0.4 or aggressive_ratio >= 0.2 or review_ratio >= 0.7:
        return "dangerous_overlap"
    if follow_ratio >= 0.6 and low_ratio <= 0.2:
        return "benign_overlap"
    return "review_overlap"


def build_matrix(root: Path) -> list[dict]:
    grouped: dict[tuple[str, str], list[dict]] = defaultdict(list)

    for final_path in sorted(root.glob("*/*_Final.txt")):
        row = arp.recommend(final_path)
        if not row["hybrid_candidate"] or not row["funnel_second_choice"]:
            continue
        pair = tuple(sorted((row["funnel"], row["funnel_second_choice"])))
        grouped[pair].append(row)

    rows: list[dict] = []
    for pair, items in sorted(grouped.items(), key=lambda kv: len(kv[1]), reverse=True):
        policy_counts = Counter(item["policy"] for item in items)
        confidence_counts = Counter(item["funnel_confidence"] for item in items)
        directional_counts = Counter((item["funnel"], item["funnel_second_choice"]) for item in items)

        count = len(items)
        follow_closely_count = policy_counts["follow_closely"]
        use_with_review_count = policy_counts["use_with_review"]
        aggressive_count = (
            policy_counts["funnel_only"]
            + policy_counts["learn_structure_not_middle_wording"]
            + policy_counts["prefer_bruto"]
            + policy_counts["alternate_hook_only"]
            + policy_counts["alternate_cta_only"]
        )
        low_conf_count = confidence_counts["low"] + confidence_counts["unknown"]

        risk = classify_pair_risk(
            count=count,
            follow_closely_count=follow_closely_count,
            use_with_review_count=use_with_review_count,
            aggressive_count=aggressive_count,
            low_conf_count=low_conf_count,
        )

        rows.append(
            {
                "pair": list(pair),
                "count": count,
                "risk": risk,
                "policy_counts": dict(policy_counts),
                "confidence_counts": dict(confidence_counts),
                "directional_counts": {f"{a} -> {b}": c for (a, b), c in directional_counts.items()},
                "example_paths": [item["path"] for item in items[:8]],
            }
        )

    return rows


def load_matrix(path: Path | None = None) -> list[dict]:
    matrix_path = path or DEFAULT_MATRIX_PATH
    if not matrix_path.exists():
        return []
    return json.loads(matrix_path.read_text(encoding="utf-8"))


def lookup_pair(rows: list[dict], funnel_a: str | None, funnel_b: str | None) -> dict | None:
    if not funnel_a or not funnel_b:
        return None
    target = sorted((funnel_a, funnel_b))
    for row in rows:
        if sorted(row.get("pair", [])) == target:
            return row
    return None


def main() -> None:
    parser = argparse.ArgumentParser(description="Build a matrix of hybrid funnel overlaps.")
    parser.add_argument("--root", required=True, help="Corpus root")
    args = parser.parse_args()
    rows = build_matrix(Path(args.root))
    print(json.dumps(rows, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
