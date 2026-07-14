"""Audit corpus Final.txt files for weak or suspicious reference quality.

Usage:
    python helpers/anuncios_reference_audit.py --root Anuncios
    python helpers/anuncios_reference_audit.py Anuncios/9119/Ad9119_Final.txt
"""

from __future__ import annotations

import argparse
import json
import re
from collections import Counter
from difflib import SequenceMatcher
from pathlib import Path


WORD_RE = re.compile(r"\w+", re.UNICODE)
SENTENCE_SPLIT_RE = re.compile(r"(?<=[.!?])\s+")

SUSPICIOUS_MARKERS = [
    "adapta.org",
    "adapta.org.br",
    "gpm",
    "ad ",
    "transcrição e legendas",
]

META_PATTERNS = [
    r"t[aá] gravando",
    r"n[aã]o era pra voc[eê] estar gravando",
    r"transcri[cç][aã]o e legendas",
    r"pedro negri",
    r"obrigado por assistir",
]


def split_units(text: str) -> list[str]:
    parts = [part.strip() for part in SENTENCE_SPLIT_RE.split(text) if part.strip()]
    if parts:
        return parts
    return [line.strip() for line in text.splitlines() if line.strip()]


def normalize(text: str) -> str:
    text = text.lower().strip()
    text = re.sub(r"\s+", " ", text)
    return text


def audit_text(text: str) -> dict:
    lowered = text.lower()
    words = WORD_RE.findall(lowered)
    units = split_units(text)
    normalized_units = [normalize(unit) for unit in units]
    unit_counts = Counter(normalized_units)
    word_counts = Counter(words)

    duplicate_units = [
        {"unit": unit, "count": count}
        for unit, count in unit_counts.items()
        if count >= 3 and len(unit.split()) >= 4
    ]
    duplicate_units.sort(key=lambda item: item["count"], reverse=True)

    suspicious_hits = {marker: lowered.count(marker) for marker in SUSPICIOUS_MARKERS if marker in lowered}
    unique_ratio = len(set(words)) / len(words) if words else 0.0
    top_word, top_word_count = word_counts.most_common(1)[0] if word_counts else ("", 0)

    weak_score = 0
    if len(words) < 12:
        weak_score += 3
    if unique_ratio < 0.45:
        weak_score += 1
    if top_word_count / max(len(words), 1) > 0.08:
        weak_score += 1
    if duplicate_units:
        weak_score += 2
    if suspicious_hits:
        weak_score += 1
    if any(re.search(pattern, lowered) for pattern in META_PATTERNS):
        weak_score += 2

    label = "strong"
    if weak_score >= 3:
        label = "weak_reference"
    elif weak_score >= 1:
        label = "review_reference"

    return {
        "label": label,
        "weak_score": weak_score,
        "word_count": len(words),
        "unique_ratio": round(unique_ratio, 3),
        "top_word": top_word,
        "top_word_count": top_word_count,
        "duplicate_units": duplicate_units[:10],
        "suspicious_hits": suspicious_hits,
    }


def audit_path(path: Path) -> dict:
    text = path.read_text(encoding="utf-8", errors="ignore")
    result = audit_text(text)
    bruto_path = path.with_name(path.name.replace("_Final.txt", "_Bruto.txt"))
    if bruto_path.exists():
        bruto = bruto_path.read_text(encoding="utf-8", errors="ignore")
        bruto_similarity = SequenceMatcher(None, bruto.lower(), text.lower()).ratio()
        result["bruto_similarity"] = round(bruto_similarity, 3)
        if bruto_similarity < 0.15 and result["label"] == "strong":
            result["label"] = "rewrite_reference"
        elif bruto_similarity < 0.15 and result["label"] == "review_reference":
            result["label"] = "rewrite_reference"
    result["path"] = str(path)
    return result


def main() -> None:
    parser = argparse.ArgumentParser(description="Audit Final.txt reference quality.")
    parser.add_argument("path", nargs="?", help="Specific Final.txt path")
    parser.add_argument("--root", help="Corpus root to scan")
    args = parser.parse_args()

    if args.path:
        print(json.dumps(audit_path(Path(args.path)), ensure_ascii=False, indent=2))
        return

    if not args.root:
        raise SystemExit("Provide either a Final.txt path or --root.")

    rows = []
    for path in sorted(Path(args.root).glob("*/*_Final.txt")):
        row = audit_path(path)
        if row["label"] != "strong":
            rows.append(row)
    print(json.dumps(rows, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
