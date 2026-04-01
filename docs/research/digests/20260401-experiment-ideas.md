# HarnessOS Experiment Ideas — 2026-04-01
수집된 채널 정보에서 실험적으로 진화 가능한 아이디어 선별

---

## Tier 1: 즉시 실험 가능 (HarnessOS 핵심과 직접 연결)

### IDEA-1: CI-Gate 기반 Readiness Score
**출처**: [LLM Readiness Harness](https://arxiv.org/abs/2603.27355) | 관련성: 10.0/10

**논문 핵심**: 평가를 배포 결정 워크플로로 전환. 벤치마크 + 비용 + 지연 + 정책 준수를 Pareto 가중 readiness score로 집계.

**HarnessOS 적용 아이디어**:
- 현재 `harness_evaluator.py`가 단순 pass/fail인데, **Pareto readiness score** 도입
- 각 실험 이터레이션에서 `quality × cost × latency` 3차원 readiness 벡터 계산
- `score >= threshold` 대신 `pareto_dominated = False` 조건으로 진화 판단
- 실험 파일: `experiments/readiness_harness/`

```python
# 개념 코드
readiness_vector = {
    "quality": eval_score,
    "efficiency": 1 / (token_count / 1000),
    "groundedness": factual_accuracy,
}
is_ready = not is_pareto_dominated(readiness_vector, past_vectors)
```

---

### IDEA-2: Verification이 오히려 해가 되는 조건 탐지
**출처**: [When Verification Hurts](https://arxiv.org/abs/2603.27076) | 관련성: 8.0/10

**논문 핵심**: 다중 에이전트 피드백이 특정 조건에서 성능을 **오히려 저하**시킴 (asymmetric effect). knowledge-graph 기반 벤치마크 516개 proof state.

**HarnessOS 적용 아이디어**:
- `stuck_agent` 실험에서 "검증이 stuck을 더 악화시키는 조건" 탐지 실험
- 현재 `semantic_inv`는 단순 유효성 검증인데 → **언제 검증이 오히려 루프를 고착시키는가?**
- 가설: 잘못된 방향으로 일관된 검증 피드백 → escape 억제
- 실험: `verification_mode = [none | strict | lenient | adaptive]` 비교

```yaml
# experiments/verification_hurt/config.yaml
verification_modes:
  - none          # 검증 없음
  - strict        # 매 스텝 검증
  - lenient       # 5스텝에 1번
  - adaptive      # 신뢰도 임계값 기반
metric: stuck_escape_rate
```

---

### IDEA-3: Self-Evolving 워크플로 합성
**출처**: [Self-evolving AI agents (VenusFactory2)](https://arxiv.org/abs/2603.27303) | 관련성: 9.0/10

**논문 핵심**: 정적 tool use → **동적 워크플로 합성**. 새 도메인에서 기존 도구 조합을 자율 재구성.

**HarnessOS 적용 아이디어**:
- `omc-live-infinite`의 goal evolution이 고정된 스킬 세트에 의존하는 문제 해결
- "스킬 조합 공간"을 동적으로 탐색하는 **workflow synthesis** 레이어 추가
- 현재: `root_goal → autopilot(fixed_skills)` → 개선: `root_goal → synthesize_workflow → execute`
- 실험: skill composition vs single skill pass율 비교

---

## Tier 2: 중기 실험 아이디어 (연구 방향 확장)

### IDEA-4: 4가지 LLM 평가 접근법 체계화
**출처**: [4 Main Approaches to LLM Evaluation](https://magazine.sebastianraschka.com/p/llm-evaluation-4-approaches) | 관련성: 6.5/10

**핵심**: Benchmark / Human / LLM-as-judge / Task-specific 4가지 평가 접근법

**HarnessOS 적용**:
- 현재 harness_evaluator가 task-specific에 편중 → LLM-as-judge 레이어 추가
- `judge_llm = claude-haiku-4-5` 활용한 자동 품질 평가 파이프라인

---

### IDEA-5: Inference-Time Scaling 카테고리화
**출처**: [Categories of Inference-Time Scaling](https://magazine.sebastianraschka.com/p/categories-of-inference-time-scaling) | 관련성: 5.0/10

**핵심**: sequential (CoT), parallel (best-of-N), iterative (self-correction) 3가지 스케일링

**HarnessOS 적용**:
- `stuck_agent`의 탈출 전략을 이 3가지 범주로 분류
- sequential escape / parallel escape / iterative escape 비교 실험

---

### IDEA-6: Heterogeneous Debate Engine
**출처**: [Heterogeneous Debate Engine](https://arxiv.org/abs/2603.27404) | 관련성: 10.0/10

**핵심**: 서로 다른 identity를 가진 에이전트들의 debate → 편향 저항성 향상

**HarnessOS 적용**:
- hypothesis_validation에서 단일 LLM judge → **heterogeneous debate** 구조
- Agent A (skeptic) vs Agent B (advocate) vs Agent C (neutral) 3-way debate
- 현재 `llm_strategies.py`에 debate 모드 추가

---

## 실험 우선순위 매트릭스

| 아이디어 | Impact | 구현 난이도 | HarnessOS 적합성 | 우선순위 |
|----------|--------|------------|-----------------|---------|
| IDEA-2 (Verification Hurt) | 높음 | 낮음 | 매우 높음 | **P0** |
| IDEA-1 (Readiness Score) | 높음 | 중간 | 높음 | **P1** |
| IDEA-6 (Debate Engine) | 중간 | 중간 | 높음 | **P1** |
| IDEA-3 (Workflow Synthesis) | 높음 | 높음 | 중간 | P2 |
| IDEA-5 (Scaling Categories) | 중간 | 낮음 | 중간 | P2 |
| IDEA-4 (LLM-as-judge) | 낮음 | 낮음 | 낮음 | P3 |

**Next experiment: IDEA-2** — `verification_mode` 비교 실험 (stuck_agent escape rate 측정)

## Related
- [[projects/HarnessOS/research/20260327-omc-live-git-checkpoint-self-evolving-research|20260327-omc-live-git-checkpoint-self-evolving-research]]
- [[projects/HarnessOS/research/20260326-omc-live-skill-critique|20260326-omc-live-skill-critique]]
- [[projects/HarnessOS/research/20260326-omc-live-self-evolving-outer-loop|20260326-omc-live-self-evolving-outer-loop]]
- [[projects/HarnessOS/research/20260328-omc-live-infinite-loop-architecture-research|20260328-omc-live-infinite-loop-architecture-research]]
