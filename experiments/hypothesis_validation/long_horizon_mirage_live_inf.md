# Long-Horizon Task Mirage — Applied to live-inf Convergence Plateau

## Source
- **Origin**: The Long-Horizon Task Mirage? Diagnosing Where and Why Agentic Systems Break
- **arXiv**: 2604.11978
- **Absorbed via**: /inhale agent_research (2026-04-16)
- **Relevance**: 10.0 × type_weight(hypothesis_validation=1.3) × novelty=1.2 → 15.6
- **Registry status**: proposed

## Core Insight
LLM agents perform strongly on short-/mid-horizon tasks but break down on long-horizon tasks
requiring extended integrated reasoning. The paper proposes a diagnostic taxonomy for *where*
the break occurs (perception / planning / memory / execution / recovery) and *why*
(context dilution, plan drift, local-optimum traps, error accumulation).

Entity's live-inf orchestrator exhibits exactly this pattern in our existing A/B data:
- **control** (no patches): 0.835 → 1.000 in **3 iters**
- **treatment** (skill_patch accumulating): 0.835 → 0.954 in **4 iters** — plateaus short of 1.0

The asymmetry is unexplained by current instrumentation. The Mirage taxonomy provides a ready-made
diagnostic framework.

## Formal Statement

- **H0**: live-inf plateau asymmetry (control reaches 1.0, treatment stalls at 0.954) is
  distributed uniformly across Mirage failure categories (no dominant failure mode).
- **H1**: The plateau is concentrated in ≥1 specific Mirage category (e.g., "context dilution"
  or "plan drift") that accumulates with each skill_patch injection.

## Variables
- **Independent**: number of accumulated skill_patches per iteration (0, 1, 2, 3…).
- **Dependent**:
  - Per-iteration Mirage-category failure counts (5 categories).
  - Convergence score trajectory.
  - Context size per iteration.
- **Controlled**: same seed set, same oracle, same initial goal.

## Measurement Method
1. Re-run existing A/B protocol (control vs treatment) with **Mirage instrumentation enabled**:
   a failure classifier (`scripts/mirage_classifier.py`, new) tags each iteration's primary
   failure reason against the paper's 5-category taxonomy.
2. Tag source: `experiments/hypothesis_validation/territory_paint_wars_failure_modes.md`
   already does partial failure tagging — extend its schema with Mirage categories.
3. Replay from `.omc/episodes.jsonl` (historical episodes) to compute baseline category distribution
   without re-running (saves compute).
4. Statistical test: chi-square goodness-of-fit on category distribution, one-sided (H1 = non-uniform).

## Success Criteria
- H1 supported at p < 0.05.
- Additionally, effect size: the dominant Mirage category accounts for ≥ 40% of treatment failures
  (vs ≤ 25% if uniformly distributed).

## Integration Points
- Input: `.omc/episodes.jsonl` (7+ recent live-inf episodes).
- Tooling: new `scripts/mirage_classifier.py` — prompt-based classifier using the paper's taxonomy.
- Downstream: if H1 supported, the dominant category feeds a targeted mitigation (e.g., context
  compaction for "context dilution", plan-restart for "plan drift"). Each mitigation becomes its
  own follow-up /exhale artifact.

## Expected Outcome
Prediction (low confidence, paper-informed): "context dilution" dominates — skill_patches
accumulate in context and degrade downstream step quality. Mitigation would be periodic
patch consolidation (merge N patches into 1 distilled prompt).

## Open Risks
- Mirage classifier is itself LLM-based; category assignments may be noisy. Mitigation: double-label
  a 20-episode subset manually and compute Cohen's κ for agreement.
- Small episode count (~7) limits statistical power. Mitigation: run additional live-inf loops
  seeded to produce failures.
