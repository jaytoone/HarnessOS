# [전문 평론] omc-live / omc-live-infinite 스킬 평론
**Date**: 2026-03-30

## 총평 (Executive Summary)

omc-live와 omc-live-infinite는 LLM 기반 자율 에이전트 아키텍처 중에서 가장 정교하게 설계된 자가 진화 외부 루프(self-evolving outer loop) 중 하나다. 특히 Novelty Escape, Pareto 수렴, HER(Hindsight Experience Replay) 등 강화학습 연구에서 입증된 메커니즘을 LLM 에이전트 루프에 체계적으로 통합한 점은 2026년 기준 동종 시스템 대비 기술적 선도성을 갖는다. 그러나 **자기 평가 편향(self-evaluation bias)에 대한 구조적 해결이 불완전**하고, **수렴 기준이 단일 스칼라 평균에 과도하게 의존**하며, **컨텍스트 오염에 대한 방어가 auto-compact에 전적으로 위임**되어 있다는 점에서 실전 운영 시 거짓 수렴(false convergence)과 품질 퇴행(quality regression)의 위험이 존재한다. omc-live-infinite는 omc-live의 논리적 확장이지만, 추가된 복잡성(World Model, Novelty Escape, Pareto 벡터, HER) 대비 실증적 개선 근거가 아직 부족하며, 특히 세션 간 상태 직렬화의 신뢰성이 시스템 전체의 단일 실패점(single point of failure)이 될 수 있다.

---

## 1. 강점 분석

### 1.1 연구 기반의 체계적 설계

두 스킬 모두 학술 논문을 명시적으로 인용하며 설계 결정을 정당화한다. AI Scientist-v2 (arXiv:2504.08066), Agent0 (arXiv:2511.16043), SE-Agent (NeurIPS 2025), A-MEM (arXiv:2502.12110), POET (arXiv:1901.01753) 등 다양한 분야의 연구를 참조한다. 이는 단순 경험적 설계가 아닌 이론적 근거에 기반한 아키텍처임을 보여준다.

### 1.2 다중 안전장치 (Defense-in-Depth)

- **정렬 검사(Alignment Check)**: 반복 2부터 매 반복 전 original_goal과의 의미적 정렬 점검
- **Goal Fidelity Gate**: goal_fidelity < 0.7이면 EVOLVE를 차단하고 plateau로 처리
- **Score Ensemble**: 3회 독립 채점 후 평균으로 단일 호출 분산 감소
- **적응적 재표본(Adaptive Resampling)**: 분산 > 0.15면 2배 앙상블 재실행
- **Score Uncertain Flag**: 높은 분산이 지속되면 plateau_count 증가를 건너뜀
- **CONVERGED_STALE 분류**: 수렴했으나 품질이 낮으면 별도 경로로 처리
- **Git 체크포인트**: 매 반복 커밋으로 안전한 롤백 보장

이 다중 안전장치는 Anthropic의 하네스 설계 원칙("제약 + 피드백 루프 + 검증 + 수정") [FACT-1, FACT-2]과 일맥상통한다.

### 1.3 확장 가능한 도메인 프로파일

domain-profile.md 템플릿을 통해 ML 연구, 약물 탐색, 재료과학 등 다양한 도메인으로 확장 가능하다. Score Dimensions, Score Oracle, Convergence Rule의 3-섹션 구조는 간결하면서도 유연하다. 특히 Auto Oracle Detection(pytest/npm test 자동 탐지)은 사용자 설정 없이도 측정 가능한 차원에 대해 객관적 점수를 확보하는 실용적 해법이다.

### 1.4 실패 학습 체계

Cross-trajectory recombination (SE-Agent 영감)과 Failure Taxonomy (Tier 1/2/3 분류)는 단순 성공/실패 이진 분류를 넘어 실패의 구조적 재활용을 가능하게 한다. Zettelkasten episode linking도 에피소드 메모리를 단순 로그가 아닌 지식 그래프로 발전시키는 방향성을 보여준다.

### 1.5 omc-live-infinite 고유 강점

- **Novelty Escape Protocol**: POET/Novelty Search의 핵심 통찰을 LLM 목표 진화에 적용. plateau 시 즉시 수렴 선언이 아닌 행동적 거리(behavioral distance)가 먼 목표를 시도하는 것은 지역 최적해 탈출의 정석.
- **Pareto 벡터 수렴**: 총합 스칼라가 아닌 모든 차원의 동시 정체를 확인해야 수렴으로 판단. 단일 차원 개선이 총합에 묻히는 문제를 방지.
- **HER (Hindsight Experience Replay)**: 전체적으로 정체한 반복에서도 부분적 개선을 추출하여 다음 목표 진화의 힌트로 사용. 비직관적이지만 강화학습에서 검증된 기법.

---

## 2. 약점 및 리스크

