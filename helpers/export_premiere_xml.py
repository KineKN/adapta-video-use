"""Export a video-use EDL as Premiere-importable FCP 7 XML (XMEML).

Premiere Pro imports legacy Final Cut Pro XML via File > Import. This exporter
creates an editable local handoff timeline: source media references, video cuts,
matching audio cuts, and optional rendered overlay media on higher video tracks.
Burned subtitles, FFmpeg grades, and loudness processing remain render-only
concerns unless they are first rendered as media and referenced by the EDL.

Example:
    python helpers/export_premiere_xml.py edit/edl.json -o edit/premiere_export.xml --width 1080 --height 1350
"""

from __future__ import annotations

import argparse
import json
import math
import subprocess
import xml.etree.ElementTree as ET
from dataclasses import dataclass
from pathlib import Path
from urllib.parse import quote
from xml.dom import minidom


def run_json(cmd: list[str]) -> dict:
    proc = subprocess.run(cmd, text=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=True)
    return json.loads(proc.stdout)


def parse_rate(rate_text: str | None) -> tuple[float, int, bool]:
    if not rate_text or rate_text == "0/0":
        return 30.0, 30, False
    if "/" in rate_text:
        numerator, denominator = rate_text.split("/", 1)
        fps = float(numerator) / float(denominator)
    else:
        fps = float(rate_text)

    ntsc = abs(fps - 23.976) < 0.02 or abs(fps - 29.97) < 0.02 or abs(fps - 59.94) < 0.02
    if abs(fps - 23.976) < 0.02:
        timebase = 24
    elif abs(fps - 29.97) < 0.02:
        timebase = 30
    elif abs(fps - 59.94) < 0.02:
        timebase = 60
    else:
        timebase = int(round(fps))
    return fps, timebase, ntsc


@dataclass(frozen=True)
class MediaMeta:
    duration: float
    fps: float
    timebase: int
    ntsc: bool
    width: int
    height: int
    sample_rate: int
    channels: int


@dataclass(frozen=True)
class ClipRow:
    index: int
    clip_id: str
    source_path: Path
    meta: MediaMeta
    timeline_start: int
    timeline_end: int
    source_in: int
    source_out: int
    has_audio: bool


def ffprobe_media(path: Path) -> dict:
    data = run_json(
        [
            "ffprobe",
            "-v",
            "error",
            "-print_format",
            "json",
            "-show_streams",
            "-show_format",
            str(path),
        ]
    )
    video = next((stream for stream in data.get("streams", []) if stream.get("codec_type") == "video"), {})
    audio = next((stream for stream in data.get("streams", []) if stream.get("codec_type") == "audio"), {})
    duration = float(data.get("format", {}).get("duration") or video.get("duration") or audio.get("duration") or 0)
    fps, timebase, ntsc = parse_rate(video.get("avg_frame_rate") or video.get("r_frame_rate"))
    return MediaMeta(
        duration=duration,
        fps=fps,
        timebase=timebase,
        ntsc=ntsc,
        width=int(video.get("width") or 1920),
        height=int(video.get("height") or 1080),
        sample_rate=int(audio.get("sample_rate") or 48000),
        channels=int(audio.get("channels") or 0),
    )


def seconds_to_frames(seconds: float, fps: float) -> int:
    return int(round(seconds * fps))


def seconds_to_source_in_frame(seconds: float, fps: float) -> int:
    return int(math.ceil(seconds * fps - 1e-9))


def add_text(parent: ET.Element, tag: str, text: str | int | float | bool) -> ET.Element:
    child = ET.SubElement(parent, tag)
    if isinstance(text, bool):
        child.text = "TRUE" if text else "FALSE"
    else:
        child.text = str(text)
    return child


def add_rate(parent: ET.Element, timebase: int, ntsc: bool) -> None:
    rate = ET.SubElement(parent, "rate")
    add_text(rate, "timebase", timebase)
    add_text(rate, "ntsc", ntsc)


def file_url(path: Path) -> str:
    resolved = path.resolve()
    posix = resolved.as_posix()
    if len(posix) >= 2 and posix[1] == ":":
        return "file://localhost/" + quote(posix, safe="/:")
    return "file://localhost" + quote(posix, safe="/:")


def resolve_media_path(path_text: str, edl_path: Path) -> Path:
    path = Path(path_text)
    if path.is_absolute():
        return path

    candidates = [
        edl_path.parent / path,
        edl_path.parent / "edit" / path,
        edl_path.parent.parent / path,
    ]
    for candidate in candidates:
        if candidate.exists():
            return candidate
    return candidates[0]


