# Hacker News Submission

## Show HN (karma 축적 후)

**Title:**
```
Show HN: LLM agents don't degrade gradually – they cliff-edge. I built HarnessOS to survive it
```

**Body:**
```
I've been building HarnessOS, a scaffold/middleware system for running autonomous agents
indefinitely — not one session, but across context rotations, with self-evolving goals.

The core problem: most agent frameworks are session-local. They run a task, complete it
(or fail), and stop. Real autonomous work requires:
- Context that persists past the window limit
- Goals that evolve when the current one is achieved
- Failures that are classified and routed, not just retried

The architecture:

CTX: context precision layer — LLM-free retrieval, 5.2% token budget, R@5=1.0 dependency recall

omc-live: finite self-evolving outer loop
  Wave 1 (specialist strategy) → Wave 2 (execution + scoring)
  Self-scores on 5 dimensions → evolves goal if quality improves → stops at plateau

omc-live-infinite: no iteration cap
  Context rotation at 70% budget (safe handoff before cliff-edge failure)
  World model persists across rotations (epistemic state layer)
  Co-evolution feedback: strategy outcomes feed back into Wave 1

The design decisions are driven by controlled experiments:
- Hypothesis-driven debugging: 50% fewer attempts on hard bugs vs pattern-match/retry (100% first-hypothesis accuracy)
- Context degradation: threshold-based cliff, not gradual fade — agents fail silently at specific token lengths
- Autonomous agent failures: cluster around 3 patterns (wrong decomposition, role non-compliance, boundary violation)

These aren't paper findings. They're design inputs. Each one changed a component.

214 tests, 100% coverage. CTX and omc-live/infinite stable and in daily use.

GitHub: https://github.com/jaytoone/HarnessOS

Happy to discuss the context rotation design or the self-evolution mechanics.
```

---

## 일반 링크 제출 (karma 0도 가능)

**Title:**
```
Context degradation in LLM agents is a cliff-edge, not gradual – built HarnessOS to handle it
```

**URL:** `https://github.com/jaytoone/HarnessOS`

## Related
- [[projects/HarnessOS/research/20260326-omc-live-self-evolving-outer-loop|20260326-omc-live-self-evolving-outer-loop]]
- [[projects/HarnessOS/research/20260328-omc-live-infinite-loop-architecture-research|20260328-omc-live-infinite-loop-architecture-research]]
- [[projects/HarnessOS/research/20260323-hypothesis-driven-agent-research|20260323-hypothesis-driven-agent-research]]
- [[projects/HarnessOS/research/20260327-omc-live-autonomous-ai-research-2025-2026|20260327-omc-live-autonomous-ai-research-2025-2026]]
- [[projects/HarnessOS/research/20260325-autonomous-agent-goal-update-subloop-architecture|20260325-autonomous-agent-goal-update-subloop-architecture]]
- [[projects/HarnessOS/research/20260327-omc-live-git-checkpoint-self-evolving-research|20260327-omc-live-git-checkpoint-self-evolving-research]]