### 2.1 자기 평가 편향의 구조적 미해결 (Critical)

스킬 문서는 "Claude 기반 평가자가 자기 출력을 -7.4% 과소 평가한다"는 연구를 인용하며 앙상블로 분산을 줄인다고 주장한다. 그러나 이는 핵심 문제를 회피한다:

- **동일 모델 앙상블은 체계적 편향(systematic bias)을 교정하지 못한다.** 3회 호출의 평균은 랜덤 노이즈만 줄일 뿐, 모든 호출이 공유하는 방향성 편향은 그대로 남는다. 최근 연구에 따르면 LLM은 자기 생성물에 대해 self-preference bias를 보이며, "강한 모델일수록 오류 시 과대 평가가 심하다" (Diagnosing Bias and Instability in LLM Evaluation, 2025).
- **Anthropic 자체가 "자기 평가는 중재 품질의 작업을 자신감 있게 칭찬하는 경향"이 있다고 경고**하며, Generator/Evaluator 분리를 핵심 해법으로 제시했다. omc-live는 이 분리를 수행하지 않는다 -- 동일 세션의 동일 모델이 생성과 평가를 모두 수행한다.
- **Auto Oracle이 부분적 해결책**이지만, pytest 통과율과 커버리지로 측정 가능한 것은 completeness/impact뿐이다. quality, efficiency, goal_fidelity는 여전히 LLM 자기 채점에 의존한다.

**권고**: 최소한 평가 시 다른 모델(cross-model evaluation)을 사용하거나, 구조적으로 Evaluator 에이전트를 분리하는 것을 고려해야 한다. 스킬 문서 자체가 "cross-model diversity는 p=0.12로 유의하지 않다"고 주장하지만, 이는 분산 감소에 대한 것이지 방향성 편향 교정과는 다른 문제다.

### 2.2 수렴 기준의 취약성 (High)

**plateau_k=2(live) / 5(infinite)의 허위 수렴 위험:**

- plateau_k=2는 단 2회 연속 epsilon 미만 개선만으로 수렴을 선언한다. LLM 채점의 분산을 고려하면 이는 매우 공격적이다. 실제로 score_variance > 0.15일 때 score_uncertain_flag로 plateau_count 증가를 건너뛰는 보호 장치가 있지만, variance가 0.10-0.14 사이(보호 임계치 미만이지만 여전히 높은 불확실성)인 경우 거짓 수렴 위험이 존재한다.
- **epsilon=0.05의 의미**: 0.05 미만 개선을 "무의미"로 간주하지만, 0.80에서 0.84로의 개선(delta=0.04)과 0.30에서 0.34로의 개선(delta=0.04)은 질적으로 완전히 다르다. 절대 epsilon이 아닌 상대 개선율(relative improvement)을 고려해야 할 수 있다.
- **omc-live-infinite의 plateau_k=5**는 더 보수적이지만, Pareto 수렴과 스칼라 수렴이 동시에 적용되는 로직에서 어느 것이 우선하는지 불명확하다. Step 6b에서 pareto_improved=true이면 plateau_count=0으로 리셋하는 로직이 Step 6a의 스칼라 기반 plateau 로직과 충돌할 가능성이 있다.

### 2.3 목표 진화의 정렬 불안정성 (Medium-High)

- **goal_fidelity_min=0.7은 관대한 임계치**다. 원래 목표와 70% 정렬만 유지되면 진화가 허용된다는 것은, 3회 진화(max_evolution_depth=3) 후 누적 표류(cumulative drift)가 상당할 수 있음을 의미한다. 각 단계에서 0.7 정렬이면 3단계 후 이론적으로 0.7^3 = 0.343 수준의 원래 목표 정렬만 남을 수 있다(실제로는 선형적 표류가 아니지만 위험은 실재한다).
- **Alignment Check (Step 3a)는 반복 2부터만 실행**된다. 첫 번째 진화 직후에는 검사되지 않는다.
- LlamaFirewall (arXiv:2505.03574)와 Goal Drift (arXiv:2505.02709) 연구를 인용하지만, 이 연구들은 "모든 LLM이 장기 실행에서 표류를 보인다"고 결론 내린다. omc-live의 방어는 LLM 기반 정렬 점수에 의존하므로, 표류를 탐지하는 도구 자체가 표류에 취약한 순환적 약점이 있다.

### 2.4 컨텍스트 관리의 과도한 위임 (Medium)

