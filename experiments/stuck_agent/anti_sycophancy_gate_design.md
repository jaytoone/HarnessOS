# Anti-Sycophancy Behavioral Gating Design

## Source
- **Paper**: "The Silicon Mirror: Dynamic Behavioral Gating for Anti-Sycophancy in LLM Agents"
- **arXiv**: [2604.00478](https://arxiv.org/abs/2604.00478) (2026-04-02)
- **Absorbed via**: /inhale agent_research — arXiv cs.AI
- **Relevance**: 9.0/10 (evaluation category)

## Core Idea
LLMs prioritize user validation over epistemic accuracy (sycophancy).
Dynamic Behavioral Gating detects sycophancy-prone contexts and overrides
the default agreeable behavior with truth-seeking behavior.

## HarnessOS Application

### Hypothesis
> Applying Dynamic Behavioral Gating to omc-live's self-evaluation
> (SCORE PROMPT, Step 6a) can reduce self-scoring bias by 5-10%,
> making convergence detection more accurate.

### Current System (Baseline)
- evaluator_mode: "self" — same session scores its own work
- evaluator_mode: "cross_prompt" — perspective shift to skeptical reviewer
- Known issue: LLM self-evaluation has systematic bias (-7.4% vs human)

### Proposed System (Treatment)
- Add behavioral_gating layer before SCORE PROMPT execution:
  1. Detect sycophancy risk: does the prompt structure invite agreement?
  2. If risk detected: inject anti-sycophancy gate
     - "You must find at least 2 flaws before assigning any score > 0.7"
     - "Rate harshly — the user prefers honest low scores to inflated high ones"
  3. Gate strength scales with score_variance: low variance → stronger gate

### Connection to Existing evaluator_mode
```
evaluator_mode options (current):
  "self"         → baseline (sycophancy risk: HIGH)
  "cross_prompt" → perspective shift (sycophancy risk: MEDIUM)
  "oracle_only"  → external only (sycophancy risk: NONE)

New option:
  "gated_self"   → self + dynamic behavioral gating (sycophancy risk: LOW)
```

### Experiment Protocol
1. Run 20 scoring iterations with evaluator_mode="self"
2. Run 20 scoring iterations with evaluator_mode="gated_self"
3. Compare score distributions: mean, variance, correlation with oracle
4. Statistical test: paired t-test on score accuracy (vs oracle ground truth)

### Expected Outcome
- 5-10% reduction in self-scoring bias
- More accurate convergence detection (fewer false plateaus)
- Complements existing cross_prompt mode
