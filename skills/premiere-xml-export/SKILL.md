---
name: premiere-xml-export
description: Use when a video-use edit needs to be opened in Adobe Premiere Pro as an editable timeline, handed off to an editor, or exported as XML instead of only rendered MP4.
---

# Premiere XML Export

## Principle

Export an editable local timeline, not a baked master. Use `helpers/export_premiere_xml.py` to write legacy Final Cut Pro 7 XML/XMEML that Premiere can import through `File > Import`; keep final MP4 renders for burned subtitles, grade, and loudness unless those elements were rendered as separate media and referenced as overlays.

Do not require Premiere MCP, CEP panels, or a running Premiere Pro instance. XML generation is a local file export step.

## Workflow

```bash
python helpers/export_premiere_xml.py edit/edl.json -o edit/premiere_export.xml --sequence-name My_Edit
python helpers/export_premiere_xml.py edit/edl.json -o edit/premiere_export.xml --sequence-name My_Edit --width 1080 --height 1350
```

Then in Premiere Pro: `File > Import`, choose `premiere_export.xml`, open the imported sequence, and relink media if Premiere asks.

## What Carries Over

- Source media references through local `pathurl`
- Video clip in/out points
- Matching audio clip in/out points, linked to video clipitems
- Timeline order and cut timing
- Rendered overlay media from `edl.overlays[]` as a higher video track when the overlay file exists

## What Does Not Reliably Carry Over

- Burned subtitles and ASS styling
- FFmpeg grades and loudness normalization
- HyperFrames/Remotion/Manim overlays unless they are rendered first and included in `edl.overlays[]`
- video-use reasoning metadata beyond clip names and sequence structure

## Format Notes

- Premiere imports the legacy FCP 7 XML/XMEML family, not modern `.fcpxml` from Final Cut Pro X without conversion.
- Use `xmeml` sequence/media/track/clipitem/file/pathurl structures; `pathurl` must point at local media.
- Keep the XML conservative: cuts, media references, timing, and simple overlay tracks. Complex effects are not a reliable XML handoff surface.

## QC

After generating, parse the XML locally to catch malformed output. After import, compare Premiere sequence duration against `total_duration_s` from the EDL and the rendered preview. If duration differs by more than a frame or two, inspect frame rate assumptions and regenerate XML.
