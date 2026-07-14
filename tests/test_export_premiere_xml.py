from __future__ import annotations

import json
import shutil
import subprocess
import tempfile
import unittest
import xml.etree.ElementTree as ET
from pathlib import Path

from helpers.export_premiere_xml import export_xml, seconds_to_source_in_frame


class PremiereXmlExportTest(unittest.TestCase):
    def setUp(self) -> None:
        if not shutil.which("ffmpeg") or not shutil.which("ffprobe"):
            self.skipTest("ffmpeg/ffprobe required")
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name)

    def tearDown(self) -> None:
        self.tmp.cleanup()

    def _make_video(self, path: Path, duration: float, with_audio: bool = True) -> None:
        cmd = [
            "ffmpeg",
            "-hide_banner",
            "-loglevel",
            "error",
            "-y",
            "-f",
            "lavfi",
            "-i",
            f"color=c=black:s=320x240:r=30000/1001:d={duration}",
        ]
        if with_audio:
            cmd += ["-f", "lavfi", "-i", f"anullsrc=channel_layout=stereo:sample_rate=48000:d={duration}", "-shortest"]
        cmd += ["-c:v", "libx264", "-pix_fmt", "yuv420p", "-c:a", "aac", str(path)]
        subprocess.run(cmd, check=True)

    def test_exports_premiere_xmeml_with_overlay_track(self) -> None:
        source = self.root / "source.mp4"
        overlay = self.root / "overlay.mov"
        self._make_video(source, 4.0, with_audio=True)
        self._make_video(overlay, 2.0, with_audio=False)

        edl = {
            "version": 1,
            "sources": {"A": str(source)},
            "ranges": [
                {"source": "A", "start": 0.0, "end": 1.0},
                {"source": "A", "start": 2.0, "end": 3.0},
            ],
            "overlays": [{"file": str(overlay), "start_in_output": 0.5, "duration": 1.0}],
        }
        edl_path = self.root / "edl.json"
        out_path = self.root / "premiere.xml"
        edl_path.write_text(json.dumps(edl), encoding="utf-8")

        result = export_xml(edl_path, out_path, "Unit_Test", width=1080, height=1350)

        self.assertEqual(result["clips"], 2)
        self.assertEqual(result["overlay_clips"], 1)
        tree = ET.parse(out_path)
        sequence = tree.getroot().find("./project/children/sequence")
        self.assertIsNotNone(sequence)
        self.assertEqual(sequence.findtext("name"), "Unit_Test")
        self.assertEqual(sequence.findtext("./media/video/format/samplecharacteristics/width"), "1080")
        self.assertEqual(sequence.findtext("./media/video/format/samplecharacteristics/height"), "1350")
        video_tracks = sequence.findall("./media/video/track")
        audio_tracks = sequence.findall("./media/audio/track")
        self.assertEqual([len(track.findall("clipitem")) for track in video_tracks], [2, 1])
        self.assertEqual([len(track.findall("clipitem")) for track in audio_tracks], [2])
        self.assertTrue(out_path.read_text(encoding="utf-8").startswith('<?xml version="1.0" encoding="UTF-8"?>\n<!DOCTYPE xmeml>'))

    def test_source_in_frame_never_rounds_before_requested_time(self) -> None:
        fps = 30000 / 1001

        self.assertEqual(seconds_to_source_in_frame(92.34, fps), 2768)


if __name__ == "__main__":
    unittest.main()