- **omc-live**: context_budget_pct=70에서 조기 핸드오프. 이는 수동 재시작을 요구하며, 세션 간 상태 손실 위험이 있다.
- **omc-live-infinite**: auto-compact에 전적으로 의존하고 90%에서만 비상 회전. 스킬 문서는 "Claude Code /compact가 자동으로 압축한다"고 가정하지만:
  - auto-compact는 **손실(lossy) 압축**이다. 반복 3의 세부 실패 패턴이 반복 8에서 필요할 때 이미 압축으로 소실되었을 수 있다.
  - JetBrains 연구 (2025.12)에 따르면, 65%의 기업 AI 실패가 컨텍스트 고갈(exhaustion)이 아닌 **컨텍스트 표류(context drift)와 메모리 손실**에 기인한다.
  - Anthropic 자체 엔지니어링 블로그에서 "Sonnet 4.5는 컨텍스트 불안(context anxiety)을 강하게 보여 compaction만으로는 불충분했다"고 보고했다. 이에 따라 **전체 리셋(context reset)이 compaction보다 효과적**이라고 결론 내렸다.
  - omc-live-infinite의 world-model.json이 영속 상태를 보존하지만, 이것이 컨텍스트 내 추론 품질 저하를 대체할 수는 없다.

### 2.5 내부 루프(Autopilot) 실패 처리의 불투명성 (Medium)

omc-autopilot을 블랙박스로 호출하고 결과만 수신한다. 구체적으로:
- autopilot이 Phase 3에서 실패하면 omc-failure-router로 분류되지만, omc-live가 이 분류 결과를 어떻게 활용하는지 명확하지 않다.
- "Post-execution extraction"에서 autopilot_summary를 "autopilot의 최종 상태 메시지에서 추출"하라고 하지만, autopilot이 크래시하면 요약이 없을 수 있다.
- autopilot 재시도 전략이 없다. 동일 목표로 다시 autopilot을 호출하면 동일한 실패를 반복할 가능성이 높다(idempotent failure).

### 2.6 비용 추적의 명세적 허구성 (Low-Medium)

cost_history에 relative_cost를 기록하도록 명세하지만, 실제로 LLM API 호출 비용을 실시간으로 추적하는 메커니즘이 없다. 스킬 문서 자체가 "DA MAJOR: cost_history는 실제 배포에서 명세적 허구(spec fiction)"라고 인정한다. 이는 cost-aware convergence 로직이 사실상 작동하지 않음을 의미한다.

---

## 3. 외부 시스템 대비 포지셔닝

### 3.1 vs Anthropic Long-Running Harness (3-Agent Architecture)

| 차원 | Anthropic Harness | omc-live/infinite |
|------|-------------------|-------------------|
| 평가 분리 | Generator/Evaluator 완전 분리 | 동일 모델 자기 평가 (앙상블) |
| 컨텍스트 관리 | 전체 리셋 + 구조화된 핸드오프 | auto-compact 의존 / 비상 회전 |
| 품질 검증 | Playwright E2E 테스트 (하드 pass/fail) | LLM 판정 + 선택적 auto-oracle |
| 스프린트 계약 | 코드 작성 전 "완료" 정의 합의 | reward_spec 존재하나 형식적 |
| 비용 | 6시간, $200 (고비용 고품질) | 비용 추적 미구현 |

**핵심 차이**: Anthropic은 "자기 평가는 실패한다"는 전제에서 출발하여 구조적으로 평가자를 분리했다. omc-live는 "앙상블로 편향을 관리할 수 있다"는 전제에서 출발한다. 2025-2026 연구 동향은 Anthropic의 접근이 더 견고함을 시사한다.

### 3.2 vs AutoResearchClaw (23-Stage Pipeline)

| 차원 | AutoResearchClaw | omc-live/infinite |
|------|------------------|-------------------|
| 파이프라인 깊이 | 23단계 고정 파이프라인 | 유연한 반복 루프 |
| 다중 관점 | Innovator/Pragmatist/Contrarian 토론 | 단일 모델 채점 + 탐색 분기 |
| 실패 학습 | MetaClaw 교차 실행 학습 (30일 감쇠) | Failure Taxonomy (Tier 1/2/3) + 에피소드 메모리 |
| 자가 치유 | Pivot/Refine 자동 결정 | Transient/Persistent/Fatal 분류 |
| 확장성 | 연구 특화 (논문 작성 목적) | 범용 (도메인 프로파일로 확장) |

**핵심 차이**: AutoResearchClaw의 3-에이전트 토론은 다중 관점을 구조적으로 보장하는 반면, omc-live는 단일 모델의 exploration_rate로 다양성을 확률적으로만 추구한다. 그러나 omc-live의 범용성(도메인 프로파일)은 AutoResearchClaw보다 우위다.

### 3.3 vs OpenAI Harness Engineering (Codex)

| 차원 | OpenAI Codex Harness | omc-live/infinite |
|------|---------------------|-------------------|
| 제약 방식 | 커스텀 린터 + 구조적 테스트 + 맛 불변량 | reward_spec + goal_fidelity_min |
| 피드백 루프 | 자기 리뷰 + 에이전트 리뷰 + 인간 피드백 반복 | LLM 판정 + Score 앙상블 |
| 규모 | 주당 1,300 PR (Stripe Minions) | 단일 태스크 반복 최적화 |
| 인간 시간 제약 | "인간 시간이 고정 제약" 명시적 설계 | evolve_mode=true면 인간 개입 최소화 |

