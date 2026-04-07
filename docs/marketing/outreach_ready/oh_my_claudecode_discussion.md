# Yeachan-Heo/oh-my-claudecode — Discussion 즉시 게시용

Generated: 2026-04-06
Target: https://github.com/Yeachan-Heo/oh-my-claudecode/issues or Discussions
Context: oh-my-claudecode = Claude Code 기반 멀티에이전트 오케스트레이션 (Entity와 동일 기반)
Status: READY TO POST

## 게시 조건

- [ ] "long-running", "session continuity", "autonomous", "goal" 관련 Discussion/Issue 확인
- [ ] 최근 48시간 내 활성 스레드 우선
- [ ] 첫 댓글: 링크 없음, 기술적 가치 먼저

---

## Draft — Long-horizon autonomy (Discussion용)

```
Long-horizon autonomy has a compounding problem: each session
starts with less context about what happened before.

The pieces that matter for multi-session continuity:
1. Structured episode memory (compressed decision records, not chat logs)
2. Goal tree that survives context rotation (file-backed, not in-memory)
3. A "what changed" summary that fits in <500 tokens

For the "agent improving across runs" use case — the pattern that
works: each run extracts N lessons, those lessons seed the next run's
context primer. Quality of this extraction > quantity of stored data.

We've been running this as Entity, a self-evolving outer loop on top
of Claude Code (same foundation as oh-my-claudecode). The context
rotation design is open — happy to share if useful for the autonomy
use case here.
```

---

## Draft — Failure recovery (Issue용)

```
The failure taxonomy matters more than retry logic.

Not all agent failures are equal:
- Transient (rate limit, timeout) → retry with backoff
- Persistent (same approach failing 2x) → strategy change, not retry
- Fatal (task fundamentally wrong) → goal restructure

Applying backoff to persistent failures doesn't help — you're just
retrying a broken strategy. The useful intervention: load the last
successful episode for a similar task, contrast what's different.

We call this cross-trajectory recovery — it's been the most reliable
escape from stuck states in our experience with Entity, which runs
on top of Claude Code with a similar multi-session design to this repo.

What failure patterns are you seeing most often here?
```

---

## Follow-up (반응 이후)

```
Entity is open-source — github.com/[URL]. The failure router and
episode memory design are in omc-failure-router and omc-episode-memory
skills. Might be composable with oh-my-claudecode's agent team setup.
```

---

## 관련 repo 정보

- oh-my-claudecode: https://github.com/Yeachan-Heo/oh-my-claudecode
- oh-my-codex (OpenAI Codex 버전): https://github.com/Yeachan-Heo/oh-my-codex
- Issues page: https://github.com/Yeachan-Heo/oh-my-claudecode/issues
