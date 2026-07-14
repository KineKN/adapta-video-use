---
name: remove-silence-post
description: Use when a video-use edit is already decupado and the user asks for tighter pacing, shorter pauses, dynamic cuts, remove silence, or a faster ad rhythm.
---

# Remove Silence Post

## Principle

Silence removal is a post-decupagem pass. First remove wrong takes, repetitions, non-ad material, and broken copy. Only then tighten dead air without changing the copy order or cutting inside words.

## Workflow

1. Start from the approved `edit/edl.json`, not from raw footage.
2. Pick pacing: `gentle`, `balanced`, or `tight`. For ads, default to `balanced`; use `tight` when the user explicitly wants fast/short cuts, Phantom-like density, or shows residual silence in Premiere.
3. Run:

```bash
python helpers/remove_silence.py edit/edl.json --mode balanced --out edit/edl_tight.json
python helpers/remove_silence.py edit/edl.json --audio-tighten --out edit/edl_audio_tight.json
python helpers/remove_silence.py edit/edl.json --audio-tighten --mode tight --out edit/edl_audio_tight.json
python helpers/remove_silence.py edit/edl.json --audio-tighten --mode tight --ffmpeg-silence-only --threshold-db -45 --keep-silence 0.04 --out edit/edl_ffmpeg_tight.json
python helpers/remove_silence.py edit/edl.json --audio-tighten --mode tight --ffmpeg-silence-only --threshold-db -45 --max-silence-kept 0.12 --min-removed-duration 0.12 --keep-silence 0.04 --breath-edge-trim --breath-threshold-db -40 --max-breath-edge-trim 0.18 --out edit/edl_ffmpeg_breath_tight.json
python helpers/edl_boundary_audit.py edit/edl_tight.json
python helpers/render.py edit/edl_tight.json -o edit/preview_tight.mp4 --preview
```

4. Inspect/listen to every new boundary created by the tool. If a phrase onset leaks or the rhythm feels chopped, switch to `gentle` or override `--min-gap` / `--keep-silence`.
5. Render final only after semantic QC still passes.

## Tool Notes

- `remove_silence.py` uses word-level transcripts to split EDL ranges on real gaps, preserving word boundaries.
- `--audio-tighten` profiles each source from the already-decupado EDL ranges, not from the whole bruto. It derives threshold from the loud end of non-word gaps, then derives minimum silence duration, maximum silence length kept, minimum removable duration, and padding from detected silence-run distribution. This is meant to behave closer to Phantom Cut than a conservative transcript-only pass.
- `--mode` affects audio-tighten profiling. `balanced` uses a stricter upper pause percentile; `tight` keeps less silence by selecting a lower pause percentile from the same audio distribution. This is still per-video auto profiling, not a universal seconds value.
- Audio-tighten combines waveform silence candidates with transcript word-gap candidates. This catches real room-tone/breath gaps that are not quiet enough for the RMS threshold but are clearly not spoken words.
- Use `--ffmpeg-silence-only` when matching Phantom-style silence removal. It skips ASR word gaps and ASR edge trims completely, using only FFmpeg `silencedetect` regions over the already-decupado EDL ranges.
- For ffmpeg-only mode, prefer a conservative threshold first, for example `--threshold-db -45 --keep-silence 0.04`, then tighten only after listening. A high threshold can treat low-energy speech as silence.
- Use `--breath-edge-trim` only as a second layer on ffmpeg-only output when breathing/low-energy room tone remains at clip edges. This is not silence detection; it trims low-energy audio at the beginning/end of each post-silence piece and keeps `--max-breath-edge-trim` as a hard cap for entering a transcript word.
- For breath-edge, start conservative: `--breath-threshold-db -40 --max-breath-edge-trim 0.18`. Raise/lower only after inspecting the exact boundaries the user complained about. CTA endings and final words such as "grupo" or "embaixo" are mandatory review points.
- Audio-tighten also trims range edges to the first/last transcript word with only one audio-analysis window of preserved edge air. This prevents already-decupado boundaries from keeping several frames of dead air between clips.
- Audio-tighten runs a second edge trim by audio energy after word-edge trim. This catches silent phrase tails inside inflated ASR word timestamps, such as a word ending on paper later than the actual voiced audio. The trim is capped so it cannot cut deeply into a word.
- Never accept 1-frame, 2-frame, or near-invisible silence cuts. A detected silence is only split when the full silence is longer than the profiled `max_silence_kept` and the actual removed span after word-boundary protection is at least the profiled `min_removed_duration`.
- `inside_word` is a blocker in automatic/lote mode. Long continuous waveform silence inside an inflated ASR word may look removable, but it can cut real speech; only use `--allow-inside-word-audio-override` after manual review of that exact boundary.
- Breath/filler before speech should be cut by transcript-aware edge trimming: preserve words, not pre-word breathing. Premiere XML export rounds source-in upward so the imported timeline does not reintroduce pre-roll silence before the first spoken frame.
- `--threshold-db`, `--silence-duration`, `--max-silence-kept`, `--min-removed-duration`, `--keep-silence`, and `--edge-pad` are manual overrides for reproducing a user/tool setting. Do not use them as defaults and do not bake a universal dB value into a workflow.
- `--analyze-video <mp4>` runs the same auto profile plus FFmpeg `silencedetect` so the agent can inspect the detected regions before editing.
- Do not apply this to a rendered `final.mp4` as the source of truth unless no EDL/transcript exists; it should produce a cleaner EDL before render.

## Failure Modes

- If overlays already exist, tightening the EDL can desync animation timing. Prefer tightening before building overlays.
- If transcript is missing, the tool leaves that source untouched. Transcribe or use visual/audio inspection manually.
- Do not remove meaningful rhetorical pauses in premium or authority-heavy ads; silence can be persuasive.
- Audio-threshold detection can mark low-energy consonants, breaths, or room-tone transitions as silence. Always run `edl_boundary_audit.py`; `inside_word` is a blocker, while `too_close_to_*` is a review flag for tight Phantom-like pacing.
