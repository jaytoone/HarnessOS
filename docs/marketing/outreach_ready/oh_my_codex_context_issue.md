# Yeachan-Heo/oh-my-codex — Context/Session 관련 이슈 즉시 게시용 댓글

Generated: 2026-04-06
Target: https://github.com/Yeachan-Heo/oh-my-codex/issues (context limit / session persistence 이슈)
Status: READY TO POST — 아래 조건 확인 후 게시

## 게시 조건 체크리스트

- [ ] 이슈 제목에 "context", "session", "memory", "persist", "window" 포함 여부 확인
- [ ] 이슈 last activity 48시간 이내 확인
- [ ] 댓글에 링크 없음 (첫 댓글 기준)
- [ ] 250자 이내 확인 (아래 short 버전 기준)
- [ ] Entity 링크는 follow-up 댓글에만

---

## 댓글 (Full version — ~380자)

```
Context exhaustion is the hardest part of long-running multi-agent setups.

The pattern I've found reliable: treat context as a budget, not a buffer.
Reserve 30% of the window before agents start — not for content,
but for state serialization when you approach the limit.

The key insight: agents shouldn't write results into the context window.
They write to disk; the orchestrator reads compressed summaries.
This keeps context growth roughly constant regardless of how many agents ran.

For the "agent improving across sessions" use case — the missing piece
is usually a structured "what did I learn this run" extraction before
context rotation. Happy to share the episode memory design if useful.
```

## 댓글 (Short version — ~190자, 권장)

```
Context exhaustion in multi-agent setups: the pattern that works is
treating context as a budget, not a buffer.

Reserve 30% for state serialization — agents write results to disk,
orchestrator reads compressed summaries. Context growth stays constant.

The other missing piece: structured "what did I learn" extraction
before each context rotation. Happy to share details if useful.
```

---

## 이슈 탐색 키워드 (GitHub 이슈 검색용)

```
is:issue is:open label:bug "context"
is:issue is:open "session" "persist"
is:issue is:open "memory" "agent"
is:issue is:open "context window" OR "token limit"
```

## 관련 이슈 번호 (확인된 것)

- #1176: Background helper / Windows 이슈 (해당 없음)
- #1205, #1243, #1266: Apr 3-5 활성 이슈 (내용 확인 필요)

---

## Follow-up 댓글 (첫 댓글 이후 반응 있을 때)

```
We've been building this exact pattern into Entity — a self-evolving
outer loop on top of Claude Code (similar concept to Oh My Codex
but focused on the persistence + evolution layer rather than parallelism).

Repo: github.com/[Entity URL — 추후 삽입]
The context rotation design doc is in docs/research/ if you want to dig in.
```
