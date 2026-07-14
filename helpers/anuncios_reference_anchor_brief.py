"""Extract safe reference anchors based on reference policy.

Usage:
    python helpers/anuncios_reference_anchor_brief.py Anuncios/8104/Ad8104_Final.txt
"""

from __future__ import annotations

import argparse
import json
import re
from pathlib import Path

import anuncios_reference_policy as arp
import anuncios_rewrite_mining as arm


SENTENCE_SPLIT_RE = re.compile(r"(?<=[.!?])\s+")
NOISE_ANCHOR_RE = re.compile(
    r"^(boa|nada|agora para|m[uú]sica|transcri[cç][aã]o e legendas .*|obrigado por assistir)[.!?]*$",
    re.IGNORECASE,
)
CTA_RE = re.compile(
    r"clica|clique|saiba mais|assista|resgata|resgatar|garante|entra|entre|bot[aã]o|link",
    re.IGNORECASE,
)


def split_sentences(text: str) -> list[str]:
    return [part.strip() for part in SENTENCE_SPLIT_RE.split(text) if part.strip()]


def normalize_anchor(text: str) -> str:
    normalized = re.sub(r"\s+", " ", text.strip().lower())
    normalized = re.sub(r"[.!?]+$", "", normalized)
    return normalized


def clean_anchors(anchors: list[str]) -> list[str]:
    cleaned: list[str] = []
    seen: set[str] = set()
    for anchor in anchors:
        normalized = normalize_anchor(anchor)
        if not normalized:
            continue
        if NOISE_ANCHOR_RE.match(normalized):
            continue
        if normalized in seen:
            continue
        seen.add(normalized)
        cleaned.append(anchor.strip())
    return cleaned


def select_closing_anchors(sentences: list[str], count: int) -> list[str]:
    if not sentences or count <= 0:
        return []

    cleaned_tail = clean_anchors(sentences)
    if not cleaned_tail:
        return []

    cta_candidates = [sentence for sentence in cleaned_tail if CTA_RE.search(sentence)]
    chosen: list[str] = []

    for pool in (cta_candidates, list(reversed(cleaned_tail))):
        for sentence in reversed(pool) if pool is cta_candidates else pool:
            if sentence not in chosen:
                chosen.append(sentence)
            if len(chosen) >= count:
                return list(reversed(chosen))

    return list(reversed(chosen))


def build_anchor_brief(final_path: Path) -> dict:
    policy = arp.recommend(final_path)
    final_text = final_path.read_text(encoding="utf-8", errors="ignore")
    sentences = split_sentences(final_text)

    anchors: list[str] = []
    anchor_strategy = "none"

    if policy["anchor_mode"] == "core_spine":
        anchors = sentences[: min(5, len(sentences))]
        if len(sentences) > 5:
            anchors.extend(select_closing_anchors(sentences[-4:], 2))
        anchor_strategy = "opening_plus_close_with_core_middle"
    elif policy["anchor_mode"] == "light_support":
        anchors = sentences[: min(3, len(sentences))]
        if len(sentences) > 3:
            anchors.extend(select_closing_anchors(sentences[-3:], 1))
        anchor_strategy = "light_support_only"
    elif policy["anchor_mode"] == "edges_only":
        rewrite = arm.analyze_pair(final_path)
        if sentences:
            anchors.append(sentences[0])
        if len(sentences) > 1:
            anchors.extend(select_closing_anchors(sentences[-3:], 1))
        anchor_strategy = f"{rewrite.subtype}: edges only"
    elif policy["anchor_mode"] == "hook_only" and sentences:
        anchors.append(sentences[0])
        anchor_strategy = "hook_only"
    elif policy["anchor_mode"] == "cta_only" and sentences:
        anchors.extend(select_closing_anchors(sentences[-3:], 1))
        anchor_strategy = "cta_only"
    else:
        anchor_strategy = "no_reference_anchors"

    anchors = clean_anchors(anchors)

    return {
        "path": str(final_path),
        "policy": policy["policy"],
        "anchor_mode": policy["anchor_mode"],
        "wording_weight": policy["wording_weight"],
        "structure_weight": policy["structure_weight"],
        "anchor_strategy": anchor_strategy,
        "anchors": anchors,
        "editorial_instruction": policy["editorial_instruction"],
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="Extract safe reference anchors from Final.txt.")
    parser.add_argument("path", help="Specific Ad*_Final.txt path")
    args = parser.parse_args()
    print(json.dumps(build_anchor_brief(Path(args.path)), ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
