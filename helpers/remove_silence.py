"""Post-EDL silence tightening for video-use cuts.

This tool is intentionally a post-decupagem step: first remove wrong takes,
repetitions, and non-ad material; then optionally tighten dead air inside the
approved EDL for a more dynamic delivery.

Examples:
    python helpers/remove_silence.py edit/edl.json --mode balanced --out edit/edl_tight.json
    python helpers/remove_silence.py --analyze-video edit/final.mp4 --silence-duration 0.2
"""

from __future__ import annotations

import argparse
import array
import json
import math
import re
import subprocess
from copy import deepcopy
from pathlib import Path
from typing import Any


MODES = {
    "gentle": {"min_gap": 0.55, "keep_silence": 0.28, "edge_pad": 0.06},
    "balanced": {"min_gap": 0.40, "keep_silence": 0.18, "edge_pad": 0.05},
    "tight": {"min_gap": 0.28, "keep_silence": 0.10, "edge_pad": 0.04},
}


def clamp(value: float, low: float, high: float) -> float:
    return max(low, min(high, value))


def run_capture(cmd: list[str]) -> str:
    proc = subprocess.run(cmd, text=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=False)
    return (proc.stdout or "") + "\n" + (proc.stderr or "")


def run_bytes(cmd: list[str]) -> bytes:
    proc = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=True)
    return proc.stdout


def percentile(values: list[float], pct: float) -> float:
    if not values:
        return 0.0
    ordered = sorted(values)
    if len(ordered) == 1:
        return ordered[0]
    pos = (len(ordered) - 1) * pct
    low = int(math.floor(pos))
    high = int(math.ceil(pos))
    if low == high:
        return ordered[low]
    return ordered[low] + (ordered[high] - ordered[low]) * (pos - low)


def otsu_threshold(values: list[float]) -> float:
    if not values:
        return -45.0

    low = math.floor(min(values))
    high = math.ceil(max(values))
    if low >= high:
        return float(low)

    bins = list(range(low, high + 1))
    counts = [0 for _ in bins]
    for value in values:
        idx = int(round(value)) - low
        idx = max(0, min(len(counts) - 1, idx))
        counts[idx] += 1

    total = sum(counts)
    sum_total = sum(i * counts[i] for i in range(len(counts)))
    weight_bg = 0
    sum_bg = 0.0
    best_idx = 0
    best_variance = -1.0

    for i, count in enumerate(counts):
        weight_bg += count
        if weight_bg == 0:
            continue
        weight_fg = total - weight_bg
        if weight_fg == 0:
            break
        sum_bg += i * count
        mean_bg = sum_bg / weight_bg
        mean_fg = (sum_total - sum_bg) / weight_fg
        variance = weight_bg * weight_fg * ((mean_bg - mean_fg) ** 2)
        if variance > best_variance:
            best_variance = variance
            best_idx = i
    return float(bins[best_idx])


def decode_audio_levels(video_path: Path, window_seconds: float = 0.02, sample_rate: int = 16000) -> list[float]:
    raw = run_bytes(
        [
            "ffmpeg",
            "-hide_banner",
            "-loglevel",
            "error",
            "-i",
            str(video_path),
            "-vn",
            "-ac",
            "1",
            "-ar",
            str(sample_rate),
            "-f",
            "s16le",
            "-",
        ]
    )
    samples = array.array("h")
    samples.frombytes(raw)
    if not samples:
        return []

    window_size = max(1, int(round(sample_rate * window_seconds)))
    levels: list[float] = []
    for start in range(0, len(samples), window_size):
        chunk = samples[start : start + window_size]
        if not chunk:
            continue
        square_sum = sum(sample * sample for sample in chunk)
        rms = math.sqrt(square_sum / len(chunk))
        if rms <= 0:
            levels.append(-96.0)
        else:
            levels.append(20.0 * math.log10(rms / 32768.0))
    return levels


def silence_runs_from_levels(levels: list[float], threshold_db: float, window_seconds: float) -> list[dict[str, float]]:
    runs: list[dict[str, float]] = []
    open_start: int | None = None
    for index, level in enumerate(levels):
        is_silent = level <= threshold_db
        if is_silent and open_start is None:
            open_start = index
        elif not is_silent and open_start is not None:
            runs.append(
                {
                    "start": round(open_start * window_seconds, 3),
                    "end": round(index * window_seconds, 3),
                    "duration": round((index - open_start) * window_seconds, 3),
                }
            )
            open_start = None
    if open_start is not None:
        runs.append(
            {
                "start": round(open_start * window_seconds, 3),
                "end": round(len(levels) * window_seconds, 3),
                "duration": round((len(levels) - open_start) * window_seconds, 3),
            }
        )
    return runs


def window_overlaps_words(window_start: float, window_end: float, words: list[dict[str, Any]]) -> bool:
    return any(float(word["end"]) > window_start and float(word["start"]) < window_end for word in words)


