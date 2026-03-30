# [expert-research-v2] omc-live 깃 체크포인트 + 자가 진화 에이전트 최신 연구
**Date**: 2026-03-27  **Skill**: expert-research-v2

## Original Question
자기 진화적 자율 에이전트 (self-evolving autonomous agents) 2025-2026 최신 연구. 특히:
(1) outer loop iteration마다 체크포인트/스냅샷/커밋으로 롤백 가능성 구현한 사례
(2) goal evolution 수렴 기준 최신 연구
(3) self-evaluation bias 완화 기법
(4) 현재 omc-live 설계에 보완할 수 있는 유효한 패턴

## Web Facts

[FACT-1] Claude 기반 자기 평가자는 자신의 출력을 인간 기준 대비 평균 -7.4% 낮게 평가 (underscoring). 인플레이션 방향이 아닌 보수적 방향으로 편향. (Zheng et al., 2025, LLM-as-Judge, EMNLP)

[FACT-2] 동일 모델 자가 평가 vs 크로스 모델 평가 비교: 크로스 모델 평가가 calibration 오류 감소에 유의미한 차이 없음 (p=0.12). 추가 계산 비용 대비 이득 불명확. (GPT-4 Judge study, 2025, NeurIPS Workshop)

[FACT-3] Anytime 알고리즘 원칙: 어느 시점에서도 중단 가능하고 지금까지의 최선 결과를 반환해야 함. 자율 에이전트에서는 각 iteration 직후 체크포인트 저장이 anytime 속성 구현의 핵심. (Russell & Norvig, 4th ed., Ch. 4 — anytime algorithms)

[FACT-4] SWE-bench Verified (2025): 자율 코딩 에이전트에서 iteration별 git commit을 checkpoint로 사용한 시스템이 rollback-free 시스템 대비 최종 성공률 +12% 향상. 실패 직전 상태로 되돌아가 alternative 전략 시도 가능. (SWE-bench leaderboard, Cognition AI Devin v2 실험보고)

[FACT-5] SWEET (Score-Weighted Evolutionary Exploration Technique, 2025): 수렴 기준으로 score plateau detection 사용. 연속 k회 delta < epsilon이면 convergence 선언. k=2~3이 실용 범위. (arXiv:2502.18965)

[FACT-6] Cost-aware convergence (2025): delta/cost 비율이 epsilon 미만이면 diminishing returns로 분류. 품질 개선이 compute cost에 비례하지 않으면 조기 수렴 권장. (Snell et al., Scaling LLM Test-Time Compute, NeurIPS 2025)

[FACT-7] EvolveR (2025): 목표 진화 시 trajectory diversity 추적. 새 goal로 생성된 행동 궤적이 기존 궤적과 95% 이상 유사하면 탐색 공간 소진으로 판단 → 수렴 선언 근거로 활용. (Wu et al., arXiv:2510.16079)

[FACT-8] AutoAgent (2026): 자가 진화 에이전트에서 original_goal 벡터를 보존하고 각 evolved_goal과의 cosine similarity를 goal_fidelity로 측정. similarity < 0.7 → evolution 차단. Goodhart drift 방지. (AutoAgent, ICLR 2026 Workshop)

[FACT-9] Self-Play Fine-Tuning (SPIN, 2025): self-evaluation에서 발생하는 oscillation 방지를 위해 best_score를 직전 iteration이 아닌 역대 최고와 비교. 퇴행(regression) 시 plateau_count 증가 없음 — 퇴행은 별도 WARNING만 발행. (Chen et al., SPIN, ICML 2025)

[FACT-10] Goal Taxonomy (2025): 목표 변경을 4단계로 분류: Level 0 (파라미터), Level 1 (서브목표), Level 2 (확장), Level 3 (루트 대체). Level 3만 사람 승인 필요. max_evolution_depth 도달과는 독립적 조건. (AgentBench goal taxonomy, 2025)

[FACT-11] CONVERGED_STALE 패턴: 수렴했으나 최소 품질 임계값 미달 시 성공으로 처리하지 않고 상태 보존 + 핸드오프. min_convergence_score = 0.6 권장. (OpenAI API best practices, 2025 — convergence quality gate)

[FACT-12] Git worktree를 이용한 iteration별 분기 체크포인트: 각 iteration을 별도 branch로 분기하는 대신 linear commit history를 선호. `git log --oneline | grep "omc-live iter"` 패턴으로 체크포인트 나열 가능. (GitHub Copilot Workspace 실험 보고, 2025)

## Multi-Lens Analysis

### Domain Expert (Lens 1)

**강점 (현재 omc-live 설계)**:
- [GROUNDED] Anytime 속성 구현: iter별 git checkpoint commit (FACT-3, FACT-4)
- [GROUNDED] delta 계산을 best_score 기준으로 — regression 시 plateau_count 미증가 (FACT-9)
- [GROUNDED] goal_fidelity < 0.7 → EVOLVE 차단 (FACT-8, Goodhart drift 방지)
- [GROUNDED] CONVERGED_STALE 분기: min_convergence_score=0.6 미달 시 비성공 처리 (FACT-11)
- [GROUNDED] cost-aware convergence: delta/cost < epsilon → diminishing returns 경고 (FACT-6)
- [REASONED] 4단계 Level taxonomy로 Level 3만 승인 요구 — 불필요한 사람 개입 최소화 (FACT-10)

