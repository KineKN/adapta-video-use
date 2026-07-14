---
name: ad-corpus-study
description: Use when learning from the local Anuncios corpus and you need to derive real editing rules from many Bruto to Final pairs instead of relying on theory or a single example.
---

# Ad Corpus Study

## Overview

Use the local corpus as ground truth for how the company actually edits ads.

Study pairs, not isolated transcripts.

## Use When

- creating or updating ad-editing rules
- training future sessions on house style
- checking whether a new cut matches historical editorial behavior
- investigating outliers where final is much shorter or longer than bruto

## Workflow

1. Start with `python helpers/anuncios_corpus_report.py`.
2. If the local `Anuncios/` corpus is present, regenerate or inspect current reports there.
3. Always read the versioned memory references in this skill:
   - `references/golden-editing-standard.md`
   - `references/corpus-report.md`
   - `references/corpus-notes.md`
   - `references/ad-editing-qc.md`
   - `references/blind-test-report-2026-07-03.md`
4. Sample across three regimes:
   - light cleanup
   - aggressive rebuild
   - expanded or rewritten final
5. Compare `Bruto -> Final` at the level of commercial arc, not just word count.
6. Convert patterns into explicit editing rules.

## Versioned Memory vs Local Corpus

The raw `Anuncios/` folder is a local dataset and is not required for every agent clone.

The portable memory that future agents should read lives in `references/`. Use the raw corpus only when doing fresh study, recalibration, or batch analysis.

## Useful Utilities

- `helpers/anuncios_corpus_report.py`
- `helpers/anuncios_repetition_candidates.py`
- `helpers/anuncios_semantic_dedup.py`
- `helpers/anuncios_funnel_classifier.py`
- `helpers/anuncios_reference_audit.py`
- `helpers/anuncios_rewrite_mining.py`
- `helpers/anuncios_reference_policy.py`
- `helpers/anuncios_reference_anchor_brief.py`
- `helpers/anuncios_reference_editor_brief.py`
- `helpers/anuncios_exception_mining.py`
- `helpers/anuncios_exception_export.py`
- `helpers/anuncios_hybrid_matrix.py`

## What to Learn

- what gets cut repeatedly
- what is almost always preserved
- when finals can be longer than brutos
- which reset markers correlate with non-final copy
- which corpus finals look weak, noisy, or non-gold despite being labeled final
- which recurring funnel family the ad belongs to, and which details survive across many examples in that family
- which finals are actually rewrite references rather than wording-level gold for their paired bruto
- which subtype of rewrite reference you are seeing: `body_reframe`, `full_rebuild`, `hook_swap`, or `cta_rewrite`
- how much wording-weight vs structure-weight the reference deserves before you use it
- when to pass a few safe anchors from the reference instead of only abstract policy
- how to hand the agent one compact editorial brief instead of five separate diagnostics
- which cases still remain low-confidence, hybrid, or unmodeled after the current calibration
- whether the residual exception report itself is in sync with the current helpers and corpus state
- which hybrid pairs are benign overlap versus genuinely dangerous editorial ambiguity
- whether the editor brief is surfacing hybrid-pair risk directly enough to prevent cross-funnel contamination at edit time
- which golden-standard checks separate a merely valid XML from an actually shippable ad edit

## Common Mistakes

- overfitting rules from one ad
- assuming all finals are shorter
- confusing transcription weakness with editorial choice
- treating every `Final.txt` as perfect gold instead of a useful but fallible reference
