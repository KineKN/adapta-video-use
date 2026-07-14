---
name: ad-semantic-qc
description: Use when a cut looks visually fine but may still be commercially wrong, especially to catch duplicated meaning, missing hooks, broken copy arcs, or repeated CTAs in edited ads.
---

# Ad Semantic QC

## Overview

Visual QC is not enough for ads.

An ad can have:

- clean cuts
- no pops
- stable framing

and still be wrong because the copy is broken.

## Use When

- reviewing any ad cut before delivery
- checking the last third of an ad
- validating a rebuilt final from a noisy bruto
- the user says "sumiu parte do anuncio" or "ta repetindo"

## Required QC

1. Confirm `Hook -> Lead -> Body -> Proof -> CTA`.
2. Confirm the original commercial promise still exists.
3. Check for semantic repetition in nearby blocks.
4. Check the final third for echo before CTA.
5. Confirm CTA appears once unless repetition is intentional.

## High-Risk Patterns

- phrase starts, breaks, then reappears clean
- proof appears twice with different wording
- CTA appears in a setup take and then again in final take
- secondary opener replaced the true hook
- clean render but wrong commercial logic
- concrete offer details replaced by generic summary
- transcript looks clean but the actual beat is contaminated by cough, clap, overlap, or crew audio nearby
- structurally correct cut still carries obvious ASR corruption in names or channels that weaken credibility
- a segment ends exactly as an abandoned restart begins, leaking a tiny unfinished syllable across the cut

## How to Audit

- read the EDL in order
- compare each block against the source transcript
- inspect any block containing `então`, `tá`, `pera aí`, `como`, `eles têm`, `saiba mais`
- inspect any cut where the next source word begins within ~120ms after the segment end
- listen for repeated meaning, not just repeated wording
- distrust transcript-only wins when the raw source around that moment includes setup noise markers
- run `python helpers/edl_boundary_audit.py <edit>/edl.json` and manually review any reported boundary

## Pass Criteria

The ad should feel like one intentional persuasion sequence.

If the viewer would feel:

- "they already said this"
- "the ad started in the middle"
- "this CTA came twice"
- "this sounds flatter than the original sales delivery"

the cut fails QC.

## Common Mistakes

- only checking waveform and picture
- approving a final because each individual segment is good
- missing duplication that happens across segment boundaries
- assuming a clean transcript line is automatically a clean editorial keep
