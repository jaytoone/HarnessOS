# Multi-Agent RAG with Evolving Orchestration Design

## Source
- **Paper**: "Experience as a Compass: Multi-agent RAG with Evolving Orchestration and Agent Prompts"
- **arXiv**: [2604.00901](https://arxiv.org/abs/2604.00901) (2026-04-02)
- **Absorbed via**: /inhale agent_research — arXiv cs.AI
- **Relevance**: 10.0/10 (hypothesis_validation category)

## Core Idea
Multi-agent RAG where each agent has a specific role. The orchestration
and agent prompts evolve based on accumulated experience — a compass
that guides future query handling.

## HarnessOS Application

### Hypothesis
> Evolving the omc-live SKILL ROUTER's skill selection based on
> accumulated routing history (world-model.skill_routing_history)
> can improve task-type → skill matching accuracy by 20%+.

### Current System
- SKILL ROUTER uses keyword matching (Tier 1) + LLM selection (Tier 2)
- Static: same logic regardless of past routing outcomes

### Proposed System
- Add "compass" layer: weight skill selection by historical score_delta
- Skills with high past score_delta for this task_type get priority
- Skills with low past score_delta get deprioritized
- This is already partially implemented in live-inf Step 3e (world-model filter)
- Enhancement: use weighted scoring instead of binary filter

### Validation
- Compare routing accuracy before/after compass weighting
- Metric: average score_delta per routed skill across 10+ iterations
