# Autonomous Skill Selection: Implementation Templates for Claude Code Skills
**Date**: 2026-03-31 | **For Claude Code Skill Markdown Protocol** | **Ready-to-adapt**

---

## TEMPLATE 1: Semantic Router Skill

**File**: `~/.claude/skills/semantic-router/SKILL.md`

```markdown
---
name: semantic-router
description: |
  Classify task intent into skill clusters and route to 1-3 relevant specialists.
  Uses embedding-based semantic similarity for fast, accurate task classification.
---

# Semantic Router

Route incoming tasks to the most relevant skills based on semantic similarity.

## Configuration

### Skill Clusters

Define clusters as JSON in your skill inventory:

```json
{
  "version": "1.0",
  "clusters": {
    "code_modification": {
      "skills": ["file-edit", "implement-function", "fix-syntax", "refactor", "add-imports"],
      "keywords": ["write", "create", "modify", "update", "change code", "implement feature"],
      "sample_task": "Add a new function to handle authentication"
    },
    "code_analysis": {
      "skills": ["search-codebase", "analyze-deps", "measure-complexity", "profile-perf", "detect-issues"],
      "keywords": ["understand", "find", "analyze", "search", "complexity", "performance", "broken"],
      "sample_task": "What functions call this API endpoint?"
    },
    "research_synthesis": {
      "skills": ["web-search", "fetch-document", "summarize-content", "compare-approaches", "extract-data"],
      "keywords": ["research", "find information", "summarize", "fetch", "search", "compare", "explain"],
      "sample_task": "Compare semantic routing approaches in LLM agents"
    },
    "testing_validation": {
      "skills": ["run-tests", "validate-output", "check-errors", "benchmark", "coverage"],
      "keywords": ["test", "verify", "check", "validate", "run", "benchmark", "pass", "fail"],
      "sample_task": "Run all tests and report failures"
    }
  }
}
```

## Execution Protocol

### Input
- `current_goal`: The task to classify (string)
- `available_skills`: List of all available skill names (optional, for context)

### Step 1: Embed Task
Use embedding model `all-MiniLM-L6-v2` (or equivalent):
```
task_vector = embed("${CURRENT_GOAL}")
```

### Step 2: Compare to Cluster Centers
Compute cosine similarity:
```
for each cluster in clusters:
  cluster_center = mean_embedding(cluster.sample_task + cluster.keywords)
  similarity_score[cluster] = cosine_sim(task_vector, cluster_center)
```

### Step 3: Rank & Select
```
ranked = sort(similarity_score, descending=True)
top_cluster = ranked[0].cluster
confidence = ranked[0].score

if confidence >= 0.70:
  selected_skills = ranked[0].cluster.skills[0:3]  # top-3 skills
  status = "ROUTED"
else:
  selected_skills = []
  status = "ABSTAIN"
  reason = "Low confidence; please clarify task intent"
```

### Step 4: Return Results
```json
{
  "status": "ROUTED",
  "primary_cluster": "code_modification",
  "confidence": 0.82,
  "selected_skills": ["file-edit", "implement-function", "fix-syntax"],
  "confidence_per_skill": [0.82, 0.75, 0.68],
  "alternative_clusters": [
    {"cluster": "code_analysis", "confidence": 0.45}
  ]
}
```

## Integration with omc-live

### Hook Point
Execute Semantic Router at the **START** of each omc-live outer loop iteration:

```python
# In omc-live SKILL.md, Step 2:
current_goal = live_state.goal
routing_result = execute_skill("semantic-router", goal=current_goal)

if routing_result.status == "ROUTED":
  selected_skills = routing_result.selected_skills
  confidence = routing_result.confidence
  
  if confidence >= 0.75:
    # FAST PATH: Execute immediately
    execution_method = "direct"
  else:
    # MEDIUM PATH: Use ReAct Scorer
    execution_method = "react_scorer"
else:
  # SLOW PATH: Use Mixture-of-Agents
  execution_method = "moa_aggregator"

