# Ready-to-Post: anthropics/claude-code Discussion

## Posting Instructions

- **URL**: https://github.com/anthropics/claude-code/discussions (create new)
- **Category**: Ideas / Feature Requests
- **Action**: Create a new Discussion with the title and body below
- **Verify before posting**: Discussions are enabled on the repo

---

## Title

Context rotation pattern for long-running agent sessions

## Body

```markdown
## Problem

When running parallel agent workflows (e.g., multiple Task tool invocations), subagent results accumulate as user messages inside the parent context. In practice, these results can consume 90%+ of the context window within a single complex task.

The current recovery path — `/compact` — is itself an LLM operation that requires context headroom. When the window is already at 95%+, compaction fails with the same context-exceeded error. `/clear` works but destroys all state. This creates a deadlock: the context is too full to compact, and clearing loses everything.

This has been reported in several issues (#24976, #25620) but the underlying architectural pattern hasn't been discussed as a community topic.

## Observation: threshold-based degradation

I've been measuring context degradation across extended agent sessions and found that quality doesn't degrade gradually — it drops off a cliff at a specific threshold. The mental model of "slowly forgetting" is wrong. It's more like a fuse: fine until it blows.

This means reactive compaction (trigger after the cliff) is fundamentally fragile. By the time you need it, the context is already in a degraded state where compaction quality is poor.

## Proposed pattern: pre-emptive context rotation

Instead of compacting in-place, rotate the context before the cliff:

1. **Monitor token budget continuously** — not just at API call time
2. **At ~70% capacity**, serialize the current working state (decisions made, files modified, pending tasks, key findings) to a structured format on disk
3. **Start a fresh session** that loads only the serialized state as its initial context
4. **Resume execution** from the persisted state, not from a lossy summary

The key difference from compaction: you choose exactly what to preserve, rather than asking an LLM to summarize a 190K-token conversation into 40K tokens (which inevitably loses critical details).

## What the serialized state needs

From experimentation, the minimum viable state for seamless rotation includes:

- **Task graph**: what's done, what's pending, what's blocked
- **Decision log**: key choices made and why (prevents re-debating settled questions)
- **File modification record**: what was changed and the intent behind each change
- **Active hypotheses**: what the agent is currently investigating

This is essentially a "world model" — an epistemic state layer that exists outside the context window.

## For subagent result accumulation specifically

The 90%+ context consumption from subagent results has a simpler fix: agent results should persist as structured files on disk, not as conversation messages. The parent agent reads summaries from disk instead of receiving full results inline. This cuts context growth by 10-20x.

Combined with the rotation pattern above, this enables indefinite agent sessions without context exhaustion.

## Questions for the community

- Has anyone implemented context rotation in their claude-code workflows? What state did you find essential to preserve?
- Is there interest in a standardized "session state" format that tools could read/write for rotation support?
- Would a reserved compaction budget (e.g., 5-10% of the window that agent messages cannot consume) be a viable interim solution?

---

*I've been experimenting with these patterns in a scaffold for long-running autonomous tasks. Implementation reference: [github.com/jaytoone/HarnessOS](https://github.com/jaytoone/HarnessOS)*
```