def non_word_gap_threshold(
    levels: list[float],
    ranges: list[dict[str, Any]],
    words: list[dict[str, Any]],
    window_seconds: float,
) -> dict[str, Any] | None:
    if not ranges or not words or not levels:
        return None

    non_word_levels: list[float] = []
    word_levels: list[float] = []
    for row in ranges:
        row_start = float(row["start"])
        row_end = float(row["end"])
        row_words = words_inside(words, row_start, row_end)
        if not row_words:
            continue
        start_index = max(0, int(math.floor(row_start / window_seconds)))
        end_index = min(len(levels), int(math.ceil(row_end / window_seconds)))
        for index in range(start_index, end_index):
            window_start = index * window_seconds
            window_end = window_start + window_seconds
            is_word = window_overlaps_words(window_start, window_end, row_words)
            if is_word:
                word_levels.append(levels[index])
            else:
                non_word_levels.append(levels[index])

    if not non_word_levels or not word_levels:
        return None

    # Use the loud end of non-word regions. This catches breaths and room tone
    # that are still not transcript words, without using a fixed dB threshold.
    best_threshold = percentile(non_word_levels, 0.75)
    return {
        "threshold_db": round(best_threshold, 1),
        "method": "non_word_gap_upper_quartile",
        "non_word_windows": len(non_word_levels),
        "word_windows": len(word_levels),
        "non_word_percentiles_db": {
            "p50": round(percentile(non_word_levels, 0.50), 1),
            "p60": round(percentile(non_word_levels, 0.60), 1),
            "p70": round(percentile(non_word_levels, 0.70), 1),
            "p75": round(percentile(non_word_levels, 0.75), 1),
            "p80": round(percentile(non_word_levels, 0.80), 1),
        },
        "word_percentiles_db": {
            "p10": round(percentile(word_levels, 0.10), 1),
            "p25": round(percentile(word_levels, 0.25), 1),
            "p50": round(percentile(word_levels, 0.50), 1),
        },
    }


def profile_silence_settings(
    video_path: Path,
    ranges: list[dict[str, Any]] | None = None,
    words: list[dict[str, Any]] | None = None,
    mode: str = "balanced",
) -> dict[str, Any]:
    window_seconds = 0.02
    all_levels = decode_audio_levels(video_path, window_seconds=window_seconds)
    if ranges:
        selected_levels: list[float] = []
        for row in ranges:
            start_index = max(0, int(math.floor(float(row["start"]) / window_seconds)))
            end_index = min(len(all_levels), int(math.ceil(float(row["end"]) / window_seconds)))
            if end_index > start_index:
                selected_levels.extend(all_levels[start_index:end_index])
        levels = selected_levels or all_levels
    else:
        levels = all_levels
    voiced_levels = [level for level in levels if level > -95.0]
    if not voiced_levels:
        return {
            "threshold_db": -45.0,
            "silence_duration": 0.2,
            "front_padding": 0.04,
            "back_padding": 0.04,
            "max_silence_kept": 0.2,
            "min_removed_duration": 0.12,
            "analysis": {"error": "no_audio_levels"},
        }

    guided = non_word_gap_threshold(all_levels, ranges or [], words or [], window_seconds)
    threshold = guided["threshold_db"] if guided else otsu_threshold(voiced_levels)
    runs = silence_runs_from_levels(levels, threshold, window_seconds)
    durations = [float(run["duration"]) for run in runs if float(run["duration"]) > 0]
    short_pause_cutoff = percentile(durations, 0.45) if durations else window_seconds
    kept_pause_percentiles = {"gentle": 0.75, "balanced": 0.70, "tight": 0.50}
    kept_pause_percentile = kept_pause_percentiles.get(mode, kept_pause_percentiles["balanced"])
    kept_pause_cutoff = percentile(durations, kept_pause_percentile) if durations else short_pause_cutoff
    silence_duration = max(window_seconds, round(short_pause_cutoff / window_seconds) * window_seconds)
    max_silence_kept = max(silence_duration, round(kept_pause_cutoff / window_seconds) * window_seconds)

    # Padding follows the detected analysis granularity and short-pause profile:
    # tighter material gets less preserved air, sparse material gets more.
    derived_padding = max(window_seconds, min(silence_duration / 3.0, percentile(durations, 0.25) if durations else window_seconds))
    derived_padding = round(derived_padding / window_seconds) * window_seconds
    min_removed_duration = max_silence_kept
    min_removed_duration = round(min_removed_duration / window_seconds) * window_seconds

    return {
        "threshold_db": round(threshold, 1),
        "silence_duration": round(silence_duration, 3),
        "front_padding": round(derived_padding, 3),
        "back_padding": round(derived_padding, 3),
        "max_silence_kept": round(max_silence_kept, 3),
        "min_removed_duration": round(min_removed_duration, 3),
        "edge_pad": 0.0,
        "analysis": {
            "window_seconds": window_seconds,
            "profile_scope": "edl_ranges" if ranges else "full_media",
            "profile_ranges": len(ranges or []),
            "level_percentiles_db": {
                "p10": round(percentile(voiced_levels, 0.10), 1),
                "p25": round(percentile(voiced_levels, 0.25), 1),
                "p50": round(percentile(voiced_levels, 0.50), 1),
                "p75": round(percentile(voiced_levels, 0.75), 1),
                "p90": round(percentile(voiced_levels, 0.90), 1),
            },
            "threshold_method": guided["method"] if guided else "otsu_db_histogram",
            "threshold_fit": guided,
            "candidate_silence_runs": len(runs),
            "silence_duration_method": "p45_candidate_run_duration",
            "max_silence_kept_method": f"p{int(kept_pause_percentile * 100)}_candidate_run_duration",
            "padding_method": "min(p25_candidate_run_duration, silence_duration/3)",
            "min_removed_duration_method": "max_silence_kept",
            "candidate_duration_percentiles_s": {
                "p25": round(percentile(durations, 0.25), 3) if durations else 0,
                "p45": round(percentile(durations, 0.45), 3) if durations else 0,
                "p50": round(percentile(durations, 0.50), 3) if durations else 0,
                "p70": round(percentile(durations, 0.70), 3) if durations else 0,
                "p75": round(percentile(durations, 0.75), 3) if durations else 0,
            },
        },
    }


