# HarnessOS

**Scaffold/middleware for infinite autonomous tasks.**

Built on the emerging Harness Engineering discipline —
control structures that make autonomous AI agents reliable, self-improving, and indefinitely runnable.

```
HarnessOS
├── CTX                      ← context precision layer
│   └── LLM-free, 5.2% token budget, R@5=1.0 dependency recall
├── omc-live                 ← finite self-evolving outer loop
│   └── 2-Wave strategy + self-evolving goals + episode memory
├── omc-live-infinite        ← infinite outer loop
│   └── context rotation, world model, no iteration cap
├── HalluMaze                ← hallucination management (in development)
└── [future layers]
    ├── Evaluation Layer
    ├── Safety Layer
    └── Memory Tier System
```

---

## The Problem

Most agent frameworks are session-local. They run a task and stop.

Real autonomous work requires:
- **Context that persists** past the window limit without data loss
- **Goals that evolve** when the current one is achieved
- **Failures that are classified**, not just retried
- **Execution that continues** indefinitely — hours, not seconds

HarnessOS is infrastructure for this.

---

## Components

### CTX — Context Precision Layer

LLM-free context loader that classifies query type and selects the matching retrieval strategy.
Loads exactly the right files for each task.

- 5.2% average token budget (vs 40-60% for naive loading)
- R@5 = 1.0 on dependency recall
- Zero LLM calls for retrieval — pure algorithmic

### omc-live — Finite Self-Evolving Outer Loop

Wraps any inner loop with strategy consultation and self-improvement:

```
Wave 1: specialist strategy consultation (runs once per goal)
   ↓
Wave 2: execution + multi-dimensional scoring
   ↓
Self-evolves: scores output → elevates goal → continues until plateau
```

### omc-live-infinite — No Iteration Cap

Extends omc-live for indefinite execution:

- **Context rotation**: at 70% budget → safe state handoff → fresh session → resume
- **World model**: epistemic state layer persists across rotations
- **Co-evolution feedback**: strategy outcomes feed back into Wave 1

### HalluMaze — Hallucination Management *(in development)*

Maze-based evaluation harness for detecting and classifying hallucination patterns
in extended autonomous execution.

---

## Empirical Foundations

Every design decision is backed by controlled experiments:

| Question | Finding | Impact on design |
|---------|---------|-----------------|
| How should agents reason? | Hypothesis-driven: **-50% attempts** on hard bugs, 100% first-hypothesis accuracy | Default reasoning in omc-live inner loop |
| Where are context limits? | **Threshold-based cliff**, not gradual fade — silent failure at specific lengths | Context rotation at 70% in omc-live-infinite |
| Where do agents fail? | **3 predictable clusters**: wrong decomposition, role non-compliance, boundary violation | omc-failure-router classification |

---

## Quick Start

```bash
git clone https://github.com/jaytoone/HarnessOS
cd HarnessOS

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
| omc-live | Stable |
| omc-live-infinite | Stable |
| HalluMaze | In development |
| Evaluation Layer | Planned |
| Safety Layer | Planned |

---

## Why "Harness"

A harness doesn't constrain power — it channels it.

LLMs have enormous capability. Without control structure, that capability is
context-unaware, goal-unstable, failure-opaque, and session-local.

HarnessOS adds the control structure.
Not to limit the model — to make it usable for work that matters.
