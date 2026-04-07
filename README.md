# Entity

**The self-evolving outer loop for autonomous AI agents.**

> Where most agent frameworks stop when the task ends,
> Entity keeps going — accumulating knowledge, improving goals,
> and running indefinitely without losing context.

```
Entity
├── /inhale                  ← knowledge absorption (external research → session context)
├── /exhale                  ← knowledge evolution (insights → experiments + code)
├── /live                    ← finite self-evolving outer loop
│   └── SCORE → EVOLVE → converge
├── /live-inf                ← infinite outer loop (no iteration cap)
│   └── context rotation, world model, no session boundary
├── CTX                      ← context precision layer
│   └── LLM-free, 5.2% token budget, R@5=1.0 dependency recall
└── Safety Triad             ← EVOLVE gate (goal drift + reward hacking + CoT monitorability)
```

---

## What makes Entity different

| Feature | Entity | Oh My Codex | LangGraph |
|---------|--------|-------------|-----------|
| Infinite context rotation | ✓ | — | — |
| Self-evolving goals | ✓ | — | — |
| Knowledge absorption loop | ✓ | — | — |
| Safety Triad gate | ✓ | — | — |
| Parallel agent execution | via Oh My Codex | ✓ | partial |

**Oh My Codex solves**: "How do I run multiple agents in parallel right now?"
**Entity solves**: "How do I make agents improve themselves over time?"

They're not alternatives. They're layers.

---

## The Problem

Most agent frameworks are session-local. They run a task and stop.

Real autonomous work requires:
- **Context that persists** past the window limit without data loss
- **Goals that evolve** when the current one is achieved
- **Knowledge that accumulates** — each run deposits what it learned
- **Failures that are classified**, not just retried
- **Execution that continues** indefinitely — hours, not seconds

Entity is infrastructure for this.

---

## The Evolution Loop

```
/inhale (collect research) → /exhale (design experiments) → /live (execute + evolve)
        ↑                                                           |
        └───────────────── knowledge feedback ─────────────────────┘
```

Each cycle: external insights become experiments, experiments become improvements,
improvements raise the goal bar — until convergence.

---

## Components

### /inhale — Knowledge Absorption

Automated collection from research channels (arXiv, HN, newsletters, GeekNews).
Scores items by relevance, injects actionable insights into session context.

- 57-keyword relevance scoring (max 10.0)
- Reflect-type classification: stuck_agent / hypothesis_validation / skill_selection / evaluation
- Source attribution: channel → paper → date → URL (full provenance)

### /exhale — Knowledge Evolution

Transforms absorbed insights into concrete project artifacts:

- `experiment` mode → paired comparison design docs
- `code` mode → PR-ready implementation changes
- `design` mode → architecture integration specs
- `hypothesis` mode → H0/H1 with measurement protocol

All artifacts start as `proposed` → verified via experiment/test → `accepted`.

### /live — Finite Self-Evolving Outer Loop

```
iter N: autopilot → SCORE (5 dimensions) → EVOLVE goal → iter N+1
```

Stops when score improvement delta < epsilon (default 0.05) for k=3 consecutive iterations.

- score_ensemble_n=3 (multi-reviewer, reduces LLM scoring variance)
- goal_fidelity gate (min 0.7 per step, min 0.50 cumulative)
- Context budget check at 70% — triggers early handoff before exhaustion

### /live-inf — No Iteration Cap

Extends /live for indefinite execution:

- **Context rotation**: at 70% budget → safe state handoff → fresh session → resume
- **World model**: epistemic state layer persists across rotations
- **Co-evolution feedback**: strategy outcomes feed back into Wave 1

### CTX — Context Precision Layer

LLM-free context loader that classifies query type and selects the matching retrieval strategy.

- 5.2% average token budget (vs 40-60% for naive loading)
- R@5 = 1.0 on dependency recall
- Zero LLM calls for retrieval — pure algorithmic

### Safety Triad — EVOLVE Gate

Three-detector gate that must pass before any goal evolution:

1. **Goal drift detector** — alignment check against original_goal (cosine similarity)
2. **Reward hacking detector** — divergence between score and task completion signal
3. **CoT monitorability checker** — TF-IDF cosine between CoT intent and actual action

---

## Empirical Foundations

Every design decision is backed by controlled experiments:

| Question | Finding | Impact on design |
|---------|---------|-----------------|
| How should agents reason? | Hypothesis-driven: **-50% attempts** on hard bugs, 100% first-hypothesis accuracy | Default reasoning in /live inner loop |
| Where are context limits? | **Threshold-based cliff**, not gradual fade — silent failure at specific lengths | Context rotation at 70% in /live-inf |
| Where do agents fail? | **3 predictable clusters**: wrong decomposition, role non-compliance, boundary violation | omc-failure-router classification |

---

## Quick Start

```bash
git clone https://github.com/jaytoone/HarnessOS  # repo rename to Entity pending
cd Entity

# Run hypothesis-driven vs engineering debugging experiment
python3 analyze.py --run

# Run all experiments
python3 runner.py --exp a   # context degradation (1K/10K/50K/100K tokens)
python3 runner.py --exp b   # autonomous agent failure classification

# Tests
python3 -m pytest           # 214 tests, 100% coverage
```

No pip install required. No API keys required for base experiments.

---

## Documentation

- [Architecture overview](docs/ARCHITECTURE.md)
- [Positioning & concept](docs/marketing/concept.md)
- [Experiment results](docs/research/)
- [Component specs](docs/)

---

## Status

| Component | Status |
|-----------|--------|
| CTX | Stable |
| /live | Stable |
| /live-inf | Stable |
| Safety Triad | Stable |
| /inhale + /exhale | Stable |
| HalluMaze | In development |
| Evaluation Layer | Planned |

---

## Why "Entity"

An entity persists. It accumulates state, learns from experience, and acts with continuity.

LLMs have enormous capability. Without control structure, that capability is
context-unaware, goal-unstable, failure-opaque, and session-local.

Entity adds the control structure — and keeps it running.