def add_file_element(parent: ET.Element, file_id: str, path: Path, meta: MediaMeta, duration_frames: int) -> ET.Element:
    file_el = ET.SubElement(parent, "file", id=file_id)
    add_text(file_el, "name", path.name)
    add_text(file_el, "pathurl", file_url(path))
    add_rate(file_el, int(meta.timebase), bool(meta.ntsc))
    add_text(file_el, "duration", duration_frames)

    media = ET.SubElement(file_el, "media")
    video = ET.SubElement(media, "video")
    sample = ET.SubElement(video, "samplecharacteristics")
    add_rate(sample, int(meta.timebase), bool(meta.ntsc))
    add_text(sample, "width", int(meta.width))
    add_text(sample, "height", int(meta.height))

    if meta.channels > 0:
        audio = ET.SubElement(media, "audio")
        sample_audio = ET.SubElement(audio, "samplecharacteristics")
        add_text(sample_audio, "depth", 16)
        add_text(sample_audio, "samplerate", int(meta.sample_rate))
        add_text(audio, "channelcount", int(meta.channels))
    return file_el


def add_sourcetrack(parent: ET.Element, media_type: str, track_index: int = 1) -> None:
    source_track = ET.SubElement(parent, "sourcetrack")
    add_text(source_track, "mediatype", media_type)
    add_text(source_track, "trackindex", track_index)


def add_link(parent: ET.Element, media_type: str, track_index: int, clip_index: int, group_index: int | None = None) -> None:
    link = ET.SubElement(parent, "link")
    add_text(link, "mediatype", media_type)
    add_text(link, "trackindex", track_index)
    add_text(link, "clipindex", clip_index)
    if group_index is not None:
        add_text(link, "groupindex", group_index)


def add_clipitem(
    track: ET.Element,
    clip_id: str,
    source_path: Path,
    meta: MediaMeta,
    timeline_start: int,
    timeline_end: int,
    source_in: int,
    source_out: int,
    kind: str,
    clip_index: int,
    link_audio: bool = False,
) -> None:
    duration_frames = seconds_to_frames(float(meta.duration), float(meta.fps))
    clip = ET.SubElement(track, "clipitem", id=clip_id)
    add_text(clip, "name", source_path.name)
    add_text(clip, "enabled", "TRUE")
    add_text(clip, "duration", duration_frames)
    add_rate(clip, int(meta.timebase), bool(meta.ntsc))
    add_text(clip, "start", timeline_start)
    add_text(clip, "end", timeline_end)
    add_text(clip, "in", source_in)
    add_text(clip, "out", source_out)
    add_file_element(clip, f"file-{clip_id}", source_path, meta, duration_frames)

    if kind == "video":
        add_sourcetrack(clip, "video", 1)
        if link_audio:
            add_link(clip, "video", 1, clip_index)
            add_link(clip, "audio", 1, clip_index, 1)
    if kind == "audio":
        add_sourcetrack(clip, "audio", 1)
        add_link(clip, "video", 1, clip_index)
        add_link(clip, "audio", 1, clip_index, 1)


def add_timecode(parent: ET.Element, timebase: int, ntsc: bool) -> None:
    timecode = ET.SubElement(parent, "timecode")
    add_rate(timecode, timebase, ntsc)
    add_text(timecode, "string", "00:00:00:00")
    add_text(timecode, "frame", 0)
    add_text(timecode, "displayformat", "NDF")


def prettify(root: ET.Element) -> str:
    rough = ET.tostring(root, encoding="utf-8")
    pretty = minidom.parseString(rough).toprettyxml(indent="  ", encoding="UTF-8").decode("utf-8")
    lines = [line for line in pretty.splitlines() if line.strip()]
    if lines and lines[0].startswith("<?xml"):
        lines.insert(1, "<!DOCTYPE xmeml>")
    return "\n".join(lines) + "\n"


def build_clip_rows(edl: dict, edl_path: Path, metas: dict[str, MediaMeta], sources: dict[str, Path]) -> tuple[list[ClipRow], int]:
    timeline_frames = 0
    clip_rows: list[ClipRow] = []
    for index, row in enumerate(edl.get("ranges", []), start=1):
        source_name = row["source"]
        meta = metas[source_name]
        source_path = sources[source_name]
        start_frame = seconds_to_source_in_frame(float(row["start"]), float(meta.fps))
        out_frame = seconds_to_frames(float(row["end"]), float(meta.fps))
        duration_frames = max(1, out_frame - start_frame)
        clip_rows.append(
            ClipRow(
                index=index,
                clip_id=f"cut-{index:04d}",
                source_path=source_path,
                meta=meta,
                timeline_start=timeline_frames,
                timeline_end=timeline_frames + duration_frames,
                source_in=start_frame,
                source_out=out_frame,
                has_audio=meta.channels > 0,
            )
        )
        timeline_frames += duration_frames
    return clip_rows, timeline_frames


def build_overlay_rows(edl: dict, edl_path: Path, sequence_fps: float) -> list[ClipRow]:
    overlay_rows: list[ClipRow] = []
    for index, row in enumerate(edl.get("overlays", []) or [], start=1):
        file_text = row.get("file")
        if not file_text:
            continue
        path = resolve_media_path(str(file_text), edl_path)
        if not path.exists():
            continue
        meta = ffprobe_media(path)
        start = seconds_to_frames(float(row.get("start_in_output", 0.0)), sequence_fps)
        duration_seconds = float(row.get("duration") or meta.duration)
        duration = max(1, seconds_to_frames(duration_seconds, sequence_fps))
        source_out = min(seconds_to_frames(duration_seconds, meta.fps), seconds_to_frames(meta.duration, meta.fps))
        overlay_rows.append(
            ClipRow(
                index=index,
                clip_id=f"overlay-{index:04d}",
                source_path=path,
                meta=meta,
                timeline_start=start,
                timeline_end=start + duration,
                source_in=0,
                source_out=max(1, source_out),
                has_audio=False,
            )
        )
    return overlay_rows


