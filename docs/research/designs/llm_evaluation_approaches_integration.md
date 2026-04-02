# LLM Evaluation 4 Approaches — HarnessOS Integration Design

## Source
- **Absorbed via**: /inhale ml_engineering — TLDR AI / Ahead of AI
- **Relevance**: hypothesis_validation category

## 4 Approaches (from paper)
1. Human Evaluation — gold standard, expensive
2. Model-based Evaluation — LLM-as-judge (current omc-live approach)
3. Benchmark-based — standardized test suites
4. Hybrid — combine multiple approaches

## Current HarnessOS State
- omc-live uses approach #2 (SCORE PROMPT = LLM-as-judge)
- Auto-oracle provides approach #3 (pytest, lint)
- No human evaluation integration
- No hybrid weighting

## Proposed Enhancement
Implement hybrid evaluation in omc-live:
```
final_score = w1 * oracle_score + w2 * llm_score + w3 * benchmark_score
where w1 + w2 + w3 = 1.0
```

This is already partially implemented (oracle merge rule in Step 6a).
Gap: no benchmark-based component for non-test dimensions.
