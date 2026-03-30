# [expert-research-v2] omc-live 자가 진화 Outer Loop 아키텍처
**Date**: 2026-03-26  **Skill**: expert-research-v2

## Original Question
omc-live outer loop의 자가 진화 구현 — 최종 상태를 더 나아질 수 있을 때까지 goal을 재정의하면서 루프를 이어가는 self-evolving 메커니즘.

## Web Facts

[FACT-1] 반복 개선 종료는 이중 임계값 조건 사용. |S_i+1 - S_best| < epsilon이 k회 연속이면 수렴. (Yuksel et al., 2025, ACL Anthology)

[FACT-2] Lenient passing 기준: 4+ 지표 중 75% 이상 pass OR 평균 ≥ 0.85. 단일 지표 수렴으로 조기 종료 방지. (OpenAI Cookbook, self-evolving agents)

[FACT-3] EvolveR: 행동 궤적 시맨틱 다양성 추적. 새 궤적이 기존과 95% 이상 유사 → 탐색 공간 소진. (Wu et al., arXiv:2510.16079)

[FACT-4] best_score 비교 기준 — 직전이 아닌 역대 최고와 비교해야 local optima 방지. (Yuksel et al., 2025)

[FACT-5] 목표 재정의: Hypothesis Generation Agent가 역할·태스크·워크플로 변경 제안. 목표 자체가 다차원 평가 결과로 상향 재정의됨. (ACL Anthology)

[FACT-6] 목표 변경 시 보상 함수 동반 재설계 필수. 목표만 변경하고 보상 고정 → goal-reward misalignment. (arXiv:2508.07407, 기존 연구 docs)

[FACT-7] AutoContext 5단계: Competitor → Analyst → Coach → Architect → Curator. 개선 지식만 선별 누적. (Greyhaven, 2025)

[FACT-8] EvolveR 2속도 학습: 오프라인 증류(추상적 전략 원칙) + 온라인 검색(실행 시 참조). 세션 간 지식 소실 방지. (arXiv:2510.16079)

## Multi-Lens Analysis

### Domain Expert (Lens 1)

**인사이트 1** [GROUNDED]: 자가 진화 종료 기준은 단일 YES/NO가 아닌 다차원 점수 + delta 임계값
- 현재 omc-live는 YES → 즉시 종료. 개선 여지 감지 불가.
- 올바른 구현: YES → score(4차원) → |delta| < epsilon for plateau_k → CONVERGED

**인사이트 2** [GROUNDED]: goal 진화는 "약한 차원 타겟팅"으로 수행
- 4차원 중 최저 점수 차원을 찾아 그 방향으로 goal 상향
- 무작위 goal 변경이 아닌 evidence-based elevation

**인사이트 3** [REASONED]: best_score 추적이 진화 품질의 핵심
- current_score가 아닌 best_score 대비 delta 계산
- regression(score 하락)을 진화로 오인하지 않음

### Self-Critique (Lens 2)

**[OVERCONFIDENT]**: 4차원 점수의 신뢰성
- LLM이 자신의 결과물을 자체 평가 → self-serving bias 위험
- 완화: 점수 프롬프트에 구체적 증거 요구 ("구체적 근거를 1문장으로")

**[MISSING]**: goal drift 방지 메커니즘
- evolution이 깊어질수록 original_goal에서 멀어질 수 있음
- 완화: evolution_history에 original_goal 보존 + 진화 방향이 원래 의도와 부합하는지 체크

**[MISSING]**: 진화 루프와 기존 omc-failure-router 상호작용
- 진화된 goal로 autopilot이 Fatal 실패 시 → goal-tree Level 3 업데이트와 충돌 가능
- 완화: evolution_count가 0보다 크면 Level 3 에스컬레이션 전 진화 히스토리 검토 추가

### Synthesis (Lens 3)

핵심 설계 원칙:
1. YES ≠ 종료 (evolve_mode=true 기본)
2. 수렴 = plateau_k 연속 delta < epsilon (delta 기준은 best_score)
3. goal 진화 = 약한 차원 타겟팅 + original_goal 컨텍스트 유지
4. 안전장치 = max_evolution_depth + max_outer_iterations 이중 예산

## Final Conclusion

### 구현된 변경사항 (omc-live SKILL.md)

1. **Configuration 추가**: `evolve_mode`, `epsilon`, `plateau_k`, `max_evolution_depth`, `score_dimensions`
2. **Step 6a 추가**: YES 이후 4차원 점수화 + delta 계산 + 수렴/진화 결정
3. **Step 6b 추가**: goal elevation prompt → `EVOLVED_GOAL:` 파싱 → goal-tree 업데이트
4. **CONVERGED 브랜치 추가**: 수렴 보고 형식 (score trajectory + evolution history)
5. **State_Files 확장**: `best_score`, `current_score`, `plateau_count`, `evolution_count`, `score_history`
6. **Integration Map 업데이트**: YES → SCORE → EVOLVE/CONVERGED 흐름

### 종료 조건 (최종)

| 조건 | 진화 모드 | 동작 |
|------|---------|------|
| plateau_count >= plateau_k | 전용 | CONVERGED (성공 보고) |
| evolution_count >= max_evolution_depth | 전용 | CONVERGED (깊이 제한) |
| max_outer_iterations 도달 | 공통 | FORCE STOP (Handoff) |
| 사용자 stop | 공통 | omc-cancel |
| evolve_mode=false AND YES | 클래식 | ACHIEVED (즉시 종료) |

## Sources

- https://aclanthology.org/2025.realm-1.4.pdf — Yuksel et al., multi-agent iterative improvement
- https://developers.openai.com/cookbook/examples/partners/self_evolving_agents/ — OpenAI self-evolving agents
- https://arxiv.org/abs/2510.16079 — EvolveR, semantic trajectory diversity
- https://github.com/greyhaven-ai/autocontext — AutoContext closed-loop architecture
- https://arxiv.org/abs/2508.07407 — Self-Evolving AI Agents Three Laws (기존 연구 docs)
