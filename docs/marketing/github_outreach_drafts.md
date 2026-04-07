# GitHub Outreach Drafts — Verification-Gated Distribution

Generated: 2026-04-02
Strategy: Pure technical value first. No links. Build credibility → engagement → then share repo.

---

## Wave 1: Issue-Specific Drafts

### Issue 1: [anthropics/claude-code#24976] — Context Limit Reached, auto-compact fails with parallel agents

**URL**: https://github.com/anthropics/claude-code/issues/24976
**Status**: CLOSED/LOCKED — cannot comment. Use Discussion post instead (see `outreach_ready/claude_code_discussion.md`).
**Pain point**: When parallel background agents (Task tool) return results simultaneously, they accumulate as user messages (97.5% of context), exhausting the window. `/compact` fails with the same error, leaving `/clear` (total state loss) as the only option.

### Draft Comment (archived — issue locked):
```
The 97.5% accumulation from subagent results is the key diagnostic here. Compaction is reactive — it triggers after the cliff, not before it.

What works: monitor token budget continuously and trigger state preservation at ~70% capacity, not 95%. At 70% you still have headroom to serialize the world state (agent results, task graph, decision history) before rotating to a fresh context.

The critical piece: agent results need to persist as structured state outside the context window, not as conversation messages inside it. File-based result passing (agents write to disk, parent reads summaries) cuts context growth by 10-20x compared to inline message accumulation.

For the "no recovery path" problem — reserving a compaction budget (5-10% of the window) as a guaranteed floor that agent messages cannot consume would prevent the deadlock state.
```

**Word count**: 120
**Follow-up strategy**: Redirect to Discussion post.

---

### Issue 2: [anthropics/claude-code#25620] — Can't /compact when context fully exhausted

**URL**: https://github.com/anthropics/claude-code/issues/25620
**Status**: CLOSED/LOCKED — cannot comment. Use Discussion post instead.
**Pain point**: At 199,125 tokens with auto-compact disabled, `/compact` itself fails because it needs context headroom to run. No recovery path.

### Draft Comment (archived — issue locked):
```
This is a fundamental architectural issue: compaction is itself an LLM operation that consumes context, so it can't run when the context is already at ceiling. It's a deadlock by design.

Two approaches that work in practice:

1. Reserved compaction budget: Hold back 5-8% of the context window that normal messages cannot consume. When the usable portion fills, compaction runs using the reserved headroom.

2. Pre-emptive context rotation: Serialize the current state (decisions made, files modified, pending tasks) to disk at ~70% capacity, then start a fresh session that loads only the serialized state. Sidesteps the compaction-needs-context paradox entirely.

Key insight: approach 2 is more robust because compaction quality degrades as context grows — a 190K-token conversation summarized into 40K still loses critical details. Rotation with explicit state persistence preserves exactly what you choose.
```

**Word count**: 137
**Follow-up strategy**: Redirect to Discussion post.

---

### Issue 3: [crewAIInc/crewAI#1355] — Agents stuck in loop after LiteLLM migration

**URL**: https://github.com/crewAIInc/crewAI/issues/1355
**Status**: CLOSED — resolved in crewAI 0.64.0. Low engagement potential on a resolved issue. Archive for pattern reuse.

### Draft Comment (archived — issue resolved):
```
The "Action and Final Answer at the same time" loop is a classic prompt-format mismatch after an LLM routing change. The agent's ReAct parser expects a specific output structure, but the new adapter subtly alters how the model interprets format instructions.

The deeper issue: when you swap the LLM routing layer, system prompt and parsing logic become coupled to the new adapter's behavior. Integration tests pass on the happy path, but edge cases in output formatting cause silent loops.

Two preventive measures after provider migrations:

1. Output format verification: Run a canary test checking whether the model's raw output matches the expected ReAct/function-call schema. Classify parse failures as "persistent" (won't self-resolve) vs. "transient."

2. Loop detection with circuit breaker: If the same agent makes 3+ consecutive LLM calls without progress (no new tool invocation, no state change), break the loop and surface raw output for debugging.
```

**Word count**: 143
**Follow-up strategy**: Save pattern for future crewAI issues.

---

### Issue 4: [google/adk-python#4178] — 429/503 errors cause agent workflow & context corruption