live_state.skill_selection_method = execution_method
live_state.selected_skills = selected_skills
```

## Maintenance

### Updating Clusters
- Add new cluster when 5+ related skills emerge
- Merge clusters if <3 skills and high confusion
- Periodically re-compute cluster centers from skill descriptions

### Tuning Thresholds
- Initial threshold: 0.70
- If >90% accuracy on test set: lower to 0.65
- If <70% accuracy on test set: raise to 0.75

### Monitoring
Log all routing decisions:
```json
{
  "timestamp": "2026-03-31T15:30:00Z",
  "task": "Add error handling to API",
  "routed_cluster": "code_modification",
  "confidence": 0.84,
  "selected_skills": ["file-edit", "implement-function"],
  "actual_skill_used": "implement-function",
  "success": true
}
```

## Performance Targets
- **Latency**: <100ms (single embedding call + matrix multiply)
- **Accuracy**: >80% on test set (matches human classification)
- **Recall**: >95% (rare false negatives)

---

## TEMPLATE 2: ReAct Tool Scorer Skill

**File**: `~/.claude/skills/react-tool-scorer/SKILL.md`

```markdown
---
name: react-tool-scorer
description: |
  Multi-prompt reasoning loop to score and select the best skill.
  Uses: understand → identify → plan → score → select pattern.
---

# ReAct Tool Scorer

When Semantic Router confidence is low (0.65-0.75), use ReAct scoring for deliberate skill selection.

## Skill Registry

Each skill in registry has:
```json
{
  "name": "code-search",
  "description": "Search codebase using semantic similarity",
  "preconditions": ["indexed_codebase"],
  "postconditions": ["returns_matches"],
  "estimated_tokens": 1200,
  "estimated_latency_ms": 500,
  "domain_tags": ["analysis", "code", "research"]
}
```

## Reasoning Loop (4 Prompts)

### Prompt 1: UNDERSTAND (Extract task requirements)
```
Task: ${CURRENT_GOAL}

Analyze this task deeply:
1. What information do you need to solve it?
2. What are your key assumptions?
3. What would success look like?

Answer in 2-3 bullets.
```

### Prompt 2: IDENTIFY (Find candidate skills)
```
Available skills:
${SKILL_REGISTRY_JSON}

Given the task above, which 5-7 skills could help?
For each candidate, explain in one sentence why.

Format: "- {skill_name}: {why}"
```

### Prompt 3: PLAN (Design execution order)
```
From the candidates above, design an execution sequence:

1. What should execute FIRST? Why?
2. After observing results, what happens NEXT?
3. What are success criteria for each step?

Be concrete about data flow.
```

### Prompt 4: SCORE (Rate candidates)
```
For each candidate skill, estimate:

RELEVANCE (0.0-1.0): How directly does this address the task?
INFO_GAIN (0.0-1.0): Will it provide missing information?
COST (tokens): Estimated token consumption

Scoring formula:
score = (relevance × 0.50) + (info_gain × 0.35) - (cost_ratio × 0.15)

Return JSON:
[
  {"skill": "code-search", "relevance": 0.9, "info_gain": 0.7, "cost": 1200, "score": 0.85},
  {"skill": "dependency-analyze", "relevance": 0.6, "info_gain": 0.8, "cost": 800, "score": 0.68},
  ...
]

Sort by score descending.
```

## Execution Flow

```python
def react_score_skills(goal: str, skill_registry: list) -> dict:
    # Execute 4-prompt loop
    responses = {
        "understand": llm(prompt_1, goal),
        "candidates": llm(prompt_2, goal, skill_registry),
        "plan": llm(prompt_3, goal, candidates),
        "scores": llm(prompt_4, goal, skill_registry, plan)
    }
    
    # Parse scores JSON
    scored_skills = json.loads(responses["scores"])
    
    # Select top-1 for execution, queue top-3
    return {
        "reasoning_trace": responses,
        "selected_skill": scored_skills[0],
        "backup_skills": scored_skills[1:3],
        "confidence": scored_skills[0].score
    }
```