def suggest_threshold_db(video_path: Path) -> dict[str, float | None]:
    profile = profile_silence_settings(video_path)
    output = run_capture(
        [
            "ffmpeg",
            "-hide_banner",
            "-nostats",
            "-i",
            str(video_path),
            "-af",
            "volumedetect",
            "-f",
            "null",
            "-",
        ]
    )
    mean_match = re.search(r"mean_volume:\s*(-?\d+(?:\.\d+)?) dB", output)
    max_match = re.search(r"max_volume:\s*(-?\d+(?:\.\d+)?) dB", output)
    mean_volume = float(mean_match.group(1)) if mean_match else None
    max_volume = float(max_match.group(1)) if max_match else None
    return {
        "mean_volume_db": mean_volume,
        "max_volume_db": max_volume,
        "suggested_threshold_db": profile["threshold_db"],
    }


def detect_silences(video_path: Path, threshold_db: float, min_duration: float) -> list[dict[str, float]]:
    output = run_capture(
        [
            "ffmpeg",
            "-hide_banner",
            "-nostats",
            "-i",
            str(video_path),
            "-af",
            f"silencedetect=noise={threshold_db}dB:d={min_duration}",
            "-f",
            "null",
            "-",
        ]
    )

    regions: list[dict[str, float]] = []
    open_start: float | None = None
    for line in output.splitlines():
        start_match = re.search(r"silence_start:\s*([0-9.]+)", line)
        if start_match:
            open_start = float(start_match.group(1))
            continue
        end_match = re.search(r"silence_end:\s*([0-9.]+)\s*\|\s*silence_duration:\s*([0-9.]+)", line)
        if end_match and open_start is not None:
            end = float(end_match.group(1))
            duration = float(end_match.group(2))
            regions.append({"start": round(open_start, 3), "end": round(end, 3), "duration": round(duration, 3)})
            open_start = None
    return regions


def detect_silences_from_audio_levels(
    video_path: Path,
    threshold_db: float,
    window_seconds: float = 0.02,
) -> list[dict[str, float]]:
    levels = decode_audio_levels(video_path, window_seconds=window_seconds)
    return silence_runs_from_levels(levels, threshold_db, window_seconds)


def load_words(edit_dir: Path, source: str) -> list[dict[str, Any]]:
    path = edit_dir / "transcripts" / f"{source}.json"
    if not path.exists():
        return []
    data = json.loads(path.read_text(encoding="utf-8"))
    return [
        word
        for word in data.get("words", [])
        if word.get("type") == "word" and word.get("start") is not None and word.get("end") is not None
    ]


def words_inside(words: list[dict[str, Any]], start: float, end: float) -> list[dict[str, Any]]:
    return [word for word in words if float(word["end"]) > start and float(word["start"]) < end]


def transcript_gap_regions(row: dict[str, Any], words: list[dict[str, Any]], min_gap: float) -> list[dict[str, float]]:
    row_words = words_inside(words, float(row["start"]), float(row["end"]))
    regions: list[dict[str, float]] = []
    for prev_word, next_word in zip(row_words, row_words[1:]):
        prev_end = float(prev_word["end"])
        next_start = float(next_word["start"])
        if next_start - prev_end >= min_gap:
            regions.append(
                {
                    "start": round(prev_end, 3),
                    "end": round(next_start, 3),
                    "duration": round(next_start - prev_end, 3),
                }
            )
    return regions