**URL**: https://github.com/google/adk-python/issues/4178
**Status**: OPEN — ready to post. See `outreach_ready/adk_python_4178.md` for final version.
**Pain point**: After 429/503 errors, subsequent queries don't start fresh — the agent resumes incomplete previous workflows, mixing contexts. State corruption, not just retry failure.

### Draft Comment:
```
The state corruption after 429/503 is more dangerous than the rate-limiting itself. What's happening: the agent's execution context (internal state, tool call history, partial results) persists across the failure boundary, so the next query inherits a half-completed workflow state.

This is a state isolation problem, not a retry problem. RetryConfig handles the HTTP layer but doesn't reset the agent's cognitive state after a failed workflow step.

What works: checkpoint-based state management where each agent turn is atomic. Before every LLM call, snapshot the current state. On 429/503, restore to the last clean checkpoint rather than continuing from the corrupted mid-execution state.

For the immediate workaround: the suggestion to use the native Gemini adapter instead of LiteLLM is correct — it handles retry + state reset more cleanly because it doesn't add an extra abstraction layer where state can leak.
```

**Word count**: 130
**Follow-up strategy**: If engagement, discuss checkpoint/rollback patterns and how world model persistence handles failure recovery.

---

### Issue 5: [OpenHands/OpenHands#5535] — Headless mode keeps sending "continue" after task completion

**URL**: https://github.com/OpenHands/OpenHands/issues/5535
**Status**: CLOSED with fix. Lower engagement potential but pattern is reusable.

### Draft Comment (archived — issue closed):
```
The core issue is that the headless controller can't distinguish "agent is waiting because it finished" from "agent is waiting because it's stuck." Both surface as AWAITING_USER_INPUT, so auto-continue treats completion the same as a pause.

What's needed is an explicit completion signal — a terminal state distinct from "waiting for input." The agent should declare "task complete, here are results" vs. "I need more information," and the controller should only auto-continue on the latter.

A practical pattern: have the agent emit a structured completion marker that the controller recognizes as terminal. Then check: did the agent signal completion? If yes, stop. If non-terminal wait, continue. If continued N times without progress (no new actions, no state change), break and report — that's a stuck agent, not a working one.
```

**Word count**: 128
**Follow-up strategy**: Discuss termination detection patterns for autonomous agent loops.

---

## Wave 2: New Open Issues

### Issue 6: [openai/openai-agents-python#111] — Proper way of managing large context window for ComputerTool

**URL**: https://github.com/openai/openai-agents-python/issues/111
**Status**: OPEN (opened 2025-03-13, labeled needs-more-info)
**Pain point**: User wants a persistent agent lasting 10,000+ turns but hits context size limit. No built-in context management — the SDK has no mechanism for long-running agent sessions.
**Our relevant finding**: Context rotation at 70% capacity with world model persistence enables indefinite agent sessions without hitting the ceiling.

### Draft Comment:
```
The core challenge with persistent agents (max_turns > 10000) is that the conversation history grows unboundedly. Every screenshot, tool result, and reasoning step accumulates in the message list until you hit the ceiling.

Two approaches that work for long-running sessions:

1. Sliding window with state extraction: Periodically extract key state (accomplishments, current objective, findings) into a structured summary, then trim older messages. The summary becomes the new starting context.

2. Context rotation: At ~70% of the context limit, serialize agent state to disk — current task, progress, pending actions — and start a fresh session loading only the serialized state. You choose exactly what persists, avoiding lossy summarization.

For ComputerTool specifically, screenshots are the biggest context consumers. Writing screenshots to disk and referencing file paths instead of inline base64 drastically reduces per-turn context growth.
```

**Word count**: 137
**Follow-up strategy**: If engagement, share context degradation threshold findings and rotation implementation details.

---

### Issue 7: [strands-agents/sdk-python#1138] — Agent State Management: Snapshot, Pause, and Resume

**URL**: https://github.com/strands-agents/sdk-python/issues/1138
**Status**: OPEN (opened 2025-11-04, feature request)
**Pain point**: No way to capture and restore complete agent state during execution. Long-running workflows can't be paused/resumed. State lost on restarts. No checkpoint capability.
**Our relevant finding**: World model persistence — explicit state serialization at each turn enables pause/resume, failure recovery, and cross-session continuity.

