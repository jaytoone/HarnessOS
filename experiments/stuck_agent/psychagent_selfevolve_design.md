# PsychAgent Self-Evolving Pattern Application Design

## Source
- **Paper**: "PsychAgent: An Experience-Driven Lifelong Learning Agent for Self-Evolving Psychological Counselor"
- **arXiv**: [2604.00931](https://arxiv.org/abs/2604.00931) (2026-04-02)
- **Absorbed via**: /inhale agent_research — arXiv cs.AI (knowledge-channels.yaml)
- **Relevance**: 10.0/10 (skill_selection category)

## Core Idea from Paper
PsychAgent replaces static fine-tuning with experience-driven lifelong learning.
The agent accumulates interaction experiences and evolves its strategies over time,
contrasting with the conventional approach of training on fixed datasets.

## HarnessOS Application

### Hypothesis
> Applying PsychAgent's experience-driven evolution pattern to omc-episode-memory
> can improve cross-trajectory recombination quality by 15-25%, measured by
> the relevance score of retrieved episodes to the current task.

### Current System (Baseline)
```
omc-episode-memory:
  - TF-IDF cosine similarity for episode retrieval (when >= 5 episodes)
  - Tag-based fallback (< 5 episodes)
  - Static retrieval: episodes are stored and retrieved, not evolved
```

### Proposed System (Treatment)
```
omc-episode-memory + experience evolution:
  - After each successful run: extract "experience patterns" (not just raw episodes)
  - Pattern format: {task_type, strategy_used, outcome, key_decision, generalizability_score}
  - Experience compression: merge similar episodes into "experience clusters"
  - Retrieval uses experience patterns first, raw episodes as fallback
  - Evolution: patterns that lead to success get reinforced (weight += delta)
```

### Experiment Protocol
1. **Baseline**: Current omc-episode-memory with 20+ episodes
2. **Treatment**: Experience-pattern-enhanced retrieval
3. **Metric**: episode_relevance_score (human-rated 1-5 scale, 10 retrievals)
4. **Secondary**: escape_rate when using retrieved episodes as context
5. **Statistical test**: Paired t-test (same 10 task queries, both systems)

### Implementation Plan
```
experiments/stuck_agent/
  psychagent_selfevolve_design.md  ← this file
  experience_patterns.py           ← new: extract patterns from episodes
  pattern_retrieval.py             ← new: pattern-based retrieval
```

### Expected Outcome
- 15-25% improvement in episode relevance scores
- Better cross-trajectory recombination quality
- Validates PsychAgent's experience-driven approach in agent debugging context
