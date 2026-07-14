"""Mine corpus exception candidates for funnel, policy, and anchor calibration.

Usage:
    python helpers/anuncios_exception_mining.py --root Anuncios
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path

import anuncios_reference_anchor_brief as arab
import anuncios_reference_policy as arp


def mine_path(final_path: Path) -> dict:
    policy = arp.recommend(final_path)
    anchors = arab.build_anchor_brief(final_path)

    issues: list[str] = []
    priority = "low"
    if policy["funnel"] == "unknown":
        issues.append("unknown_funnel")
        priority = "high"
    if policy["funnel_confidence"] == "low":
        issues.append("low_funnel_confidence")
        priority = "high"
    if policy["hybrid_candidate"] and policy["hybrid_risk"] == "dangerous_overlap":
        issues.append("dangerous_hybrid_overlap")
        priority = "high"
    elif policy["hybrid_candidate"] and policy["hybrid_risk"] == "review_overlap":
        issues.append("review_hybrid_overlap")
        if priority != "high":
            priority = "medium"
    elif policy["hybrid_candidate"] and policy["hybrid_risk"] == "benign_overlap":
        issues.append("benign_hybrid_overlap")
    if not anchors["anchors"] and policy["anchor_mode"] != "none":
        issues.append("anchor_mode_without_surviving_anchors")
        priority = "high"

    return {
        "path": str(final_path),
        "funnel": policy["funnel"],
        "funnel_confidence": policy["funnel_confidence"],
        "funnel_second_choice": policy["funnel_second_choice"],
        "hybrid_risk": policy["hybrid_risk"],
        "reference_label": policy["reference_label"],
        "rewrite_subtype": policy["rewrite_subtype"],
        "policy": policy["policy"],
        "anchor_mode": policy["anchor_mode"],
        "anchor_count": len(anchors["anchors"]),
        "priority": priority,
        "issues": issues,
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="Mine corpus exception candidates for calibration work.")
    parser.add_argument("--root", required=True, help="Corpus root")
    args = parser.parse_args()

    rows = []
    for final_path in sorted(Path(args.root).glob("*/*_Final.txt")):
        row = mine_path(final_path)
        if row["issues"]:
            rows.append(row)
    print(json.dumps(rows, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
