# Dev.to Post — HarnessOS

**Title:**
```
HarnessOS: scaffold/middleware for infinite autonomous tasks — built on Harness Engineering
```

**Tags:** `ai`, `agents`, `opensource`, `productivity`

**Body:**
```markdown
There's a concept gaining traction in AI systems engineering: **Harness Engineering**.

Not the testing tool. The idea: raw LLM capability is like raw power — high voltage,
hard to control, dangerous to run indefinitely. Harness Engineering is the discipline of
building the control structures that make that power *usable at scale*.
Context managers. Evaluation loops. Failure classifiers. Goal trackers. Memory tiers.

I think it's going to be one of the defining disciplines of serious AI systems work.
And I've been building a platform around it.

---

## What I Built

**HarnessOS** is a scaffold/middleware system for running infinite autonomous tasks.

The key word is *infinite*. Not one task. Not one session. An agent that:
- Runs continuously, across context window rotations
- Evolves its own goals when it succeeds at the current one
- Persists state across sessions without losing context
- Classifies its own failures and routes them appropriately

This is the architecture:

```
HarnessOS
├── CTX                      ← context precision layer
│   └── LLM-free retrieval, 5.2% token budget, R@5=1.0 dependency recall
├── omc-live                 ← finite outer loop
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

## The Problem with Current Agent Frameworks

Most agent frameworks are built for tasks that complete in one session.

Spin up → run → done.

That's fine for demos. It breaks for real autonomous work:

1. **Context exhaustion**: At ~70% context capacity, agents start losing earlier decisions.
   Not gracefully. They cliff-edge — sudden degradation, not gradual fade.

2. **No goal evolution**: An agent that succeeds at "write tests" has no mechanism to
   ask "what's the next improvement?" It just stops.

3. **Failure is terminal**: Most frameworks catch exceptions. Few *classify* them —
   transient vs persistent vs fundamental goal mismatch.

HarnessOS is built specifically to address all three.

---

## What I Measured (The Empirical Foundation)

Before building anything, I ran controlled experiments on questions I couldn't find
good empirical answers to anywhere else.

### Q1: How should autonomous agents reason about problems?

Compared **hypothesis-driven debugging** (observe → hypothesize → verify)
against **engineering-only** (pattern match → retry) on 12 bug scenarios.

| Bug type | Engineering | Hypothesis | Delta |
|---------|------------|------------|-------|
| Simple | 1.0 attempts | 1.0 attempts | none |
| Causal | 1.75 attempts | 1.0 attempts | **-43%** |
| Assumption | 2.0 attempts | 1.0 attempts | **-50%** |

First-hypothesis accuracy: **100%**. This is now the default reasoning strategy in omc-live.

### Q2: Where do context limits actually hit?

Measured Lost-in-the-Middle across 1K/10K/50K/100K token contexts.

**Key finding: degradation is threshold-based, not gradual.**

Agents don't slowly forget. They cliff-edge at a specific token length and fail silently.
This changed how `omc-live-infinite` handles context — it monitors budget and triggers
a safe rotation handoff at 70%, before the cliff.

### Q3: Where do autonomous agents actually fail?

OpenHands on 20-step coding tasks. Failure clusters:
1. Wrong task decomposition (incorrect sub-goals from the start)
2. Role non-compliance (agent exceeds defined scope)
3. Boundary violations (unexpected state mutations)

Predictable = preventable. The omc-failure-router classifies failures into these
categories and routes them appropriately instead of generic retry.

---

## The Architecture in Practice

### omc-live: Finite Self-Evolving Loop

```
Wave 1: Strategy consultation (specialist agents, runs once)
   ↓
Wave 2: Execution loop
   ↓
Judgment: Goal achieved?
   ├── NO  → update goal tree, retry
   └── YES → Score (5 dimensions)
                ├── delta ≥ epsilon → EVOLVE goal, continue
                └── plateau × 3    → CONVERGED, stop
```

When the system succeeds, it scores the output, finds the weakest dimension,
generates an elevated goal, and continues — until quality plateaus.

### omc-live-infinite: No Iteration Cap

New mechanisms beyond the finite version:
- **Context rotation**: at 70% budget → save state → fresh session → resume
- **World model**: epistemic state layer that persists across rotations
- **Co-evolution feedback**: strategy outcomes feed back into Wave 1 planning

Enables agents that work on complex goals for hours, not seconds.

### CTX: Precision Context Loading

Query classification → retrieval strategy selection:
- EXPLICIT_SYMBOL → direct lookup
- SEMANTIC_FUNCTIONALITY → embedding search
- STRUCTURAL_RELATIONSHIP → dependency graph
- RECENT_CHANGE → git recency

Result: 5.2% average token budget, R@5=1.0. No LLM calls for retrieval.

---

## Why "Harness Engineering" Is the Right Frame

A harness doesn't constrain power — it *channels* it.

LLMs have enormous capability. Without control structure, that capability is:
context-unaware, goal-unstable, failure-opaque, session-local.

HarnessOS adds the control structure. Not to limit the model — to make it usable
for work that spans hours, not seconds.

---

## Current State & Quick Start

214 tests, 100% coverage. CTX and omc-live/infinite are stable and used daily.

```bash
git clone https://github.com/jaytoone/HarnessOS
python3 analyze.py --run
```

No pip install. No required API keys for base experiments.

GitHub: https://github.com/jaytoone/HarnessOS

If you're building autonomous agents and thinking about long-run reliability — happy to compare notes.
```
