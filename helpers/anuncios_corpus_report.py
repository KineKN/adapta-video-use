"""Analyze Adapta ad corpus pairs (Bruto -> Final) and emit a report.

Usage:
    python helpers/anuncios_corpus_report.py
    python helpers/anuncios_corpus_report.py --root Anuncios --output report.md
"""

from __future__ import annotations

import argparse
import json
import math
import re
import statistics as stats
from collections import Counter
from dataclasses import dataclass
from pathlib import Path


SENTENCE_SPLIT_RE = re.compile(r"(?<=[.!?])\s+")
WORD_RE = re.compile(r"\w+", re.UNICODE)

RESET_MARKERS = [
    "volta",
    "faz de novo",
    "de novo",
    "mais",
    "aí",
    "pera aí",
    "opa",
    "gravando",
    "corta isso",
]

META_MARKERS = [
    "saiba mais",
    "clique",
    "clica",
    "botão",
    "link aqui embaixo",
]


@dataclass
class PairStats:
    ad_id: str
    bruto_words: int
    final_words: int
    compression_ratio: float
    bruto_resets: int
    final_resets: int
    bruto_meta: int
    final_meta: int


def count_words(text: str) -> int:
    return len(WORD_RE.findall(text))


def count_markers(text: str, markers: list[str]) -> int:
    lowered = text.lower()
    return sum(lowered.count(m) for m in markers)


def load_pairs(root: Path) -> list[tuple[str, Path, Path]]:
    pairs: list[tuple[str, Path, Path]] = []
    for child in sorted(root.iterdir()):
        if not child.is_dir():
            continue
        bruto = next(child.glob("Ad*_Bruto.txt"), None)
        final = next(child.glob("Ad*_Final.txt"), None)
        if bruto and final:
            pairs.append((child.name, bruto, final))
    return pairs


def analyze_pairs(root: Path) -> tuple[list[PairStats], dict[str, int]]:
    pairs = load_pairs(root)
    results: list[PairStats] = []
    regime_counts = Counter()

    for ad_id, bruto_path, final_path in pairs:
        bruto = bruto_path.read_text(encoding="utf-8", errors="ignore")
        final = final_path.read_text(encoding="utf-8", errors="ignore")
        bruto_words = count_words(bruto)
        final_words = count_words(final)
        ratio = final_words / bruto_words if bruto_words else math.nan
        if ratio < 0.25:
            regime = "aggressive_rebuild"
        elif ratio > 1.15:
            regime = "expanded_or_rewritten"
        else:
            regime = "light_to_medium_cleanup"
        regime_counts[regime] += 1
        results.append(
            PairStats(
                ad_id=ad_id,
                bruto_words=bruto_words,
                final_words=final_words,
                compression_ratio=ratio,
                bruto_resets=count_markers(bruto, RESET_MARKERS),
                final_resets=count_markers(final, RESET_MARKERS),
                bruto_meta=count_markers(bruto, META_MARKERS),
                final_meta=count_markers(final, META_MARKERS),
            )
        )
    return results, dict(regime_counts)


def format_report(results: list[PairStats], regimes: dict[str, int]) -> str:
    bruto_words = [r.bruto_words for r in results]
    final_words = [r.final_words for r in results]
    ratios = [r.compression_ratio for r in results if not math.isnan(r.compression_ratio)]

    lines = [
        "# Anuncios Corpus Report",
        "",
        f"Pairs analyzed: {len(results)}",
        "",
        "## Corpus Shape",
        "",
        f"- Median bruto words: {stats.median(bruto_words):.1f}",
        f"- Median final words: {stats.median(final_words):.1f}",
        f"- Median final/bruto ratio: {stats.median(ratios):.3f}",
        f"- Mean final/bruto ratio: {stats.mean(ratios):.3f}",
        "",
        "## Editorial Regimes",
        "",
    ]
    for key, val in sorted(regimes.items()):
        lines.append(f"- {key}: {val}")

    lines.extend(
        [
            "",
            "## Outliers",
            "",
            "Lowest ratios usually indicate very noisy bruto transcripts or heavy reconstruction.",
            "Highest ratios usually indicate rewritten finals or weak bruto transcripts.",
            "",
            "### Lowest ratios",
            "",
        ]
    )
    for row in sorted(results, key=lambda r: r.compression_ratio)[:10]:
        lines.append(
            f"- {row.ad_id}: bruto={row.bruto_words}, final={row.final_words}, ratio={row.compression_ratio:.3f}"
        )

    lines.extend(["", "### Highest ratios", ""])
    for row in sorted(results, key=lambda r: r.compression_ratio, reverse=True)[:10]:
        lines.append(
            f"- {row.ad_id}: bruto={row.bruto_words}, final={row.final_words}, ratio={row.compression_ratio:.3f}"
        )

    lines.extend(
        [
            "",
            "## Marker Trends",
            "",
            f"- Total reset markers in bruto: {sum(r.bruto_resets for r in results)}",
            f"- Total reset markers in final: {sum(r.final_resets for r in results)}",
            f"- Total CTA/meta markers in bruto: {sum(r.bruto_meta for r in results)}",
            f"- Total CTA/meta markers in final: {sum(r.final_meta for r in results)}",
            "",
            "## Interpretation",
            "",
            "- Most pairs are not full rewrites. They are cleanup passes that preserve the commercial arc.",
            "- A minority of pairs are aggressive rebuilds, typically when bruto text is highly redundant or low signal.",
            "- Finals can be longer than brutos when the bruto transcript is weak, incomplete, or conversationally malformed.",
        ]
    )
    return "\n".join(lines) + "\n"


def build_json(results: list[PairStats], regimes: dict[str, int]) -> dict:
    return {
        "pairs": [r.__dict__ for r in results],
        "regimes": regimes,
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="Analyze Bruto -> Final ad pairs.")
    parser.add_argument("--root", default="Anuncios", help="Root corpus directory")
    parser.add_argument("--output", help="Optional markdown output path")
    parser.add_argument("--json-output", help="Optional JSON output path")
    args = parser.parse_args()

    root = Path(args.root)
    results, regimes = analyze_pairs(root)
    report = format_report(results, regimes)
    print(report, end="")

    if args.output:
        Path(args.output).write_text(report, encoding="utf-8")
    if args.json_output:
        Path(args.json_output).write_text(
            json.dumps(build_json(results, regimes), ensure_ascii=False, indent=2),
            encoding="utf-8",
        )


if __name__ == "__main__":
    main()
