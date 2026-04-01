# Document Index

## Architecture
- [ARCHITECTURE.md](ARCHITECTURE.md) — LiveCode 전체 아키텍처 개념도 — 3개 실험 스트림 + analyze.py + harness_evaluator + app.py dashboard

## Experiments
- [verification_hurt/runner.py](../experiments/verification_hurt/runner.py) — Verification mode 비교 실험 (none/strict/lenient/adaptive escape_rate 측정)

## Specs
- [2026-03-22 LLM 장기 컨텍스트 실험 설계](superpowers/specs/2026-03-22-llm-longcontext-experiment-design.md)

## Plans
- [2026-03-22 LLM 장기 컨텍스트 실험 구현 계획](superpowers/plans/2026-03-22-llm-longcontext-experiment.md)

## Knowledge Pipeline
- [knowledge-channels.yaml](knowledge-channels.yaml) — RSS 채널 레지스트리 (AI/ML/Engineering/Startup/KR)
- [digests/](research/digests/) — 날짜별 자동 수집 다이제스트 (scripts/collect.sh 생성)

## Research
- [2026-04-01 Verification Hurt 실험 결과 — none/strict/lenient/adaptive escape rate 비교](research/digests/20260401-verification-hurt-results.md)
- [2026-04-01 Experiment Ideas — 채널 수집 기반 HarnessOS 실험 아이디어 선별](research/digests/20260401-experiment-ideas.md)
- [2026-04-01 Knowledge Digest — agent_research](research/digests/20260401-agent_research.md)
- [2026-03-30 가설 기반 vs 엔지니어링 디버깅 실험 결과](research/20260330-hypothesis-experiment-results.md)
- [2026-03-30 가설 기반 사고 vs 엔지니어링적 사고 — 난제 해결 실효성](research/20260330-hypothesis-vs-engineering-thinking.md)
- [2026-03-30 AI 하네스(Harness) 개념 및 사용법](research/20260330-harness-engineering.md)
- [2026-03-23 OpenHands Docker 권한 노이즈 제거](research/20260323-openhands-docker-permission-solution.md)
- [2026-03-23 가설-검증 기반 사고가 자율 에이전트 성능에 미치는 영향](research/20260323-hypothesis-driven-agent-research.md)
- [2026-03-24 OpenHands 전역 자율 에이전트 설정 아키텍처](research/20260324-openhands-autonomous-global-setup.md)
- [2026-03-24 자율 에이전트 vs 인터랙티브 AI 분업 경계](research/20260324-autonomous-agent-vs-interactive-ai-division.md)
- [2026-03-25 omc-autopilot 루프 vs 자율 에이전트 연구 동향 비교 분석](research/20260325-omc-autopilot-loop-vs-agent-research-trends.md)
- [2026-03-25 완전 자율 에이전트 — 목표 자율 업데이트 + 하위 루프 구성법](research/20260325-autonomous-agent-goal-update-subloop-architecture.md)
- [2026-03-25 omc-live 3개 패치 설계 평론](research/20260325-omc-live-patch-critique.md)
- [2026-03-26 omc-live 자가 진화 Outer Loop 아키텍처](research/20260326-omc-live-self-evolving-outer-loop.md)
- [2026-03-26 omc-live 스킬 전문가 평론 (자가 진화 버전)](research/20260326-omc-live-skill-critique.md)
- [2026-03-27 omc-live 깃 체크포인트 + 자가 진화 에이전트 최신 연구](research/20260327-omc-live-git-checkpoint-self-evolving-research.md)
- [2026-03-27 자율 AI 연구 에이전트 2025-2026 최신 동향 (3-agent pipeline)](research/20260327-omc-live-autonomous-ai-research-2025-2026.md)
- [2026-03-28 무한 자율 에이전트 실행 — 순환구조와 방법론 SOTA](research/20260328-omc-live-infinite-loop-architecture-research.md)
- [2026-03-28 omc-live 과학 연구 / 고전문 분야 확장성](research/20260328-omc-live-science-research-domain-expansion.md)
- [2026-03-30 자율 에이전트 인사이트 수집 및 LiveCode 개선 보고서](agent-improvement-report-20260330.md)
- [2026-03-30 omc-live / omc-live-infinite 스킬 전문 평론](research/20260330-omc-live-critique.md)
- [2026-03-31 Category-Aware Strategy Selection for Stuck Agents — 논문 프레임 v1](research/paper-frame-category-aware-strategy.md)

## Marketing
- [marketing/concept.md](marketing/concept.md) — HarnessOS 포지셔닝 문서 (Harness Engineering 트렌드, scaffold/middleware 본질, 컴포넌트 스택, AGI 로드맵)
- [marketing/devto_post.md](marketing/devto_post.md) — Dev.to 영문 포스트 (scaffold/middleware for infinite autonomous tasks, Harness Engineering 포지셔닝)
- [marketing/hn_submission.md](marketing/hn_submission.md) — Hacker News Show HN + 일반 링크 제출 텍스트 (context rotation, self-evolving goals)
- [marketing/disquiet_log.md](marketing/disquiet_log.md) — disquiet.io 한국어 로그 (무한 자율 작업 scaffold/middleware)
- [marketing/tldr_email.md](marketing/tldr_email.md) — TLDR AI 뉴스레터 이메일 제출 텍스트
- [marketing/github_issue_comment.md](marketing/github_issue_comment.md) — GitHub 이슈 댓글 템플릿 4종 (컨텍스트/실패/목표진화/Harness Engineering)

## Related
- [[projects/HarnessOS/research/20260328-omc-live-infinite-loop-architecture-research|20260328-omc-live-infinite-loop-architecture-research]]
- [[projects/HarnessOS/research/20260330-hypothesis-experiment-results|20260330-hypothesis-experiment-results]]
- [[projects/HarnessOS/research/20260331-autonomous-skill-selection-research|20260331-autonomous-skill-selection-research]]
- [[projects/HarnessOS/research/20260330-omc-live-critique|20260330-omc-live-critique]]
- [[projects/HarnessOS/research/digests/20260401-experiment-ideas|20260401-experiment-ideas]]
- [[projects/HarnessOS/superpowers/plans/2026-03-22-llm-longcontext-experiment|2026-03-22-llm-longcontext-experiment]]
- [[projects/HarnessOS/research/paper-frame-category-aware-strategy|paper-frame-category-aware-strategy]]
- [[projects/HarnessOS/research/digests/20260401-verification-hurt-results|20260401-verification-hurt-results]]