## Result Format
```json
{
  "status": "SCORED",
  "selected_skill": {
    "name": "code-search",
    "score": 0.85,
    "reasoning": "Highest relevance and information gain for task"
  },
  "backup_skills": [
    {"name": "dependency-analyze", "score": 0.68},
    {"name": "file-read", "score": 0.62}
  ],
  "confidence": 0.85,
  "reasoning_trace": "..."
}
```

## Integration with Tiered Routing

In omc-live:
```python
# Tier 1 returned low confidence (0.65-0.75)
if semantic_router.confidence < 0.75:
    react_result = execute_skill("react-tool-scorer", goal=current_goal)
    
    if react_result.confidence >= 0.80:
        selected_skill = react_result.selected_skill
        execution_method = "single_skill"
    else:
        # Fall through to Tier 3
        execution_method = "moa_aggregator"
```

## Performance Targets
- **Latency**: 500ms - 2s (4 LLM calls)
- **Accuracy**: >10% improvement vs Semantic Router on ambiguous tasks
- **Reasoning Quality**: Human-interpretable explanations

---

## TEMPLATE 3: Mixture-of-Agents Aggregator

**File**: `~/.claude/skills/moa-executor/SKILL.md`

```markdown
---
name: moa-executor
description: |
  Layered agent architecture: Layer 1 (4 discovery agents) + Layer 2 (4 analysis agents)
  + Aggregation. Best for high-stakes decisions.
---

# Mixture-of-Agents Executor

For complex or high-stakes tasks, run 8 specialist agents in layers + synthesize consensus.

## Layered Architecture

### Layer 1: Discovery (Parallel, independent)
Execute 4 agents that understand the task from different angles:

**Agent 1A: Semantic Analyzer**
```
Task: ${ORIGINAL_TASK}

Analyze this task from first principles:
1. What is the core objective?
2. What are the constraints?
3. What information is essential vs. nice-to-have?
```

**Agent 1B: Dependency Mapper**
```
Task: ${ORIGINAL_TASK}

What code/systems/components does this task touch?
- List 5-10 related files/modules
- Show dependency graph
- Identify potential risks
```

**Agent 1C: Pattern Detector**
```
Task: ${ORIGINAL_TASK}

Search your knowledge of similar tasks:
- Have we solved something like this before?
- What patterns apply?
- What antipatterns to avoid?
```

**Agent 1D: Requirement Extractor**
```
Task: ${ORIGINAL_TASK}

What does this task actually require?
- Functional requirements (must-have)
- Non-functional requirements (performance, security, etc.)
- Success criteria
```

**Collect**: [response_1a, response_1b, response_1c, response_1d]

### Layer 2: Analysis (Parallel, sees Layer 1 outputs)
Each agent refines based on Layer 1 context:

**Agent 2A: Impact Assessor**
```
Task: ${ORIGINAL_TASK}

Layer 1 findings:
${response_1a}
${response_1b}
${response_1c}
${response_1d}

Given above, what will change?
- Affected systems
- Breaking changes
- Downstream impacts
```

**Agent 2B: Feasibility Checker**
```
Task: ${ORIGINAL_TASK}

Can this actually be done?
- Blockers or constraints?
- Required skills/tools available?
- Timeline realistic?
```

**Agent 2C: Quality Estimator**
```
Task: ${ORIGINAL_TASK}

Will the result meet quality bar?
- Code quality
- Test coverage needed
- Documentation required
```

**Agent 2D: Efficiency Analyzer**
```
Task: ${ORIGINAL_TASK}

What's the optimal approach?
- Most efficient path
- Resource usage (tokens, time, compute)
- Cost-benefit tradeoff
```

**Collect**: [response_2a, response_2b, response_2c, response_2d]

### Aggregation: Synthesis

```
Original Task: ${ORIGINAL_TASK}

Layer 1 Perspectives:
- Semantic: ${response_1a}
- Dependencies: ${response_1b}
- Patterns: ${response_1c}
- Requirements: ${response_1d}

Layer 2 Refinements:
- Impact: ${response_2a}
- Feasibility: ${response_2b}
- Quality: ${response_2c}
- Efficiency: ${response_2d}

