# [expert-research] omc-live 과학 연구 / 고전문 분야 확장성
**Date**: 2026-03-28  **Skill**: expert-research (lean protocol) + research-explore + multi-lens

## Original Question
omc-live infinite loop를 과학적 실험/연구 논문 자동화 및 고차원/고전문 분야(의학, 법률, 양자컴퓨팅 등)에 적용할 때의 확장성과 한계.

## Web Facts

- [FACT-1] AI Scientist-v2 (arXiv:2504.08066, Sakana AI, Apr 2025): End-to-end agentic system. Progressive agentic tree-search. 최초 AI 완전 자동 생성 peer-review 통과 논문. 평균 리뷰 점수 6.33 (상위 45%). Human-authored code template 불필요. (source: https://arxiv.org/abs/2504.08066)
- [FACT-2] Kosmos (arXiv:2511.02824, Edison Scientific, Nov 2025): 12시간 실행, 200 agent rollouts, 42,000 코드 라인, 1,500 논문 읽기/run. 20 사이클 ≈ 6개월 연구 노력. 정확도 79.4% (= 오류율 20.6%). $200/run, 30K 사용자. (source: https://arxiv.org/abs/2511.02824)
- [FACT-3] AI-Researcher (NeurIPS 2025 Spotlight, HKUDS): Production-ready 자율 과학 혁신 시스템. novix.science 운영. (source: https://github.com/HKUDS/AI-Researcher)
- [FACT-4] Jr. AI Scientist (arXiv:2511.04583): 과학 도메인 특화 hallucination 위험 보고서 포함. (source: https://arxiv.org/abs/2511.04583)
- [FACT-5] Quantum Computing Multi-Agent (arXiv:2601.10194): 텐서 네트워크 시뮬레이션 90% 성공. Ground-state, open quantum dynamics, photochemical reactions 커버. (source: https://arxiv.org/abs/2601.10194)
- [FACT-6] Drug Discovery Agents (arXiv:2510.27130, Oct 2025): J&J, Moderna 생산 배포. 수개월 다학제 협업 → 2시간으로 압축. Pre-clinical 단계 특화. (source: https://arxiv.org/abs/2510.27130)
- [FACT-7] Medical AI Regulation: EMA (Mar 2025) AI 방법론 첫 qualification opinion. EU AI Act 고위험 조항 2026년 8월 발효. (source: https://www.fdli.org/2025/07/regulating-the-use-of-ai-in-drug-development-legal-challenges-and-compliance-strategies/)
- [FACT-8] Materials Science Agent (arXiv:2512.19458): 물리적 일관성 보장하는 도메인 특화 에이전트. 제1원리 계산 자동화. (source: https://arxiv.org/abs/2512.19458)

## Multi-Lens Analysis

### Domain Analysis (Lens 1)

**구조적 동형 (Isomorphism)**
omc-live outer loop ↔ Scientific research cycle:
- Goal elevation = Hypothesis refinement
- Score = Evaluation metric (p-value, benchmark accuracy, effect size)
- Evolve 3 candidates = Parallel experimental arms / ablation
- Plateau convergence = Stopping rule (statistical significance)
- episodes.jsonl = Lab notebook (trajectory log)

[GROUNDED] 구조적 매핑 강도 HIGH. 핵심 갭: omc-live scoring은 객관적으로 계산 가능한 출력을 전제. 과학에서는 도메인별 검증 오라클 필요.

[REASONED] Kosmos vs omc-live 핵심 차이: Kosmos world model은 epistemic state ("X를 시도했고, Y 결과 → Z 가능성 낮음")를 추적. omc-live episodes.jsonl은 단순 trajectory log. 연구 자동화에서 이 차이가 결정적.

**도메인 확장성 점수 (5점 척도)**
- ML/CS 연구: 5.0 / 5
- 재료과학: 3.8 / 5 (물리 법칙을 hard constraint로 적용)
- 양자컴퓨팅: 3.8 / 5 (ground truth 존재 → hallucination-free scoring)
- 퀀트 금융: 3.6 / 5 (backtesting oracle 존재)
- 약물 발굴 (전임상): 3.0 / 5 (생산 사례 있음, 독성 검증 인간 필수)
- 임상 의학: 1.6 / 5
- 법률: 1.6 / 5

### Self-Critique (Lens 2)

[OVERCONFIDENT] AI Scientist-v2 "peer-review 통과" = Workshop level (상위 45%), NeurIPS/ICML main track (상위 25%) 아님. 이는 중요한 구분.

[OVERCONFIDENT] FACT-6의 "수개월 → 2시간" 주장은 physical experiment 자체가 아니라 literature synthesis + protocol generation에만 해당. Physical experiment는 여전히 수일-수년 소요.

[MISSING] Knowledge Boundary Problem: 미발표 negative results에 접근 불가. Kosmos의 1,500 논문/run으로도 lab tacit knowledge 획득 불가. 에이전트가 체계적으로 dead end를 재발견할 위험.

[MISSING] Async execution: omc-live inner loop은 동기 실행 전제. 과학 실험은 비동기 (수 시간~수 개월) → 현재 아키텍처 적용 불가.

### Synthesized Answer (Lens 3)

**가장 중요한 단일 숫자: 20.6% (Kosmos 오류율)**
- ML 연구: 허용 (벤치마크 실패로 자기수정)
- 약물 발굴: 위험 (1/5 프로토콜 오류)
- 임상 의학: 허용 불가 (의료 안전 기준 대비 10-100배 높음)

## Final Conclusion

### 도메인 분류

| 분야 | 분류 | 조건 |
|---|---|---|
| ML/CS 연구, 생물정보 | ✅ 즉시 적용 | config 변경만 |
| 재료과학, 양자컴퓨팅, 퀀트 금융 | ⚠️ 조건부 | 도메인 oracle + 검증 API |
| 약물 발굴 (전임상) | ⚠️ 조건부 | 독성/합성 단계 인간 QA 필수 |
| 임상 의학, 법률 | ❌ 비권장 | 오류율 + EU AI Act (2026.08) |

### omc-live → Research Agent 최소 수정 3가지

1. **Async Execution Adapter**: execute phase 비동기화 + job queue + callback
2. **Epistemic State Layer**: episodes.jsonl → world model (Kosmos 패턴)
3. **Domain-Specific Scoring Oracle**: 도메인별 전문가 작성 scoring 교체

### 다음 스텝

- **즉시 (1-2주)**: ML 연구 논문 자동화 프로토타입 (NeurIPS/ICLR workshop 타겟)
  - arXiv API 연동 + 3회 독립 재현 검증 추가
  - omc-live 강점: failure pattern 재사용 + Zettelkasten memory
- **1-2개월**: 교육 커리큘럼 자동 설계 파일럿 (규제 없음, 학습 성과로 수렴 판정)
- **6개월+**: 재료과학 / 양자 알고리즘 자동화 (외부 시뮬레이션 API 연동)

## Sources
- [AI Scientist-v2](https://arxiv.org/abs/2504.08066)
- [Kosmos](https://arxiv.org/abs/2511.02824)
- [AI-Researcher NeurIPS 2025](https://github.com/HKUDS/AI-Researcher)
- [Quantum Computing Multi-Agent](https://arxiv.org/abs/2601.10194)
- [Drug Discovery Agents](https://arxiv.org/abs/2510.27130)
- [Materials Science Agent](https://arxiv.org/abs/2512.19458)
- [AI Medical Devices Regulation 2025](https://intuitionlabs.ai/articles/ai-medical-devices-regulation-2025)

## Related
- [[projects/LiveCode/research/20260330-omc-live-critique|20260330-omc-live-critique]]
- [[projects/LiveCode/research/20260326-omc-live-skill-critique|20260326-omc-live-skill-critique]]
- [[projects/LiveCode/research/20260326-omc-live-self-evolving-outer-loop|20260326-omc-live-self-evolving-outer-loop]]
- [[projects/LiveCode/research/20260328-omc-live-infinite-loop-architecture-research|20260328-omc-live-infinite-loop-architecture-research]]
- [[projects/LiveCode/research/20260325-omc-live-patch-critique|20260325-omc-live-patch-critique]]
- [[projects/LiveCode/research/20260330-hypothesis-experiment-results|20260330-hypothesis-experiment-results]]
- [[projects/LiveCode/research/20260327-omc-live-git-checkpoint-self-evolving-research|20260327-omc-live-git-checkpoint-self-evolving-research]]
