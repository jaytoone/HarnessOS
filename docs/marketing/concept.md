# HarnessOS — Scaffold/Middleware for Infinite Autonomous Tasks

## The Shift: Harness Engineering

Something is changing in how serious AI engineers think about autonomous agents.

The early question was "can the agent do this task?" The emerging question is
"how do we make the agent *reliably* do any task, indefinitely, without falling apart?"

That second question is **Harness Engineering** — the practice of building control structures
around raw AI capability. Context managers, evaluation loops, failure classifiers, memory tiers,
goal trackers. The infrastructure that channels model power into reliable, directed work.

It's becoming a discipline. And HarnessOS is built around it.

---

## What HarnessOS Is

HarnessOS is a **scaffold/middleware system** for running infinite autonomous tasks.

Not a framework for one-off prompts. Not a wrapper around a single model call.
A layered platform that makes continuous, self-improving autonomous execution possible.

Three defining properties:

**1. Infinite execution**
Not single-session. Runs indefinitely — across context rotations, across sessions,
across goal evolutions. The system tracks its own state, upgrades its goals when it
succeeds, and resumes exactly where it left off.

**2. Layered middleware**
Each component addresses one dimension of agent reliability:

```
HarnessOS
├── CTX                      ← context precision layer
│   └── LLM-free retrieval, 5.2% token budget, R@5=1.0 dependency recall
├── omc-live                 ← finite outer loop
│   └── 2-Wave strategy + self-evolving goals + episode memory
├── omc-live-infinite        ← infinite outer loop
│   └── context rotation, world model persistence, no iteration cap
├── HalluMaze                ← hallucination management (in development)
└── [future layers]
    ├── Evaluation Layer
    ├── Safety Layer
    └── Memory Tier System
```

**3. Measurement-first**
No claims without evidence. Every architectural decision backed by controlled experiments:
- Hypothesis-driven debugging vs engineering-only (50% reduction in attempts on hard bugs)
- Context degradation is threshold-based, not gradual (cliff-edge, not fade)
- Autonomous agent failures cluster around 3 predictable patterns

---

## Why This Matters Now

The current generation of AI tools runs tasks. The next generation runs *indefinitely*.

- Agents that work for days without human intervention
- Goals that evolve as progress is made
- Context that persists across sessions without loss
- Failures that are classified and routed, not just caught and re-thrown

Most agent frameworks add capabilities. HarnessOS adds **control structure**.

The difference:
- Capability tools: "Here's what the agent can do"
- Harness tools: "Here's how the agent stays aligned, reliable, and improvable while doing it"

---

## Platform Trajectory

```
Today:         Scaffold for autonomous coding agents
Near-term:     Cross-domain task execution (research, analysis, writing, strategy)
Forward:       Composable autonomous systems — indefinite, reliable, self-improving
```

HarnessOS is not an AGI platform claim. It's the infrastructure that any serious path
toward reliable autonomous systems will need to build anyway. We're building it now,
with experiments driving every design decision.

---

## The Component Stack, Explained

### CTX — Context Precision Layer

The problem: autonomous agents waste 40-60% of their context on irrelevant files.
CTX is an LLM-free context loader that uses trigger classification + retrieval strategies
to load exactly the right files. 5.2% average token budget, R@5=1.0 on dependency recall.

### omc-live — Finite Outer Loop

The problem: autopilot inner loops complete a task but can't improve beyond first success.
omc-live wraps any inner loop with a self-evolving outer loop:
Wave 1 (specialist strategy consultation) → Wave 2 (iterative execution + scoring).
Goals evolve when quality plateaus. Runs until convergence.

### omc-live-infinite — Infinite Outer Loop

The problem: extended autonomous runs exhaust context mid-task, losing state.
omc-live-infinite adds context rotation (safe handoff across sessions),
a World Model (epistemic state layer, persists across rotations),
and no iteration budget. Terminates on convergence, not timeout.

### HalluMaze — Hallucination Management (in development)

The problem: hallucinations in long autonomous runs compound silently.
HalluMaze is a maze-based evaluation harness designed to detect and classify
hallucination patterns in extended agent execution. Design underway.

---

## Empirical Foundations

The platform design is driven by measured findings:

| Question | Finding |
|---------|---------|
| How should agents reason? | Hypothesis-driven: 50% fewer attempts on hard bugs, 100% first-hypothesis accuracy |
| Where are context limits? | Threshold-based cliff-edge, not gradual fade — silent failure at specific token lengths |
| Where do agents fail? | 3 clusters: wrong decomposition, role non-compliance, boundary violation |

These aren't academic results. They're design inputs. Every finding changed how a component was built.

---

## Quick Start

```bash
git clone https://github.com/jaytoone/HarnessOS
python3 analyze.py --run
```

No pip install. No required API keys for base experiments. 214 tests, 100% coverage.

---

## Links

- GitHub: https://github.com/jaytoone/HarnessOS
- Architecture: `docs/ARCHITECTURE.md`
- Experiment results: `results/` directory
- Research: `docs/research/`

## Related
- [[projects/HarnessOS/research/20260328-omc-live-infinite-loop-architecture-research|20260328-omc-live-infinite-loop-architecture-research]]
- [[projects/HarnessOS/research/20260330-hypothesis-experiment-results|20260330-hypothesis-experiment-results]]
- [[projects/HarnessOS/research/20260326-omc-live-self-evolving-outer-loop|20260326-omc-live-self-evolving-outer-loop]]
- [[projects/HarnessOS/research/20260330-harness-engineering|20260330-harness-engineering]]
- [[projects/HarnessOS/research/20260323-hypothesis-driven-agent-research|20260323-hypothesis-driven-agent-research]]
- [[projects/HarnessOS/research/20260327-omc-live-autonomous-ai-research-2025-2026|20260327-omc-live-autonomous-ai-research-2025-2026]]
- [[projects/HarnessOS/research/20260327-omc-live-git-checkpoint-self-evolving-research|20260327-omc-live-git-checkpoint-self-evolving-research]]
- [[projects/HarnessOS/research/20260325-autonomous-agent-goal-update-subloop-architecture|20260325-autonomous-agent-goal-update-subloop-architecture]]
