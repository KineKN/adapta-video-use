---
name: ad-editorial-decupagem
description: Use when turning a noisy bruto ad transcript into a clean final cut and you need practical rules for what to cut, what to preserve, and how to handle resets, retakes, and repeated ideas.
---

# Ad Editorial Decupagem

## Overview

This is an editorial skill, not just a silence-removal skill.

Cut what does not belong to the ad. Preserve the copy that sells.

## Use When

- bruto has retakes, restarts, or on-set direction
- the same line appears multiple times
- speaker comments on wording mid-take
- you need to choose between cleaner audio and stronger commercial logic

## Remove Aggressively

- set direction
- performance comments
- wording discussions
- aborted sentence starts
- exact repetitions
- semantic echo of the same idea
- dead air

## Preserve Aggressively

- promise
- tension
- mechanism
- proof
- condition
- CTA

## Decision Rules

### Repeated line

Keep the strongest delivered version once.

### Aborted line then clean restart

Cut the aborted line entirely unless it contains unique meaning.

If a kept phrase is followed immediately by an aborted restart, end the segment before the next word attack. Do not set `end` on the timestamp where the aborted word begins; even a few milliseconds can leak the start of the abandoned phrase. If the next word starts within roughly 120ms of the kept phrase ending, treat that boundary as high-risk and verify it with audio/waveform QC.

### Two CTAs

Default to one CTA only.

### Cleaner secondary line vs original hook

Keep the original hook if it carries the sales promise.

### Punchy performance fragments

Keep them when they add persuasion, urgency, surprise, or rhythm.

Examples:

- `Oitavo!`
- `Free.`
- `Exato.`
- `Vai, clica!`

Cut them only when they are obvious set noise, not when they are intentional direct-response energy.

### Reference trust ladder

When `Final.txt` exists, do not trust it blindly.

- `strong reference`: clean, coherent, low repetition, commercially intact
- `rewrite reference`: clean, but far from the bruto; use for structural learning, not wording imitation
- `review reference`: useful, but inspect for duplication, truncation, or flattening
- `weak reference`: prefer the bruto's better commercial logic over literal imitation

Signals of weak reference:

- obvious corruption
- repeated brand slug many times
- repeated full clauses
- broken ending
- lower commercial clarity than the bruto

Signals of rewrite reference:

- final is clean and commercially good
- but brute-to-final similarity is very low
- the final likely reflects a more rewritten or reformulated copy than the captured bruto

In rewrite-reference cases:

- learn the funnel and structural moves
- do not force the wording to match that final

Common rewrite-reference subtypes:

- `body_reframe`: opening and close still align, but the middle was heavily rewritten
- `hook_swap`: the final replaces the opener while preserving most of the rest
- `cta_rewrite`: the final lands a different close
- `full_rebuild`: the pair is too far apart for wording-level imitation

Use:

- `body_reframe` for structure and middle-block compression heuristics
- `hook_swap` to learn alternate opener strategy, not literal wording
- `cta_rewrite` to learn alternate closing strategy
- `full_rebuild` only for high-level funnel learning

Practical weighting heuristic:

- `strong`: wording high, structure high
- `review_reference`: wording medium, structure high
- `rewrite_reference/body_reframe`: wording low, structure high
- `rewrite_reference/full_rebuild`: wording near zero, structure medium
- `weak_reference`: wording near zero, structure low-to-medium

Operational rule:

- for `follow_closely`, policy alone may be too abstract; pass a few safe anchors from the reference
- for `use_with_review`, pass only light anchors, not the whole wording spine
- for `body_reframe`, pass only edge anchors when useful
- for `funnel_only`, do not pass wording anchors

Recommended helper:

- `python helpers/anuncios_reference_editor_brief.py <AdXXXX_Final.txt>`

Use it when a corpus pair exists and you want one compact brief for the editor containing:

- funnel
- reference strength
- rewrite subtype
- wording vs structure weighting
- safe anchors
- case-specific QC reminders

If the brief reports:

- `funnel_confidence: medium` or `low`: do not overfit family rules
- `hybrid_candidate: true`: preserve concrete details supporting both candidate families
- `policy: use_with_review` even with `reference_label: strong`: this usually means the reference is clean, but the funnel reading is still too split for wording-level imitation

### House-funnel details

Treat recurring offer details as structural, not decorative.

Examples:

- exact quantity of tools
- exact price anchor
- named flagship products
- qualifier threshold
- ranking position
- the one condition that unlocks the offer

### Obvious ASR repair

Repair high-confidence transcript corruption when the intended meaning is clear and commercially important.

Typical cases:

- brand/platform names
- product names
- person names
- known social channels
- obvious malformed words inside otherwise clean sentences

Examples:

- `Cloud` -> `Claude`
- `Adaapta` -> `Adapta`
- `Antropic` -> `Anthropic`
- corrupted channel names like `Estragando Cariani` when the intended phrase is clearly `Instagram do Cariani`

Do not invent new facts.

Only repair when:

- the surrounding sentence makes the target obvious
- the repaired version increases clarity
- the repair does not change the commercial claim itself

### Bruto extremely redundant

Treat as aggressive rebuild, but keep the commercial arc intact.

### Boundary audit

After building an EDL from word-level transcripts, run:

`python helpers/edl_boundary_audit.py <edit>/edl.json`

Any `next_word_too_close_to_end`, `previous_word_too_close_to_start`, `start_inside_word`, or `end_inside_word` issue needs manual review before delivery.

## Corpus Signals

Reset markers that usually mean "not final copy":

- `volta`
- `mais`
- `aí`
- `pera aí`
- `opa`
- `gravando`

## Output Standard

A good final:

- reads as one intentional ad
- does not sound stitched from indecision
- does not repeat the same promise twice
- preserves context and intention

## Common Mistakes

- Editing for cleanliness instead of persuasion
- Removing a lead because another line is shorter
- Leaving a partial proof before the real proof
- Letting CTA echo because both takes sound usable
- Flattening the speaker's persuasive rhythm into overly neutral prose
- Keeping the funnel skeleton while stripping the specific nouns and numbers that actually sell
