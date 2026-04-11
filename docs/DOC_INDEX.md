# Document Index

## Architecture
- [ARCHITECTURE.md](ARCHITECTURE.md) — LiveCode 전체 아키텍처 개념도 — 3개 실험 스트림 + analyze.py + harness_evaluator + app.py dashboard

## Experiments
- [verification_hurt/runner.py](../experiments/verification_hurt/runner.py) — Verification mode 비교 실험 (none/strict/lenient/adaptive escape_rate 측정)
- [hypothesis_validation/uncertainty_guided_trajectory.md](../experiments/hypothesis_validation/uncertainty_guided_trajectory.md) — 불확실성 기반 순차 증거 수집 live-inf 실험 설계 (arXiv:2604.05116)
- [hypothesis_validation/uncertainty_gate_report.md](../experiments/hypothesis_validation/uncertainty_gate_report.md) — Uncertainty Gate A/B 실험 결과 보고서 (예비 n=1, H1 미지지, 재실험 가이드 포함)
- [hypothesis_validation/territory_paint_wars_failure_modes.md](../experiments/hypothesis_validation/territory_paint_wars_failure_modes.md) — A/B 실험 실패 모드 분류 설계 (arXiv:2604.04983)

## Specs
- [2026-03-22 LLM 장기 컨텍스트 실험 설계](superpowers/specs/2026-03-22-llm-longcontext-experiment-design.md)

## Plans
- [2026-03-22 LLM 장기 컨텍스트 실험 구현 계획](superpowers/plans/2026-03-22-llm-longcontext-experiment.md)

## Knowledge Pipeline
- [knowledge-channels.yaml](knowledge-channels.yaml) — RSS 채널 레지스트리 (AI/ML/Engineering/Startup/KR)
- [research/designs/openharness_vs_entity_positioning.md](research/designs/openharness_vs_entity_positioning.md) — OpenHarness vs Entity 경쟁 포지셔닝 분석 (마켓 배포 대응)
- [research/designs/global_agent_skill_critique_2026.md](research/designs/global_agent_skill_critique_2026.md) — Expert critique: Claude global agents/skills — 7 critical defects + improvement roadmap (EN, 2026-04-09)
- [research/designs/full_skill_agent_review_2026.md](research/designs/full_skill_agent_review_2026.md) — Full review: all 75 skills + 65 agent types — 24 issues, 10 applied fixes, improvement roadmap (EN, 2026-04-09)
- [research/designs/skill_agent_audit.md](research/designs/skill_agent_audit.md) — Skill/Agent 분류 오류 감사 — omc 제외, P1~P3 수정 항목 선별 (2026-04-09)
- [digests/](research/digests/) — 날짜별 자동 수집 다이제스트 (scripts/collect.sh 생성)

