"""Audit EDL boundaries against word-level transcripts.

Flags segment starts/ends that are too close to neighboring words in the
same source transcript. This catches tiny leaks from aborted restarts that
can survive visual QC but sound wrong in the final edit.

Usage:
    python helpers/edl_boundary_audit.py teste/edit/edl.json
    python helpers/edl_boundary_audit.py teste/edit/edl.json --min-gap 0.12
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path


def load_words(edit_dir: Path, source: str) -> list[dict]:
    path = edit_dir / "transcripts" / f"{source}.json"
    if not path.exists():
        return []
    data = json.loads(path.read_text(encoding="utf-8"))
    return [
        w
        for w in data.get("words", [])
        if w.get("type") == "word" and w.get("start") is not None and w.get("end") is not None
    ]


def find_prev_next(words: list[dict], start: float, end: float) -> tuple[dict | None, dict | None, dict | None, dict | None]:
    prev_before_start = None
    first_inside = None
    last_inside = None
    next_after_end = None

    for word in words:
        ws = float(word["start"])
        we = float(word["end"])
        if we <= start:
            prev_before_start = word
        if first_inside is None and we > start and ws < end:
            first_inside = word
        if we > start and ws < end:
            last_inside = word
        if ws >= end:
            next_after_end = word
            break

    return prev_before_start, first_inside, last_inside, next_after_end


def audit_edl(edl_path: Path, min_gap: float) -> list[dict]:
    edl = json.loads(edl_path.read_text(encoding="utf-8"))
    edit_dir = edl_path.parent
    words_by_source: dict[str, list[dict]] = {}
    issues: list[dict] = []

    for index, row in enumerate(edl.get("ranges", [])):
        source = row["source"]
        words = words_by_source.setdefault(source, load_words(edit_dir, source))
        if not words:
            continue

        start = float(row["start"])
        end = float(row["end"])
        prev_before_start, first_inside, last_inside, next_after_end = find_prev_next(words, start, end)

        if first_inside:
            start_gap = start - float(first_inside["start"])
            if start_gap > 0.02 and not row.get("allow_start_inside_word_audio_silence"):
                issues.append(
                    {
                        "range_index": index,
                        "beat": row.get("beat"),
                        "type": "start_inside_word",
                        "start": start,
                        "word": first_inside.get("text"),
                        "word_start": first_inside["start"],
                        "word_end": first_inside["end"],
                    }
                )

        if last_inside:
            tail_after_word = end - float(last_inside["end"])
            if tail_after_word < -0.02 and not row.get("allow_end_inside_word_audio_silence"):
                issues.append(
                    {
                        "range_index": index,
                        "beat": row.get("beat"),
                        "type": "end_inside_word",
                        "end": end,
                        "word": last_inside.get("text"),
                        "word_start": last_inside["start"],
                        "word_end": last_inside["end"],
                    }
                )

        if prev_before_start:
            gap = start - float(prev_before_start["end"])
            if 0 <= gap < min_gap:
                issues.append(
                    {
                        "range_index": index,
                        "beat": row.get("beat"),
                        "type": "previous_word_too_close_to_start",
                        "gap": round(gap, 3),
                        "word": prev_before_start.get("text"),
                        "word_end": prev_before_start["end"],
                        "start": start,
                    }
                )

        if next_after_end:
            gap = float(next_after_end["start"]) - end
            if gap < min_gap:
                issues.append(
                    {
                        "range_index": index,
                        "beat": row.get("beat"),
                        "type": "next_word_too_close_to_end",
                        "gap": round(gap, 3),
                        "word": next_after_end.get("text"),
                        "end": end,
                        "word_start": next_after_end["start"],
                    }
                )

    return issues


def main() -> None:
    parser = argparse.ArgumentParser(description="Audit EDL boundaries against word-level transcript timing.")
    parser.add_argument("edl", type=Path, help="Path to edl.json")
    parser.add_argument("--min-gap", type=float, default=0.12, help="Warn when neighboring words are closer than this many seconds.")
    args = parser.parse_args()

    issues = audit_edl(args.edl, args.min_gap)
    print(json.dumps(issues, ensure_ascii=False, indent=2))
    if issues:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
