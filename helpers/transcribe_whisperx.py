"""Local WhisperX transcription wrapper for ad editing workflows.

This provides a local fallback to ElevenLabs for batch work and offline study.

Usage:
    python helpers/transcribe_whisperx.py input.mp4
    python helpers/transcribe_whisperx.py input.mp4 --model large-v3 --language pt
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path

import whisperx


def main() -> None:
    parser = argparse.ArgumentParser(description="Transcribe media locally with WhisperX.")
    parser.add_argument("input", help="Input media file")
    parser.add_argument("--output", help="Output JSON path")
    parser.add_argument("--model", default="large-v3", help="Whisper model name")
    parser.add_argument("--language", default=None, help="Optional language code, e.g. pt")
    parser.add_argument("--batch-size", type=int, default=8)
    parser.add_argument("--compute-type", default="float16")
    parser.add_argument("--device", default="cuda")
    args = parser.parse_args()

    input_path = Path(args.input)
    output_path = Path(args.output) if args.output else input_path.with_suffix(".whisperx.json")

    audio = whisperx.load_audio(str(input_path))
    model = whisperx.load_model(
        args.model,
        args.device,
        compute_type=args.compute_type,
        language=args.language,
    )
    result = model.transcribe(audio, batch_size=args.batch_size)

    align_model, metadata = whisperx.load_align_model(
        language_code=result["language"],
        device=args.device,
    )
    result = whisperx.align(
        result["segments"],
        align_model,
        metadata,
        audio,
        args.device,
        return_char_alignments=False,
    )

    payload = {
        "source": str(input_path),
        "engine": "whisperx",
        "model": args.model,
        "language": result.get("language"),
        "segments": result.get("segments", []),
    }
    output_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"saved: {output_path}")


if __name__ == "__main__":
    main()
