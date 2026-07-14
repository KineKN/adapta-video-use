"""Recommend how strongly to trust a corpus Final.txt for wording vs structure.

Usage:
    python helpers/anuncios_reference_policy.py Anuncios/8116/Ad8116_Final.txt
    python helpers/anuncios_reference_policy.py --root Anuncios
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path

import anuncios_funnel_classifier as afc
import anuncios_hybrid_matrix as ahm
import anuncios_reference_audit as ara
import anuncios_rewrite_mining as arm


POLICY_TABLE = {
    ("strong", "none"): {
        "wording_weight": 0.9,
        "structure_weight": 0.95,
        "policy": "follow_closely",
        "anchor_mode": "core_spine",
        "notes": ["reference is clean and paired closely enough to the bruto"],
        "editorial_instruction": [
            "keep the commercial arc and much of the wording close to the reference",
            "still prefer the bruto when the reference would introduce obvious set noise or ASR corruption",
        ],
    },
    ("review_reference", "none"): {
        "wording_weight": 0.55,
        "structure_weight": 0.8,
        "policy": "use_with_review",
        "anchor_mode": "light_support",
        "notes": ["reference is usable but should be checked for flattening, duplication, or truncation"],
        "editorial_instruction": [
            "use the reference as support, not as literal gold",
            "borrow structure confidently, but inspect wording for flattening, duplication, or truncation",
        ],
    },
    ("weak_reference", "none"): {
        "wording_weight": 0.1,
        "structure_weight": 0.35,
        "policy": "prefer_bruto",
        "anchor_mode": "none",
        "notes": ["reference looks corrupted or commercially weaker than the bruto"],
        "editorial_instruction": [
            "treat the bruto as the main truth source",
            "use the reference only as a weak hint, not as wording or structural authority",
        ],
    },
    ("rewrite_reference", "body_reframe"): {
        "wording_weight": 0.25,
        "structure_weight": 0.85,
        "policy": "learn_structure_not_middle_wording",
        "anchor_mode": "edges_only",
        "notes": ["opening/close are still informative, but the middle was heavily reformulated"],
        "editorial_instruction": [
            "borrow the structural moves and transitions from the reference",
            "do not imitate the middle wording literally; rebuild it from the bruto",
        ],
    },
    ("rewrite_reference", "full_rebuild"): {
        "wording_weight": 0.05,
        "structure_weight": 0.55,
        "policy": "funnel_only",
        "anchor_mode": "none",
        "notes": ["pair is too far apart for wording imitation; use only high-level funnel learning"],
        "editorial_instruction": [
            "use the reference only to learn the funnel and type of promise",
            "derive wording almost entirely from the bruto",
        ],
    },
    ("rewrite_reference", "hook_swap"): {
        "wording_weight": 0.2,
        "structure_weight": 0.75,
        "policy": "alternate_hook_only",
        "anchor_mode": "hook_only",
        "notes": ["reference may teach an alternative opener, but should not dominate the whole cut"],
        "editorial_instruction": [
            "treat the reference opener as an alternate strategy, not literal truth",
            "keep the rest of the cut anchored to the bruto unless the reference clearly improves structure",
        ],
    },
    ("rewrite_reference", "cta_rewrite"): {
        "wording_weight": 0.2,
        "structure_weight": 0.75,
        "policy": "alternate_cta_only",
        "anchor_mode": "cta_only",
        "notes": ["reference may teach an alternative close, but should not dominate the whole cut"],
        "editorial_instruction": [
            "treat the reference close as an alternate CTA strategy, not literal truth",
            "keep the rest of the cut anchored to the bruto unless the reference clearly improves structure",
        ],
    },
}


FUNNEL_ADJUSTMENTS = {
    "whisper_secret": {"wording_weight_delta": 0.1, "structure_weight_delta": 0.0, "reason": "voice sensitivity is very high"},
    "authority_watch_report_back": {"wording_weight_delta": -0.05, "structure_weight_delta": 0.05, "reason": "borrowed-authority ads vary more in captured wording"},
    "summit_event": {"wording_weight_delta": -0.05, "structure_weight_delta": 0.1, "reason": "event ads often preserve chronology better than literal wording"},
    "pdf_gabarito": {"wording_weight_delta": 0.05, "structure_weight_delta": 0.0, "reason": "mechanism wording is often load-bearing and stable"},
}


def clamp(value: float) -> float:
    return max(0.0, min(1.0, round(value, 2)))


def override_follow_closely_for_funnel_ambiguity(
    *,
    base: dict,
    funnel: dict,
    wording_weight: float,
    structure_weight: float,
    notes: list[str],
    editorial_instruction: list[str],
) -> tuple[dict, float, float, list[str], list[str]]:
    if base["policy"] != "follow_closely":
        return base, wording_weight, structure_weight, notes, editorial_instruction

    confidence = funnel["funnel_confidence"]
    score_margin = funnel["score_margin"]
    hybrid_candidate = funnel["hybrid_candidate"]
    second_funnel = funnel["second_funnel"]

    should_downgrade = False
    downgrade_reason = None

    if confidence == "low":
        should_downgrade = True
        downgrade_reason = "funnel confidence is low, so wording-level trust should be reduced"
    elif confidence == "medium" and hybrid_candidate and (score_margin is None or score_margin <= 1):
        should_downgrade = True
        downgrade_reason = "funnel reading is still materially split, so wording-level trust should be reduced"

    if not should_downgrade:
        return base, wording_weight, structure_weight, notes, editorial_instruction

    adjusted = dict(POLICY_TABLE[("review_reference", "none")])
    wording_weight = clamp(min(wording_weight, 0.55))
    structure_weight = clamp(min(structure_weight, 0.85))
    notes = list(notes)
    notes.append(f"policy downgrade: {downgrade_reason}")
    if second_funnel:
        notes.append(f"policy downgrade context: second funnel candidate is {second_funnel}")
    editorial_instruction = [
        "use the reference confidently for structure, but do not treat the wording as literal gold while the funnel reading is still ambiguous",
        "prefer concrete beats that survive across both funnel interpretations",
    ]
    adjusted["notes"] = list(adjusted["notes"])
    adjusted["editorial_instruction"] = editorial_instruction
    return adjusted, wording_weight, structure_weight, notes, editorial_instruction


def override_follow_closely_for_hybrid_risk(
    *,
    base: dict,
    funnel: dict,
    wording_weight: float,
    structure_weight: float,
    notes: list[str],
    editorial_instruction: list[str],
    hybrid_risk: str | None,
) -> tuple[dict, float, float, list[str], list[str]]:
    if base["policy"] != "follow_closely":
        return base, wording_weight, structure_weight, notes, editorial_instruction
    if hybrid_risk != "dangerous_overlap":
        return base, wording_weight, structure_weight, notes, editorial_instruction

    adjusted = dict(POLICY_TABLE[("review_reference", "none")])
    wording_weight = clamp(min(wording_weight, 0.55))
    structure_weight = clamp(min(structure_weight, 0.85))
    notes = list(notes)
    notes.append("policy downgrade: hybrid pair is classified as dangerous_overlap corpus-wide")
    if funnel["second_funnel"]:
        notes.append(f"policy downgrade context: second funnel candidate is {funnel['second_funnel']}")
    editorial_instruction = [
        "use the reference for structure and framing, but do not treat the wording as literal gold in this dangerous hybrid pair",
        "confirm the real mechanism, proof block, and CTA path from the bruto before trusting the reference wording",
    ]
    adjusted["notes"] = list(adjusted["notes"])
    adjusted["editorial_instruction"] = editorial_instruction
    return adjusted, wording_weight, structure_weight, notes, editorial_instruction


def recommend(final_path: Path) -> dict:
    audit = ara.audit_path(final_path)
    funnel = afc.classify_path(final_path)
    hybrid_risk = None
    if funnel["hybrid_candidate"] and funnel["second_funnel"]:
        hybrid_row = ahm.lookup_pair(ahm.load_matrix(), funnel["top_funnel"], funnel["second_funnel"])
        hybrid_risk = hybrid_row["risk"] if hybrid_row else None
    subtype = "none"
    if audit["label"] == "rewrite_reference":
        subtype = arm.analyze_pair(final_path).subtype

    base = POLICY_TABLE.get((audit["label"], subtype))
    if base is None:
        base = POLICY_TABLE[("strong", "none")]

    wording_weight = base["wording_weight"]
    structure_weight = base["structure_weight"]
    notes = list(base["notes"])
    editorial_instruction = list(base["editorial_instruction"])

    adjustment = FUNNEL_ADJUSTMENTS.get(funnel["top_funnel"])
    if adjustment:
        wording_weight = clamp(wording_weight + adjustment["wording_weight_delta"])
        structure_weight = clamp(structure_weight + adjustment["structure_weight_delta"])
        notes.append(f"funnel adjustment: {adjustment['reason']}")

    if funnel["top_funnel"] == "unknown":
        wording_weight = clamp(wording_weight - 0.15)
        structure_weight = clamp(structure_weight - 0.1)
        notes.append("funnel is still unknown; do not overfit to house-funnel assumptions")
        editorial_instruction.append(
            "because the funnel is not yet classified, rely more on the raw commercial arc in the bruto than on family-specific assumptions"
        )
    elif funnel["funnel_confidence"] == "low":
        wording_weight = clamp(wording_weight - 0.1)
        structure_weight = clamp(structure_weight - 0.05)
        notes.append("funnel confidence is low; family-specific guidance should be treated cautiously")
    elif funnel["funnel_confidence"] == "medium":
        notes.append("funnel confidence is medium; verify family-specific details against the actual copy")

    if funnel["hybrid_candidate"]:
        notes.append("hybrid funnel candidate: preserve the concrete details that support both the top and second funnel hypotheses")
        if hybrid_risk:
            notes.append(f"hybrid pair risk: {hybrid_risk}")

    base, wording_weight, structure_weight, notes, editorial_instruction = override_follow_closely_for_funnel_ambiguity(
        base=base,
        funnel=funnel,
        wording_weight=wording_weight,
        structure_weight=structure_weight,
        notes=notes,
        editorial_instruction=editorial_instruction,
    )
    base, wording_weight, structure_weight, notes, editorial_instruction = override_follow_closely_for_hybrid_risk(
        base=base,
        funnel=funnel,
        wording_weight=wording_weight,
        structure_weight=structure_weight,
        notes=notes,
        editorial_instruction=editorial_instruction,
        hybrid_risk=hybrid_risk,
    )

    return {
        "path": str(final_path),
        "funnel": funnel["top_funnel"],
        "funnel_confidence": funnel["funnel_confidence"],
        "funnel_second_choice": funnel["second_funnel"],
        "funnel_score_margin": funnel["score_margin"],
        "hybrid_candidate": funnel["hybrid_candidate"],
        "hybrid_risk": hybrid_risk,
        "reference_label": audit["label"],
        "rewrite_subtype": subtype,
        "policy": base["policy"],
        "anchor_mode": base["anchor_mode"],
        "wording_weight": wording_weight,
        "structure_weight": structure_weight,
        "notes": notes,
        "editorial_instruction": editorial_instruction,
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="Recommend reference-trust policy for Ad Final.txt pairs.")
    parser.add_argument("path", nargs="?", help="Specific Ad*_Final.txt path")
    parser.add_argument("--root", help="Corpus root")
    args = parser.parse_args()

    if args.path:
        print(json.dumps(recommend(Path(args.path)), ensure_ascii=False, indent=2))
        return

    if not args.root:
        raise SystemExit("Provide either a Final.txt path or --root.")

    rows = []
    for final_path in sorted(Path(args.root).glob("*/*_Final.txt")):
        rows.append(recommend(final_path))
    print(json.dumps(rows, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
