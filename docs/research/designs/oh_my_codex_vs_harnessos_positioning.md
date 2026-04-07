# Oh My Codex vs HarnessOS — Competitive Positioning Analysis

## Source
- **Post**: GitHub 역사상 가장 빠르게 10만 개의 스타를 기록한 오픈소스 프로젝트 (Sigrid Jin & Bellman)
- **URL**: https://news.hada.io/topic?id=28223
- **Absorbed via**: /inhale trending_tools — GeekNews (2026-04-05)
- **Relevance**: 8.5/10 (general)

## Core Idea
Oh My Codex (Bellman 유지보수): tmux 세션 기반 멀티에이전트 swarm 런타임.
GitHub 역사상 최속 10만 스타 달성. 주요 특징:
- AI 에이전트들을 위한 런타임 + 하네스(harness)
- Claw-Code 통합 (Claude Code 래퍼)
- 자동 swarm 오케스트레이션

## Positioning Matrix

| 차원 | Oh My Codex | HarnessOS |
|------|-------------|-----------|
| **핵심 추상화** | tmux 세션 swarm | 무한 자율 루프 |
| **목표** | 병렬 에이전트 실행 | 자기진화 에이전트 |
| **컨텍스트 처리** | 세션 격리 | CTX 레이어 (5.2% 예산) |
| **진화 메커니즘** | 없음 (런타임만) | inhale→exhale→live 파이프라인 |
| **안전장치** | 없음 | Safety Triad + EVOLVE 게이트 |
| **목표 진화** | 정적 | GoalTree 자동 진화 |
| **주 사용자** | 개발자 (즉각적 병렬화) | 연구자 (장기 자율 실행) |
| **오픈소스** | Yes (10만 스타) | Yes (초기) |

## Differentiation Analysis

### HarnessOS의 고유 강점
1. **Knowledge Evolution Loop** — /inhale → /exhale → /live 파이프라인 없음
2. **Safety Triad** — EVOLVE 게이트 기반 안전 제어 없음
3. **Infinite Context Rotation** — 컨텍스트 창 한계를 넘는 실행 없음
4. **GoalTree 자동진화** — 목표가 달성되면 다음 목표 자동 생성

### Oh My Codex의 강점 (HarnessOS 약점)
1. **즉각적 병렬화** — HarnessOS는 순차 루프 중심
2. **사용자 친화적 진입장벽** — tmux 기반으로 직관적
3. **커뮤니티 규모** — 10만 스타 vs HarnessOS 초기

## Strategic Implications

### HarnessOS가 취해야 할 포지션
```
Oh My Codex = "지금 당장 빠르게 병렬 실행"
HarnessOS   = "장기적으로 스스로 개선되며 무한 실행"
```

**타겟 사용자 분리**:
- Oh My Codex: 개발자가 지금 당장 여러 에이전트 돌리고 싶을 때
- HarnessOS: 연구자/ML엔지니어가 수일~수주 자율 실행 + 지식 축적 원할 때

### 통합 가능성
Oh My Codex를 HarnessOS의 **실행 레이어**로 사용:
```
HarnessOS (목표 진화 + 안전 제어)
    └── Oh My Codex (병렬 실행 레이어)
            └── Claude Code × N workers
```

### 위험 요소
- Oh My Codex가 진화 기능 추가하면 직접 경쟁 발생
- 10만 스타 커뮤니티가 HarnessOS 흡수할 가능성

## Action Items
1. Oh My Codex GitHub 상세 분석 — 실제 코드 구조 파악
2. HarnessOS README에 포지셔닝 차별화 명시
3. Oh My Codex를 execution_backend로 통합하는 PoC 검토
