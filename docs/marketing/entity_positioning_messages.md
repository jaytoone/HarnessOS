# Entity — Positioning Message Cards

Generated: 2026-04-06
Purpose: Oh My Codex 트렌딩에 올라타는 채널별 메시지 모음

---

## Core Positioning

**Entity = Oh My Codex의 "다음 레이어"**

```
Oh My Codex solves:  "How do I run multiple agents in parallel right now?"
Entity solves:       "How do I make agents improve themselves over time?"

They're not alternatives. They're layers.
```

---

## Channel-Specific Messages

### GitHub (기술적 피어)

> Entity is the outer loop that makes your agents smarter each run.
> Knowledge absorption → experiment design → self-evolving goals.
> Built on top of Claude Code — same foundation as Oh My Codex.

---

### Reddit r/LocalLLaMA (개발자 커뮤니티)

> Oh My Codex blew up with 100k stars for good reason — parallel agents are huge.
> But there's a gap: after the agents finish, all that knowledge disappears.
>
> Entity is the "memory + evolution" layer on top.
> Each run deposits what it learned. Next run starts smarter.
> Goals evolve automatically when they're met, not when you update them manually.
>
> Different problem, complementary solution.

---

### Hacker News (기술 커뮤니티)

> Show HN: Entity — self-evolving outer loop for autonomous AI agents
>
> After watching Oh My Codex reach 100k stars, I realized the missing piece
> isn't parallel execution (Oh My Codex nails this) — it's persistence.
>
> Entity adds: knowledge absorption (/inhale), experiment evolution (/exhale),
> and an infinite execution loop that rotates context without losing state (/live-inf).
>
> The design goal: an agent that keeps running and keeps improving,
> not one that needs to be restarted with fresh context every session.

---

### dev.to (튜토리얼 독자)

> **Oh My Codex + Entity: The Complete Autonomous Agent Stack**
>
> Oh My Codex = your agent's arms and legs (runs things in parallel)
> Entity = your agent's brain and memory (learns and evolves across runs)
>
> Step 1: Oh My Codex executes tasks in parallel tmux sessions
> Step 2: Entity absorbs what was learned (/inhale)
> Step 3: Entity designs next experiments (/exhale)
> Step 4: Entity runs the evolved goal (/live-inf)
> Step 5: Repeat forever

---

### GeekNews / 요즘IT (한국어)

> Oh My Codex가 GitHub 역사상 최속 10만 스타를 기록하며 멀티에이전트 병렬 실행을 대중화했습니다.
>
> Entity는 그 다음 레이어입니다.
> 에이전트가 실행을 마친 뒤 무엇을 배웠는지 축적하고,
> 다음 실행에서 더 나은 목표를 스스로 설정합니다.
>
> 핵심 구조:
> - /inhale: 외부 연구를 자동 수집·정제
> - /exhale: 인사이트를 실험 설계로 변환
> - /live-inf: 수렴할 때까지 자율 실행
>
> Oh My Codex가 "지금 빠르게"라면, Entity는 "계속 개선되며 무한히".

---

## Anti-Patterns (쓰지 말 것)

| ❌ 하지 말 것 | ✅ 대신 |
|-------------|--------|
| "Oh My Codex보다 낫습니다" | "Oh My Codex와 함께 쓰면" |
| 첫 댓글에 링크 삽입 | 가치 제공 후 "더 궁금하면..." |
| "혁신적인 AI 도구" | 구체적 문제 + 구체적 해결책 |
| 기능 목록 나열 | 사용자가 겪는 문제 → 어떻게 해결 |

---

## 배포 우선순위 (트래픽 기준)

1. **Oh My Codex GitHub Issues** — 트래픽 최대, 기술 독자, Draft A/B/C 사용
2. **r/LocalLLaMA** — 검증된 채널 (기존 포스트 성과 있음), 위 메시지 사용
3. **GeekNews** — 한국어 커뮤니티, 요즘IT 채널 활용
4. **dev.to** — Oh My Codex + Entity 통합 튜토리얼 (PoC 후)
5. **HN Show HN** — 마지막 (가장 높은 노출, 가장 높은 기준)