**핵심 차이**: OpenAI는 "에이전트의 판단이 아닌 도구의 출력을 신뢰한다" -- 커스텀 린터의 에러 메시지가 수정 지시를 직접 주입한다. omc-live는 LLM 판단에 더 많이 의존한다. Stripe Minions의 성공 요인인 "좁은 작업 설계 + 샌드박스 격리" [FACT-6]는 omc-live의 "넓은 목표 + 자가 진화" 접근과 대조적이다.

### 3.4 vs POET / Novelty Search (학술 알고리즘)

omc-live-infinite의 Novelty Escape는 POET의 핵심 아이디어를 차용했으나 중요한 차이가 있다:

- **POET**: 환경과 에이전트의 **공동 진화(co-evolution)** -- 환경이 점진적으로 어려워지면서 에이전트도 함께 성장. 전이 학습(transfer)으로 한 환경의 해법이 다른 환경으로 전파.
- **omc-live-infinite**: 목표만 진화하고 에이전트(autopilot)는 고정. "목표 난이도가 증가해도 도구 능력은 변하지 않는다"는 비대칭이 존재한다.
- **Novelty 측정**: POET는 행동 공간에서의 거리를 정량적으로 계산하지만, omc-live-infinite는 "tried_strategy와 50% 이상 겹치면 재생성"이라는 **LLM 기반 정성적 유사도**에 의존한다. 이는 novelty 측정의 재현성과 객관성을 보장하지 못한다.

---

## 4. 차원별 세부 평론 (A~G)

### A. 수렴 기준 (Convergence Criteria)

**현행**: plateau_k=2(live) / 5(infinite), epsilon=0.05, 단일 스칼라 total score 기반.

**평가**:
- **거짓 수렴(false convergence)**: plateau_k=2는 지나치게 공격적이다. LLM 채점 분산이 0.05-0.10 범위에서도 2회 연속 "개선 없음"은 통계적으로 무의미할 수 있다. score_uncertain_flag가 분산 > 0.15에서만 작동하므로, 0.10-0.14 범위의 "회색 지대"가 보호받지 못한다.
- **거짓 비수렴(false non-convergence)**: 반대로, 실제로 최적에 도달했지만 LLM 채점 노이즈로 매 반복 미세한 점수 변동이 있으면 수렴을 선언하지 못하고 불필요한 반복이 계속될 수 있다. omc-live-infinite에서 이 위험이 특히 크다(무한 반복이므로).
- **Pareto 수렴(infinite만)**: 훨씬 견고한 기준이지만, Step 6b의 Pareto 로직과 Step 6a의 스칼라 로직 간 우선순위가 불명확하다.

**권고**: (1) plateau_k를 최소 3(live) / 7(infinite)로 상향. (2) epsilon을 점수 수준에 따라 적응적으로 조정 (예: current_score < 0.5이면 epsilon=0.10, > 0.8이면 epsilon=0.03). (3) Pareto와 스칼라 수렴의 관계를 "Pareto가 스칼라를 override" 또는 "AND 조건"으로 명확히 정의.

### B. 점수화 시스템 (Scoring System)

**현행**: quality/completeness/efficiency/impact/goal_fidelity 5차원, 동등 가중 평균.

**평가**:
- **차원 정의 모호성**: "quality"와 "completeness"의 경계가 불분명하다. 테스트가 전부 통과하면 completeness인가 quality인가? "impact"는 사용자 가치인가 코드 범위인가?
- **동등 가중의 문제**: 모든 차원에 동일 가중치를 부여하는 것은 도메인 무관한 단순화다. 도메인 프로파일로 차원을 재정의할 수 있지만 가중치는 재정의할 수 없다.
- **Auto Oracle의 편향적 매핑**: test_pass_rate를 completeness로, coverage를 impact로 매핑하는 것은 자의적이다. 100% 테스트 통과율이 반드시 "완전성"을 의미하지 않는다 (테스트 자체가 불완전할 수 있다).
- **앙상블 한계**: 앞서 논의했듯이 동일 모델 앙상블은 분산만 줄이고 방향성 편향은 유지한다. 스킬 문서가 인용하는 AI Scientist-v2의 "balanced accuracy 69%"는 사실 인간 리뷰어 수준(inter-human consistency)과 비교한 것이지 절대 정확도가 아니다.

**권고**: (1) 차원별 가중치를 설정 가능하게. (2) quality → code_quality, completeness → requirement_coverage 등 더 구체적 명칭 사용. (3) 가능한 모든 차원에 결정론적 oracle을 확보하고 LLM 채점 의존도를 최소화.