## Research
- [2026-04-11 WTP 연구 시리즈 메타-리뷰 — 내부 모순 3개 + 과잉주장 4개 + 향후 방향 (iter 8)](research/20260411-wtp-meta-review.md)
- [2026-04-11 Social_Amplifier 검증 실험 설계 — 곱셈 vs 덧셈, ₩12만/2.5주 (iter 7)](research/20260411-wtp-social-amplifier-experiment.md)
- [2026-04-11 VALUE GAP vs JTBD 비교 분석 — 수요 이론 확장성 판정 (iter 6)](research/20260411-wtp-jtbd-comparison.md)
- [2026-04-11 커리어 궤적 거울 MVP 설계 — L5 WTP 제품 8-10주 빌드 스펙 (iter 5)](research/20260411-wtp-career-mirror-mvp.md)
- [2026-04-11 WTP VALUE GAP 역분석 — 퍼블리/클래스101/리멤버/MKYU/폴인 진단 (iter 4)](research/20260411-wtp-korean-product-audit.md)
- [2026-04-11 WTP 전략 원페이저 — 5분 의사결정 가이드 (진단+처방+한국 채널, iter 3)](research/20260411-wtp-one-pager.md)
- [2026-04-11 WTP 이론 → 제품 설계 패턴 — pricing tiers, activation hooks, CLG GTM, 한국 B2C (iter 2)](research/20260411-wtp-product-design-patterns.md)
- [2026-04-11 WTP 수요 발생 이론 — VALUE GAP · 정체성 갭 · 빠짐 안티패턴 (3-agent debate synthesis)](research/20260411-wtp-demand-genesis-theory.md)
- [2026-04-07 Playwright Test Agents v1.56 — Claude Code 활성화 가이드](research/digests/20260407-playwright-test-agents-claude-code.md)
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
- [marketing/github_outreach_drafts.md](marketing/github_outreach_drafts.md) — GitHub 이슈별 맞춤 기술 댓글 초안 9건 (Wave 1: claude-code, crewAI, adk-python, OpenHands / Wave 2: openai-agents-python, strands-agents)
- [marketing/outreach_ready/adk_python_4178.md](marketing/outreach_ready/adk_python_4178.md) — google/adk-python#4178 즉시 게시 가능 댓글 (429/503 state corruption)
- [marketing/outreach_ready/claude_code_discussion.md](marketing/outreach_ready/claude_code_discussion.md) — anthropics/claude-code Discussion 게시용 RFC (context rotation pattern)
- [marketing/outreach_ready/oh_my_codex_context_issue.md](marketing/outreach_ready/oh_my_codex_context_issue.md) — Yeachan-Heo/oh-my-codex context/session 이슈 즉시 게시용 댓글 (short/full 버전 + follow-up)
- [marketing/geeknews_post.md](marketing/geeknews_post.md) — GeekNews/요즘IT 한국어 포스트 초안 (Entity vs Oh My Codex 레이어 설명 + 요즘IT 투고용)
- [marketing/outreach_ready/oh_my_claudecode_discussion.md](marketing/outreach_ready/oh_my_claudecode_discussion.md) — Yeachan-Heo/oh-my-claudecode Discussion/Issue 즉시 게시용 (long-horizon + failure recovery 2종)
- [marketing/outreach_ready/oh_my_claudecode_2059.md](marketing/outreach_ready/oh_my_claudecode_2059.md) — Yeachan-Heo/oh-my-claudecode#2059 Coordinator Mode 즉시 게시용 (Bellman 직접 제안 이슈)
- [marketing/outreach_ready/openai_codex_context_issues.md](marketing/outreach_ready/openai_codex_context_issues.md) — openai/codex context compaction 이슈 3종 즉시 게시용 (#10823/#3997/#8365)
- [marketing/reddit_localllama.md](marketing/reddit_localllama.md) — Reddit r/LocalLLaMA 포스트 (cliff-edge 발견 + HarnessOS, 2026-04-01 LIVE)

## Research (Recent)
- [2026-04-03 Optimal Top-N for Knowledge Pipeline](research/20260403-optimal-top-n-knowledge-pipeline.md) — Adaptive K 공식 도출 (RAG/Miller's Law/Precision@K 기반)

## Research Designs
- [research/designs/autonomous_evolution_safety_design.md](research/designs/autonomous_evolution_safety_design.md) — 자율 진화 안전성 3-Paper Synthesis (Safety Gate Drift + Reward Hacking + CoT Monitorability)
- [research/designs/llm_evaluation_approaches_integration.md](research/designs/llm_evaluation_approaches_integration.md) — LLM Evaluation 4 Approaches HarnessOS 통합 설계
- [research/designs/cot_monitorability_break_predictor.md](research/designs/cot_monitorability_break_predictor.md) — CoT Monitorability Break Predictor 설계 (autonomy_classifier 확장, TF-IDF cosine consistency)
- [research/designs/oss_agent_tools_2026_integration.md](research/designs/oss_agent_tools_2026_integration.md) — OSS AI Agent Tools 2026 HarnessOS 통합 평가 (Fireship, Priority 1-3 분류)
- [research/designs/oh_my_codex_vs_harnessos_positioning.md](research/designs/oh_my_codex_vs_harnessos_positioning.md) — Oh My Codex vs HarnessOS 포지셔닝 분석 (10만 스타 경쟁자, 실행레이어 통합 가능성)

## Marketing
- [marketing/entity_rebrand_strategy.md](marketing/entity_rebrand_strategy.md) — HarnessOS→Entity 리브랜딩 전략 (Oh My Codex 경쟁 포지셔닝, 체크리스트, README 초안)
- [marketing/oh_my_codex_outreach.md](marketing/oh_my_codex_outreach.md) — Oh My Codex GitHub 아웃리치 초안 (Draft A/B/C + Wave 2 통합 발표용)
- [marketing/entity_positioning_messages.md](marketing/entity_positioning_messages.md) — Entity 채널별 포지셔닝 메시지 카드 (GitHub/Reddit/HN/dev.to/GeekNews)
- [marketing/ceo_outreach_response_templates.md](marketing/ceo_outreach_response_templates.md) — CEO 아웃리치 답장 템플릿 (Outward Reception A/B 테스트 +0.70 delta, 3개 프로필별 템플릿)

## Hypothesis Validation Experiments (Recent)
- [experiments/hypothesis_validation/reward_hacking_misalignment_safety.md](../experiments/hypothesis_validation/reward_hacking_misalignment_safety.md) — Reward Hacking → Safety Triad 4번째 감지기 실험 설계
- [experiments/hypothesis_validation/cot_interp_benchmark_design.md](../experiments/hypothesis_validation/cot_interp_benchmark_design.md) — Hard CoT Interpretation Benchmark 실험 설계 (verification gate false-positive)

## Related
- [[projects/Entity/research/20260330-hypothesis-experiment-results|20260330-hypothesis-experiment-results]]
- [[projects/Entity/research/20260331-autonomous-skill-selection-research|20260331-autonomous-skill-selection-research]]
- [[projects/Entity/research/designs/global_agent_skill_critique_2026|global_agent_skill_critique_2026]]
- [[projects/Entity/marketing/outreach_ready/oh_my_codex_context_issue|oh_my_codex_context_issue]]
- [[projects/Entity/research/20260330-omc-live-critique|20260330-omc-live-critique]]
- [[projects/Entity/marketing/reddit_localllama|reddit_localllama]]
- [[projects/Entity/research/digests/20260401-experiment-ideas|20260401-experiment-ideas]]
- [[projects/Entity/research/designs/full_skill_agent_review_2026|full_skill_agent_review_2026]]
