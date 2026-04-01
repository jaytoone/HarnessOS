# Autonomous Skill Selection: Quick Reference
**Date**: 2026-03-31 | **For**: omc-live and 50+ skill scenarios | **Format**: Decision tree + implementation checklists

---

## TOP 3 RANKED APPROACHES

### 1. SEMANTIC ROUTING (Rank: Best)
**Score**: 9.5/10 practical applicability | **Latency**: 50-100ms | **Cost**: ~100 tokens

**What It Does**: Embeds task → classifies into skill clusters → routes to 1-3 specialists

**Implementation Time**: 1-2 weeks | **Complexity**: Low

**Key Metric**: 80%+ routing accuracy, <100ms latency

**When To Use**: 70% of tasks (default fast path)

**Research Backing**:
- vLLM Semantic Router (2025) — production-proven
- RedHat LLM Semantic Router (2025) — embeddings + caching
- RouteLLM (Berkeley 2024) — cost-effective routing with transfer learning

**Pseudo-Code**:
```python
def route(task: str) -> List[Skill]:
    query_vector = embed(task)  # all-MiniLM-L6-v2
    scores = cosine_similarity(query_vector, cluster_centers)
    if max(scores) >= 0.70:
        return top_k(skills_by_score(scores), k=3)
    else:
        return ABSTAIN  # request clarification
```

**Pro**: Fast, stateless, no training | **Con**: Needs manual skill taxonomy

---

### 2. ReAct WITH TOOL SCORING (Rank: Second)
**Score**: 8.5/10 practical applicability | **Latency**: 500ms-2s | **Cost**: ~1000 tokens

**What It Does**: Multi-prompt reasoning loop: understand → identify candidates → plan → score → select

**Implementation Time**: 1-2 weeks | **Complexity**: Medium

**Key Metric**: 10%+ improvement in selection quality vs Tier 1

**When To Use**: 25% of tasks (ambiguous/complex)

**Research Backing**:
- Pre-Act (DeepSeek 2025) — multi-step planning before acting
- ReAct Grounding (EMNLP 2025) — track world state during reasoning
- ReAct Survey (Springer 2025) — inherent vs external reasoning tools

**Prompt Sequence**:
```
1. UNDERSTAND: What information gaps? What assumptions?
2. IDENTIFY: Which 5 skills could help? Why each?
3. PLAN: Execution order? Success criteria?
4. SCORE: For each candidate → relevance/info_gain/cost → rank
5. SELECT: Execute top-1, queue top-3
```

**Pro**: Transparent reasoning, handles novel tasks | **Con**: Slower, requires good skill descriptions

---

### 3. MIXTURE-OF-AGENTS (Rank: Third)
**Score**: 7.5/10 practical applicability | **Latency**: 5-15s | **Cost**: ~5000 tokens

**What It Does**: Layer 1 (4 discovery agents) → Layer 2 (4 analysis agents, see Layer 1) → Aggregation

**Implementation Time**: 2-3 weeks | **Complexity**: High

**Key Metric**: 2-3% quality improvement over best single agent

**When To Use**: <5% of tasks (high-stakes: security, critical refactoring)

**Research Backing**:
- Mixture-of-Agents (Wang et al., Stanford 2024) — surpasses GPT-4 Omni on AlpacaEval 2.0
- Agent0 Co-evolution (Qwen 2025) — +18% math, +24% general reasoning
- MoA open-source models outperform GPT-4 Omni by +7.6%

**Architecture**:
```
Layer 1 (parallel):
  - semantic-analyzer, dependency-mapper, pattern-detector, requirement-extractor

Layer 2 (parallel, sees Layer 1):
  - impact-assessor, feasibility-checker, quality-estimator, efficiency-analyzer

Aggregation:
  - Meta-LLM synthesizes all 8 responses → unified recommendation
```

**Pro**: Best quality, consensus-driven, robust to individual failures | **Con**: Expensive, slow, overkill for simple tasks

---

## RECOMMENDED ARCHITECTURE: TIERED ROUTING

