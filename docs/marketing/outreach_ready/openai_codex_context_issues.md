# openai/codex — Context Compaction 이슈 즉시 게시용

Generated: 2026-04-06
Targets:
  - https://github.com/openai/codex/issues/10823 (Unable to compact — 12h lost)
  - https://github.com/openai/codex/issues/3997 ([Critical] session terminates on overflow)
  - https://github.com/openai/codex/issues/8365 (compaction loop, 5% stall)
Status: READY TO POST

## 왜 이 이슈들인가

openai/codex는 oh-my-codex의 upstream. context compaction 실패 이슈가
다수 open 상태 — Entity의 context rotation(예산 기반 핸드오프) 접근이
직접적 해법을 제시함. 대형 repo(수만 stars) 트래픽 탑승 가능.

---

## 댓글 A — Issue #10823 (12시간 compaction 실패)

```
The root issue here is treating context as something to compress rather than rotate.

Compaction tries to preserve the full session in a smaller form — but at 95%+
context usage, there's no safe compression budget left. The operation fails
or hangs because it's attempting the impossible.

The pattern that actually works for long-running sessions: budget-based rotation.
At ~70% context usage (not 95%), serialize the critical state — current goal,
last N decisions, open file handles — and hand off to a fresh session.
The fresh session starts from the serialized state, not from a compressed history.

This keeps sessions from ever reaching the compaction failure threshold.
We've been running this as the core of Entity (a Claude Code outer loop) —
the context never grows past 70% because the handoff happens before it needs to.
```

---

## 댓글 B — Issue #3997 ([Critical] session terminates)

```
[Critical] is right — the failure mode is worse than it looks.

Context overflow mid-task doesn't just lose the current step. It loses the
implicit state: which files were read, which decisions were made, what the
agent was about to do next. That state can't be reconstructed from the
visible output.

The mitigation pattern: treat 70% context as a hard checkpoint trigger,
not a warning. At 70%, agent writes a state file (current_goal + decision_log
+ open_tasks), exits cleanly, new session reads the state file and resumes.

The agent never terminates uncleanly — it either succeeds or hands off.
We built this rotation into Entity for exactly this reason. Happy to share
the serialization format if useful for a fix here.
```

---

## 댓글 C — Issue #8365 (compaction loop stall)

```
Compaction loop is a specific failure: the session tries to compact,
the compact operation itself consumes context, the remaining context
is too small to complete the compact, repeat.

The exit condition that works: detect when remaining_context < compact_overhead
(empirically ~15% of window) BEFORE starting compaction. At that point,
skip compaction entirely — do a hard checkpoint + rotation instead.

A soft signal: if compaction has run twice without reducing context by >10%,
treat it as a loop and trigger rotation. The session is already in a
degraded state; rotation is less destructive than continued stalling.
```

---

## 게시 우선순위

1. **#10823** (most recent, active) — 댓글 A
2. **#3997** ([Critical] label, high visibility) — 댓글 B
3. **#8365** (technical loop issue) — 댓글 C

## 게시 전 체크

- [ ] 각 이슈 open 상태 확인
- [ ] 이미 비슷한 해결책 언급된 댓글 있는지 확인 (중복 방지)
- [ ] 링크 없이 첫 댓글 (Entity 링크는 follow-up)
- [ ] 댓글 A/B: ~200자 이내로 편집 권장
