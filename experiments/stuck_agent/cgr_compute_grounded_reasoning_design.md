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

### Implementation Plan — REVISED 2026-04-17

**Original plan assumed Python infrastructure (`scripts/corpus_router.py`, `scripts/quality_gate.py`) that does not exist in this repo.** Re-scoped to skill-level implementation matching Entity's actual architecture (prompt-level Quality Gate, not Python classifier).

**Shipped (2026-04-17):**
1. `~/.claude/skills/entity/SKILL.md` — added **QG29 (CGR Compute Grounding)** as 29th check. Triggers on any model assertion about codebase/environment/test state; repair paths: (a) execute compute → retag `[CGR:tool:target]`, (b) retag `[UNCERTAIN: method=<specific>]`.
2. `~/.claude/skills/entity/SKILL.md` — QG table row 29 added; heading "27 checks" → "29 checks"; `[ENTITY_GROUNDING_METRICS]` footer extended with `cgr_rate` (target ≥ 0.80).
3. Skill frontmatter description updated: "27-check" → "29-check Quality Gate (QG29 = CGR compute grounding)".

**Deferred (requires runtime evidence, not in this iteration):**
- Benchmark measurement. The 22-task ameva benchmark runs against a Python harness (`experiments/hypothesis_validation/ameva_benchmark.py`), but Entity's QG is evaluated at skill invocation time — there is no Python hook to toggle. Measurement requires either (a) a manual control/treatment session-pair comparison, or (b) a bench harness that invokes `/entity` as a subprocess and scrapes the response for `[CGR:]` tags.

### Expected Outcome (post-skill-update)
Entity responses that reference files, test results, scores, or env state will now carry `[CGR:compute_id]` tags after genuine tool execution, or `[UNCERTAIN: method]` when deferred. `cgr_rate` footer field makes compliance observable in every response.

### Measurement Path Forward
1. Run `/entity` on a codebase-claim query with and without QG29 awareness (control = pre-2026-04-17 snapshot; treatment = current).
2. Count: claims matching QG29 triggers / claims carrying `[CGR:]` or `[GROUNDED:]` or `[UNCERTAIN: method]` tags.
3. Target: cgr_rate ≥ 0.80 on treatment, uncertain_ratio ≤ 0.40.

## Open Risks
- **Fabricated CGR receipts**: model emits `[CGR:grep:X]` without actually running grep. Mitigation: QG29 FAIL criterion — tag must reference an actual tool call *in the current turn*.
- **Self-enforcement is imperfect**: skill-level QG relies on the model reading and following its own rubric. Cross-prompt or oracle-based measurement needed to verify compliance (the very problem CGR tries to fix — recursive).
- **Budget exhaustion**: 3 CGR calls/response may be too low for audit-heavy tasks; fallback to `[UNCERTAIN: method]` must not degrade output quality.