def merge_silence_regions(regions: list[dict[str, float]]) -> list[dict[str, float]]:
    if not regions:
        return []
    ordered = sorted(regions, key=lambda region: (float(region["start"]), float(region["end"])))
    merged: list[dict[str, float]] = []
    for region in ordered:
        start = float(region["start"])
        end = float(region["end"])
        if not merged or start > float(merged[-1]["end"]):
            merged.append({"start": round(start, 3), "end": round(end, 3), "duration": round(end - start, 3)})
            continue
        merged[-1]["end"] = round(max(float(merged[-1]["end"]), end), 3)
        merged[-1]["duration"] = round(float(merged[-1]["end"]) - float(merged[-1]["start"]), 3)
    return merged


def sort_silence_regions(regions: list[dict[str, float]]) -> list[dict[str, float]]:
    return sorted(regions, key=lambda region: (float(region["start"]), float(region["end"])))


def make_child_range(row: dict[str, Any], start: float, end: float, index: int, removed_reason: str) -> dict[str, Any]:
    child = deepcopy(row)
    child["start"] = round(start, 3)
    child["end"] = round(end, 3)
    child["silence_tightened"] = True
    child["silence_piece"] = index
    child["reason"] = f"{row.get('reason', '').strip()} Silence tighten: {removed_reason}".strip()
    return child


def trim_range_edges_to_words(
    row: dict[str, Any],
    words: list[dict[str, Any]],
    max_edge_silence: float,
    min_piece: float,
) -> tuple[dict[str, Any], dict[str, Any]]:
    start = float(row["start"])
    end = float(row["end"])
    row_words = words_inside(words, start, end)
    if not row_words:
        return row, {}

    first_word_start = float(row_words[0]["start"])
    last_word_end = float(row_words[-1]["end"])
    new_start = start
    new_end = end

    if first_word_start - start > max_edge_silence:
        new_start = first_word_start - max_edge_silence
    if end - last_word_end > max_edge_silence:
        new_end = last_word_end + max_edge_silence
    if new_end - new_start < min_piece:
        return row, {}

    trim_start = new_start - start
    trim_end = end - new_end
    if trim_start <= 0 and trim_end <= 0:
        return row, {}

    trimmed = deepcopy(row)
    trimmed["start"] = round(new_start, 3)
    trimmed["end"] = round(new_end, 3)
    trimmed["edge_trimmed"] = True
    trim = {
        "range_beat": row.get("beat"),
        "source": row.get("source"),
        "trim_start_s": round(trim_start, 3),
        "trim_end_s": round(trim_end, 3),
        "new_start": trimmed["start"],
        "new_end": trimmed["end"],
        "first_word": row_words[0].get("text"),
        "last_word": row_words[-1].get("text"),
    }
    return trimmed, trim


def trim_range_edges_to_audio(
    row: dict[str, Any],
    levels: list[float],
    threshold_db: float,
    window_seconds: float,
    max_edge_silence: float,
    min_piece: float,
    words: list[dict[str, Any]] | None = None,
    max_inside_word_trim: float | None = None,
) -> tuple[dict[str, Any], dict[str, Any]]:
    start = float(row["start"])
    end = float(row["end"])
    if not levels or end <= start:
        return row, {}

    start_index = max(0, int(math.floor(start / window_seconds)))
    end_index = min(len(levels), int(math.ceil(end / window_seconds)))
    if end_index <= start_index:
        return row, {}

    first_voiced: int | None = None
    last_voiced: int | None = None
    for index in range(start_index, end_index):
        if levels[index] > threshold_db:
            first_voiced = index
            break
    for index in range(end_index - 1, start_index - 1, -1):
        if levels[index] > threshold_db:
            last_voiced = index
            break
    if first_voiced is None or last_voiced is None or first_voiced > last_voiced:
        return row, {}

    new_start = max(start, first_voiced * window_seconds - max_edge_silence)
    new_end = min(end, (last_voiced + 1) * window_seconds + max_edge_silence)
    if words:
        row_words = words_inside(words, start, end)
        if row_words:
            first_word_start = float(row_words[0]["start"])
            last_word_end = float(row_words[-1]["end"])
            max_word_trim = max_inside_word_trim if max_inside_word_trim is not None else max_edge_silence * 6.0
            if new_start > first_word_start and new_start - first_word_start > max_word_trim:
                new_start = start
            if new_end < last_word_end and last_word_end - new_end > max_word_trim:
                new_end = end
    if new_end - new_start < min_piece:
        return row, {}

    trim_start = new_start - start
    trim_end = end - new_end
    if trim_start <= max_edge_silence and trim_end <= max_edge_silence:
        return row, {}

    trimmed = deepcopy(row)
    trimmed["start"] = round(new_start, 3)
    trimmed["end"] = round(new_end, 3)
    trimmed["audio_edge_trimmed"] = True
    if words:
        row_words = words_inside(words, start, end)
        if row_words:
            if new_start > float(row_words[0]["start"]):
                trimmed["allow_start_inside_word_audio_silence"] = True
            if new_end < float(row_words[-1]["end"]):
                trimmed["allow_end_inside_word_audio_silence"] = True
    trim = {
        "range_beat": row.get("beat"),
        "source": row.get("source"),
        "trim_start_s": round(max(0.0, trim_start), 3),
        "trim_end_s": round(max(0.0, trim_end), 3),
        "new_start": trimmed["start"],
        "new_end": trimmed["end"],
        "threshold_db": round(threshold_db, 1),
    }
    return trimmed, trim


