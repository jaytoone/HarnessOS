# [expert-research-v2] 자율 AI 연구 에이전트 2025-2026 최신 동향
**Date**: 2026-03-27  **Skill**: expert-research-v2 (3-agent pipeline)

## Original Question
자율 AI 연구 에이전트 2025-2026 최신 동향. omc-live 자가 진화 outer loop에 적용 가능한 검증된 패턴 발굴.
(1) 병렬 가설 탐색 (2) 자동 동료 검토 (3) 실패 패턴 원칙화 (4) AI Scientist 후속 (5) Reflexion 변종

## Collected Facts (Fact Finder, web-verified)

- [FACT-1] AI Scientist-v2 (Sakana AI, Apr 2025, arXiv:2504.08066): "progressive agentic tree-search" 핵심 메커니즘. 실험 관리자 에이전트가 병렬 경로 트리 관리. 인간 코드 템플릿 불필요.
- [FACT-2] AI Scientist-v2: ICLR 2025 ICBINB 워크숍 peer review 통과 (평균 6.33점, 인간 상위 55%). Sakana 자진 철회.
- [FACT-3] Nature 2026 (2026-03-26 게재): Automated Reviewer balanced accuracy 69%, F1 > 인간 간 일관성. (source: nature.com/articles/s41586-026-10265-5)
- [FACT-4] Automated Reviewer 구조: 5개 독립 리뷰 앙상블 + Area Chair 역할로 최종 결정. NeurIPS 가이드라인 기반 프롬프팅.
- [FACT-5] Beel et al. 2025 (arXiv:2502.14297): v1 실험 42% 실패, 논문 1편 $6-15, 인간 참여 3.5시간.
- [FACT-7] REMOR (arXiv:2505.11718, May 2025): Multi-Objective RL(GRPO) reviewer. 인간 평균 보상 2배 달성. "AI 최우수 리뷰 = 인간 최우수 리뷰, 저품질 긴 꼬리 제거".
- [FACT-9] SE-Agent (NeurIPS 2025): cross-trajectory revision/recombination/refinement. SWE-bench Verified 오픈소스 SOTA, 최대 +55% 상대적 개선.
- [FACT-10] Agent0 (arXiv:2511.16043, Nov 2025): curriculum + executor 공진화. 수학 추론 +18%, 일반 추론 +24%.
- [FACT-11] Symbolic Learning (AI Open 2025, Ou et al.): back-propagation 유추로 실패를 텍스트 "loss"→prompt 자동 업데이트.
- [FACT-12] Self-Evolving Agents Survey (arXiv:2508.07407, Aug 2025): 4요소 프레임워크 — System Inputs / Agent System / Environment / Optimisers.

## Cross-Validation Matrix

| 주제 | 합의 수준 | 핵심 근거 |
|------|---------|---------|
| 병렬 탐색 트렌드 | STRONG | FACT-1 (progressive tree-search) |
| LLM reviewer "30-50%" 수치 | REJECT | CONTRADICTED by FACT-3 (69%), FACT-7 (2x) |
| AI reviewer 실용성 | CONFIRMED | FACT-3 Nature 2026 |
| Cross-trajectory recombination | CONFIRMED-STRONG | FACT-9 (+55%) |
| AI Scientist v2 존재 | CONFIRMED-STRONG | FACT-1,2 |
| Co-evolution | CONFIRMED-STRONG | FACT-10 (+18-24%) |
| Failure taxonomy 3-tier | STRONG | FACT-11 지지 |

## Devil's Advocate 핵심 비평

- **CRITICAL**: Analyst의 "30-50% reviewer" 수치 → Nature 2026 (69%) + REMOR (2x)로 완전 반박
- **MAJOR**: ToT 메커니즘 오귀인 → AI Scientist-v2 "progressive agentic tree-search"가 정확한 명칭
- **MAJOR**: SE-Agent, Symbolic Learning, Agent0, Survey 4건 누락
- **MAJOR**: AI Scientist v2 LOW confidence → FACT-1,2로 반증
- **MAJOR**: Cross-model review 전제 오류 → Ensemble이 이미 효과적 (FACT-4)

## Final Conclusion — omc-live 적용 제안

### P1 (즉시 적용, 이번 세션 완료)

**[P1-1] Ensemble Scoring (score_ensemble_n: 3)**
- 근거: Sakana AI Nature 2026 — 5 독립 리뷰 앙상블 → balanced accuracy 69%
- 구현: SCORE PROMPT를 3회 독립 실행 → 평균값 사용. variance > 0.15 → UNCERTAIN 경고.
- Configuration에 `score_ensemble_n: 3` 추가, Score Parser 업데이트. ✅ 완료

**[P1-2] Cross-Trajectory Recombination (PRE-LOOP Step 1)**
- 근거: SE-Agent NeurIPS 2025 — 실패 궤적 recombination → +55% SWE-bench
- 구현: PRE-LOOP에서 실패 에피소드 3개 추가 로드 → "Past failure patterns" 인스트럭션 주입
- ✅ 완료

### P2 (다음 세션 고려)

**[P2-1] Progressive Tree-Search (EVOLVE 시 3 후보 경로)**
- 근거: AI Scientist-v2 progressive agentic tree-search
- 구현: EVOLVE 시 단일 EVOLVED_GOAL 대신 3개 후보 생성 → 빠른 pruning → 최우수 경로만 full 실행

**[P2-2] Co-evolution 명시적 루프**
- 근거: Agent0 +18-24%
- 구현: EVOLVE 시 "이전 iteration 성공 유형"을 goal elevation 입력으로 명시 사용

### P3 (선택적)
- Failure taxonomy 3-tier → CONVERGED 시 goal-tree.json에 failure_patterns[] 기록

## Reference Sources
- https://arxiv.org/abs/2504.08066 — AI Scientist-v2
- https://sakana.ai/ai-scientist-nature/ — Nature 2026 게재 보고
- https://www.nature.com/articles/s41586-026-10265-5 — Nature 원문
- https://arxiv.org/html/2502.14297v3 — Beel et al. v1 평가
- https://arxiv.org/abs/2505.11718 — REMOR
- https://neurips.cc/virtual/2025/poster/116517 — SE-Agent
- https://arxiv.org/abs/2511.16043 — Agent0
- https://www.sciencedirect.com/science/article/pii/S2666651025000208 — Symbolic Learning
- https://arxiv.org/abs/2508.07407 — Self-Evolving Agents Survey

## Related
- [[projects/LiveCode/research/20260326-omc-live-self-evolving-outer-loop|20260326-omc-live-self-evolving-outer-loop]]
- [[projects/LiveCode/research/20260327-omc-live-git-checkpoint-self-evolving-research|20260327-omc-live-git-checkpoint-self-evolving-research]]
- [[projects/LiveCode/research/20260326-omc-live-skill-critique|20260326-omc-live-skill-critique]]
- [[projects/LiveCode/research/20260328-omc-live-infinite-loop-architecture-research|20260328-omc-live-infinite-loop-architecture-research]]
- [[projects/LiveCode/research/20260328-omc-live-science-research-domain-expansion|20260328-omc-live-science-research-domain-expansion]]
