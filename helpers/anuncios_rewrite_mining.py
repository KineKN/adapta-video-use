"""Classify rewrite-reference pairs into practical rewrite subtypes.

Usage:
    python helpers/anuncios_rewrite_mining.py --root Anuncios
    python helpers/anuncios_rewrite_mining.py Anuncios/8118/Ad8118_Final.txt
"""

from __future__ import annotations

import argparse
import json
import re
from dataclasses import dataclass, asdict
from difflib import SequenceMatcher
from pathlib import Path


SENTENCE_SPLIT_RE = re.compile(r"(?<=[.!?])\s+")


@dataclass
class RewriteAnalysis:
    path: str
    bruto_similarity: float
    subtype: str
    first_similarity: float | None
    last_similarity: float | None
    max_cross_similarity: float
    notes: list[str]


def normalize(text: str) -> str:
    return re.sub(r"\s+", " ", text.lower().strip())


def split_sentences(text: str) -> list[str]:
    parts = [part.strip() for part in SENTENCE_SPLIT_RE.split(text) if part.strip()]
    if parts:
        return parts
    return [line.strip() for line in text.splitlines() if line.strip()]


def sim(a: str, b: str) -> float:
    return SequenceMatcher(None, normalize(a), normalize(b)).ratio()


def analyze_pair(final_path: Path) -> RewriteAnalysis:
    bruto_path = final_path.with_name(final_path.name.replace("_Final.txt", "_Bruto.txt"))
    bruto = bruto_path.read_text(encoding="utf-8", errors="ignore")
    final = final_path.read_text(encoding="utf-8", errors="ignore")

    bruto_sents = split_sentences(bruto)
    final_sents = split_sentences(final)
    bruto_similarity = sim(bruto, final)

    first_similarity = None
    last_similarity = None
    max_cross_similarity = 0.0
    notes: list[str] = []

    if bruto_sents and final_sents:
        first_similarity = max(sim(final_sents[0], sent) for sent in bruto_sents)
        last_similarity = max(sim(final_sents[-1], sent) for sent in bruto_sents)
        for fs in final_sents[: min(5, len(final_sents))]:
            for bs in bruto_sents[: min(12, len(bruto_sents))]:
                max_cross_similarity = max(max_cross_similarity, sim(fs, bs))

    subtype = "full_rebuild"
    body_reframe = False
    if first_similarity is not None and first_similarity < 0.35 and bruto_similarity >= 0.10:
        subtype = "hook_swap"
        notes.append("opening of final is materially different from captured bruto")
    if last_similarity is not None and last_similarity < 0.35 and subtype != "hook_swap":
        subtype = "cta_rewrite"
        notes.append("close of final is materially different from captured bruto")
    if first_similarity is not None and last_similarity is not None:
        if first_similarity >= 0.45 and last_similarity >= 0.45 and bruto_similarity < 0.15:
            body_reframe = True
            notes.append("edges align but internal copy appears heavily reformulated")
    if bruto_similarity < 0.08 and not body_reframe:
        subtype = "full_rebuild"
        notes.append("pair similarity is extremely low across the whole transcript")
    if body_reframe:
        subtype = "body_reframe"
    if first_similarity is not None and first_similarity < 0.35 and last_similarity is not None and last_similarity < 0.35:
        subtype = "full_rebuild"
        notes.append("both opening and close are materially different")

    return RewriteAnalysis(
        path=str(final_path),
        bruto_similarity=round(bruto_similarity, 3),
        subtype=subtype,
        first_similarity=None if first_similarity is None else round(first_similarity, 3),
        last_similarity=None if last_similarity is None else round(last_similarity, 3),
        max_cross_similarity=round(max_cross_similarity, 3),
        notes=notes,
    )


def main() -> None:
    parser = argparse.ArgumentParser(description="Mine rewrite-reference subtypes.")
    parser.add_argument("path", nargs="?", help="Specific Ad*_Final.txt path")
    parser.add_argument("--root", help="Corpus root")
    args = parser.parse_args()

    if args.path:
        print(json.dumps(asdict(analyze_pair(Path(args.path))), ensure_ascii=False, indent=2))
        return

    if not args.root:
        raise SystemExit("Provide either a Final.txt path or --root.")

    rows = []
    for final_path in sorted(Path(args.root).glob("*/*_Final.txt")):
        bruto_path = final_path.with_name(final_path.name.replace("_Final.txt", "_Bruto.txt"))
        if not bruto_path.exists():
            continue
        rows.append(asdict(analyze_pair(final_path)))
    print(json.dumps(rows, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