### C. 목표 진화 (Goal Evolution)

**현행**: 3-후보 생성 + Look-ahead 가지치기 + 약한 차원 기반 + 탐색 분기.

**평가**:
- **강점**: AI Scientist-v2의 progressive tree-search를 잘 적용했다. 3-후보 병렬 생성 후 가지치기는 단일 진화보다 견고하다. Look-ahead의 dimension_fit * 0.5 + novelty * 0.3 + feasibility * 0.2 가중치는 합리적이다.
- **약점 1 -- 누적 표류**: 앞서 언급한 대로, goal_fidelity_min=0.7의 3회 누적 적용 시 원래 목표와의 정렬이 크게 약화될 수 있다. Alignment Check(Step 3a)가 이를 사후 검출하지만, **진화를 허용한 후에 탐지**하는 것이므로 이미 1회분의 autopilot 비용이 낭비될 수 있다.
- **약점 2 -- 탐색률 조정의 과적합 위험**: score_variance 기반 exploration_rate 동적 조정은 이론적으로 타당하지만, score_variance 자체가 LLM 채점의 잡음을 반영하므로 잡음에 기반한 탐색 결정이 될 수 있다.
- **약점 3 -- success_patterns의 활용 불명확**: "Goal elevation targets areas BEYOND current success patterns"이라고 하지만, 이 "beyond"를 어떻게 측정하는지 구체적 로직이 없다.

### D. 에피소드 메모리 (Episode Memory)

**현행**: episodes.jsonl + world-model.json (infinite만) + TF-IDF 유사도 검색.

**평가**:
- **강점**: TF-IDF 코사인 유사도를 통한 관련 에피소드 검색은 간단하지만 효과적이다. Cross-trajectory recombination (실패 에피소드에서도 교훈 추출)은 MetaClaw의 교차 실행 학습과 유사한 접근이다. Zettelkasten linking은 에피소드 간 관계를 명시적으로 추적한다.
- **약점 1 -- 메모리 오염**: episodes.jsonl에 저장된 에피소드의 품질이 일정하지 않다. CONVERGED_STALE로 종료된 저품질 에피소드도 동일한 가중치로 검색된다. high_quality 플래그가 있지만 검색 시 이를 어떻게 활용하는지 명시되지 않았다.
- **약점 2 -- 시간 감쇠 없음**: AutoResearchClaw의 MetaClaw는 30일 시간 감쇠를 적용한다. omc-live의 에피소드 메모리에는 시간 감쇠가 없어 오래된 (더 이상 관련 없는) 에피소드가 검색 결과를 오염시킬 수 있다.
- **약점 3 -- World Model의 확장성**: tried_strategies 배열이 무한히 성장한다. 100회 이상 반복 시 JSON 파일 크기와 검색 효율성 문제가 발생할 수 있다.

### E. 내부 루프 품질 (Inner Loop -- Autopilot)

**현행**: omc-autopilot을 Phase 0-5 블랙박스로 호출.

**평가**:
- **강점**: 관심사 분리(separation of concerns)가 명확하다. 외부 루프는 "무엇을 할 것인가"에, 내부 루프는 "어떻게 할 것인가"에 집중한다.
- **약점 1 -- 재시도 전략 부재**: autopilot이 같은 이유로 반복 실패하면 omc-live는 "NO → GoalTree Level 1 update → loop again"으로 동일한 구조를 반복한다. 실패 원인이 목표가 아닌 구현 전략에 있을 때 GoalTree 업데이트는 무의미하다.
- **약점 2 -- Phase 정보 활용 미흡**: autopilot이 Phase 3(구현)에서 실패한 것과 Phase 4(검증)에서 실패한 것은 질적으로 다르지만, omc-live는 둘 다 "failure"로 동일하게 처리한다.
- **약점 3 -- autopilot 크래시 복구**: autopilot이 중간에 크래시하면 autopilot_summary 추출이 실패하고, 이후 SCORE PROMPT에 "N/A"가 입력된다. 이 상태에서의 채점 신뢰성은 매우 낮다.

### F. 컨텍스트 관리 (Context Management)

**현행**: omc-live는 70%에서 조기 핸드오프, omc-live-infinite는 auto-compact 의존 + 90% 비상 회전.

**평가**:
- **omc-live의 70% 핸드오프**: 합리적이지만, 핸드오프 후 수동 재시작이 필요하므로 "완전 자율"이라는 약속과 모순된다.
- **omc-live-infinite의 auto-compact 의존**: Anthropic Claude Code의 /compact이 자동으로 컨텍스트를 압축한다는 가정에 기반하지만:
  - auto-compact의 정확한 작동 조건과 품질이 외부에서 제어 불가
  - 압축 후 중요 정보 손실 여부를 검증하는 메커니즘이 없음
  - 최근 연구(Zylos AI, 2026.02)에 따르면 "context rot zone"은 모델 컨텍스트 한계의 약 25% 이전부터 시작될 수 있다
  - "맥락 표류(context drift)" 문제는 토큰 수가 아닌 추론 품질의 점진적 저하로 나타나므로, 토큰 수 기반 체크만으로는 감지 불가
