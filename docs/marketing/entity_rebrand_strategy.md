# Entity — Rebranding Strategy (HarnessOS → Entity)

Generated: 2026-04-06
Trigger: Oh My Codex 10만 스타 달성 → 경쟁 인텔리전스 + 리브랜딩 기회

---

## Why Rebrand Now

| 이유 | 설명 |
|------|------|
| **프로젝트명 통일** | 코드베이스 디렉토리가 이미 `Entity`임. HarnessOS는 별도 브랜드로 혼선 유발 |
| **포지셔닝 명확화** | Oh My Codex(런타임)와 Entity(진화 루프)의 차별화를 브랜드 레벨에서 구현 |
| **트렌딩 타이밍** | "harness" 키워드가 TLDR AI 등에서 트렌딩 → Entity로 주목 받기 좋은 시점 |
| **검색 노출** | "entity" = AI 에이전트 문맥에서 자연스러운 키워드 (knowledge entity, agent entity) |

---

## Positioning Statement

```
Entity: The Self-Evolving Outer Loop for Autonomous AI Agents

Where Oh My Codex runs agents in parallel,
Entity makes them evolve — learning from every run,
accumulating knowledge, and improving their own goals.
```

**한 줄 태그라인**: *"Agents that get smarter every time they run."*

---

## Competitive Framing

### Entity vs Oh My Codex (협력 포지셔닝)

```
Oh My Codex  ──────────────────────────►  Entity
  "Run N agents now"            "Run agents forever, improving each time"

  Use Oh My Codex for:           Use Entity for:
  - Parallel task execution      - Long-horizon autonomous goals
  - Quick multi-agent sprints    - Knowledge accumulation across runs
  - tmux-based workflow          - Self-evolving goal management

  Together: Oh My Codex as Entity's execution backend (PoC available)
```

**메시지 핵심**: Entity는 Oh My Codex를 대체하지 않는다. Oh My Codex가 "지금 실행"이라면, Entity는 "계속 개선되며 실행"이다.

---

## Rebranding Checklist

### 즉시 (이번 세션)
- [ ] README.md 상단 "HarnessOS" → "Entity" 교체
- [ ] `docs/marketing/` 신규 아웃리치 초안 작성 (이 파일과 함께)
- [ ] GitHub repo description 업데이트 예정 문구 준비

### 단기 (1주)
- [ ] `README.md` 전면 개편 — Entity 브랜드 기준으로
- [ ] `docs/` 내 HarnessOS 언급 → Entity로 점진 교체
- [ ] GitHub topic 태그: `entity`, `autonomous-agents`, `self-evolving`, `outer-loop`

### 중기 (1개월)
- [ ] Oh My Codex execution backend PoC 구현 → 통합 데모
- [ ] dev.to 포스트: "Entity + Oh My Codex: The Complete Autonomous Agent Stack"
- [ ] r/LocalLLaMA 업데이트 포스트

---

## GitHub README 새 인트로 (초안)

```markdown
# Entity

**The self-evolving outer loop for autonomous AI agents.**

> Where most agent frameworks stop when the task ends,
> Entity keeps going — accumulating knowledge, improving goals,
> and running indefinitely without losing context.

## What makes Entity different

| Feature | Entity | Oh My Codex | LangGraph |
|---------|--------|-------------|-----------|
| Infinite context rotation | ✓ | — | — |
| Self-evolving goals | ✓ | — | — |
| Knowledge absorption loop | ✓ | — | — |
| Safety Triad gate | ✓ | — | — |
| Parallel agent execution | via Oh My Codex | ✓ | partial |

## The Evolution Loop

/inhale (collect research) → /exhale (design experiments) → /live (execute + evolve)
```

---

## 아웃리치 우선순위

1. **Oh My Codex Issues/Discussions** (고트래픽) — `oh_my_codex_outreach.md`
2. **Dev.to 포스트** — "Oh My Codex + Entity 통합 가이드"
3. **GeekNews** — 한국어 소개글 (yozm_it 채널 활용)
4. **r/LocalLLaMA** 업데이트 — Entity 리브랜딩 + Oh My Codex 통합 발표
