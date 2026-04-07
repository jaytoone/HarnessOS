---
name: entity-exhale
description: Transform absorbed research insights into actionable experiments, code changes, or design documents — bridges knowledge absorption to project advancement
version: 1.0.0
author: jaytoone
tags: [entity, agent, evolution, experiment-design, execution, self-evolving]
category: development
---

# Entity Exhale — Knowledge-to-Experiment Converter

Part of the **Entity** self-evolving agent framework. Takes insights from `/inhale` and converts them into concrete, executable artifacts: experiment designs, code changes, or architecture documents.

```
/exhale
```

## What It Does

1. Reads injected context from `/inhale` (or session memory)
2. Identifies the highest-leverage insight for your current project state
3. Designs a concrete experiment or implementation plan
4. Produces an artifact — ready for `/live` to execute autonomously

## When to Use

- After `/inhale` has absorbed new research — convert it to action
- When you have insights but need a structured execution plan
- Before starting a `/live` autonomous loop — to set a clear hypothesis

## Do Not Use When

- You haven't run `/inhale` or don't have external context to convert
- You want to directly implement (skip design) — use `/live` directly

## Configuration

```
/exhale --mode experiment    # output: experiment design document
/exhale --mode code          # output: implementation diff/plan
/exhale --mode architecture  # output: design document
```

## Output Format

```
[exhale] Processing 3 insights from session context

Selected insight: "AI Scientist-v2 ensemble reviewer achieves 69% balanced accuracy"
Project relevance: SCORE phase scoring reliability

Experiment design:
  Hypothesis: Ensemble scoring (N=3) reduces false convergence vs single-call
  Method: A/B — single-call vs 3-call ensemble on 10 live-inf runs
  Metric: plateau_count at convergence, final best_score variance
  Artifact: .omc/live-config.json → score_ensemble_n: 3

→ Ready for /live execution
```

## Artifact Types

| Mode | Output | Used By |
|------|--------|---------|
| `experiment` | Hypothesis + method + metrics | `/live` outer loop |
| `code` | Implementation diff + file targets | `/live` autopilot |
| `architecture` | Design document | Manual review |

## Part of Entity Framework

```
/inhale  → absorb external knowledge
/exhale  → design experiments from insights  ← you are here
/live    → execute until convergence
```

See [Entity on GitHub](https://github.com/jaytoone/HarnessOS) for full framework.