- **World Model이 부분적 해결**: world-model.json이 핵심 상태를 영속화하므로 auto-compact으로 세션 내 맥락이 손실되더라도 구조적 정보는 보존된다. 그러나 "왜 이 전략이 실패했는지"의 뉘앙스는 JSON 필드로 포착되지 않는다.

**권고**: (1) 반복 N의 핵심 결정과 교훈을 world-model.json에 구조화하여 auto-compact 손실에 대비. (2) 반복 시작 시 이전 반복의 핵심 맥락을 world-model에서 재주입하는 "context priming" 단계 추가. (3) Anthropic 권고대로 주기적 전체 리셋(매 K 반복마다)을 고려.

### G. 실용성 (Practicality)

**현행**: 완전 자율, 사용자 개입은 UNCERTAIN/FATAL/ALIGNMENT_FAIL/DEAD_ENDS 시에만.

**평가**:
- **강점**: infinite-stop.txt 파일로 비침습적 정지 신호를 지원하는 것은 실용적이다. ESC 복구 프로토콜도 실전적이다.
- **문제 1 -- 장시간 무응답**: omc-live-infinite가 정상 작동 중이면 사용자에게 어떤 피드백도 없이 수 시간 동안 실행될 수 있다. 진행 상황 모니터링 메커니즘(대시보드, 로그 스트리밍)이 없다.
- **문제 2 -- 실행 비용 불투명**: cost_history가 명세적 허구이므로, 사용자는 10회 반복 후 얼마의 API 비용이 발생했는지 알 수 없다. Anthropic 하네스의 $200/6시간 같은 비용 가시성이 없다.
- **문제 3 -- 목표 진화의 사용자 가시성**: 사용자가 "테스트 작성"을 요청했는데, 3회 진화 후 목표가 "성능 프로파일링 및 벤치마크 자동화"로 변할 수 있다. Alignment Check가 이를 탐지하지만, 사용자에게 진화 과정을 실시간으로 보여주는 메커니즘이 약하다.
- **문제 4 -- 복구 시나리오**: Git 체크포인트로 롤백은 가능하지만, "어느 반복이 최적이었는지"를 사용자가 판단해야 한다. best_score 기준의 자동 복구 메커니즘이 없다.

---

## 5. omc-live vs omc-live-infinite 비교

### 5.1 적절한 사용 시나리오

| 시나리오 | 적합한 스킬 | 이유 |
|----------|------------|------|
| 버그 수정 + 테스트 추가 | omc-live | 5회 이내 완료 가능, 비용 제한 필요 |
| 새 기능 구현 + 리팩토링 | omc-live | max_evolution_depth=3이면 충분 |
| 코드베이스 전체 품질 향상 | omc-live-infinite | 다차원 동시 개선 필요, Pareto 수렴 유용 |
| 연구 프로토타입 최적화 | omc-live-infinite | 수렴까지 반복 수 예측 불가, Novelty Escape 유용 |
| 비용 민감 프로젝트 | omc-live | 반복 상한으로 비용 제한 |
| 데드라인 있는 프로젝트 | omc-live | 시간 제한과 반복 상한으로 종료 보장 |

### 5.2 omc-live-infinite의 실질적 이점

1. **Novelty Escape**: 지역 최적해에서 탈출 가능. omc-live는 plateau 시 즉시 수렴 선언하므로 더 나은 해가 인접 탐색 공간에 있어도 발견하지 못한다.
2. **Pareto 수렴**: 단일 차원이 개선되어도 전체 평균이 미미하게 변할 때, omc-live는 plateau로 판단하지만 infinite는 개선으로 인정한다. 이는 다차원 최적화에서 중요하다.
3. **World Model**: 세션 간 시도한 전략의 구조적 기록. omc-live의 에피소드 메모리보다 더 세밀한 추적이 가능하다.
4. **HER**: 전체적으로 정체한 반복에서도 부분적 개선을 활용하는 것은 강화학습에서 검증된 기법이다.

### 5.3 omc-live-infinite의 복잡성은 정당화되는가?

**부분적으로만 정당화된다.**