```
TASK INPUT
    │
    ├─→ TIER 1: Semantic Router (10ms)
    │   └─→ confidence >= 0.75?
    │       ├─ YES → EXECUTE (70% of tasks)
    │       └─ NO → Tier 2
    │
    ├─→ TIER 2: ReAct Scorer (1-2s)
    │   └─→ score >= 0.8?
    │       ├─ YES → EXECUTE (25% of tasks)
    │       └─ NO → Tier 3
    │
    └─→ TIER 3: MoA Aggregation (10-15s)
        └─→ EXECUTE with expert consensus (5% of tasks)

COST PROFILE:
- Tier 1 (70%):  100 tokens × 0.70 = 70 tokens
- Tier 2 (25%): 1000 tokens × 0.25 = 250 tokens
- Tier 3 (5%):  5000 tokens × 0.05 = 250 tokens
─────────────────────────────────────────────────────
TOTAL AVERAGE: ~570 tokens/task
vs. Always MoA: 5000 tokens/task (8.8x savings)
```

---

## IMPLEMENTATION PHASES

### Phase 1: Semantic Router (Week 1-2)
**File**: `~/.claude/skills/semantic-router/SKILL.md`

```
[ ] 1. Define skill taxonomy (50+ → 10-12 clusters)
[ ] 2. Pre-compute cluster centers (embedding model)
[ ] 3. Implement cosine similarity routing
[ ] 4. Test on 20 sample tasks
[ ] 5. Measure: latency <100ms, accuracy >80%
[ ] 6. Deploy to omc-live as Tier 1
```

**Success**: Route to top-3 skills in <100ms

---

### Phase 2: ReAct Scorer (Week 3-4)
**File**: `~/.claude/skills/react-tool-scorer/SKILL.md`

```
[ ] 1. Design 4-prompt loop (understand → plan → score)
[ ] 2. Implement scoring formula (relevance/info_gain/cost)
[ ] 3. A/B test vs Tier 1 on 50 tasks
[ ] 4. Measure: decision quality +10%?
[ ] 5. Integrate fallback logic (Tier 1 → Tier 2)
[ ] 6. Deploy to omc-live as Tier 2
```

**Success**: ReAct improves selection by >10% on ambiguous cases

---

### Phase 3: MoA Aggregator (Week 5-7, optional)
**File**: `~/.claude/skills/moa-executor/SKILL.md`

```
[ ] 1. Define Layer 1 & Layer 2 skill sets
[ ] 2. Implement parallel execution + aggregation
[ ] 3. Test on 10 high-stakes tasks
[ ] 4. Measure: quality improvement >2%
[ ] 5. Setup cost/latency guardrails
[ ] 6. Deploy as Tier 3 (on-demand)
```

**Success**: MoA consensus >2% more accurate than best single skill

---

### Phase 4: Integration (Week 8)
```
[ ] 1. Add skill_selection_method config to live-state.json
[ ] 2. Hook Tier 1 at omc-live outer loop START
[ ] 3. Implement fallback chain (T1 → T2 → T3)
[ ] 4. Log all selection decisions (audit trail)
[ ] 5. Measure impact on convergence speed + quality
```

---

## SKILL TAXONOMY TEMPLATE

For semantic routing, pre-define clusters:

```yaml
clusters:
  code_modification:
    - file-create, implement-feature, fix-syntax, refactor-code
  
  code_analysis:
    - search-codebase, analyze-dependencies, measure-complexity
  
  research_synthesis:
    - search-papers, summarize-findings, compare-approaches
  
  validation_testing:
    - run-tests, validate-output, performance-check
```

---

## KEY PARAMETERS & THRESHOLDS

| Parameter | Recommended | Tuning Rule |
|-----------|-------------|------------|
| Semantic routing threshold | 0.70 | If >90% accuracy, lower to 0.65 |
| ReAct scoring threshold | 0.80 | If ReAct selection fails, lower to 0.75 |
| MoA activation complexity | >0.75 | Tune based on task difficulty |
| Layer 1 timeout | 5 min | Increase if skills timeout |
| Cluster similarity metric | cosine | Use dot-product if angle matters |

