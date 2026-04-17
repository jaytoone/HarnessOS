# Mirage Classification — Iter 1 Preliminary Findings

- **Date**: 2026-04-17
- **Classifier**: `scripts/mirage_classifier.py` (heuristic mode)
- **Source data**: `.omc/episodes.jsonl` (n=5)
- **Report**: `experiments/hypothesis_validation/mirage_classification_iter1_report.json`
- **Source artifact**: `experiments/hypothesis_validation/long_horizon_mirage_live_inf.md`

## Numbers

| Metric | Value |
|---|---|
| Episodes loaded | 5 |
| Classified | 2 |
| Unclassified | 3 |
| Dominant category | perception (2/2 classified) |
| H1 preliminary | "supported" at 100% perception |
| Statistical power | **insufficient** (n=2, need n≥25) |

## The real finding: sample bias

The 3 unclassified episodes were all **successes** describing patch applications
and stats-display verification — no failure keywords to match. Only the 2
failure-adjacent episodes matched, and both were about the "Output Parser" issue
→ classified as **perception** (parsing errors).

This exposes a sampling problem the source artifact did not anticipate:

**`.omc/episodes.jsonl` records FINAL episode summaries, not per-iteration failures.**

Most entries describe successful convergences with lists of patches applied.
The per-iteration failure modes that cause plateau asymmetry (control 0.835→1.0
vs treatment 0.835→0.954) are not preserved in this file — they are compressed
away at the success-summary level.

## What this means for H1

The hypothesis (plateau asymmetry concentrates in ≥1 Mirage category) cannot be
tested from `.omc/episodes.jsonl` alone. We would need either:

1. **Per-iteration failure logs** — raw stderr/stdout from each live-inf step,
   tagged with iteration number, score delta, and failure reason.
2. **Replay with instrumentation** — re-run the control/treatment A/B with the
   classifier invoked on every iteration's reasoning trace (requires
   re-executing live-inf with the Mirage prompt injected into its failure-
   detection path).
3. **More episodes** — continue to let episodes accumulate until n≥25, but the
   sampling bias will persist; this only gains power on terminal failure types.

## Recommendation

**Path A (cheap)**: Add a "per_iteration_failures" field to episode schema
going forward. Back-fill is impossible for existing 5 episodes.

**Path B (expensive)**: Wrap live-inf with a per-iteration failure logger that
emits structured records to `.omc/iter-failures.jsonl`. Run the A/B protocol
once to generate ~10 iterations of data, then classify.

**Path C (defer)**: Wait until more live-inf runs accumulate failure data
naturally. Classifier is now in place and will run against richer data when
available.

## What shipped this iter

- `scripts/mirage_classifier.py` — 5-category keyword classifier + optional
  `--llm-fallback` via `claude -p`. Syntax OK, runs clean against episode
  schema, margin-based confidence reporting.
- `experiments/hypothesis_validation/mirage_classification_iter1_report.json`
  — baseline distribution (biased sample, documented).
- This notes file — the honest interpretation.

## Status

Source artifact (`long_horizon_mirage_live_inf.md`) status: `proposed` → `verified_neutral`.
H1 cannot be tested from available data; this iter produced infrastructure
(classifier) and diagnosis (sample bias), not a verdict on the hypothesis.