### Draft Comment:
```
The snapshot/resume problem has a subtlety that pure serialization misses: you need to capture the agent's epistemic state, not just its data state.

Data state (messages, tool results, variables) is straightforward to serialize. But the agent's "understanding" — which hypotheses it's pursuing, what it's ruled out, what decisions it's made and why — is embedded in the conversation history and gets lost in naive serialization.

What works: a structured "world model" layer that explicitly tracks decisions made (with rationale), active hypotheses, task graph (done/pending/blocked), and key findings. This world model is updated at each turn and is the unit of serialization.

On resume, the agent loads the world model instead of replaying the full conversation history. This is cheaper, faster, and more robust than conversation replay — and it survives context rotation, not just pause/resume.
```

**Word count**: 134
**Follow-up strategy**: If engagement, describe the world model schema and how it integrates with context rotation for indefinite execution.

---

### Issue 8: [strands-agents/sdk-python#1230] — Optimize Session State with Checkpoint Model

**URL**: https://github.com/strands-agents/sdk-python/issues/1230
**Status**: OPEN (feature request)
**Pain point**: Session state is conversation-centric (store all messages) rather than checkpoint-centric (store state snapshot). Expensive to store, load, and operate at scale. Storage costs grow linearly with conversation length.
**Our relevant finding**: Checkpoint-based state (world model snapshots) vs. conversation replay is exactly the pattern omc-live-infinite uses for context rotation.

### Draft Comment:
```
The conversation-centric vs. checkpoint-centric distinction is the right framing. Storing all messages is essentially an append-only log — useful for debugging but terrible for operational efficiency.

A checkpoint model needs to answer one question: "what does the agent need to know to continue from this exact point?" That's typically much smaller than the full conversation.

From implementing this pattern: the minimum viable checkpoint is (1) task graph state (done/pending/blocked), (2) key decisions with rationale, (3) accumulated findings, and (4) active context (current objective + relevant file references). This compresses a 1000-message conversation into a structured object that loads in milliseconds.

One caveat: checkpoints should be immutable snapshots, not mutable state. If the agent needs to backtrack, it loads a previous checkpoint rather than mutating the current one. This gives you free rollback and makes failure recovery trivial.
```

**Word count**: 138
**Follow-up strategy**: If engagement, discuss how checkpoint-based state enables context rotation for indefinite execution without storage cost growth.

---

### Issue 9: [openai/openai-agents-python#1093] — Better Error Handling for Long Contexts

**URL**: https://github.com/openai/openai-agents-python/issues/1093
**Status**: OPEN (opened 2025-07-14, enhancement)
**Pain point**: RAG tools can overflow context windows. Current workaround is wrapping every tool output with token truncation manually. No built-in abstraction for context limit management.
**Our relevant finding**: Context monitoring should be continuous and pre-emptive, not reactive error handling after overflow.

### Draft Comment:
```
The deeper issue isn't error handling — it's that context overflow is treated as an exception rather than an expected operational state. In any agent that uses RAG or tool calls, context will eventually fill up. The question is what happens when it does.

Wrapping tool outputs with truncation is a band-aid because it treats each tool independently. What you actually need is a context budget manager that tracks cumulative usage across all sources and makes pre-emptive decisions.

A pattern that works: before each tool call, check remaining context budget. If the result would push past a threshold (e.g., 70%), either (a) request a compressed output, (b) write the full result to disk and pass a reference, or (c) trigger a context rotation preserving current state.

The threshold should be well below the hard limit — quality degrades before the API errors out.
```

**Word count**: 140
**Follow-up strategy**: If engagement, share context degradation measurement data (cliff-edge vs. gradual fade findings).

---

## Posting Priority

### Tier 1 — Post immediately (OPEN, high relevance):
1. **Issue 4: adk-python#4178** — State corruption after API errors. Ready-to-post version in `outreach_ready/`.
2. **Issue 6: openai-agents-python#111** — Context management for persistent agents. Core HarnessOS value prop.
3. **Issue 7: strands-agents#1138** — Agent state snapshot/resume. Maps directly to world model persistence.

### Tier 2 — Post this week (OPEN, good fit):
4. **Issue 8: strands-agents#1230** — Checkpoint-based session state. Complements Issue 7.
5. **Issue 9: openai-agents-python#1093** — Context overflow handling. Good entry point for context rotation discussion.

### Tier 3 — Discussion format (LOCKED original issues):
6. **claude-code Discussion** — Context rotation RFC. Ready-to-post version in `outreach_ready/`.

### Tier 4 — Archived (CLOSED, pattern reuse only):
7. Issues 1, 2, 3, 5 — Archived drafts for reference. Reuse patterns on future issues.
