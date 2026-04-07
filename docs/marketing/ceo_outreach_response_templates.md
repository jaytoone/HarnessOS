# CEO 아웃리치 답장 템플릿 — Outward Reception 적용

> **생성**: 2026-04-06
> **기반**: Outward Reception A/B 테스트 (+0.70 delta, 3개 시나리오 중 최고)
> **원칙**: 인사이트는 바뀌지 않는다 — 전달 언어만 바뀐다.

---

## 핵심 인사이트 (고정)

CEO 아웃리치에서 가장 흔한 "나중에 연락주세요" 패턴은 거절이 아니다.
intuition-first 화자가 선형 인과로 막혀 있는 상태다:
**"프로세스 없음 → 시기상조"** — 이 블로킹 체인 자체를 재정의해야 한다.

---

## 시나리오별 템플릿

### Type A — intuition-first / linear / external (가장 흔한 패턴)

**신호**: "뭔가 아직 준비가 안 된 것 같아서", "시기상조인 것 같기도 해요", "나중에 연락주세요"

**Step 0 프로필**:
```
epistemic_basis: intuition-first
causal_model: linear (블로킹 조건 체인)
locus_of_control: external (행위 주체 회피)
gaps: [no_data_anchor, no_agency]
```

**Treatment 응답**:
> What I'm noticing here — '아직 준비가 안 된 것 같다'는 감각은 사실 AI 도입의 가장 정확한 신호 중 하나입니다.
> 실제로 잘 됐던 케이스들은 '준비 완료 후 시작'이 아니라 '그 불편함에서 시작'이었습니다.
>
> One thing worth adding: 지금 그 '안 갖춰진 느낌'이 어느 순간 가장 강하게 오는지 — 그게 사실 첫 번째 작업이 될 가능성이 높습니다.
>
> Does that match what you're sensing?

**왜 작동하는가**:
- "안 갖춰진 감각" = 문제가 아닌 신호로 재정의 (anti-sycophancy)
- "준비 후 시작" 선형 체인을 깨지 않고, 시작점을 바꿈
- 마지막 질문이 CEO를 다시 행위 주체로 만듦 (no_agency gap surfacing)

---

### Type B — data-driven / linear / internal (소수이지만 고WTP)

**신호**: "ROI 데이터가 있나요?", "타사 도입 사례 수치가 있으면 공유해주세요", "구체적인 개선 지표가 필요합니다"

**Step 0 프로필**:
```
epistemic_basis: data-driven
causal_model: linear
locus_of_control: internal
gaps: [no_feedback_loop]
```

**Treatment 응답**:
> The pattern in the data points to this: AI 도입 ROI의 80%는 '무엇을 도입했는가'가 아니라 '의사결정 오류를 얼마나 줄였는가'에서 나옵니다.
>
> 현재 저희가 추적하는 지표는 [지표 1], [지표 2]입니다.
> One thing worth adding: 이 개선이 반복 가능한 시스템에서 나오는지, 아니면 일회성 최적화인지가 핵심 변수입니다.
>
> What does your data show on this — 현재 어떤 의사결정에서 불확실성이 가장 높으신가요?

---

### Type C — authority-referencing / linear / external (대기업 임원 패턴)

**신호**: "업계에서 검증된 사례가 있나요?", "글로벌 기업들은 어떻게 하고 있나요?", "전문가들이 권고하는 방법이 뭔가요?"

**Step 0 프로필**:
```
epistemic_basis: authority-referencing
causal_model: linear
locus_of_control: external
gaps: [no_data_anchor (자체 데이터 없음), no_feedback_loop]
```

**Treatment 응답**:
> This maps to a well-established pattern: AI 도입에서 가장 높은 ROI를 보인 기업들(McKinsey 2025 보고서 기준)은 공통적으로 '도구 도입' 전에 '의사결정 패턴 진단'을 먼저 했습니다.
>
> One thing worth adding: 검증된 프레임워크를 따르는 것이 ROI를 보장하지 않는 이유가 있습니다 — 프레임워크는 실행 지침이고, 어떤 결정에 적용할지는 별개의 진단이 필요합니다.
>
> Is that consistent with what you've seen work — 주변에서 잘 됐다고 생각하는 AI 도입 사례가 있으신가요?

---

## A/B 테스트 결과 요약

| 차원 | Control (프로필 무시) | Treatment (Step 0 적용) | Delta |
|------|---------------------|------------------------|-------|
| recognition_depth | 0.25 | 0.90 | **+0.65** |
| anti_sycophancy | 0.10 | 0.85 | **+0.75** |
| frame_match | 0.20 | 0.90 | **+0.70** |
| **total** | **0.18** | **0.88** | **+0.70** |

**Control의 가장 흔한 실패**: "네, 알겠습니다. 준비되시면 연락주세요."
→ intuition-first 화자의 블로킹 체인을 그대로 수용 → 대화 종료

**Treatment의 핵심 무브**:
1. 화자의 언어 프레임으로 열기 (오프닝 앵커)
2. 말하지 않은 것 이름 붙이기 (gap surfacing)
3. 질문으로 닫기 — CEO를 다시 행위 주체로 만들기

---

## 실사용 체크리스트

답장을 보내기 전:

- [ ] 상대 메시지에서 epistemic_basis 감지 (데이터/직관/권위 중 무엇?)
- [ ] causal_model 감지 (선형 블로킹 체인인가?)
- [ ] 상대가 말하지 않은 것 확인 (no_data_anchor / no_agency / no_feedback_loop)
- [ ] 오프닝 앵커 선택 (data / narrative / precedent)
- [ ] gap surfacing 문장 1개 추가
- [ ] 마지막을 질문으로 마무리

---

## 관련 파일

- `experiments/paradigm_communication/paradigm_detector.py` — Python spec (regex 기반, 검증용)
- `experiments/paradigm_communication/response_adapter.py` — Python spec (응답 적응 로직)
- `experiments/paradigm_communication/eval.py` — 평가 파이프라인 (score: 0.954)
- `~/.claude/skills/entity/SKILL.md` — Step 0 Outward Reception (LLM 추론 버전, production)
