---
name: ad-local-asr-nlp
description: Use when working on ad decupagem in this repo and you need the local CUDA transcription and NLP stack for fallback ASR, repetition detection, corpus study, or batch preparation.
---

# Ad Local ASR NLP

## Overview

This repo has a local ad-analysis environment at `.venv_ads`.

Use it when ElevenLabs is unavailable, expensive for batch work, or insufficient for offline study.

## Stack

- `torch 2.8.0+cu128`
- `whisperx`
- `transformers`
- `rapidfuzz`
- `sentence-transformers`
- `pandas`
- `scikit-learn`
- `spacy`

## Verified State

- CUDA is available in `.venv_ads`
- WhisperX wrapper works on a real sample clip
- MPNet-based semantic dedup works in `.venv_ads`
- NLP stack imports cleanly

## Commands

### Activate

PowerShell:

```powershell
.\\.venv_ads\\Scripts\\Activate.ps1
```

### WhisperX transcription

```powershell
.\\.venv_ads\\Scripts\\python.exe helpers/transcribe_whisperx.py input.mp4 --model small --language pt
```

### Semantic dedup

```powershell
.\\.venv_ads\\Scripts\\python.exe helpers/anuncios_semantic_dedup.py path\\to\\AdXXXX_Bruto.txt
```

Default wrapper behavior:

- loads audio in memory
- transcribes with WhisperX
- runs alignment
- saves JSON

## Known Limitation

`pyannote` may warn about missing `torchcodec` on Windows.

Current status:

- this does not block the wrapper, because the wrapper preloads audio with WhisperX
- treat it as a warning, not a hard failure

## Use Cases

- batch fallback transcription
- offline audit of a cut
- local corpus mining
- repetition and reset analysis
- semantic duplicate detection with MPNet embeddings

## Common Mistakes

- using system Python instead of `.venv_ads`
- assuming a clean visual cut means no need for transcript audit
- treating WhisperX output as final truth without editorial review