def split_range_on_word_gaps(
    row: dict[str, Any],
    words: list[dict[str, Any]],
    min_gap: float,
    keep_silence: float,
    edge_pad: float,
    min_piece: float,
) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    start = float(row["start"])
    end = float(row["end"])
    kept_words = words_inside(words, start, end)
    if len(kept_words) < 2:
        return [row], []

    pieces: list[dict[str, Any]] = []
    cuts: list[dict[str, Any]] = []
    piece_start = start

    for prev_word, next_word in zip(kept_words, kept_words[1:]):
        prev_end = float(prev_word["end"])
        next_start = float(next_word["start"])
        gap = next_start - prev_end
        if gap < min_gap:
            continue

        left_end = clamp(prev_end + (keep_silence / 2.0), piece_start, end)
        right_start = clamp(next_start - (keep_silence / 2.0), start, end)
        if right_start <= left_end:
            continue
        if left_end - piece_start < min_piece:
            continue

        removed = right_start - left_end
        reason = f"removed {removed:.2f}s gap after '{prev_word.get('text', '')}' before '{next_word.get('text', '')}'"
        pieces.append(make_child_range(row, piece_start, left_end + edge_pad, len(pieces) + 1, reason))
        cuts.append(
            {
                "range_beat": row.get("beat"),
                "source": row.get("source"),
                "remove_start": round(left_end, 3),
                "remove_end": round(right_start, 3),
                "removed_s": round(removed, 3),
                "previous_word": prev_word.get("text"),
                "next_word": next_word.get("text"),
            }
        )
        piece_start = max(start, right_start - edge_pad)

    if pieces and end - piece_start >= min_piece:
        pieces.append(make_child_range(row, piece_start, end, len(pieces) + 1, "kept tail after final tightened gap"))

    return (pieces if pieces else [row]), cuts


def split_range_on_audio_silences(
    row: dict[str, Any],
    silences: list[dict[str, float]],
    words: list[dict[str, Any]],
    front_padding: float,
    back_padding: float,
    max_silence_kept: float,
    min_removed_duration: float,
    edge_pad: float,
    min_piece: float,
    allow_inside_word_audio_override: bool = False,
) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    start = float(row["start"])
    end = float(row["end"])
    piece_start = start
    piece_start_allow_inside_word = False
    pieces: list[dict[str, Any]] = []
    cuts: list[dict[str, Any]] = []
    row_words = words_inside(words, start, end) if words else []

    for silence in silences:
        silence_start = max(start, float(silence["start"]))
        silence_end = min(end, float(silence["end"]))
        if silence_end <= silence_start:
            continue

        silence_duration = silence_end - silence_start
        if silence_duration <= max_silence_kept:
            continue

        left_end = clamp(silence_start + back_padding, piece_start, end)
        right_start = clamp(silence_end - front_padding, start, end)
        if right_start <= left_end:
            continue
        allow_inside_word_audio_silence = False
        overlapping_words = words_inside(row_words, left_end, right_start)
        if overlapping_words:
            mid = (left_end + right_start) / 2.0
            adjusted_left = left_end
            adjusted_right = right_start
            crossed_middle = False
            for word in overlapping_words:
                word_start = float(word["start"])
                word_end = float(word["end"])
                if word_start < mid < word_end:
                    crossed_middle = True
                    break
                if word_end <= mid:
                    adjusted_left = max(adjusted_left, word_end)
                if word_start >= mid:
                    adjusted_right = min(adjusted_right, word_start)
            if crossed_middle:
                if not allow_inside_word_audio_override or silence_duration < max_silence_kept * 4.0:
                    continue
                allow_inside_word_audio_silence = True
            else:
                left_end = adjusted_left
                right_start = adjusted_right
                if right_start <= left_end:
                    continue
        removed = right_start - left_end
        if removed < min_removed_duration:
            continue
        if left_end - piece_start < min_piece:
            continue

        reason_prefix = "long audio silence inside ASR word" if allow_inside_word_audio_silence else "audio-threshold"
        reason = f"{reason_prefix} removed {removed:.2f}s silence at {silence_start:.2f}-{silence_end:.2f}"
        child = make_child_range(row, piece_start, left_end + edge_pad, len(pieces) + 1, reason)
        if piece_start_allow_inside_word:
            child["allow_start_inside_word_audio_silence"] = True
        if allow_inside_word_audio_silence:
            child["allow_end_inside_word_audio_silence"] = True
        pieces.append(child)
        cuts.append(
            {
                "range_beat": row.get("beat"),
                "source": row.get("source"),
                "remove_start": round(left_end, 3),
                "remove_end": round(right_start, 3),
                "removed_s": round(removed, 3),
                "silence_start": round(silence_start, 3),
                "silence_end": round(silence_end, 3),
                "inside_word_audio_override": allow_inside_word_audio_silence,
            }
        )
        piece_start = max(start, right_start - edge_pad)
        piece_start_allow_inside_word = allow_inside_word_audio_silence

    if pieces and end - piece_start >= min_piece:
        child = make_child_range(row, piece_start, end, len(pieces) + 1, "kept tail after final audio-threshold cut")
        if piece_start_allow_inside_word:
            child["allow_start_inside_word_audio_silence"] = True
        pieces.append(child)

    return (pieces if pieces else [row]), cuts


