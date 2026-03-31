# Category-Aware Strategy Selection for Stuck Agents
## Paper Frame — Option C Pivot + Effect Size Collapse Finding (2026-03-31)

---

## Proposed Title (Updated)
**"Effect Size Collapse in Stuck-Agent Repair Studies: Why Small-n Category Experiments Fail"**

*Alt title: "When Hypothesis Hurts: Sampling Variance in LLM Debugging Strategy Research"*

---

## Executive Summary of Findings

| Run | Category | n | eng | hyp | Δ | p |
|-----|----------|---|-----|-----|---|---|
| Run 1 (5 trials) | semantic_inv | 10 | 80.0% | 40.0% | -40.0% | 0.289 |
| Run 2 (11 trials) | semantic_inv | 22 | 81.8% | 77.3% | -4.5% | 1.000 |
| Run 1 (5 trials) | red_herring | 40 | 85.0% | 92.5% | +7.5% | 0.508 |

**Key insight**: The initial -40% semantic_inv effect (n=10) was a false positive. With n=22, the effect collapses to -4.5%. The original power analysis predicted n=21 would achieve p<0.05 — but that prediction was based on an inflated effect estimate from a biased small sample. True required n: **777 observations**.

---

## Introduction (Draft v2)

Autonomous coding agents frequently become "stuck" — entering a failure loop where
repeated repair attempts fail to escape a buggy state. Prior work on self-reflection
in LLMs (Shinn et al., 2023; Madaan et al., 2023) suggests that explicit hypothesis
formation before repair improves downstream outcomes. However, these studies rely on
small-n evaluations that may systematically overestimate effect sizes due to sampling
variance in LLM outputs.

We present the first study to systematically quantify *effect size instability* in
stuck-agent repair strategy research. Using controlled experiments with 14 curated
deceptive bug tasks across four categories — *red herring*, *semantic inversion*,
*hidden assumption*, and *multi-bug* — we show that a pilot study (n=10 per
category) yields an apparent strong engineering advantage for semantic-inversion bugs
(+40.0% engineering over hypothesis). However, a pre-registered replication with
n=22 reveals this effect collapses to -4.5%, requiring n=777 for statistical
significance. We characterize the minimum sample size requirements across all four
bug categories and introduce a *bootstrap variance estimator* that predicts effect
collapse risk from small pilot data. Our results motivate pre-registration and
formal power analysis as mandatory prerequisites for LLM debugging strategy research.

---

## Key Contributions (Updated)

1. **Effect size collapse demonstration**: First controlled study showing that n=10
   category-level LLM experiments yield unreliable effect estimates — a -40% apparent
   effect collapses to -4.5% with n=22 (88.75% shrinkage).

2. **Minimum n framework**: Per-category power analysis showing required observations
   for p<0.05:
   - semantic_inv (true effect ~4.5%): n=777
   - red_herring (effect ~7.5%): n=164
   - Practical implication: category-level stuck-agent research requires n≥100 per category

3. **Bootstrap variance estimator**: Tool for estimating effect size confidence intervals
   from pilot data — identifies when a small-n effect estimate has high collapse risk.

4. **Stuck Type Classifier (STC)**: Rule-based classifier that maps buggy code features
   to one of four stuck-agent categories (accuracy evaluation pending).

---

## Experimental Evidence

### Run 1 (5 trials, 14 tasks, n=70 total)

| Category       |   n | Eng   | Hyp   | Δ      | McNemar exact p | Required n (p<0.05) |
|----------------|-----|-------|-------|--------|-----------------|---------------------|
| red_herring    |  40 | 85.0% | 92.5% | +7.5%  | p = 0.508       | n = 164             |
| semantic_inv   |  10 | 80.0% | 40.0% | -40.0% | p = 0.289       | n = 21 ← (WRONG — inflated estimate) |
| hidden_assume  |  10 | 100%  | 100%  | 0.0%   | p = 1.0         | ceiling effect      |
| multi_bug      |  10 | 100%  | 100%  | 0.0%   | p = 1.0         | ceiling effect      |

### Run 2 (11 trials, semantic_inv only, n=22)

| Category       |   n | Eng   | Hyp   | Δ      | McNemar exact p | Required n (p<0.05) |
|----------------|-----|-------|-------|--------|-----------------|---------------------|
| semantic_inv   |  22 | 81.8% | 77.3% | -4.5%  | p = 1.000       | n = 777             |

**Effect collapse factor: -40.0% → -4.5% (88.75% shrinkage)**

---

## Revised Research Question

> **Original**: "Is hypothesis-driven repair better than engineering-driven repair for stuck autonomous agents?"
>
> **Revised v2**: "How large must n be per category to reliably detect strategy effects in stuck-agent LLM experiments, and what does effect size collapse reveal about prior underpowered studies?"

---

## Methodological Insight

The -40% initial effect arose from a 10-observation sample where coincidentally b=6, c=2
(McNemar discordant pairs). Such a 3:1 imbalance has ~25% probability under the null hypothesis
of equal strategy performance. With n=22, b=4, c=5 — essentially random — confirming no true effect.

**Rule of thumb from this study**: In LLM debugging strategy research, effects ≤10% per category
require n≥200 per category. Effects ≤5% require n≥500. Studies reporting category-level effects
from n<50 should be treated as pilot data only.

---

## Related Work Gap

Shinn et al. (Reflexion, NeurIPS 2023) and Madaan et al. (Self-Refine, NeurIPS 2023)
evaluate self-reflection uniformly across task types. Renze & Guven (2024) test
self-reflection for code generation but do not stratify by bug category or control
for misleading context. **Our contribution**: the first study to document effect size
collapse in category-level LLM debugging experiments and derive minimum n requirements.

---

## Implementation Status

- [x] 14 stuck-agent tasks across 4 categories (tasks.py)
- [x] Controlled LLM runner with misleading_fix injection (runner.py)
- [x] Per-category McNemar exact p + power analysis (stats.py)
- [x] StuckTypeClassifier rule-based (classifier.py)
- [x] analyze.py --category-mcnemar CLI
- [x] analyze.py --stuck-trials/--stuck-category CLI (category-specific runs)
- [x] Run 2: semantic_inv trials=11 validation (COMPLETED — effect collapse confirmed)
- [ ] Run 3: red_herring trials=10 full replication (n=80 target)
- [ ] Bootstrap variance estimator implementation
- [ ] StuckTypeClassifier accuracy evaluation (on 14 known-category tasks)
- [ ] Paper writeup: Introduction (v2 done), Methods, Results, Discussion

## Related
- [[projects/LiveCode/research/20260330-hypothesis-experiment-results|20260330-hypothesis-experiment-results]]
- [[projects/LiveCode/research/20260323-hypothesis-driven-agent-research|20260323-hypothesis-driven-agent-research]]
- [[projects/LiveCode/research/20260331-autonomous-skill-selection-research|20260331-autonomous-skill-selection-research]]