- **정당화되는 부분**: Novelty Escape와 Pareto 수렴은 개념적으로 건전하며, 장기 실행 시나리오에서 실질적 차이를 만들 수 있다. World Model은 세션 간 상태 보존의 핵심이다.
- **과잉 설계 우려**: HER는 이론적으로 우아하지만, LLM 기반 목표 진화에서 "부분적 개선"의 정의가 정밀하지 않아 실제 효과가 불확실하다. 또한 World Model의 tried_strategies가 무한히 성장하는 것에 대한 가비지 컬렉션이 없다.
- **복잡성 비용**: 추가된 5개 메커니즘(World Model, Novelty Escape, Pareto, HER, Context Rotation)은 각각이 새로운 실패 지점(failure point)을 추가한다. Anthropic의 하네스 설계 원칙 -- "모델이 향상되면 하네스 복잡도를 줄여라" -- 와 대조적이다.
- **실증 부재**: 이 복잡한 메커니즘들이 실제로 omc-live 대비 더 나은 결과를 산출한다는 실증 데이터가 스킬 문서에 제시되지 않았다. 벤치마크 비교 없이 이론적 이점만 제시된 상태다.

---

## 6. 개선 권고사항 (우선순위별)

### P0 (즉시)

1. **평가자 분리**: 최소한 채점 시 다른 모델을 사용하거나, 별도 세션에서 평가를 수행하는 옵션 추가. 현재의 동일-모델 앙상블은 분산만 줄이고 방향성 편향은 유지한다. 참조: Anthropic Generator/Evaluator 분리 아키텍처.

2. **수렴 임계치 상향**: plateau_k를 최소 3(live) / 7(infinite)로 상향. 분산이 0.10-0.14인 "회색 지대"에서도 score_uncertain_flag를 적용하거나, plateau_count 증가를 절반(+0.5)으로 감쇠.

3. **결정론적 Oracle 확대**: Auto Oracle의 매핑을 사용자가 재정의 가능하게. 또한 lint 결과, 빌드 성공, 타입 체크 등 추가 결정론적 신호를 Auto Oracle에 포함.

### P1 (단기)

4. **적응적 epsilon**: 점수 수준에 따라 epsilon을 동적 조정. 고점수 영역에서는 더 작은 개선도 의미있고, 저점수 영역에서는 더 큰 개선이 필요하다.

5. **컨텍스트 프라이밍**: 매 반복 시작 시 world-model.json에서 핵심 교훈과 금지 전략을 추출하여 autopilot 컨텍스트에 주입. auto-compact 손실에 대한 방어.

6. **진행 상황 모니터링**: .omc/live-progress.log에 반복별 점수, 목표, 소요 시간을 기록하여 사용자가 실시간으로 진행 상황을 확인 가능하게.

### P2 (중기)

7. **autopilot 재시도 전략 분화**: Phase별 실패에 따른 차별적 재시도. Phase 3 실패는 구현 전략 변경, Phase 4 실패는 검증 조건 완화 또는 부분 수정.

8. **goal_fidelity 누적 추적**: 각 진화 단계에서의 goal_fidelity를 누적 곱으로 추적하고, 누적 fidelity가 0.5 미만이면 강제 정지.

9. **World Model 가비지 컬렉션**: tried_strategies가 50건 초과 시 가장 오래되고 낮은 점수의 항목을 요약 후 아카이브.

### P3 (장기)

10. **교차 모델 평가**: 채점에 다른 모델(예: Gemini, GPT)을 사용하여 방향성 편향을 교정. 비용이 증가하지만 점수 신뢰도가 크게 향상된다.

11. **환경 공동 진화**: POET처럼 목표뿐 아니라 autopilot 자체의 능력(사용 가능한 도구, 전략 목록)도 함께 진화시키는 메커니즘.

12. **A/B 수렴 검증**: 수렴 선언 전 "반대 방향 1회 시도"를 자동 수행하여 진짜 수렴인지 지역 최적해인지 확인 (omc-live-infinite의 Novelty Escape가 이 방향이지만, 더 체계적으로).

---

## 7. 종합 점수

| 차원 | omc-live | omc-live-infinite | 비고 |
|------|----------|-------------------|------|
| A. 수렴 기준 | 6/10 | 7.5/10 | infinite의 Pareto 수렴이 더 견고. 둘 다 plateau_k 과소 |
| B. 점수화 시스템 | 5.5/10 | 5.5/10 | 동일 시스템 상속. 자기평가 편향 미해결이 공통 약점 |
| C. 목표 진화 | 7/10 | 8/10 | 3-후보 + Look-ahead 건전. Novelty Escape가 큰 이점 |
| D. 에피소드 메모리 | 6.5/10 | 7.5/10 | World Model이 구조적 기억 제공. 시간 감쇠 부재 공통 |
| E. 내부 루프 품질 | 5/10 | 5/10 | autopilot 재시도 전략 부재가 공통 약점 |
| F. 컨텍스트 관리 | 6/10 | 6.5/10 | auto-compact 의존 위험. World Model이 부분 보완 |
| G. 실용성 | 7/10 | 6/10 | live가 더 단순하고 예측 가능. infinite는 비용/시간 불투명 |
| **종합** | **6.1/10** | **6.6/10** | infinite가 이론적으로 우세하나 복잡성 비용 고려 필요 |

