# Oh My Codex GitHub Outreach — Entity 노출 전략

Generated: 2026-04-06
Updated: 2026-04-06 (repo URL 확인 완료)
Target repo: Oh My Codex (Bellman/Yeachan Heo 유지보수)
Repo URLs:
  - oh-my-codex (OmX, OpenAI Codex CLI): https://github.com/Yeachan-Heo/oh-my-codex
  - oh-my-claudecode (Claude Code 버전): https://github.com/Yeachan-Heo/oh-my-claudecode
  - claw-code (100k stars, Rust 구현체): https://github.com/ultraworkers/claw-code
Strategy: 기술적 가치 먼저 — 경쟁 아닌 보완 포지션으로 자연 노출

---

## 아웃리치 원칙

1. **링크 먼저 금지** — 첫 댓글에 Entity 링크 삽입하지 않음
2. **문제 해결 먼저** — 실제 Oh My Codex 이슈에 가치 있는 기술적 답변 제공
3. **자연스러운 언급** — "비슷한 문제를 해결하면서..." 형태로 Entity 언급
4. **협력 프레임** — "대안"이 아닌 "보완재/다음 단계"로 포지셔닝

---

## Wave 1: 이슈/디스커션 타겟 선별 기준

Oh My Codex 이슈에서 Entity가 자연스럽게 언급될 수 있는 이슈 유형:

| 이슈 유형 | Entity 연관성 | 댓글 전략 |
|-----------|--------------|-----------|
| 컨텍스트 창 한계 | CTX 레이어 (5.2% 예산) | 컨텍스트 압축 기법 공유 → Entity 언급 |
| 에이전트 실패 후 복구 | Safety Triad + failure router | 실패 분류 패턴 공유 |
| 장기 실행 / 세션 지속성 | context rotation, live-inf | 무한 루프 아키텍처 경험 공유 |
| 목표 관리 / 태스크 추적 | GoalTree | 자율 목표 진화 패턴 제안 |
| 에이전트 품질 측정 | execution_reward, SCORE PROMPT | 평가 메트릭 설계 경험 공유 |

---

## Draft Comments

### Draft A — 컨텍스트 한계 관련 이슈

```
Context exhaustion is the hardest part of long-running multi-agent setups.

The pattern I've found reliable: treat context as a budget, not a buffer.
Reserve 30% of the window before agents start — not for content,
but for state serialization when you approach the limit.

The key insight: agents shouldn't write results into the context window.
They write to disk; the orchestrator reads compressed summaries.
This keeps context growth roughly constant regardless of how many agents ran.

For the session persistence problem — if you need agents to keep
improving across sessions, the missing piece is usually a structured
"what did I learn this run" extraction before context rotation.
We've been building this pattern into Entity (our self-evolving outer loop
on top of Claude Code) — happy to share the episode memory design if useful.
```

**적용 조건**: Oh My Codex에 "context limit", "session persistence", "agent memory" 관련 이슈 존재 시

---

### Draft B — 에이전트 실패/복구 관련 이슈

```
The failure taxonomy matters more than the retry logic.

Not all agent failures are equal:
- Transient (rate limit, timeout) → simple retry with backoff
- Persistent (same approach failing 2x) → strategy change, not retry
- Fatal (task fundamentally wrong) → goal restructure

The mistake I see most often: applying exponential backoff to
persistent failures. It doesn't help — you're just retrying a broken strategy.

For persistent failures, the useful intervention is: load the last
successful episode for a similar task and contrast what's different.
This recombination approach (we call it cross-trajectory recovery)
has been the most effective escape from stuck states in our experience
with Entity, an autonomous loop we run on top of your project.

What failure patterns are you seeing most often?
```

**적용 조건**: "agent stuck", "retry", "failure handling", "recovery" 관련 이슈

---

### Draft C — 장기 실행 / 자율성 관련 Discussion

```
Long-horizon autonomy has a compounding problem: each session
starts with less context about what happened before.

The pieces that actually matter for multi-session continuity:
1. Structured episode memory (not chat logs — compressed decision records)
2. Goal tree that survives context rotation (file-backed, not in-memory)
3. A "what changed" summary that fits in <500 tokens

For the "agent improving across runs" use case — the pattern that
works is: each run extracts N lessons, those lessons seed the next run's
context primer. The quality of this extraction matters more than the
quantity of stored data.

We've been running this as Entity — a self-evolving outer loop
that sits on top of Claude Code (similar to Oh My Codex's approach
but focused on the persistence + evolution layer rather than parallelism).
The design is open — would be interested in whether the context
rotation pattern maps to your architecture at all.
```

**적용 조건**: Discussions — "long-running agents", "autonomous execution", "session continuity" 주제

---

## Wave 2: Oh My Codex Integration PoC 발표용 초안

*(PoC 구현 완료 후 사용)*

```
We prototyped using Oh My Codex as the execution backend for Entity
(our self-evolving outer loop for Claude Code agents).

Short version: Oh My Codex handles the "run N agents now" layer,
Entity handles the "improve goals across runs" layer.
They compose cleanly because their concerns don't overlap.

Architecture:
  Entity (goal tree + knowledge evolution + safety gate)
    └── Oh My Codex (parallel execution + tmux management)
          └── Claude Code × N workers

The integration point is simple: Entity writes task specs to disk,
Oh My Codex picks them up, runs them, writes results back.
Entity reads results, scores, evolves the goal, writes next task spec.

Demo repo / writeup: [Entity GitHub URL]

Curious if this matches anything you've been thinking about for
extensibility in Oh My Codex — the "plug in your own orchestrator" use case.
```

**사용 시점**: PoC 완료 후, Oh My Codex Discussion "Integrations" 또는 "Ecosystem" 스레드

---

## 실행 체크리스트

- [x] Oh My Codex GitHub repo URL 확인 (Bellman/Yeachan Heo): https://github.com/Yeachan-Heo/oh-my-codex
- [ ] 활성 이슈 중 Draft A/B/C 적용 가능한 이슈 3개 선별
- [ ] 각 이슈 last activity 확인 (48시간 이내 활성 이슈 우선)
- [ ] 댓글 게시 전 검토: 링크 없음, 250자 이내, 가치 먼저
- [ ] Wave 2는 PoC 완료 후 진행
