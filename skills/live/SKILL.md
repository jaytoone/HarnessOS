---
name: entity-live
description: Fully autonomous self-evolving outer loop — runs until convergence, elevates goals automatically, and learns from each iteration via episode memory
version: 1.0.0
author: jaytoone
tags: [entity, agent, autonomous, loop, self-evolving, outer-loop, convergence]
category: development
---

# Entity Live — Self-Evolving Outer Loop

Part of the **Entity** self-evolving agent framework. The outer loop that makes agents get smarter each run. Executes, scores, evolves goals, and repeats — until convergence.

```
/live Goal: <your task>
/live -i Goal: <your task>    # infinite mode (no iteration limit)
```

## What It Does

1. **Executes** — runs an inner autopilot loop on your goal
2. **Scores** — multi-dimensional evaluation (quality, completeness, efficiency, impact)
3. **Evolves** — if the goal is met, elevates to the next level of excellence
4. **Repeats** — until improvement plateaus (self-convergence)

No manual intervention needed. The loop terminates only when there's nothing left to improve.

## When to Use

- Any task that benefits from iteration — code, research, writing, optimization
- When you want the agent to keep improving without you defining every step
- When a single autopilot run isn't enough — quality matters

## Modes

| Command | Mode | Terminates When |
|---------|------|-----------------|
| `/live Goal: X` | Bounded (5 iterations) | Budget OR convergence |
| `/live -i Goal: X` | Infinite | Convergence only (no budget) |

## Architecture

```
/live (Outer Loop)
    ├── [SCORE] Multi-dimensional evaluator
    │     dimensions: quality, completeness, efficiency, impact
    ├── [EVOLVE] Goal elevation engine
    │     "Goal met at 0.82 → elevate to next level"
    ├── [ROUTE] Autonomous skill router
    │     routes task_type → best specialist skill/agent
    └── Autopilot (Inner Loop)
          ├── Phase 0: Explore
          ├── Phase 1: Plan
          ├── Phase 2: Implement
          ├── Phase 3: Verify
          └── Phase 4: Cleanup
```

## Self-Evolution Mechanism

```
start_score: 0.72
iter 1: quality +0.08, completeness +0.05 → score: 0.80 → EVOLVE goal
iter 2: impact +0.12 → score: 0.89 → EVOLVE goal
iter 3: delta < epsilon for 3 iterations → CONVERGED (score: 0.91)
```

Goal evolution example:
```
v0: "write a unit test suite"
v1: "write unit tests + add edge cases for null inputs"  ← auto-elevated
v2: "write tests + edge cases + performance benchmarks"  ← auto-elevated
CONVERGED at v2 score: 0.91
```

## State Files

```
.omc/
  goal-tree.json       ← current goal + evolution history
  live-state.json      ← iteration counter + scores
  episodes.jsonl       ← execution history (cross-session learning)
  world-model.json     ← epistemic state (infinite mode)
  live-progress.log    ← per-iteration score log
```

## Example Output

```
[live] Outer goal: write a unit test suite
[live] iter 1/5: success | score: 0.72 → EVOLVE
[live] iter 2/5: success | score: 0.84 → EVOLVE
[live] iter 3/5: success | score: 0.91 → plateau(1/3)
[live] iter 4/5: success | score: 0.91 → plateau(2/3)
[live] iter 5/5: success | score: 0.91 → plateau(3/3)
[live] CONVERGED | best: 0.91 | 2 goal evolutions
```

## Configuration

```json
// .omc/live-config.json (optional overrides)
{
  "max_outer_iterations": 5,
  "epsilon": 0.05,
  "plateau_k": 3,
  "score_ensemble_n": 3,
  "evaluator_mode": "self"
}
```

## Part of Entity Framework

```
/inhale  → absorb external knowledge
/exhale  → design experiments from insights
/live    → execute until convergence  ← you are here
```

See [Entity on GitHub](https://github.com/jaytoone/HarnessOS) for full framework.
