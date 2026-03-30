# [expert-research-v2] 가설 기반 사고 vs 엔지니어링적 사고 — 난제 해결 실효성 연구
**Date**: 2026-03-30  **Skill**: expert-research-v2

## Original Question
"엔지니어링적 사고만으로는 난제를 해결할 수 없다. 과학자적 가설 기반 사고가 난제를 해결할 수 있다"
— 이미 연구된 사실인가? 자율 진화 하네스 프로젝트에 적용 가능한가?

## Web Facts
[FACT-1] SWE-Bench Verified (2025.03): Claude Opus 4.5 최고 0.809, 평균 0.622 (source: llm-stats.com)
[FACT-2] SWE-Bench++: SOTA 모델 실패의 주요 원인 = "잘못된 가정" (yamllint: 토큰이 전처리됐다고 암묵 가정 → 실제 raw 버퍼) (source: arxiv.org/2512.17419)
[FACT-3] HypoBench: 가설 기반 최대 38% 복구율. 어려울수록 급락. O3도 완전 불가 (source: openreview.net)
[FACT-4] Literature + Data 결합이 real-world 데이터셋 최고 성능 — 순수 데이터(엔지니어링)보다 우수 (source: openreview.net)
[FACT-5] BioVerge Generation-Evaluation 루프 → 가설 신규성·관련성 현저히 개선 (source: arxiv.org/2511.08866)
[FACT-6] 순차 몬테카를로 기반 가설 가중치 부여 → 복잡 멘탈 추론 개선 (source: arxiv.org/2502.11881)
[FACT-7] 특성 발견(FDR) 근 완벽 but 관계 추론(RC)은 중간 수준 — "어떻게 연결"이 병목 (source: openreview.net)
[FACT-8] Double Agent(분리 메모리) = 다양한 탐색. Single Agent = 비용 효율. 명시적 트레이드오프 (source: arxiv.org/2511.08866)

## Final Conclusion
(see below)

## Sources
- https://arxiv.org/abs/2512.17419 (SWE-Bench++)
- https://openreview.net/pdf?id=cizEoSePyT (HypoBench)
- https://arxiv.org/pdf/2511.08866 (BioVerge Agent)
- https://arxiv.org/abs/2502.11881 (Hypothesis-Driven ToM)
- https://llm-stats.com/benchmarks/swe-bench-verified
