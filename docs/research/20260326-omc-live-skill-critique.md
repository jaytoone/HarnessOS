# [expert-research-v2] omc-live 스킬 전문가 평론 (자가 진화 버전)
**Date**: 2026-03-26  **Skill**: expert-research-v2

## Original Question
현재 omc-live 스킬 전체 설계에 대한 전문가 평론 — 자가 진화 루프(self-evolving outer loop) 포함 버전.

## Web Facts (Code-Internal — SKILL.md 직접 분석)

[FACT-1] 3중 종료 조건: plateau_k(2), max_evolution_depth(3), max_outer_iterations(5) 독립 동작.

[FACT-2] delta 로직: `delta = current_score - best_score`. current_score > best_score이면 best 갱신, else plateau_count++.

[FACT-3] SCORE PROMPT: 4차원(quality/completeness/efficiency/impact) 0.0-1.0 float. "total:" 라인 파싱.

[FACT-4] GOAL EVOLUTION PROMPT: 최저 차원 타겟팅. EVOLVED_GOAL + RATIONALE 출력.

[FACT-5] CONVERGED 처리: best_score 값 관계없이 episode(success, high_quality=true) 저장.

[FACT-6] 상태 파일 4개 분리: live-state.json + goal-tree.json + episodes.jsonl + failure-history.json.

[FACT-7] "Level 3 goal substitution without approval" stop condition 존재. "Level 3"의 정의 미명시.

## Multi-Lens Analysis

### Domain Expert (Lens 1)

**강점**:
- 3중 독립 종료 조건 — 단일 조건 오동작으로 무한 루프 불가
- parse failure → UNCERTAIN 폴백 — fail-safe 방향 올바름
- evolution_history + original_goal 분리 보존 — 사후 분석 가능
- episodes.jsonl 비삭제 — 세션 간 학습 기반

**결함 1 [HIGH]**: delta 음수(퇴행) 처리 미정의 → 조기 수렴 오판 위험
**결함 2 [HIGH]**: LLM 자가 평가 편향 + 차원 트레이드오프 (Goodhart's Law) → goal drift
**결함 3 [HIGH]**: CONVERGED ≠ 성공. 최소 품질 임계값 없음 → 저품질 성공 신호 가능
**결함 4 [MEDIUM]**: "Level 3 substitution" 조건 — max_evolution_depth와 중복 or 미정의

### Self-Critique (Lens 2)

- [OVERCONFIDENT] 자가 평가 편향을 인플레이션 방향으로만 서술. 실제로는 oscillation도 동등 위험.
- [MISSING] 차원 트레이드오프: efficiency↑ + completeness↓ → total average 개선 가능 → 사용자에게 퇴행 결과 전달
- [INTERNAL CONFLICT] CONVERGED → success가 의미적으로 부정확

### Synthesis (Lens 3)

개선 우선순위:
- P0: delta 음수 처리 명시 + CONVERGED_STALE 분기(min_convergence_score=0.6)
- P1: goal_fidelity 5번째 차원 + Level 3 조건 정의 명확화
- P2: 상태 파일 원자적 쓰기

## Final Conclusion

**전체 평가: ADEQUATE-STRONG**. 설계 의도 올바름. 자가 진화 추가로 구조적 리스크 3개 도입.
수정 없이 프로덕션 투입 시 수렴 오판 또는 목표 발산 가능성 있음.

**즉시 수정 필요 (P0)**:
1. `plateau_count`를 "best_score 경신 못한 횟수"에서 "엡실론 이상 개선 없는 연속 횟수"로 재정의. 퇴행 시 plateau_count 증가 안 함.
2. Configuration에 `min_convergence_score: 0.6` 추가. best_score < threshold 시 CONVERGED_STALE로 분기.

**신뢰도**: MEDIUM-HIGH (구조 분석 HIGH / 자가 평가 실제 동작 MEDIUM — 실험 필요)

## Sources
- /home/jayone/.claude/skills/omc-live/SKILL.md (직접 분석)
- docs/research/20260326-omc-live-self-evolving-outer-loop.md (전 세션 연구)
- docs/research/20260325-omc-live-patch-critique.md (이전 패치 평론)

## Related
- [[projects/LiveCode/research/20260326-omc-live-self-evolving-outer-loop|20260326-omc-live-self-evolving-outer-loop]]
- [[projects/LiveCode/research/20260330-omc-live-critique|20260330-omc-live-critique]]
- [[projects/LiveCode/research/20260325-omc-live-patch-critique|20260325-omc-live-patch-critique]]
- [[projects/LiveCode/research/20260327-omc-live-git-checkpoint-self-evolving-research|20260327-omc-live-git-checkpoint-self-evolving-research]]
- [[projects/LiveCode/research/20260328-omc-live-science-research-domain-expansion|20260328-omc-live-science-research-domain-expansion]]
- [[projects/LiveCode/research/20260328-omc-live-infinite-loop-architecture-research|20260328-omc-live-infinite-loop-architecture-research]]
