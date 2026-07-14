from __future__ import annotations

import json
import shutil
import subprocess
import tempfile
import unittest
from pathlib import Path

from helpers.remove_silence import (
    profile_silence_settings,
    sort_silence_regions,
    split_range_on_audio_silences,
    tighten_edl,
    trim_range_edges_to_audio,
    trim_range_edges_to_words,
    transcript_gap_regions,
)


class RemoveSilenceAutoProfileTest(unittest.TestCase):
    def setUp(self) -> None:
        if not shutil.which("ffmpeg") or not shutil.which("ffprobe"):
            self.skipTest("ffmpeg/ffprobe required")
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name)

    def tearDown(self) -> None:
        self.tmp.cleanup()

    def _make_profile_fixture(self, path: Path) -> None:
        cmd = [
            "ffmpeg",
            "-hide_banner",
            "-loglevel",
            "error",
            "-y",
            "-f",
            "lavfi",
            "-i",
            "sine=frequency=440:duration=0.6",
            "-f",
            "lavfi",
            "-i",
            "anullsrc=channel_layout=mono:sample_rate=48000:duration=0.3",
            "-f",
            "lavfi",
            "-i",
            "sine=frequency=440:duration=0.6",
            "-filter_complex",
            "[0:a][1:a][2:a]concat=n=3:v=0:a=1[a]",
            "-map",
            "[a]",
            str(path),
        ]
        subprocess.run(cmd, check=True)

    def test_profile_derives_threshold_from_audio_and_transcript(self) -> None:
        media = self.root / "voice_gap.wav"
        self._make_profile_fixture(media)
        ranges = [{"start": 0.0, "end": 1.5}]
        words = [
            {"type": "word", "text": "one", "start": 0.0, "end": 0.55},
            {"type": "word", "text": "two", "start": 0.95, "end": 1.5},
        ]

        profile = profile_silence_settings(media, ranges, words)

        self.assertEqual(profile["analysis"]["profile_scope"], "edl_ranges")
        self.assertEqual(profile["analysis"]["threshold_method"], "non_word_gap_upper_quartile")
        self.assertIsInstance(profile["threshold_db"], float)
        self.assertGreater(profile["silence_duration"], 0)
        self.assertGreaterEqual(profile["max_silence_kept"], profile["silence_duration"])
        self.assertGreater(profile["min_removed_duration"], 0)
        self.assertGreaterEqual(profile["min_removed_duration"], profile["max_silence_kept"])

    def test_tight_profile_keeps_less_silence_than_balanced(self) -> None:
        media = self.root / "voice_gap.wav"
        self._make_profile_fixture(media)
        ranges = [{"start": 0.0, "end": 1.5}]
        words = [
            {"type": "word", "text": "one", "start": 0.0, "end": 0.55},
            {"type": "word", "text": "two", "start": 0.95, "end": 1.5},
        ]

        balanced = profile_silence_settings(media, ranges, words, mode="balanced")
        tight = profile_silence_settings(media, ranges, words, mode="tight")

        self.assertLessEqual(tight["max_silence_kept"], balanced["max_silence_kept"])
        self.assertGreaterEqual(tight["min_removed_duration"], tight["max_silence_kept"])

    def test_audio_tighten_records_auto_profile_without_manual_threshold(self) -> None:
        media = self.root / "voice_gap.wav"
        self._make_profile_fixture(media)
        edit_dir = self.root / "edit"
        transcripts = edit_dir / "transcripts"
        transcripts.mkdir(parents=True)
        edl_path = edit_dir / "edl.json"
        edl_path.write_text(
            json.dumps(
                {
                    "version": 1,
                    "sources": {"A": str(media)},
                    "ranges": [{"source": "A", "start": 0.0, "end": 1.5, "beat": "TEST"}],
                }
            ),
            encoding="utf-8",
        )
        (transcripts / "A.json").write_text(
            json.dumps(
                {
                    "words": [
                        {"type": "word", "text": "one", "start": 0.0, "end": 0.55},
                        {"type": "word", "text": "two", "start": 0.95, "end": 1.5},
                    ]
                }
            ),
            encoding="utf-8",
        )

        _, report = tighten_edl(
            edl_path,
            mode="balanced",
            min_gap=None,
            keep_silence=None,
            edge_pad=None,
            min_piece=0.1,
            audio_tighten=True,
            threshold_db=None,
            silence_duration=None,
        )

        self.assertIn("A", report["audio_profiles"])
        self.assertIsNone(report["config"].get("manual_threshold_db"))
        self.assertGreaterEqual(report["new_ranges"], 1)
        profile = report["audio_profiles"]["A"]
        for gap in report["removed_gaps"]:
            self.assertGreaterEqual(gap["removed_s"], profile["min_removed_duration"] - 0.001)

    def test_ffmpeg_silence_only_ignores_asr_word_protection_and_edge_trims(self) -> None:
        media = self.root / "voice_gap.wav"
        self._make_profile_fixture(media)
        edit_dir = self.root / "edit_ffmpeg_only"
        transcripts = edit_dir / "transcripts"
        transcripts.mkdir(parents=True)
        edl_path = edit_dir / "edl.json"
        edl_path.write_text(
            json.dumps(
                {
                    "version": 1,
                    "sources": {"A": str(media)},
                    "ranges": [{"source": "A", "start": 0.0, "end": 1.5, "beat": "TEST"}],
                }
            ),
            encoding="utf-8",
        )
        (transcripts / "A.json").write_text(
            json.dumps(
                {
                    "words": [
                        {"type": "word", "text": "inflated", "start": 0.0, "end": 1.5},
                    ]
                }
            ),
            encoding="utf-8",
        )

        _, report = tighten_edl(
            edl_path,
            mode="tight",
            min_gap=None,
            keep_silence=0.04,
            edge_pad=None,
            min_piece=0.1,
            audio_tighten=True,
            threshold_db=-45.0,
            silence_duration=0.12,
            max_silence_kept=0.12,
            min_removed_duration=0.12,
            ffmpeg_silence_only=True,
        )

        self.assertTrue(report["ffmpeg_silence_only"])
        self.assertGreater(len(report["removed_gaps"]), 0)
        self.assertEqual(report["edge_trims"], [])

    def test_ffmpeg_silence_only_can_breath_trim_clip_edges_with_cap(self) -> None:
        media = self.root / "voice_breath_tail.wav"
        subprocess.run(
            [
                "ffmpeg",
                "-hide_banner",
                "-loglevel",
                "error",
                "-y",
                "-f",
                "lavfi",
                "-i",
                "sine=frequency=440:duration=0.6",
                "-f",
                "lavfi",
                "-i",
                "sine=frequency=440:duration=0.3",
                "-filter_complex",
                "[1:a]volume=0.1[breath];[0:a][breath]concat=n=2:v=0:a=1[a]",
                "-map",
                "[a]",
                str(media),
            ],
            check=True,
        )
        edit_dir = self.root / "edit_breath"
        transcripts = edit_dir / "transcripts"
        transcripts.mkdir(parents=True)
        edl_path = edit_dir / "edl.json"
        edl_path.write_text(
            json.dumps(
                {
                    "version": 1,
                    "sources": {"A": str(media)},
                    "ranges": [{"source": "A", "start": 0.0, "end": 0.9, "beat": "TEST"}],
                }
            ),
            encoding="utf-8",
        )
        (transcripts / "A.json").write_text(
            json.dumps({"words": [{"type": "word", "text": "tail", "start": 0.1, "end": 0.74}]}),
            encoding="utf-8",
        )

        edl, report = tighten_edl(
            edl_path,
            mode="tight",
            min_gap=None,
            keep_silence=0.04,
            edge_pad=None,
            min_piece=0.1,
            audio_tighten=True,
            threshold_db=-45.0,
            silence_duration=0.12,
            max_silence_kept=0.12,
            min_removed_duration=0.12,
            ffmpeg_silence_only=True,
            breath_edge_trim=True,
            breath_threshold_db=-38.0,
            max_breath_edge_trim=0.18,
        )

        self.assertTrue(report["breath_edge_trim"])
        self.assertGreater(len(report["audio_edge_trims"]), 0)
        self.assertLess(edl["ranges"][0]["end"], 0.9)

    def test_transcript_gap_regions_catch_room_tone_pauses(self) -> None:
        row = {"start": 10.0, "end": 12.0}
        words = [
            {"type": "word", "text": "one", "start": 10.0, "end": 10.5},
            {"type": "word", "text": "two", "start": 10.74, "end": 11.0},
            {"type": "word", "text": "three", "start": 11.1, "end": 12.0},
        ]

        regions = transcript_gap_regions(row, words, min_gap=0.16)

        self.assertEqual(regions, [{"start": 10.5, "end": 10.74, "duration": 0.24}])

    def test_trim_range_edges_to_words_removes_boundary_air(self) -> None:
        row = {"source": "A", "start": 10.0, "end": 12.0, "beat": "TEST"}
        words = [
            {"type": "word", "text": "first", "start": 10.2, "end": 10.5},
            {"type": "word", "text": "last", "start": 11.2, "end": 11.7},
        ]

        trimmed, trim = trim_range_edges_to_words(row, words, max_edge_silence=0.02, min_piece=0.25)

        self.assertEqual(trimmed["start"], 10.18)
        self.assertEqual(trimmed["end"], 11.72)
        self.assertEqual(trim["trim_start_s"], 0.18)
        self.assertEqual(trim["trim_end_s"], 0.28)

    def test_trim_range_edges_to_audio_removes_silent_tail_after_words(self) -> None:
        row = {"source": "A", "start": 0.0, "end": 1.0, "beat": "TEST"}
        levels = [-20.0] * 30 + [-70.0] * 20
        words = [{"type": "word", "text": "last", "start": 0.1, "end": 0.8}]

        trimmed, trim = trim_range_edges_to_audio(
            row,
            levels,
            threshold_db=-32.0,
            window_seconds=0.02,
            max_edge_silence=0.02,
            min_piece=0.25,
            words=words,
            max_inside_word_trim=0.2,
        )

        self.assertEqual(trimmed["end"], 0.62)
        self.assertTrue(trimmed["allow_end_inside_word_audio_silence"])
        self.assertEqual(trim["trim_end_s"], 0.38)

    def test_trim_range_edges_to_audio_rejects_deep_word_cut(self) -> None:
        row = {"source": "A", "start": 0.0, "end": 1.0, "beat": "TEST"}
        levels = [-20.0] * 30 + [-70.0] * 20
        words = [{"type": "word", "text": "last", "start": 0.45, "end": 0.95}]

        trimmed, trim = trim_range_edges_to_audio(
            row,
            levels,
            threshold_db=-32.0,
            window_seconds=0.02,
            max_edge_silence=0.02,
            min_piece=0.25,
            words=words,
            max_inside_word_trim=0.2,
        )

        self.assertEqual(trimmed, row)
        self.assertEqual(trim, {})

    def test_transcript_gap_survives_rejected_audio_region(self) -> None:
        row = {"source": "A", "start": 0.0, "end": 2.0, "beat": "TEST"}
        words = [
            {"type": "word", "text": "one", "start": 0.2, "end": 0.8},
            {"type": "word", "text": "two", "start": 1.1, "end": 1.4},
        ]
        broad_audio_region = {"start": 0.4, "end": 1.1, "duration": 0.7}
        transcript_regions = transcript_gap_regions(row, words, min_gap=0.16)

        _, cuts = split_range_on_audio_silences(
            row,
            sort_silence_regions([broad_audio_region, *transcript_regions]),
            words,
            front_padding=0.04,
            back_padding=0.04,
            max_silence_kept=0.2,
            min_removed_duration=0.08,
            edge_pad=0.0,
            min_piece=0.1,
        )

        self.assertEqual(len(cuts), 1)
        self.assertEqual(cuts[0]["remove_start"], 0.84)
        self.assertEqual(cuts[0]["remove_end"], 1.06)

    def test_rejects_two_frame_silence_cuts(self) -> None:
        row = {"source": "A", "start": 0.0, "end": 2.0, "beat": "TEST"}
        words = [
            {"type": "word", "text": "one", "start": 0.2, "end": 0.8},
            {"type": "word", "text": "two", "start": 1.0, "end": 1.4},
        ]

        _, cuts = split_range_on_audio_silences(
            row,
            [{"start": 0.8, "end": 0.94, "duration": 0.14}],
            words,
            front_padding=0.04,
            back_padding=0.04,
            max_silence_kept=0.12,
            min_removed_duration=0.12,
            edge_pad=0.0,
            min_piece=0.1,
        )

        self.assertEqual(cuts, [])

    def test_rejects_long_audio_silence_inside_asr_word_by_default(self) -> None:
        row = {"source": "A", "start": 0.0, "end": 3.0, "beat": "TEST"}
        words = [
            {"type": "word", "text": "inflated", "start": 0.5, "end": 1.4},
            {"type": "word", "text": "next", "start": 2.0, "end": 2.3},
        ]

        _, cuts = split_range_on_audio_silences(
            row,
            [{"start": 0.9, "end": 1.6, "duration": 0.7}],
            words,
            front_padding=0.04,
            back_padding=0.04,
            max_silence_kept=0.12,
            min_removed_duration=0.12,
            edge_pad=0.0,
            min_piece=0.1,
        )

        self.assertEqual(cuts, [])

    def test_marks_long_audio_silence_inside_inflated_asr_word_when_explicitly_allowed(self) -> None:
        row = {"source": "A", "start": 0.0, "end": 3.0, "beat": "TEST"}
        words = [
            {"type": "word", "text": "inflated", "start": 0.5, "end": 1.4},
            {"type": "word", "text": "next", "start": 2.0, "end": 2.3},
        ]

        _, cuts = split_range_on_audio_silences(
            row,
            [{"start": 0.9, "end": 1.6, "duration": 0.7}],
            words,
            front_padding=0.04,
            back_padding=0.04,
            max_silence_kept=0.12,
            min_removed_duration=0.12,
            edge_pad=0.0,
            min_piece=0.1,
            allow_inside_word_audio_override=True,
        )

        self.assertEqual(len(cuts), 1)
        self.assertTrue(cuts[0]["inside_word_audio_override"])
        self.assertGreaterEqual(cuts[0]["removed_s"], 0.12)


if __name__ == "__main__":
    unittest.main()
