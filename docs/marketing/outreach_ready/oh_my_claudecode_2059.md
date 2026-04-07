# Yeachan-Heo/oh-my-claudecode#2059 — Coordinator Mode 즉시 게시용

Generated: 2026-04-06
Target: https://github.com/Yeachan-Heo/oh-my-claudecode/issues/2059
Issue: "Feature: Coordinator Mode for multi-agent orchestration"
Opened by: Yeachan-Heo (Bellman) — 2026-03-31
Status: READY TO POST

## 왜 이 이슈인가

Bellman이 직접 올린 Feature Request — main session이 orchestrator로 동작,
worker 결과를 synthesize. Entity의 GoalTree + outer loop 구조와 직접 맞닿음.
"synthesize-then-delegate" 방식 = Entity의 /live + autopilot 분리와 동일 패턴.

---

## 댓글 (English, ~280자)

```
This pattern maps closely to what we've been calling the "outer loop / inner loop"
separation — the coordinator doesn't just delegate, it maintains a goal tree that
survives across worker cycles and improves based on aggregate results.

A few design notes from our experience:
- Coordinator state should be file-backed (not in the session context) — otherwise
  worker results overflow the coordinator's context window over long runs
- The synthesize step benefits from a scoring pass before delegating next tasks:
  score the aggregate, elevate the goal standard, then re-delegate
- Worker failure classification matters: transient vs persistent vs fatal
  determines whether to re-delegate the same task or restructure the goal

We built this as Entity, a self-evolving outer loop on top of Claude Code with
the same Claude Code foundation as oh-my-claudecode. The coordinator/worker split
is the core of how it runs indefinitely. Happy to share the design if useful.
```

---

## 댓글 (Short version — ~170자, 권장)

```
The key insight for long-running coordinator stability: coordinator state must be
file-backed, not session context — otherwise worker results eventually overflow it.

We use a scoring pass before each re-delegation: score aggregate → elevate goal →
re-delegate. Keeps the coordinator from repeating work the workers already solved.

Built this pattern into Entity (Claude Code outer loop). Happy to share details.
```

---

## Follow-up (반응 후)

```
Entity: github.com/jaytoone/HarnessOS (rename to Entity pending)
The coordinator design is in .omc/goal-tree.json + omc-live skill.
Might be composable with oh-my-claudecode's agent team setup directly.
```

---

## 게시 전 체크

- [ ] 이슈 #2059 여전히 open 확인 (https://github.com/Yeachan-Heo/oh-my-claudecode/issues/2059)
- [ ] 링크 없이 첫 댓글 게시 (follow-up에서 링크)
- [ ] 250자 이내 — Short version 사용 권장