def tighten_edl(
    edl_path: Path,
    mode: str,
    min_gap: float | None,
    keep_silence: float | None,
    edge_pad: float | None,
    min_piece: float,
    audio_tighten: bool = False,
    threshold_db: float | None = None,
    silence_duration: float | None = None,
    max_silence_kept: float | None = None,
    min_removed_duration: float | None = None,
    allow_inside_word_audio_override: bool = False,
    ffmpeg_silence_only: bool = False,
    breath_edge_trim: bool = False,
    breath_threshold_db: float | None = None,
    max_breath_edge_trim: float = 0.18,
) -> tuple[dict[str, Any], dict[str, Any]]:
    edl = json.loads(edl_path.read_text(encoding="utf-8"))
    edit_dir = edl_path.parent
    config = MODES[mode].copy()
    if min_gap is not None:
        config["min_gap"] = min_gap
    if keep_silence is not None:
        config["keep_silence"] = keep_silence
    if edge_pad is not None:
        config["edge_pad"] = edge_pad

    words_by_source: dict[str, list[dict[str, Any]]] = {}
    silences_by_source: dict[str, list[dict[str, float]]] = {}
    audio_profiles_by_source: dict[str, dict[str, Any]] = {}
    audio_levels_by_source: dict[str, list[float]] = {}
    source_ranges: dict[str, list[dict[str, Any]]] = {}
    for source_row in edl.get("ranges", []):
        source_ranges.setdefault(source_row["source"], []).append(source_row)
    new_ranges: list[dict[str, Any]] = []
    removed_gaps: list[dict[str, Any]] = []
    edge_trims: list[dict[str, Any]] = []
    audio_edge_trims: list[dict[str, Any]] = []
    untouched_no_transcript: set[str] = set()
    untouched_no_source: set[str] = set()

    original_duration = sum(float(row["end"]) - float(row["start"]) for row in edl.get("ranges", []))
    for row in edl.get("ranges", []):
        source = row["source"]
        if audio_tighten:
            source_path_text = edl.get("sources", {}).get(source)
            words = words_by_source.setdefault(source, load_words(edit_dir, source))
            if not source_path_text:
                untouched_no_source.add(source)
                new_ranges.append(row)
                continue
            source_path = Path(source_path_text)
            if source not in silences_by_source:
                if not source_path.exists():
                    untouched_no_source.add(source)
                    silences_by_source[source] = []
                else:
                    profile = profile_silence_settings(source_path, source_ranges.get(source, []), words, mode)
                    audio_profiles_by_source[source] = profile
                    source_threshold = threshold_db if threshold_db is not None else float(profile["threshold_db"])
                    source_silence_duration = silence_duration if silence_duration is not None else float(profile["silence_duration"])
                    if ffmpeg_silence_only:
                        duration_for_detect = max_silence_kept if max_silence_kept is not None else float(profile["max_silence_kept"])
                        profile.setdefault("analysis", {})["detection_method"] = "ffmpeg_silencedetect_only"
                        silences_by_source[source] = detect_silences(source_path, source_threshold, duration_for_detect)
                        if breath_edge_trim:
                            window_seconds = float(profile.get("analysis", {}).get("window_seconds", 0.02))
                            audio_levels_by_source[source] = decode_audio_levels(source_path, window_seconds=window_seconds)
                    elif silence_duration is None:
                        window_seconds = float(profile.get("analysis", {}).get("window_seconds", 0.02))
                        profile.setdefault("analysis", {})["detection_method"] = "windowed_rms_all_silence_runs"
                        levels = decode_audio_levels(source_path, window_seconds=window_seconds)
                        audio_levels_by_source[source] = levels
                        silences_by_source[source] = silence_runs_from_levels(levels, source_threshold, window_seconds)
                    else:
                        profile.setdefault("analysis", {})["detection_method"] = "ffmpeg_silencedetect_manual_duration"
                        silences_by_source[source] = detect_silences(source_path, source_threshold, source_silence_duration)
            profile = audio_profiles_by_source.get(source, {})
            front_padding = float(profile.get("front_padding", 0.0))
            back_padding = float(profile.get("back_padding", 0.0))
            source_edge_pad = float(profile.get("edge_pad", 0.0)) if edge_pad is None else float(config["edge_pad"])
            if keep_silence is not None:
                front_padding = float(keep_silence) / 2.0
                back_padding = float(keep_silence) - front_padding
            source_max_silence_kept = (
                max_silence_kept
                if max_silence_kept is not None
                else float(profile.get("max_silence_kept", profile.get("silence_duration", 0.0)))
            )
            source_min_removed_duration = (
                min_removed_duration
                if min_removed_duration is not None
                else float(profile.get("min_removed_duration", source_max_silence_kept))
            )
            pieces, cuts = split_range_on_audio_silences(
                row,
                silences_by_source[source]
                if ffmpeg_silence_only
                else sort_silence_regions(
                    [
                        *silences_by_source[source],
                        *transcript_gap_regions(row, words, source_max_silence_kept),
                    ]
                ),
                [] if ffmpeg_silence_only else words,
                front_padding=front_padding,
                back_padding=back_padding,
                max_silence_kept=source_max_silence_kept,
                min_removed_duration=source_min_removed_duration,
                edge_pad=source_edge_pad,
                min_piece=min_piece,
                allow_inside_word_audio_override=allow_inside_word_audio_override,
            )
            if not ffmpeg_silence_only:
                max_edge_silence = float(profile.get("analysis", {}).get("window_seconds", 0.02))
                trimmed_pieces: list[dict[str, Any]] = []
                for piece in pieces:
                    trimmed_piece, trim = trim_range_edges_to_words(piece, words, max_edge_silence, min_piece)
                    if trim:
                        edge_trims.append(trim)
                    levels = audio_levels_by_source.get(source)
                    if levels:
                        audio_trimmed_piece, audio_trim = trim_range_edges_to_audio(
                            trimmed_piece,
                            levels,
                            threshold_db=source_threshold,
                            window_seconds=max_edge_silence,
                            max_edge_silence=max_edge_silence,
                            min_piece=min_piece,
                            words=words,
                            max_inside_word_trim=source_max_silence_kept * 2.0,
                        )
                        trimmed_piece = audio_trimmed_piece
                        if audio_trim:
                            audio_edge_trims.append(audio_trim)
                    trimmed_pieces.append(trimmed_piece)
                pieces = trimmed_pieces
            elif breath_edge_trim:
                window_seconds = float(profile.get("analysis", {}).get("window_seconds", 0.02))
                breath_threshold = breath_threshold_db if breath_threshold_db is not None else source_threshold + 7.0
                levels = audio_levels_by_source.get(source)
                if levels:
                    trimmed_pieces = []
                    for piece in pieces:
                        trimmed_piece, audio_trim = trim_range_edges_to_audio(
                            piece,
                            levels,
                            threshold_db=breath_threshold,
                            window_seconds=window_seconds,
                            max_edge_silence=window_seconds,
                            min_piece=min_piece,
                            words=words,
                            max_inside_word_trim=max_breath_edge_trim,
                        )
                        trimmed_pieces.append(trimmed_piece)
                        if audio_trim:
                            audio_trim["breath_edge_trim"] = True
                            audio_edge_trims.append(audio_trim)
                    pieces = trimmed_pieces
        else:
            words = words_by_source.setdefault(source, load_words(edit_dir, source))
            if not words:
                untouched_no_transcript.add(source)
                new_ranges.append(row)
                continue
            pieces, cuts = split_range_on_word_gaps(
                row,
                words,
                min_gap=float(config["min_gap"]),
                keep_silence=float(config["keep_silence"]),
                edge_pad=float(config["edge_pad"]),
                min_piece=min_piece,
            )
        new_ranges.extend(pieces)
        removed_gaps.extend(cuts)

    tightened = deepcopy(edl)
    tightened["ranges"] = new_ranges
    tightened["total_duration_s"] = round(sum(float(row["end"]) - float(row["start"]) for row in new_ranges), 3)
    tightened["silence_tightening"] = {
        "mode": mode,
        "min_gap": config["min_gap"],
        "keep_silence": config["keep_silence"],
        "edge_pad": config["edge_pad"],
        "audio_tighten": audio_tighten,
        "threshold_db": threshold_db,
        "silence_duration": silence_duration if audio_tighten else None,
        "max_silence_kept": max_silence_kept if audio_tighten else None,
        "min_removed_duration": min_removed_duration if audio_tighten else None,
        "allow_inside_word_audio_override": allow_inside_word_audio_override if audio_tighten else None,
        "ffmpeg_silence_only": ffmpeg_silence_only if audio_tighten else None,
        "breath_edge_trim": breath_edge_trim if audio_tighten else None,
        "breath_threshold_db": breath_threshold_db if audio_tighten else None,
        "max_breath_edge_trim": max_breath_edge_trim if audio_tighten else None,
        "auto_audio_profiles": audio_profiles_by_source,
        "source_edl": str(edl_path),
    }

    report = {
        "mode": mode,
        "config": config,
        "original_duration_s": round(original_duration, 3),
        "new_duration_s": tightened["total_duration_s"],
        "removed_duration_s": round(original_duration - float(tightened["total_duration_s"]), 3),
        "original_ranges": len(edl.get("ranges", [])),
        "new_ranges": len(new_ranges),
        "removed_gaps": removed_gaps,
        "edge_trims": edge_trims,
        "audio_edge_trims": audio_edge_trims,
        "ffmpeg_silence_only": ffmpeg_silence_only if audio_tighten else None,
        "breath_edge_trim": breath_edge_trim if audio_tighten else None,
        "untouched_no_transcript": sorted(untouched_no_transcript),
        "untouched_no_source": sorted(untouched_no_source),
        "audio_profiles": audio_profiles_by_source,
        "overlay_warning": bool(edl.get("overlays")),
    }
    return tightened, report