Synthesize into one coherent recommendation:
1. What's the core recommendation?
2. Areas of agreement across agents
3. Conflicts/trade-offs
4. Confidence level (0-1)
5. Risks to monitor
```

## Execution Algorithm

```python
def moa_execute(task: str, skill_config: dict) -> dict:
    # Validate task complexity
    complexity = estimate_complexity(task)
    if complexity < 0.75:
        return {"status": "SKIP_MoA", "reason": "Use Tier 1/2 instead"}
    
    # Layer 1: Parallel execution
    layer1_results = parallel_execute([
        ("semantic-analyzer", task),
        ("dependency-mapper", task),
        ("pattern-detector", task),
        ("requirement-extractor", task)
    ], timeout=300)
    
    if any_timeout(layer1_results):
        return {"status": "TIMEOUT", "reason": "Layer 1 exceeded timeout"}
    
    # Layer 2: Parallel execution with Layer 1 context
    layer2_results = parallel_execute([
        ("impact-assessor", task, layer1_results),
        ("feasibility-checker", task, layer1_results),
        ("quality-estimator", task, layer1_results),
        ("efficiency-analyzer", task, layer1_results)
    ], timeout=300)
    
    # Aggregation
    final = llm_synthesize(task, layer1_results, layer2_results)
    
    return {
        "status": "AGGREGATED",
        "final_recommendation": final.recommendation,
        "layer1_responses": layer1_results,
        "layer2_responses": layer2_results,
        "confidence": final.confidence,
        "execution_time_ms": elapsed_time()
    }
```

## Cost Control

```python
# Budget guard: Skip MoA if too expensive
def should_run_moa(task: str, latency_budget_ms: int) -> bool:
    estimated_time = 2 * 300  # 2 layers * 300ms timeout
    token_budget = 5000  # estimated tokens for 8 agents
    
    if estimated_time > latency_budget_ms:
        return False  # Fall back to Tier 1/2
    
    if current_session_tokens + token_budget > total_budget:
        return False  # Cost exceeded
    
    return True
```

## When to Use MoA

- Task complexity > 0.75 (computed by ReAct scorer)
- High-stakes decision (security, critical refactoring)
- User explicitly requests "expert review" or "thorough analysis"
- Confidence from Tier 1/2 < 0.70

## Performance Targets
- **Latency**: 5-15s (2 layers of parallel execution)
- **Quality**: 2-3% improvement over best single-agent
- **Cost**: 3000-5000 tokens per task

---

## SUMMARY: Which Template to Use

| Scenario | Template | Time | Cost | Quality |
|----------|----------|------|------|---------|
| 70% of tasks (confident) | Template 1 | <100ms | ~100 tokens | 0.75-0.85 |
| 25% of tasks (ambiguous) | Template 2 | 500-2000ms | ~1000 tokens | 0.80-0.90 |
| 5% of tasks (high-stakes) | Template 3 | 5-15s | ~5000 tokens | 0.90-0.98 |

For omc-live: Implement all 3 in sequence, with fallback from T1 → T2 → T3.

## Related
- [[projects/HarnessOS/research/20260331-autonomous-skill-selection-research|20260331-autonomous-skill-selection-research]]
- [[projects/HarnessOS/research/20260327-omc-live-autonomous-ai-research-2025-2026|20260327-omc-live-autonomous-ai-research-2025-2026]]
- [[projects/HarnessOS/research/20260328-omc-live-infinite-loop-architecture-research|20260328-omc-live-infinite-loop-architecture-research]]
- [[projects/HarnessOS/research/20260325-autonomous-agent-goal-update-subloop-architecture|20260325-autonomous-agent-goal-update-subloop-architecture]]
- [[projects/HarnessOS/research/20260326-omc-live-skill-critique|20260326-omc-live-skill-critique]]
- [[projects/HarnessOS/research/20260326-omc-live-self-evolving-outer-loop|20260326-omc-live-self-evolving-outer-loop]]
- [[projects/HarnessOS/research/20260331-skill-selection-quick-reference|20260331-skill-selection-quick-reference]]
