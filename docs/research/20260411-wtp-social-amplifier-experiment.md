# Social_Amplifier 검증 실험 설계: 곱셈 vs 덧셈 구조

**Date**: 2026-04-11  
**Method**: live-inf iter 7/∞ — research-scientist 실험 설계  
**Validates**: [20260411-wtp-demand-genesis-theory.md](20260411-wtp-demand-genesis-theory.md) — Social_Amplifier 메커니즘  
**Status**: 실행 가능 (비용 ~₩120,000, 기간 2.5주)

---

## 검증 대상 주장

**VALUE GAP**: D(WTP) = [Gap_Intensity × Attainability] × **[Social_Amplifier]** × [Ethical_Coefficient]

Social_Amplifier가 **곱셈적**이라는 주장:
- 갭의 사회적 가시성이 WTP를 Gap_Intensity에 비례해서 비선형 증폭
- JTBD "social job" 이론은 고정 프리미엄(덧셈)을 예측

---

## 가설

- **H0 (덧셈)**: WTP_social = WTP_private + k (k는 Gap_Intensity와 무관한 상수)
- **H1 (곱셈)**: WTP_social = WTP_private × m (m > 1, Gap_Intensity에 무관하게 비율 일정)

**결정적 차이**: H0에서 (social−private) 차이는 Gap 강도와 무관하게 일정. H1에서 비율(social/private)은 일정하지만 절대 차이는 Gap 강도에 비례 증가.

---

## 실험 설계: 2×2 Between-Subjects

### 자극(Stimulus): 생산성 감사 리포트 시나리오

프리랜서/창업가가 자신의 시간 사용 방식, 손실, 비용을 분석한 리포트.

**조건별 내용 동일** (Gap_Intensity × Attainability 고정), **사회적 가시성만 변화**:

| | Private 조건 | Social 조건 |
|---|---|---|
| **Low Gap** (주 3시간 손실) | Cell A | Cell B |
| **High Gap** (주 10시간 손실) | Cell C | Cell D |

**Private 조건**: "이 리포트는 당신만 봅니다. 의뢰했다는 사실과 결과를 아무도 모릅니다."

**Social 조건**: "이 리포트는 분기 리뷰에서 비즈니스 파트너 / 핵심 클라이언트와 공유됩니다. 갭과 당신의 대응 여부를 그들이 봅니다."

**조작 확인 (필수)**: 시나리오 후 2문항
- "이 갭이 중요한 타인에게 얼마나 가시적인가?" (1–7)
- "이 갭을 닫는 것이 얼마나 긴급하게 느껴지는가?" (1–7)

Social 셀이 가시성에서만 높아야 함. 긴급성에서 차이 나면 Gap_Intensity 오염 → 해당 응답자 제외.

---

## 측정

**WTP 유도**: Van Westendorp PSM (4개 가격점: 너무 저렴 / 적정 / 비쌈 / 너무 비쌈)
- 설문 맥락에 적합, 금전적 약정 불필요
- 한국 소비자 조사 표준 방법
- BDM은 실제 결제 인프라 필요하므로 제외

**샘플**: 한국 프리랜서 + 초기 창업가 (1-5인 운영)
- 모집 채널: Kmong 커뮤니티, Disquiet.io, 관련 카카오 오픈채팅
- Between-subjects (각 응답자는 1개 셀만)
- 통제 변수: 단독 vs 팀 운영, 월 수익 구간, 생산성 툴 이전 사용 여부

**필요 샘플 수**:
- 2×2 ANOVA, 중간 상호작용 효과(f=0.25), α=0.05, 파워 80%
- 셀당 n≈52, 총 N=208 → 탈락률 13% 감안 **N=240**
- 최소 하한: 셀당 40명(N=160) — 대형 효과(f=0.35) 감지 가능

---

## 분석 계획

**주요 검정**: PSM 최적 가격점에 대한 2×2 ANOVA

| 효과 | 예측 | 진단 의미 |
|---|---|---|
| Social 주효과 | 유의 (양 이론 모두 예측) | 차별자 아님 |
| Gap_Intensity 주효과 | 유의 (양 이론 모두 예측) | 차별자 아님 |
| **Gap × Social 상호작용** | **VALUE GAP: 유의 / JTBD: 비유의** | **결정적 검정** |

**곱셈 구조 확인 방법**:
- ratio_low = B/A, ratio_high = D/C
- Bootstrap 95% CI 계산
- CI 중첩 + 두 비율 모두 >1 → 곱셈 구조 지지

예시: A=₩30,000, B=₩54,000 (비율 1.8) → C=₩90,000이면 D≈₩162,000 (동일 비율 1.8)

**VALUE GAP 반증 기준**: 상호작용 비유의(p>0.10) AND social 프리미엄이 Gap_Intensity 수준에 무관하게 ±15% 이내 평탄 → JTBD 고정 프리미엄 모델이 더 간명

**핵심 결과물**: 상호작용 플롯 (non-parallel lines = 곱셈 구조의 경험적 시그니처)

---

## 실행 계획

| 항목 | 세부 | 비용 |
|---|---|---|
| 플랫폼 | Typeform Business (1개월), 분기 로직으로 4개 시나리오 랜덤 배정 | ₩45,000 |
| 모집 인센티브 | ₩5,000 카카오 기프티콘 추첨 × 10명 | ₩50,000 |
| **합계** | | **≈₩95,000–120,000** |

**타임라인**:
- 자극 설계 + Typeform 구축: 3일
- 모집 오픈 (240응답): 7–10일
- 분석: 2일
- **총 2.5주**

---

## 이 실험이 전체 이론에서 차지하는 위치

```
검증되면: VALUE GAP의 곱셈 공식 경험적 지지
          → JTBD 평탄 프리미엄 모델 대비 우월한 WTP 예측 도구 주장 가능

반증되면: Social_Amplifier를 덧셈 항으로 수정
          D(WTP) = [Gap_Intensity × Attainability] + Social_Premium + [Ethical_Coefficient]
          → 이론 범위 축소 (고관여 시장에만 곱셈 적용)
```
