# [expert-research-v2] omc-live 3개 패치 설계 평론
**Date**: 2026-03-25  **Skill**: expert-research-v2

## Original Question
이번 omc-live 세션에서 완료한 3개 패치 (sg1: omc-live 판단 구조화, sg2: 에피소드 압축 전략, sg3: Reflexion 루프) 결과에 대한 전문가 평론

## Web Facts
- [FACT-1] Reflexion (Shinn 2023): 91% pass@1 HumanEval vs GPT-4 80%. 핵심 약점: 평가자 신호 품질 critical. (arxiv.org/abs/2303.11366)
- [FACT-2] Active Context Compression: 22.7~57% 토큰 절감, 정확도 유지. 에이전트 주도 압축 권장. (arXiv 2601.07190)
- [FACT-3] Episodic Memory: Encoding/Retrieval/Consolidation 3단계. 정적 키워드 매칭 불충분 — 시맨틱 매칭 필요. (arXiv 2502.06975)
- [FACT-4] Termination: 다중 종료 기준 레이어 필수. 종료 조건은 자동 임계값이 아닌 정책 결정. (Oracle Dev Blog)
- [FACT-5] Human-in-the-loop: bounded autonomy — 명시적 의사결정 권한 + 예외 처리. (Moxo)

## Verdict Table

| 패치 | 판정 | 연구 정렬 | 핵심 강점 | 핵심 약점 | 개선 제안 |
|------|------|----------|----------|----------|----------|
| sg1 (omc-live 판단) | ADEQUATE | HIGH | 정책적 종료 + 인간 에스컬레이션 | 출력 파싱 폴백 없음; NO branch gap 비구조화 | parse 실패 → UNCERTAIN 폴백 파서 추가 |
| sg2 (에피소드 압축) | ADEQUATE | MEDIUM | 3차원 버킷 커버리지 | 태그 매칭 ≠ 시맨틱 매칭 (FACT-3 충돌) | TF-IDF 코사인 유사도 최소 레이어 |
| sg3 (Reflexion) | STRONG | HIGH | Shinn 2023 직접 구현 | 외생 실패에 잘못된 reflection 생성 | 환경 오류 사전 라우팅 추가 |

## System-Level Risk
sg1 파싱 실패 → 에피소드 미저장 → sg2 BUCKET B 누락 → sg3 미발동 연쇄 실패 경로 존재.
sg1 출력 파싱 강화가 전체 시스템 단일 장애점 방어의 최우선 과제.

## Sources
- https://arxiv.org/abs/2303.11366
- https://arxiv.org/abs/2601.07190
- https://arxiv.org/html/2502.06975
- https://blogs.oracle.com/developers/what-is-the-ai-agent-loop-the-core-architecture-behind-autonomous-ai-systems
- https://www.moxo.com/blog/agentic-ai-strategy

## Related
- [[projects/LiveCode/research/20260327-omc-live-autonomous-ai-research-2025-2026|20260327-omc-live-autonomous-ai-research-2025-2026]]
- [[projects/LiveCode/research/20260328-omc-live-infinite-loop-architecture-research|20260328-omc-live-infinite-loop-architecture-research]]
- [[projects/LiveCode/research/20260326-omc-live-skill-critique|20260326-omc-live-skill-critique]]
- [[projects/LiveCode/research/20260326-omc-live-self-evolving-outer-loop|20260326-omc-live-self-evolving-outer-loop]]
- [[projects/LiveCode/research/20260325-autonomous-agent-goal-update-subloop-architecture|20260325-autonomous-agent-goal-update-subloop-architecture]]