def main() -> None:
    parser = argparse.ArgumentParser(description="Tighten post-decupagem EDL silences without cutting inside words.")
    parser.add_argument("edl", type=Path, nargs="?", help="Path to edl.json")
    parser.add_argument("--out", type=Path, help="Output EDL path. Defaults to edl_tight.json next to input.")
    parser.add_argument("--report", type=Path, help="Optional report JSON path.")
    parser.add_argument("--mode", choices=sorted(MODES), default="balanced")
    parser.add_argument("--min-gap", type=float, help="Only shorten transcript gaps at or above this duration.")
    parser.add_argument("--keep-silence", type=float, help="Silence left around each removed gap.")
    parser.add_argument("--edge-pad", type=float, help="Extra pad around generated child ranges.")
    parser.add_argument("--min-piece", type=float, default=0.25, help="Do not create output pieces shorter than this.")
    parser.add_argument("--audio-tighten", action="store_true", help="Split ranges using FFmpeg silencedetect instead of transcript word gaps.")
    parser.add_argument("--analyze-video", type=Path, help="Run FFmpeg volume/silence analysis on this rendered/source video.")
    parser.add_argument("--threshold-db", type=float, help="Manual silencedetect threshold override. Omit for per-source auto profile.")
    parser.add_argument("--silence-duration", type=float, help="Manual minimum silence duration override. Omit for per-source auto profile.")
    parser.add_argument("--max-silence-kept", type=float, help="Manual maximum silence length kept. Omit for per-source auto profile.")
    parser.add_argument("--min-removed-duration", type=float, help="Manual minimum duration worth removing. Omit for per-source auto profile.")
    parser.add_argument(
        "--allow-inside-word-audio-override",
        action="store_true",
        help="Allow long audio-silence cuts inside ASR word timestamps. Unsafe by default; use only after manual review.",
    )
    parser.add_argument(
        "--ffmpeg-silence-only",
        action="store_true",
        help="Use FFmpeg silencedetect regions only; skip ASR word gaps and ASR edge trimming.",
    )
    parser.add_argument(
        "--breath-edge-trim",
        action="store_true",
        help="After ffmpeg-only silence cuts, trim low-energy breath/noise from clip edges with a capped word-overlap guard.",
    )
    parser.add_argument("--breath-threshold-db", type=float, help="Manual RMS threshold for breath edge trim. Defaults to silence threshold + 7 dB.")
    parser.add_argument("--max-breath-edge-trim", type=float, default=0.18, help="Maximum seconds breath trim may enter an ASR word at a clip edge.")
    args = parser.parse_args()

    analysis: dict[str, Any] | None = None
    if args.analyze_video:
        profile = profile_silence_settings(args.analyze_video)
        threshold = args.threshold_db if args.threshold_db is not None else float(profile["threshold_db"])
        silence_duration = args.silence_duration if args.silence_duration is not None else float(profile["silence_duration"])
        analysis = {
            "video": str(args.analyze_video),
            "profile": profile,
            "threshold_db": threshold,
            "silence_duration": silence_duration,
            "silences": detect_silences(args.analyze_video, threshold, silence_duration),
        }

    if not args.edl:
        print(json.dumps(analysis or {}, ensure_ascii=False, indent=2))
        return

    tightened, report = tighten_edl(
        args.edl,
        args.mode,
        args.min_gap,
        args.keep_silence,
        args.edge_pad,
        args.min_piece,
        audio_tighten=args.audio_tighten,
        threshold_db=args.threshold_db,
        silence_duration=args.silence_duration,
        max_silence_kept=args.max_silence_kept,
        min_removed_duration=args.min_removed_duration,
        allow_inside_word_audio_override=args.allow_inside_word_audio_override,
        ffmpeg_silence_only=args.ffmpeg_silence_only,
        breath_edge_trim=args.breath_edge_trim,
        breath_threshold_db=args.breath_threshold_db,
        max_breath_edge_trim=args.max_breath_edge_trim,
    )
    if analysis is not None:
        report["ffmpeg_analysis"] = analysis

    out_path = args.out or args.edl.with_name("edl_tight.json")
    out_path.write_text(json.dumps(tightened, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    report_path = args.report or out_path.with_suffix(".report.json")
    report_path.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    print(json.dumps({"edl": str(out_path), "report": str(report_path), **report}, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
