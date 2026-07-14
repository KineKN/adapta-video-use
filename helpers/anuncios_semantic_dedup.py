"""Find semantically similar nearby units using sentence-transformers.

Usage:
    .venv_ads\\Scripts\\python.exe helpers/anuncios_semantic_dedup.py path\\to\\AdXXXX_Bruto.txt
"""

from __future__ import annotations

import argparse
import re
from pathlib import Path

import numpy as np
from sentence_transformers import SentenceTransformer


SENTENCE_SPLIT_RE = re.compile(r"(?<=[.!?])\s+")


def split_units(text: str) -> list[str]:
    parts = [p.strip() for p in SENTENCE_SPLIT_RE.split(text) if p.strip()]
    if parts:
        return parts
    return [line.strip() for line in text.splitlines() if line.strip()]


def cosine_similarity(a: np.ndarray, b: np.ndarray) -> float:
    denom = np.linalg.norm(a) * np.linalg.norm(b)
    if denom == 0:
        return 0.0
    return float(np.dot(a, b) / denom)


def main() -> None:
    parser = argparse.ArgumentParser(description="Detect semantic duplication candidates.")
    parser.add_argument("path", help="Path to Bruto/Final transcript txt")
    parser.add_argument(
        "--model",
        default="sentence-transformers/paraphrase-multilingual-mpnet-base-v2",
        help="Sentence-transformers model",
    )
    parser.add_argument("--window", type=int, default=8, help="Compare only nearby units")
    parser.add_argument("--threshold", type=float, default=0.86, help="Cosine threshold")
    args = parser.parse_args()

    path = Path(args.path)
    text = path.read_text(encoding="utf-8", errors="ignore")
    units = split_units(text)

    model = SentenceTransformer(args.model)
    embeddings = model.encode(units, normalize_embeddings=True, show_progress_bar=False)

    hits = []
    for i in range(len(units)):
        for j in range(i + 1, min(len(units), i + 1 + args.window)):
            score = cosine_similarity(embeddings[i], embeddings[j])
            if score >= args.threshold:
                hits.append((i + 1, j + 1, score, units[i], units[j]))

    print(f"units={len(units)} hits={len(hits)} model={args.model}")
    for a, b, score, left, right in hits[:100]:
        print(f"\n[{a}] vs [{b}] score={score:.3f}")
        print(f"- {left}")
        print(f"- {right}")


if __name__ == "__main__":
    main()
