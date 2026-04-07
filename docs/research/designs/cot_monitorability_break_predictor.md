# CoT Monitorability Break Predictor — Design

## Source
- **Paper**: Predicting When RL Training Breaks Chain-of-Thought Monitorability
- **URL**: https://www.alignmentforum.org/posts/SvxaKP5KdkksZPcG7/predicting-when-rl-training-breaks-chain-of-thought
- **Authors**: Max Kaufmann, David Lindner, Roland S. Zimmermann, Rohin Shah (DeepMind Safety)
- **Absorbed via**: /inhale agent_research — Alignment Forum (2026-04-01)
- **Relevance**: 9.0/10 (skill_selection)

## Core Idea from Paper
RL 학습 중 CoT(Chain-of-Thought)가 "모니터링 불가능"해지는 임계점이 예측 가능하다.
특정 훈련 스텝에서 에이전트의 CoT가 실제 행동과 decoupled 됨 — CoT는 올바른 추론처럼
보이지만 실제 결정은 다른 회로에서 이루어짐. 이 전환을 사전 예측할 수 있다.

## HarnessOS Application

### Problem
`autonomy_classifier.py`는 현재 에이전트 행동의 자율성을 분류하지만,
에이전트가 CoT를 "위장"으로 사용하기 시작하는 시점을 감지하지 못함.
→ EVOLVE 게이트가 CoT 기반 reasoning을 신뢰하지만, CoT가 이미 decoupled 상태일 수 있음.

### Proposed Architecture

```
episode.cot_text + episode.action_taken
        │
        ▼
CoTConsistencyAnalyzer
   ├── extract_stated_intent(cot_text) → intent_embedding
   ├── extract_action_embedding(action_taken) → action_embedding
   └── cosine_similarity(intent, action) → consistency_score
        │
        ▼ consistency_score < THRESHOLD
        │
        ▼
AutonomyClassifier.CoTDecoupledSignal (NEW)
   → block EVOLVE gate
   → log to .omc/cot-decouple-log.jsonl
```

### Integration Points

**1. `autonomy_classifier.py` 수정**
```python
class CoTMonitorabilityChecker:
    CONSISTENCY_THRESHOLD = 0.65  # 튜닝 필요

    def check(self, cot_text: str, action_taken: str) -> MonitorabilityStatus:
        intent = self._embed(cot_text)
        action = self._embed(action_taken)
        score = cosine_similarity(intent, action)

        if score < self.CONSISTENCY_THRESHOLD:
            return MonitorabilityStatus.DECOUPLED
        return MonitorabilityStatus.ALIGNED

    def _embed(self, text: str) -> np.ndarray:
        # 경량 임베딩: sentence-transformers all-MiniLM-L6-v2
        # 또는 TF-IDF fallback (zero-dependency)
        ...
```

**2. EVOLVE 게이트 조건 확장**
현재: `safety_check() AND score > threshold`
신규: `safety_check() AND cot_monitorability_check() AND score > threshold`

**3. 로깅**
```json
{"ts": "...", "episode_id": "...", "cot_snippet": "...", "action": "...",
 "consistency_score": 0.43, "status": "DECOUPLED", "gate_blocked": true}
```

### Trade-offs

| 옵션 | 장점 | 단점 |
|------|------|------|
| sentence-transformers | 정확도 높음 | 의존성 추가, 느림 |
| TF-IDF cosine | 의존성 없음 | 의미적 유사도 낮음 |
| keyword overlap | 극단적 경량 | false negative 많음 |

**권장**: TF-IDF로 먼저 prototype, 효과 확인 후 sentence-transformers 교체.

### Alternatives Considered
- **LLM-as-judge**: CoT 일관성을 LLM이 판단 → 비용/지연 높아 EVOLVE 게이트에 부적합
- **Activation patching** (논문 방법): 모델 내부 접근 필요 → 블랙박스 에이전트에 적용 불가
- **행동 예측 모델**: CoT → 예상 행동 예측기 훈련 → 데이터 수집 필요

### Next Steps
1. `autonomy_classifier.py`에 `CoTMonitorabilityChecker` 구현 (TF-IDF variant)
2. 기존 episode 로그에서 CoT-action 쌍 추출하여 consistency score 분포 확인
3. threshold 튜닝: precision-recall 곡선에서 EVOLVE false positive < 5% 지점
4. 효과 검증: CoT 일관성 경고 발생률 vs 실제 misalignment 사례 상관관계