**종합 판정**: 두 스킬 모두 학술적으로 잘 설계된 자가 진화 에이전트 루프이며, 동종 오픈소스/상용 시스템 대비 높은 정교함을 보여준다. 그러나 **평가자 분리의 부재**가 전체 아키텍처의 가장 큰 구조적 약점이며, 이는 Anthropic과 OpenAI가 2025-2026년에 독립적으로 도달한 핵심 교훈("자기 평가는 신뢰할 수 없다")과 상충한다. 이 약점을 해결하면 종합 점수는 1-1.5점 상승할 것으로 예상된다.

---

## Sources

### 웹 리서치
- [Anthropic: Harness design for long-running application development](https://www.anthropic.com/engineering/harness-design-long-running-apps)
- [Anthropic: Effective harnesses for long-running agents](https://www.anthropic.com/engineering/effective-harnesses-for-long-running-agents)
- [Anthropic: Effective context engineering for AI agents](https://www.anthropic.com/engineering/effective-context-engineering-for-ai-agents)
- [OpenAI: Harness engineering](https://openai.com/index/harness-engineering/)
- [OpenAI: Unrolling the Codex agent loop](https://openai.com/index/unrolling-the-codex-agent-loop/)
- [OpenAI: Self-Evolving Agents Cookbook](https://cookbook.openai.com/examples/partners/self_evolving_agents/autonomous_agent_retraining)
- [JetBrains Research: Efficient Context Management](https://blog.jetbrains.com/research/2025/12/efficient-context-management/)
- [Zylos AI: AI Agent Context Compression Strategies](https://zylos.ai/research/2026-02-28-ai-agent-context-compression-strategies)
- [Will Lethain: Context window compaction](https://lethain.com/agents-context-compaction/)
- [InfoQ: Claude Opus 4.6 Context Compaction](https://www.infoq.com/news/2026/03/opus-4-6-context-compaction/)
- [Oracle: AI Agent Loop Architecture](https://blogs.oracle.com/developers/what-is-the-ai-agent-loop-the-core-architecture-behind-autonomous-ai-systems)
- [TowardsDataScience: Multi-Agent 17x Error Trap](https://towardsdatascience.com/why-your-multi-agent-system-is-failing-escaping-the-17x-error-trap-of-the-bag-of-agents/)
- [MDPI: Diagnosing Bias and Instability in LLM Evaluation](https://www.mdpi.com/2078-2489/16/8/652)
- [MindStudio: Stripe Minions Harness](https://www.mindstudio.ai/blog/what-is-ai-agent-harness-stripe-minions)

### 학술 논문 (스킬 문서 인용)
- AI Scientist-v2 (Sakana AI, arXiv:2504.08066, ICLR 2025 workshop)
- Agent0 co-evolution (arXiv:2511.16043)
- SE-Agent (NeurIPS 2025)
- A-MEM (arXiv:2502.12110, NeurIPS 2025)
- POET (arXiv:1901.01753)
- SSP self-play (arXiv:2510.18821)
- LlamaFirewall (arXiv:2505.03574)
- Goal Drift (arXiv:2505.02709)
- Multi-Agent Evolve (arXiv:2510.23595)
- Novelty Search (Lehman & Stanley, Evolutionary Computation)
- Hindsight Experience Replay (Andrychowicz et al., NeurIPS 2017)
- NSGA-II Multi-objective Evolution

### 프로젝트 내 참조 문서
- [LiveCode 자율 에이전트 인사이트 보고서](../agent-improvement-report-20260330.md)
- [AI 하네스 개념 및 사용법 리서치](20260330-harness-engineering.md)

## Related
- [[projects/LiveCode/research/20260328-omc-live-infinite-loop-architecture-research|20260328-omc-live-infinite-loop-architecture-research]]
- [[projects/LiveCode/research/20260330-harness-engineering|20260330-harness-engineering]]
- [[projects/LiveCode/research/20260326-omc-live-self-evolving-outer-loop|20260326-omc-live-self-evolving-outer-loop]]
- [[projects/LiveCode/research/20260327-omc-live-autonomous-ai-research-2025-2026|20260327-omc-live-autonomous-ai-research-2025-2026]]
- [[projects/LiveCode/research/20260327-omc-live-git-checkpoint-self-evolving-research|20260327-omc-live-git-checkpoint-self-evolving-research]]
- [[projects/LiveCode/research/20260325-omc-autopilot-loop-vs-agent-research-trends|20260325-omc-autopilot-loop-vs-agent-research-trends]]
- [[projects/LiveCode/research/20260325-autonomous-agent-goal-update-subloop-architecture|20260325-autonomous-agent-goal-update-subloop-architecture]]
- [[projects/LiveCode/research/20260328-omc-live-science-research-domain-expansion|20260328-omc-live-science-research-domain-expansion]]
