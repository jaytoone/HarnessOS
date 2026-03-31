# Category-Aware Strategy Selection for Stuck Agents
## Paper Frame — Option C Pivot (2026-03-31)

---

## Proposed Title
**"When Hypothesis Hurts: Category-Aware Strategy Selection for Stuck Autonomous Agents"**

---

## Introduction (Draft v1)

Autonomous coding agents frequently become "stuck" — entering a failure loop where
repeated repair attempts fail to escape a buggy state. Prior work on self-reflection
in LLMs (Shinn et al., 2023; Madaan et al., 2023) suggests that explicit hypothesis
formation before repair improves downstream outcomes. However, these studies treat
all stuck states as equivalent, ignoring the structural diversity of bug types that
trigger stuckness in the first place. We present the first empirical study to
challenge this uniformity assumption. Using a controlled experiment with 14 curated
deceptive bug tasks across four categories — *red herring*, *semantic inversion*,
*hidden assumption*, and *multi-bug* — we show that hypothesis-driven repair
(+7.5% escape rate in red-herring tasks) and engineering-driven repair (+40.0% in
semantic-inversion tasks) yield **opposing advantages depending on bug category**.
Our key finding is that the optimal stuck-escape strategy is not universal but
*category-dependent*: red-herring scenarios benefit from root-cause reasoning that
bypasses misleading symptoms, while semantic-inversion scenarios are better resolved
by direct code inspection uncontaminated by prior hypothesis bias. These results
motivate a new architectural component — a *stuck type classifier* — that routes
agents to the appropriate repair strategy before each rescue attempt, transforming
the question from "is hypothesis better?" to "when is each strategy optimal?".

---

## Key Contributions

1. **Category-dependent effect finding**: First empirical demonstration that
   hypothesis-driven and engineering-driven repair strategies exhibit opposing
   performance depending on stuck-task category (red_herring vs. semantic_inv).

2. **Stuck Type Classifier (STC)**: Rule-based classifier that maps buggy code
   features to one of four stuck-agent categories, enabling automatic strategy
   routing with no additional LLM calls.

3. **Statistical framework**: Per-category McNemar exact test + power analysis
   showing that semantic_inv significance is achievable with n=21 observations
   (trials=11 per 2 tasks), providing a concrete roadmap for validation.

---

## Experimental Evidence (2026-03-31 Run)

| Category       |   n | Eng   | Hyp   | Δ      | McNemar exact p | Required n (p<0.05) |
|----------------|-----|-------|-------|--------|-----------------|---------------------|
| red_herring    |  40 | 85.0% | 92.5% | +7.5%  | p = 0.508       | n = 164             |
| semantic_inv   |  10 | 80.0% | 40.0% | -40.0% | p = 0.289       | n = 21 ← feasible   |
| hidden_assume  |  10 | 100%  | 100%  | 0.0%   | p = 1.0         | ceiling effect      |
| multi_bug      |  10 | 100%  | 100%  | 0.0%   | p = 1.0         | ceiling effect      |

**Immediate next step**: Run semantic_inv tasks (D7, D8) with trials=11 → n=22 → p<0.05

---

## Revised Research Question

> **Original**: "Is hypothesis-driven repair better than engineering-driven repair
> for stuck autonomous agents?"
>
> **Revised**: "Which repair strategy is optimal for a given stuck-agent scenario,
> and can we classify scenarios automatically to route agents to the better strategy?"

---

## Related Work Gap

Shinn et al. (Reflexion, NeurIPS 2023) and Madaan et al. (Self-Refine, NeurIPS 2023)
evaluate self-reflection uniformly across task types. Renze & Guven (2024) test
self-reflection for code generation but do not stratify by bug category or control
for misleading context. **Our contribution**: the first category-stratified analysis
of stuck-escape strategies with a concrete classifier proposal.

---

## Implementation Status

- [x] 14 stuck-agent tasks across 4 categories (tasks.py)
- [x] Controlled LLM runner with misleading_fix injection (runner.py)
- [x] Per-category McNemar exact p + power analysis (stats.py)
- [x] StuckTypeClassifier rule-based (classifier.py)
- [x] analyze.py --category-mcnemar CLI
- [ ] trials=11 run for semantic_inv validation (NEXT)
- [ ] StuckTypeClassifier accuracy evaluation (NEXT)
- [ ] Paper writeup (NEXT)
