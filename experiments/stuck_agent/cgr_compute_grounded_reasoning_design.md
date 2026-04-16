# Compute-Grounded Reasoning (CGR) for Entity QG Design

## Source
- **Origin**: Spatial Atlas: Compute-Grounded Reasoning for Spatial-Aware Research Agent Benchmarks
- **arXiv**: 2604.12102
- **Absorbed via**: /inhale agent_research (2026-04-16)
- **Relevance**: 10.0 × type_weight(stuck_agent=1.5) × novelty=1.2 → 18.0
- **Registry status**: proposed

## Core Insight
CGR (Compute-Grounded Reasoning) is a design paradigm where *every answerable sub-problem is
resolved by executable compute*, not by model assertion. The paper applies it to spatial research
agents; the underlying principle — "no INFERRED claim survives without an executable verification
step" — generalizes to any research-agent harness that produces grounded claims.

Entity's current Quality Gate (QG26, ameva/SKILL.md Iter 68) already flags ACTION-UNCERTAIN
dominance as a failure mode. CGR formalizes the fix: replace uncertainty-laden inference with a
dispatched compute call whose result becomes the grounded evidence.

## Application

### Hypothesis
> Replacing Entity's top-N INFERRED claims with CGR-style executable verification steps reduces
> QG26 ACTION-UNCERTAIN rate by ≥ 30% without regressing grounded-claim density or [GROUNDED:doc_id]
> citation coverage.

### Current State (Baseline)
- Entity corpus router produces `[GROUNDED:doc_id]` citations, but non-cited reasoning steps
  remain model-asserted (INFERRED).
- QG26 detects ACTION-UNCERTAIN dominance but does not rewrite the reasoning chain.
- Known fact (registry): ameva third-party test reached `best_score=0.928` with P23/P24 applied;
  Semantic Fallback Tier designed but not CGR-grounded.

### Proposed Change (Treatment)
1. Extend the corpus router with a **CGR dispatch layer**: any reasoning step tagged INFERRED
   above confidence threshold `0.08` (current P23 threshold) triggers an executable sub-task
   (code_search / grep / test_run / file_read) whose return value becomes the grounding.
2. Re-label the step as `[CGR:compute_id]` instead of INFERRED once executed.
3. QG26 updated: ACTION-UNCERTAIN only counts steps that are *neither* [GROUNDED:] *nor* [CGR:].

### Experiment Protocol
- **Design**: paired comparison (same 22-task ameva benchmark, same seeds).
- **Conditions**:
  - `control` — current Entity + QG26 as of 2026-04-13 (best_score 0.928).
  - `treatment` — CGR-extended Entity (dispatch layer + QG26 rewrite).
- **Metrics**:
  - QG26 ACTION-UNCERTAIN rate per task.
  - Grounded-claim density ([GROUNDED:] + [CGR:] citations per 100 tokens).
  - Overall score (existing oracle scoring).
  - Latency overhead (CGR dispatches add compute — must stay < 2× baseline).
- **Success criteria**:
  - ACTION-UNCERTAIN rate ↓ ≥ 30% (H1 supported).
  - Overall score ≥ baseline − 0.02 (no regression).
  - Latency ≤ 2× baseline.
- **Statistical test**: paired Wilcoxon signed-rank on per-task ACTION-UNCERTAIN counts.

### Implementation Plan
1. `scripts/corpus_router.py` — add `dispatch_cgr(claim, confidence)` returning `(compute_id, result)`.
2. `scripts/quality_gate.py` (or ameva/SKILL.md QG26 block) — extend classifier to recognize
   `[CGR:compute_id]` as grounded.
3. `experiments/hypothesis_validation/ameva_benchmark.py` — add `--cgr-enabled` flag.
4. Run 22-task benchmark in both conditions; log to `.omc/evolution-registry.jsonl`.

### Expected Outcome
ACTION-UNCERTAIN rate drops 30–50%; score holds or improves modestly; latency 1.3–1.8×.
If latency > 2×, fall back to CGR-on-high-confidence-INFERRED-only (threshold tuning).

## Open Risks
- CGR dispatch could mask genuine uncertainty (overconfidence) if compute returns a plausible-but-wrong
  value. Mitigation: CGR results themselves pass through a secondary grounding check.
- Determinism: CGR calls must be reproducible for benchmark comparability.