---

## VALIDATION CHECKLIST

### Before Deploying Tier 1 (Semantic Router)
- [ ] 20+ sample tasks classified correctly
- [ ] Latency <100ms consistently
- [ ] Confidence scores calibrated (high score = high accuracy)
- [ ] Skill taxonomy covers >90% of use cases
- [ ] Handles edge cases (ambiguous, multi-domain tasks)

### Before Deploying Tier 2 (ReAct Scorer)
- [ ] Reasoning output is human-interpretable
- [ ] Scores correlate with actual success
- [ ] A/B test shows >10% improvement on Tier 1 failures
- [ ] No infinite reasoning loops (step limit enforced)
- [ ] Cost estimates accurate within 20%

### Before Deploying Tier 3 (MoA)
- [ ] Layer 1 + Layer 2 execute in parallel without conflicts
- [ ] Aggregation handles conflicting opinions gracefully
- [ ] Quality gains >2% justify 10-15s latency
- [ ] Cost guardrails prevent budget explosion

---

## REFERENCES (Cited Research)

**Key Papers**:
1. RouteLLM (arXiv:2406.18665) — Cost-effective routing
2. Mixture-of-Agents (arXiv:2406.04692) — Layered architecture
3. Pre-Act (DeepSeek 2025) — Planning before acting
4. Agent0 (arXiv:2511.16043) — Co-evolution
5. vLLM Semantic Router (2025) — Production implementation

**Full Details**: See `20260331-autonomous-skill-selection-research.md` (652 lines, 2024-2026 research synthesis)

---

## DECISION TREE: WHICH APPROACH FOR YOUR USE CASE?

```
START: "How many available skills?"
├─ <10 skills
│  └─→ Use ReAct Scorer (explicit reasoning for small set)
│
├─ 10-50 skills
│  ├─ "Need fast routing?"
│  │  ├─ YES → Semantic Router (Tier 1) + ReAct (Tier 2)
│  │  └─ NO → ReAct Scorer (single-stage)
│  │
│  └─ "High-stakes decisions?"
│     ├─ YES → Add MoA (Tier 3)
│     └─ NO → Tiers 1 + 2 sufficient
│
└─ >50 skills
   ├─ "Unbounded task diversity?" (like omc-live)
   │  └─ YES → Semantic Router (Tier 1) + fallback chain
   │
   └─ "Tasks from fixed domains?"
      └─ YES → Pre-partition into domain-specific routers
         then apply same tiering per domain
```

For **omc-live specifically**: Use all 3 tiers (Semantic → ReAct → MoA) because:
- Unbounded skill set (50+)
- Uncertain task complexity
- Convergence quality matters
- Can afford 5-15s on hard problems

## Related
- [[projects/HarnessOS/research/20260331-autonomous-skill-selection-research|20260331-autonomous-skill-selection-research]]
- [[projects/HarnessOS/research/20260328-omc-live-infinite-loop-architecture-research|20260328-omc-live-infinite-loop-architecture-research]]
- [[projects/HarnessOS/research/20260327-omc-live-autonomous-ai-research-2025-2026|20260327-omc-live-autonomous-ai-research-2025-2026]]
- [[projects/HarnessOS/research/20260331-skill-selection-implementation-templates|20260331-skill-selection-implementation-templates]]
- [[projects/HarnessOS/research/20260326-omc-live-skill-critique|20260326-omc-live-skill-critique]]
- [[projects/HarnessOS/research/20260326-omc-live-self-evolving-outer-loop|20260326-omc-live-self-evolving-outer-loop]]
- [[projects/HarnessOS/research/20260328-omc-live-science-research-domain-expansion|20260328-omc-live-science-research-domain-expansion]]
- [[projects/HarnessOS/research/20260324-openhands-autonomous-global-setup|20260324-openhands-autonomous-global-setup]]
