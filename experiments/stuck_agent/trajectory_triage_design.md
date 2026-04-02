# Trajectory Triage Experiment Design

## Source
- **Paper**: "Signals: Trajectory Sampling and Triage for Agentic Interactions"
- **arXiv**: [2604.00356](https://arxiv.org/abs/2604.00356) (2026-04-02)
- **Absorbed via**: `/absorb agent_research` — knowledge-channels.yaml > arXiv cs.AI
- **Relevance**: 10.0/10 (stuck_agent category)

## Core Idea from Paper
Agentic applications rely on multi-step interaction loops (planning, action execution,
environment observation). The paper proposes **trajectory sampling and triage** to:
1. Sample key decision points from agent trajectories
2. Classify trajectory health early (before full execution completes)
3. Triage: route healthy trajectories to continue, stuck ones to intervention

## HarnessOS Application

### Hypothesis
> Applying trajectory triage to omc-failure-router can detect stuck-agent states
> **2-3 steps earlier** than the current post-failure classification, reducing
> wasted computation and enabling preemptive escape strategy selection.

### Current System (Baseline)
```
omc-autopilot Phase 3 (implementation)
  → failure occurs
  → omc-failure-router classifies: Transient / Persistent / Fatal
  → response: retry / restructure / escalate
```
**Problem**: Classification happens AFTER failure. Agent may have been stuck for
multiple steps before failure is detected, wasting compute.

### Proposed System (Treatment)
```
omc-autopilot Phase 3 (implementation)
  → trajectory sampler runs every N steps (configurable)
  → samples: {step_number, action_type, outcome_signal, repetition_count}
  → triage classifier: HEALTHY / AT_RISK / STUCK
  → if AT_RISK: inject course-correction hint
  → if STUCK: preemptive escape (skip to failure-router with pre-classified type)
```

### Trajectory Signals to Sample
Based on the Signals paper + HarnessOS stuck-agent experiment results:

| Signal | Description | Stuck Indicator |
|--------|-------------|-----------------|
| `action_repetition` | Same tool call pattern repeated | >= 3 consecutive |
| `output_similarity` | Cosine similarity between consecutive outputs | > 0.95 |
| `error_cycling` | Same error message recurring | >= 2 identical errors |
| `progress_stall` | No new files modified / no test delta | >= 2 steps |
| `strategy_fixation` | Same approach despite failure signal | classifier confidence < 0.3 |

### Triage Decision Matrix

| Signals Fired | Classification | Action |
|---------------|---------------|--------|
| 0 signals | HEALTHY | Continue normally |
| 1 signal | HEALTHY | Log warning, continue |
| 2 signals | AT_RISK | Inject hint: "Consider alternative approach" |
| 3+ signals | STUCK | Preemptive escape → failure-router (skip remaining steps) |

### Connection to Existing Classifier
The existing `classifier.py` categorizes bugs into:
- `red_herring` → hypothesis-driven strategy (+7.5%)
- `semantic_inv` → engineering-driven strategy (+40.0%)
- `hidden_assume` → hypothesis-driven
- `multi_bug` → needs decomposition

**Integration**: When trajectory triage detects STUCK, pass the accumulated
trajectory signals to the classifier to **pre-select** the optimal escape strategy
BEFORE the full failure occurs. This is the key speedup.

### Experiment Protocol

**Design**: Within-subject, paired comparison (same as existing stuck-agent experiments)

1. **Tasks**: Reuse existing `get_stuck_tasks()` from `tasks.py` (N=20 tasks)
2. **Trials per task**: 5 (statistical power)
3. **Conditions**:
   - Control: Current system (failure → classify → rescue)
   - Treatment: Trajectory triage (sample → triage → preemptive rescue)
4. **Metrics**:
   - Primary: `escape_rate` (treatment vs control)
   - Secondary: `steps_to_escape` (how many steps before escape succeeds)
   - Secondary: `compute_saved` (steps avoided by preemptive triage)
5. **Statistical test**: McNemar's test (paired binary outcomes), same as verification_hurt experiment

### Implementation Plan

```
experiments/stuck_agent/
  trajectory_triage_design.md    ← this file
  trajectory_sampler.py          ← new: samples signals from trajectory
  trajectory_triage.py           ← new: triage classifier (HEALTHY/AT_RISK/STUCK)
  runner.py                      ← modify: add TriageLLMStuckRunner
```

**Phase 1** (sampler): Extract trajectory signals from existing runner logs
**Phase 2** (triage): Build rule-based triage classifier
**Phase 3** (integration): Wire into runner.py as new TriageLLMStuckRunner
**Phase 4** (experiment): Run paired comparison, compute McNemar's

### Expected Outcome
- 10-20% improvement in escape_rate due to earlier intervention
- 30-50% reduction in steps_to_escape (preemptive vs reactive)
- Validates that /absorb pipeline → experiment design → execution loop works end-to-end

### Dependencies
- `experiments/stuck_agent/runner.py` — existing runner infrastructure
- `experiments/stuck_agent/classifier.py` — existing bug type classifier
- `omc-failure-router` — target for integration after experiment validation
