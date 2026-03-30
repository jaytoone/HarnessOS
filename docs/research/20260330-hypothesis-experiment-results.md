# Hypothesis-Driven vs Engineering-Only Debugging: Experiment Results
**Date**: 2026-03-30
**Method**: Deterministic evaluation with actual code execution (v2 -- replaces probability model)

## Experiment Design

### Core Hypothesis
"Engineering-only thinking (pattern matching + retry) hits a performance ceiling on hard problems. Hypothesis-driven thinking (explicit cause hypothesis + verification) raises that ceiling by reducing the number of attempts needed."

### Method
- 9 buggy Python functions across 3 difficulty categories (3 per category)
- Two strategies with researcher-coded attempt sequences
- Each attempt is actual Python code, run against real test cases
- No probability models, no Monte Carlo simulation, no randomness

### Categories
| Category | Description | Example Bug |
|----------|-------------|-------------|
| **Simple (A)** | Obvious bugs (off-by-one, wrong operator) | `range(len-k)` vs `range(len-k+1)` |
| **Causal (B)** | Requires causal reasoning | Closure variable capture, mutation during iteration |
| **Assumption (C)** | Wrong implicit assumptions | Unicode normalization, mutable default args |

### Strategies
- **Engineering**: Try fix based on symptom observation -> fail -> try different fix. No explicit causal reasoning.
- **Hypothesis**: Declare cause hypothesis -> write fix informed by hypothesis -> if wrong, refine hypothesis.

## Results

| Category | Eng Solved | Hyp Solved | Eng Avg Attempts | Hyp Avg Attempts | Attempt Savings |
|----------|------------|------------|------------------|------------------|-----------------|
| Simple | 3/3 | 3/3 | 1.0 | 1.0 | 0.0 |
| Causal | 3/3 | 3/3 | 1.7 | 1.0 | +0.7 |
| Assumption | 3/3 | 3/3 | 2.0 | 1.0 | +1.0 |

**Overall**: Both strategies solve all 9 tasks. Engineering: avg 1.6 attempts. Hypothesis: avg 1.0 attempts.

### Per-Task Details

| Task | Bug Type | Eng Attempts | Hyp Attempts | Hypothesis |
|------|----------|--------------|--------------|------------|
| A1 | Off-by-one (range) | 1 | 1 | Range upper bound off by 1 |
| A2 | Wrong operator (!= vs ==) | 1 | 1 | Comparison operator inverted |
| A3 | Missing edge case (div/0) | 1 | 1 | Missing b==0 guard |
| B1 | List mutation during iteration | 2 | 1 | Mutation during iteration skips elements |
| B2 | Closure variable capture | 2 | 1 | Closure captures loop var by reference |
| B3 | Float equality comparison | 1 | 1 | Direct == fails on floats |
| C1 | Unicode normalization | 4 | 1 | Combining characters need NFC normalization |
| C2 | Empty input handling | 1 | 1 | max() on empty sequence |
| C3 | Mutable default argument | 1 | 1 | Dict default persists across calls |

## Key Findings

1. **No difference on simple bugs (A1-A3)**: Both strategies solve obvious bugs in 1 attempt. For simple bugs, hypothesis overhead adds no value.

2. **Moderate advantage on causal bugs (B1, B2)**: Engineering takes 2 attempts on tasks requiring causal understanding (closure capture, iterator mutation). Hypothesis identifies root cause on first attempt. B3 (float comparison) is straightforward enough that engineering also solves it in 1 attempt.

3. **Largest advantage on assumption bugs (C1)**: The unicode normalization bug (C1) shows the starkest difference: engineering tries 4 approaches (strip ASCII, list-based counting, encode/decode, finally NFC normalize) while hypothesis immediately identifies "combining characters need NFC" and solves in 1 attempt. C2 and C3 are simple enough that both strategies solve in 1 attempt.

4. **First hypothesis accuracy**: 100% -- all researcher-coded hypotheses correctly identify the root cause on the first attempt.

## Validity Assessment

### What This Experiment Shows
- Given researcher-coded attempt sequences representing each strategy's "typical" approach, hypothesis-driven attempts reach the correct solution in fewer iterations.
- The attempt code actually runs against real test cases, so correctness is verified, not assumed.
- The biggest advantage appears on bugs requiring domain knowledge outside the immediate code context (unicode normalization).

### What This Experiment Does NOT Show
- Whether a real LLM given a "hypothesis-first" prompt would actually follow the hypothesis reasoning path.
- Whether a real LLM given a "just fix it" prompt would actually produce the inefficient attempts modeled here.
- External validity: the 9 tasks and researcher-coded attempts may not represent real-world debugging distributions.

### Why This Is Still Useful
- Demonstrates the **theoretical upper bound** of hypothesis-driven strategy's advantage over symptom-driven strategy.
- Identifies **which bug categories** benefit most from explicit causal reasoning (assumption > causal > simple).
- The attempt sequences themselves document real debugging anti-patterns (e.g., "strip non-ASCII characters" as a response to unicode bugs).
- Provides a concrete framework for testing with real LLM calls in future work.

### Researcher Bias Disclosure
- Attempt sequences were designed by the researcher, who was aware of the expected outcome.
- The hypothesis strategy is "idealized" -- real agents may form incorrect hypotheses.
- The engineering strategy represents "typical wrong approaches" but actual LLMs may find shortcuts.

### Path to Real Experiment
1. Replace researcher-coded attempts with actual LLM API calls (Claude, GPT-4) using two prompt templates.
2. Measure pass@k (k=1, 3, 5) across both strategies on the same test cases.
3. Record actual token consumption per strategy.
4. Expand to 50-100 diverse debugging tasks from real codebases.
5. Add a "mixed" strategy baseline (hypothesis on first failure, engineering otherwise).

## Implications for Autonomous Evolution Harness

### When to Use Which Strategy
- **Simple/mechanical tasks**: Engineering approach is sufficient and faster.
- **Debugging failures, unexpected behavior**: Default to hypothesis-driven. Force the agent to declare "I believe the cause is X because Y" before attempting fixes.
- **Hidden assumption bugs**: Hypothesis approach is essential. Without explicit assumption enumeration, agents may never consider the right fix dimension.

### Integration Points
1. **Failure classification**: Classify failures by category before choosing strategy.
2. **Hypothesis logging**: Record hypotheses in evolution logs for cross-iteration pattern analysis.
3. **Attempt budget**: Set different retry budgets by category (simple: 1-2, causal: 2-3, assumption: 3-5).

## Source Code
- Tasks: `experiments/hypothesis_validation/tasks.py`
- Strategies: `experiments/hypothesis_validation/strategies.py`
- Runner: `experiments/hypothesis_validation/runner.py`
- Analyzer: `experiments/hypothesis_validation/analyzer.py`
- Tests: `tests/test_hypothesis_validation.py`
- Research background: `docs/research/20260330-hypothesis-vs-engineering-thinking.md`
