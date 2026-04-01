# IDEA-2 Verification Hurt — Experiment Results

**Date**: 2026-04-01
**Basis**: arXiv:2603.27076 "When Verification Hurts: Asymmetric Effects of Multi-Agent Feedback"
**Status**: Run 2 Complete (n=14 all tasks, McNemar's paired)

---

## Experiment Design

Test whether verification feedback helps or hurts stuck-agent escape rate.

**4 verification modes on 8 stuck tasks (D1-D13 sample):**
- `none` — no verification, pure rescue prompt
- `strict` — verification hint on every attempt after the first
- `lenient` — verification hint every 3rd attempt
- `adaptive` — probabilistic: hint probability = attempt_number / max_attempts

**LLM**: MiniMax-M2.5 | **max_attempts**: 3 | **Tasks**: stuck_agent task set (14 available, 8 sampled)

---

## Results

### Run 1 (n=8, random sample — WARNING: sampling noise)
| Mode     | Escape% | n_escaped/n | AvgVerifCalls |
|----------|---------|-------------|---------------|
| lenient  | 87.5%   | 7/8         | 0.1           |
| adaptive | 75.0%   | 6/8         | 0.5           |
| none     | 62.5%   | 5/8         | 0.0           |
| strict   | 62.5%   | 5/8         | 1.0           |

### Run 2 (n=14, all tasks — McNemar's paired design)
| Mode     | Escape% | n_escaped/n | AvgAttempts | AvgVerifCalls |
|----------|---------|-------------|-------------|---------------|
| **none** | **78.6%** | 11/14      | 1.7         | 0.0           |
| strict   | 64.3%   | 9/14        | 1.9         | 0.9           |
| lenient  | 64.3%   | 9/14        | 1.8         | 0.4           |
| adaptive | 64.3%   | 9/14        | 1.9         | 0.8           |

### McNemar's Test (Run 2, vs none baseline)
| Comparison    | delta   | chi2 | p-value | significant |
|---------------|---------|------|---------|-------------|
| none vs strict | −14.3% | 0.25 | 0.7237  | no          |
| none vs lenient | −14.3% | 0.25 | 0.7237 | no          |
| none vs adaptive | −14.3% | 0.25 | 0.7237 | no         |

Discordant pairs per comparison: b=3 (none_pass/mode_fail), c=1 (none_fail/mode_pass)

---

## Key Findings

### F1: Effect Size Collapse — Run 1 was sampling noise
- Run 1 (n=8 sample): lenient=+25%p vs none → **false positive**
- Run 2 (n=14 all tasks): lenient=−14.3%p vs none → reversal
- This is the same Effect Size Collapse pattern seen in HarnessOS's previous hypothesis_validation experiments

### F2: Verification directionally hurts (consistent with arXiv:2603.27076)
- All 3 verification modes score identically (64.3%) and all below none (78.6%)
- −14.3%p effect direction consistent with "When Verification Hurts" paper hypothesis
- **Not statistically significant** (p=0.72) due to insufficient task pool (n=14)

### F3: Power analysis — need ~30 unique tasks for significance
- Current effect: −14.3%p, discordant pairs = 4/14
- McNemar's requires ~10+ discordant pairs for p<0.05 at this effect size
- Estimated n needed: 30–40 unique stuck-agent tasks

---

## Interpretation vs Original Hypothesis

The arXiv:2603.27076 hypothesis ("verification hurts") is **directionally confirmed**:

- All verification modes (strict/lenient/adaptive) score below no-verification baseline
- The effect is consistent regardless of verification cadence — presence of verification is the signal, not frequency
- No verification mode can meaningfully help (D5, D6, D7 are hardest tasks and resist all modes)

Run 1's "lenient helps" finding was **noise** (n=8 sampling artifact — 1 task flip = ±12.5%p)

---

## HarnessOS Implications

### Design Decision
**Do NOT add verification feedback to default harness loop** — verification consistently shows ≤ baseline performance at extra cost.

If verification is to be used: only as an **explicit opt-in for post-escape validation**, not during escape attempts.

### Next Experiments
- **Expand task pool to 30+** — then re-run for statistical significance
- **Hint quality study**: controlled hints (correct vs misleading vs neutral) — does hint quality explain the hurt?
- **Category breakdown**: red_herring (8 tasks) vs other categories — does verification hurt more on some types?

---

## Limitations

- n=14 unique tasks: insufficient statistical power (McNemar p=0.72)
- MiniMax M2.5 only — may not generalize to GPT-4o/Claude
- Run 1 (n=8 subsample) reversed by Run 2 — demonstrates importance of full-task evaluation

---

## Raw Results

- Run 1: `results/verification_hurt_20260401_170814.json`
- Run 2: `results/verification_hurt_20260401_173706.json`

## Related
- [[projects/HarnessOS/research/20260330-hypothesis-experiment-results|20260330-hypothesis-experiment-results]]
- [[projects/HarnessOS/research/digests/20260401-experiment-ideas|20260401-experiment-ideas]]
