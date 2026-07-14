"""Detect repeated or restarted copy candidates inside a transcript.

Usage:
    python helpers/anuncios_repetition_candidates.py path/to/AdXXXX_Bruto.txt
"""

from __future__ import annotations

import argparse
import difflib
import re
from pathlib import Path

try:
    from rapidfuzz import fuzz

    def similarity(a: str, b: str) -> int:
        return int(fuzz.ratio(a, b))
except Exception:
    def similarity(a: str, b: str) -> int:
        return int(difflib.SequenceMatcher(None, a, b).ratio() * 100)


SENTENCE_SPLIT_RE = re.compile(r"(?<=[.!?])\s+")


def normalize(text: str) -> str:
    text = text.lower().strip()
    text = re.sub(r"\s+", " ", text)
    return text


def split_units(text: str) -> list[str]:
    parts = [p.strip() for p in SENTENCE_SPLIT_RE.split(text) if p.strip()]
    if parts:
        return parts
    return [line.strip() for line in text.splitlines() if line.strip()]


def main() -> None:
    parser = argparse.ArgumentParser(description="Detect likely repetitions and restarts.")
    parser.add_argument("path", help="Path to Bruto/Final transcript txt")
    parser.add_argument("--window", type=int, default=6, help="Compare only nearby units")
    parser.add_argument("--threshold", type=int, default=88, help="Fuzzy similarity threshold")
    args = parser.parse_args()

    path = Path(args.path)
    text = path.read_text(encoding="utf-8", errors="ignore")
    units = split_units(text)
    normalized = [normalize(u) for u in units]

    hits = []
    for i, left in enumerate(normalized):
        for j in range(i + 1, min(len(normalized), i + 1 + args.window)):
            score = similarity(left, normalized[j])
            if score >= args.threshold:
                hits.append((i + 1, j + 1, score, units[i], units[j]))

    print(f"units={len(units)} hits={len(hits)}")
    for a, b, score, left, right in hits[:100]:
        print(f"\n[{a}] vs [{b}] score={score}")
        print(f"- {left}")
        print(f"- {right}")


if __name__ == "__main__":
    main()
