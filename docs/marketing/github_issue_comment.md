# GitHub Issues 댓글 템플릿

## 타겟 이슈 검색 쿼리

```
site:github.com "autonomous agent" "context limit" OR "session" OR "long-running"
site:github.com openhands "failure" OR "stuck" OR "goal drift"
site:github.com llm-agent "infinite" OR "outer loop" OR "self-improving"
site:github.com "agent framework" "harness" OR "control structure" OR "evaluation loop"
```

---

## 댓글 템플릿 A — 컨텍스트/세션 지속성 관련 이슈

```
This is the exact problem I've been working on.

The root issue: context degradation isn't gradual — it's threshold-based.
Agents don't slowly forget. They cliff-edge at a specific token length and fail silently.
"Gradual fade" is the wrong mental model. It's more like a fuse.

I measured this across 1K/10K/50K/100K token contexts building HarnessOS.
The fix isn't "use a longer context window" — it's detecting the threshold and
triggering a safe handoff *before* the cliff.

In omc-live-infinite (our infinite outer loop), we monitor context budget and rotate
at 70% capacity: save world model state → fresh session → resume.
The world model persists across rotations as an epistemic state layer.

GitHub + design: https://github.com/jaytoone/HarnessOS

Happy to discuss the rotation mechanism in detail.
```

---

## 댓글 템플릿 B — 자율 에이전트 실패/정체 관련 이슈

```
Failure clustering is real and it's not random.

I ran OpenHands on 20-step autonomous coding tasks and classified every failure point.
Most failures cluster around 3 patterns:
1. Wrong task decomposition (incorrect sub-goals from the start — planning failure)
2. Role non-compliance (agent exceeds its defined scope mid-run)
3. Boundary violations (unexpected state mutations)

Once you have the taxonomy, you can route failures instead of retrying blindly.
That's what omc-failure-router does in HarnessOS — transient/persistent/fatal classification,
with each type handled differently.

The bigger architectural insight: the outer loop matters as much as the inner loop.
An agent that classifies "why did this fail?" behaves completely differently from one
that just retries.

Methodology + data: https://github.com/jaytoone/HarnessOS
```

---

## 댓글 템플릿 C — 에이전트 목표 진화/자가 개선 관련 이슈

```
The "agent improves itself" problem is harder than it looks.

The failure mode I kept hitting: the agent achieves the goal, stops, and calls it done.
There's no mechanism to ask "what's the next level of quality?"

In omc-live (HarnessOS), after every successful iteration:
- Score the output across 5 dimensions (quality, completeness, efficiency, impact, goal fidelity)
- If the weakest dimension is improvable → generate an elevated goal → continue
- Plateau for 3 consecutive iterations → converge

The tricky part is goal fidelity: evolved goals can drift from the original intent (Goodhart's law).
We track cumulative fidelity (product of per-step fidelity scores) with a hard floor at 0.50.

This runs inside omc-live-infinite with no iteration cap — the loop terminates on convergence,
not timeout. Enables agents that genuinely improve over hours of execution.

Architecture: https://github.com/jaytoone/HarnessOS
```

---

## 댓글 템플릿 D — Harness Engineering 개념 관련 토론

```
"Harness Engineering" is the right frame for this.

A harness doesn't constrain capability — it channels it.
The problem with current agent frameworks is they add capabilities but not control structure.
You get a more powerful agent that's still context-unaware, goal-unstable, and session-local.

HarnessOS is built as scaffold/middleware in the Harness Engineering pattern:
- CTX: context precision (5.2% token budget, LLM-free, R@5=1.0)
- omc-live: self-evolving outer loop with 2-Wave architecture
- omc-live-infinite: infinite execution with context rotation + world model

The design decisions are all experiment-driven — controlled measurements of debugging strategy,
context degradation, and failure patterns changed how each component was built.

GitHub: https://github.com/jaytoone/HarnessOS
```
