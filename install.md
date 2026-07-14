---
name: adapta-video-use-install
description: Install adapta-video-use into the current agent and wire up Python, ffmpeg, optional Node, and transcription credentials.
---

# adapta-video-use install

Use this file for first-time install or reconnect. For complete VM/setup instructions, read `AGENT_SETUP.md`. For daily editing behavior, read `SKILL.md`.

## What This Installs

`adapta-video-use` is an agent-ready fork of `video-use`.

It includes:

- core video-use helpers in `helpers/`;
- central operating instructions in `SKILL.md`;
- agent persona files in `agent/`;
- ad-editing skills and consolidated corpus memory in `skills/`;
- Premiere XML handoff through `helpers/export_premiere_xml.py`.

## Requirements

Required:

- Python `>=3.10` (`3.11` recommended);
- `ffmpeg` and `ffprobe`;
- Python deps from `pyproject.toml`;
- ElevenLabs API key only when transcription is needed.

Optional:

- Node.js `22+` for HyperFrames/Remotion animation work;
- `yt-dlp` for URL downloads;
- Manim for mathematical/technical animation;
- WhisperX/NLP local stack for offline ASR/corpus work.

## Clone

```bash
git clone https://github.com/KineKN/adapta-video-use.git ~/Developer/adapta-video-use
cd ~/Developer/adapta-video-use
```

If already cloned:

```bash
cd ~/Developer/adapta-video-use
git pull --ff-only
```

## Install Python Deps

```bash
python -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
pip install -e .
```

Or with `uv`:

```bash
uv sync
```

## Install ffmpeg

macOS:

```bash
brew install ffmpeg
```

Ubuntu/Debian:

```bash
sudo apt-get update
sudo apt-get install -y ffmpeg
```

Alpine:

```bash
apk add ffmpeg
```

## Configure ElevenLabs

Only needed for `helpers/transcribe.py`.

Create `.env` at repo root:

```bash
ELEVENLABS_API_KEY=your_key_here
```

Never commit `.env`.

## Register With An Agent

Register the whole repo directory, not only `SKILL.md`, because the skill depends on sibling `helpers/` and `skills/`.

Claude Code:

```bash
mkdir -p ~/.claude/skills
ln -sfn ~/Developer/adapta-video-use ~/.claude/skills/video-use
```

Codex:

```bash
mkdir -p "${CODEX_HOME:-$HOME/.codex}/skills"
ln -sfn ~/Developer/adapta-video-use "${CODEX_HOME:-$HOME/.codex}/skills/video-use"
```

Hermes/OpenClaw/other agents:

- import `agent/Main.md` as the main system prompt when the platform supports prompt fields;
- import `agent/persona/SOUL.md`, `agent/persona/IDENTITY.md`, and `agent/persona/USER.md` when the platform supports advanced persona files;
- make `SKILL.md`, `helpers/`, and `skills/` available to the agent in the same repo checkout.

## Verify

```bash
python helpers/transcribe.py --help
python helpers/transcribe_batch.py --help
python helpers/pack_transcripts.py --help
python helpers/render.py --help
python helpers/grade.py --help
python helpers/remove_silence.py --help
python helpers/edl_boundary_audit.py --help
python helpers/export_premiere_xml.py --help
ffmpeg -version
ffprobe -version
```

Optional if `matplotlib`/`librosa` are installed correctly:

```bash
python helpers/timeline_view.py --help
```

## What Not To Version

Do not commit:

- `.env`;
- `.venv/`, `.venv_ads/`, `node_modules/`;
- source videos, previews, renders, `edit/`;
- raw `Anuncios/` corpus;
- `blind_tests/`;
- local MCP or Premiere bridge folders.

The portable ad-editing memory is already in `skills/ad-corpus-study/references/`.
