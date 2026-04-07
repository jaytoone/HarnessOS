# GeekNews / 요즘IT 포스트 초안

Generated: 2026-04-06
Target: https://news.hada.io (GeekNews)
Status: READY TO POST

---

## 제목

```
Entity — 에이전트가 실행할 때마다 더 똑똑해지는 자가진화 루프
```

---

## 본문

Oh My Codex가 GitHub 역사상 최속 10만 스타를 기록하며 멀티에이전트 병렬 실행을 대중화했습니다.

그런데 에이전트가 작업을 마친 뒤엔 어떻게 될까요? 컨텍스트가 사라지고, 다음 실행은 처음부터 시작됩니다.

**Entity**는 그 다음 레이어입니다.

### 핵심 구조

```
/inhale  → 외부 논문/도구 트렌드를 자동 수집·정제
/exhale  → 인사이트를 실험 설계로 변환
/live    → 수렴할 때까지 자율 실행 (컨텍스트 로테이션 포함)
```

### Oh My Codex와의 관계

| | Oh My Codex | Entity |
|---|---|---|
| 핵심 문제 | "지금 에이전트 N개를 동시에 돌리고 싶다" | "에이전트가 매번 더 나아지길 원한다" |
| 메커니즘 | tmux 기반 병렬 swarm | 지식 축적 + 목표 자가진화 |
| 안전장치 | — | Safety Triad + EVOLVE 게이트 |
| 컨텍스트 | 세션 격리 | CTX 레이어 (예산 기반 회전) |

대안이 아닙니다. Oh My Codex가 실행 레이어라면, Entity는 그 위의 진화 레이어입니다.

### 왜 만들었나

실험을 반복하다 보니 패턴이 생겼습니다:
- 에이전트가 실패해도 다음 실행은 같은 실수를 반복
- 외부 연구(논문, 도구 트렌드)가 프로젝트에 반영되지 않음
- 목표가 달성돼도 다음 목표를 수동으로 설정해야 함

Entity는 이 세 가지를 자동화합니다.

---

## 태그

`#autonomous-agents` `#claude-code` `#self-evolving` `#ai-scaffolding` `#outer-loop`

---

## 링크 삽입 위치

```
[Entity GitHub URL — 추후 삽입]
```

---

## 요즘IT 투고용 (더 긴 버전)

> 제목: Oh My Codex 이후 — 에이전트를 계속 똑똑하게 만드는 방법
>
> Oh My Codex가 멀티에이전트 실행을 쉽게 만든 것처럼,
> Entity는 그 에이전트들이 매 실행마다 더 나아지도록 설계됐습니다.
>
> 핵심은 세 가지 루프입니다:
> - /inhale: 논문과 트렌딩 도구에서 인사이트를 자동 수집
> - /exhale: 인사이트를 실험 설계로 전환
> - /live: EVOLVE 게이트를 통과할 때까지 자율 실행
>
> Claude Code 기반으로 구현됐으며, Oh My Codex의 실행 레이어 위에서
> 동작하도록 설계됐습니다.
>
> [GitHub 링크]