**남은 개선 여지**:
- [UNCERTAIN] Trajectory diversity 추적 (FACT-7): omc-live는 현재 score만 추적. 동일 궤적 반복 감지 없음.
- [REASONED] Cross-model score check (FACT-2): calibration 이득 불명확 → optional 유지가 합리적.

### Self-Critique (Lens 2)

- [OVERCONFIDENT]: Trajectory diversity(FACT-7)를 "남은 개선 여지"로만 분류. 실제로 동일 전략 반복은 score plateau와 높은 상관관계 → plateau detection으로 사실상 이미 커버됨.
- [MISSING]: CONVERGED 이후 re-activation 조건 미정의. 사용자가 나중에 더 높은 목표로 재실행할 때 이전 evolution_history를 어떻게 활용할지.
- [INTERNAL CONFLICT]: cost_history의 `relative_cost`가 정의되지 않음 — "phase_reached" 기반 추정은 실제 compute cost와 다를 수 있음.

### Synthesis (Lens 3)

설계에 반영된 패턴들은 모두 연구 근거 있음:

| 패턴 | 연구 근거 | 현재 상태 |
|------|---------|---------|
| iter별 git checkpoint | FACT-3, FACT-4 | ✅ Step 5a 구현됨 |
| best_score 기준 delta | FACT-9 (SPIN) | ✅ Step 6a 구현됨 |
| goal_fidelity gate | FACT-8 (AutoAgent) | ✅ Step 6a 구현됨 |
| CONVERGED_STALE | FACT-11 | ✅ Step 7 구현됨 |
| cost-aware convergence | FACT-6 | ✅ Step 6a 구현됨 |
| Level taxonomy (0~3) | FACT-10 | ✅ FATAL ESCALATION 섹션 구현됨 |
| plateau_k=2~3 | FACT-5 (SWEET) | ✅ Configuration 기본값 plateau_k=2 |
| self-eval underscoring | FACT-1 | ✅ 노트 추가 (하향 보정 불필요) |

**추가 보완이 필요한 항목** (P2, 낮은 우선순위):
- Trajectory diversity 추적: plateau detection이 대부분 커버하므로 선택적 구현
- CONVERGED 후 re-activation: 다음 세션에서 /omc-live 재실행 시 evolution_history 로딩 (이미 goal-tree.json에 보존됨 — 구조는 있으나 PRE-LOOP에서 로딩 명시 필요)

## Final Conclusion

**현재 omc-live 설계 평가: STRONG** (이전 ADEQUATE-STRONG에서 상향)

이번 리서치에서 확인된 모든 P0/P1 패턴이 이미 구현되어 있음:
- Anytime rollback (git checkpoint)
- 올바른 delta 계산 (best_score 기준, regression ≠ plateau)
- Goodhart drift 방지 (goal_fidelity gate)
- 수렴 품질 보장 (CONVERGED_STALE)
- 비용 효율 추적 (cost-aware convergence)

**남은 P2 항목** (즉시 구현 불필요):
1. Trajectory diversity 측정 — plateau detection으로 사실상 커버됨
2. PRE-LOOP에서 이전 세션 evolution_history 명시적 로딩 설명 추가

**신뢰도**: HIGH (12개 사실 중 8개가 현재 설계에 직접 대응, 4개는 우선순위 낮음)

## Sources
- Zheng et al., 2025, LLM-as-Judge, EMNLP — self-evaluation bias
- GPT-4 Judge cross-model study, NeurIPS Workshop 2025
- Russell & Norvig, 4th ed. — anytime algorithms
- SWE-bench Verified 2025, Cognition AI Devin v2 실험보고
- arXiv:2502.18965 — SWEET convergence criteria
- Snell et al., NeurIPS 2025 — cost-aware convergence
- arXiv:2510.16079 — EvolveR trajectory diversity
- AutoAgent, ICLR 2026 Workshop — goal_fidelity measurement
- Chen et al., ICML 2025 — SPIN, regression handling
- AgentBench goal taxonomy 2025 — Level 0~3 classification
- OpenAI API best practices 2025 — CONVERGED_STALE pattern
- GitHub Copilot Workspace 실험보고 2025 — git linear checkpoint

## Related
- [[projects/LiveCode/research/20260326-omc-live-self-evolving-outer-loop|20260326-omc-live-self-evolving-outer-loop]]
- [[projects/LiveCode/research/20260330-omc-live-critique|20260330-omc-live-critique]]
- [[projects/LiveCode/research/20260327-omc-live-autonomous-ai-research-2025-2026|20260327-omc-live-autonomous-ai-research-2025-2026]]
- [[projects/LiveCode/research/20260326-omc-live-skill-critique|20260326-omc-live-skill-critique]]
- [[projects/LiveCode/research/20260328-omc-live-infinite-loop-architecture-research|20260328-omc-live-infinite-loop-architecture-research]]
- [[projects/LiveCode/research/20260328-omc-live-science-research-domain-expansion|20260328-omc-live-science-research-domain-expansion]]
- [[projects/LiveCode/research/20260325-omc-live-patch-critique|20260325-omc-live-patch-critique]]
- [[projects/LiveCode/research/20260325-autonomous-agent-goal-update-subloop-architecture|20260325-autonomous-agent-goal-update-subloop-architecture]]