def export_xml(
    edl_path: Path,
    out_path: Path,
    sequence_name: str | None = None,
    width: int | None = None,
    height: int | None = None,
    include_overlays: bool = True,
) -> dict:
    edl = json.loads(edl_path.read_text(encoding="utf-8"))
    sources = {name: Path(path) for name, path in edl.get("sources", {}).items()}
    if not sources:
        raise ValueError("EDL has no sources")

    metas = {name: ffprobe_media(path) for name, path in sources.items()}
    primary_meta = metas[next(iter(metas))]
    fps = float(primary_meta.fps)
    timebase = int(primary_meta.timebase)
    ntsc = bool(primary_meta.ntsc)
    sequence_width = int(width or edl.get("width") or edl.get("sequence_width") or primary_meta.width)
    sequence_height = int(height or edl.get("height") or edl.get("sequence_height") or primary_meta.height)

    clip_rows, timeline_frames = build_clip_rows(edl, edl_path, metas, sources)
    overlay_rows = build_overlay_rows(edl, edl_path, fps) if include_overlays else []

    root = ET.Element("xmeml", version="4")
    project = ET.SubElement(root, "project")
    add_text(project, "name", sequence_name or f"{edl_path.stem}_premiere_project")
    children = ET.SubElement(project, "children")
    sequence = ET.SubElement(children, "sequence", id="sequence-1")
    add_text(sequence, "name", sequence_name or f"{edl_path.stem}_premiere")
    add_text(sequence, "duration", timeline_frames)
    add_rate(sequence, timebase, ntsc)
    add_timecode(sequence, timebase, ntsc)

    media = ET.SubElement(sequence, "media")
    video = ET.SubElement(media, "video")
    fmt = ET.SubElement(video, "format")
    sample = ET.SubElement(fmt, "samplecharacteristics")
    add_rate(sample, timebase, ntsc)
    add_text(sample, "width", sequence_width)
    add_text(sample, "height", sequence_height)
    video_track = ET.SubElement(video, "track")
    overlay_track = ET.SubElement(video, "track") if overlay_rows else None

    audio = ET.SubElement(media, "audio")
    add_text(audio, "numOutputChannels", max(1, int(primary_meta.channels or 2)))
    audio_track = ET.SubElement(audio, "track")

    for row in clip_rows:
        add_clipitem(
            video_track,
            f"video-{row.clip_id}",
            row.source_path,
            row.meta,
            row.timeline_start,
            row.timeline_end,
            row.source_in,
            row.source_out,
            "video",
            row.index,
            link_audio=row.has_audio,
        )
        if row.has_audio:
            add_clipitem(
                audio_track,
                f"audio-{row.clip_id}",
                row.source_path,
                row.meta,
                row.timeline_start,
                row.timeline_end,
                row.source_in,
                row.source_out,
                "audio",
                row.index,
            )

    if overlay_track is not None:
        for row in overlay_rows:
            add_clipitem(
                overlay_track,
                f"video-{row.clip_id}",
                row.source_path,
                row.meta,
                row.timeline_start,
                row.timeline_end,
                row.source_in,
                row.source_out,
                "video",
                row.index,
                link_audio=False,
            )

    out_path.write_text(prettify(root), encoding="utf-8")
    return {
        "xml": str(out_path),
        "sequence_name": sequence_name or f"{edl_path.stem}_premiere",
        "clips": len(clip_rows),
        "overlay_clips": len(overlay_rows),
        "duration_frames": timeline_frames,
        "duration_s": round(timeline_frames / fps, 3) if fps else None,
        "fps": round(fps, 3),
        "width": sequence_width,
        "height": sequence_height,
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="Export video-use EDL to Premiere-importable FCP 7 XML/XMEML.")
    parser.add_argument("edl", type=Path, help="Path to edl.json")
    parser.add_argument("-o", "--out", type=Path, help="Output XML path. Defaults to premiere_export.xml next to EDL.")
    parser.add_argument("--sequence-name", help="Premiere sequence name")
    parser.add_argument("--width", type=int, help="Sequence width. Defaults to EDL/source width.")
    parser.add_argument("--height", type=int, help="Sequence height. Defaults to EDL/source height.")
    parser.add_argument("--no-overlays", action="store_true", help="Do not include rendered overlay media from EDL overlays.")
    args = parser.parse_args()

    out_path = args.out or args.edl.with_name("premiere_export.xml")
    result = export_xml(
        args.edl,
        out_path,
        args.sequence_name,
        width=args.width,
        height=args.height,
        include_overlays=not args.no_overlays,
    )
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
