# SaaS / AI Monetization Diagnostic (D1)
**corpus**: monetization | **doc_id**: D1 | **layer**: L2  
**Date**: 2026-04-12 | **Status**: stable

---

## Purpose

수익화/가격 모델 선택 전 반드시 수집해야 할 데이터와, 그 데이터를 기반으로 모델을 선택하는 진단 프로토콜.

---

## Step 1: COGS 구조 진단

```
AI 제품 여부 확인:
  YES → 추론 비용($/request or $/1k tokens) 측정
        추론 비용 × 안전 마진 3× = 최소 unit price
        [이하면 usage-based pricing은 마진 역전 위험]

  NO  → 전통 SaaS COGS (hosting, support, infra) 측정
```

**수집 지표**:
- Inference cost per output (AI 제품)
- Hosting/infra cost per active seat (전통 SaaS)
- Support cost per customer (free + paid 구분)
- Gross Margin% (현재 또는 목표)

---

## Step 2: 고객 구매 패턴 진단

5개 질문으로 가격 모델 적합성 판단:

| # | 질문 | YES → | NO → |
|---|------|-------|------|
| Q1 | 고객이 사용량을 예측할 수 있는가? | UBP 가능 | UBP 장벽, flat/hybrid 고려 |
| Q2 | 고객이 연간 예산을 편성하는 조직인가? | Flat/seat preferred | UBP or monthly subscription |
| Q3 | 고객이 ROI를 계약 전에 측정할 수 있는가? | Outcome-based 가능 | Outcome-based 위험 |
| Q4 | 사용량이 고객 성공과 비례하는가? | UBP가 Value Metric으로 적합 | Value Metric 재검토 |
| Q5 | 고객이 타사 대안 없이 우리에게 의존하는가? | 가격 결정권 높음 | 경쟁 가격 전략 필요 |

---

## Step 3: GTM 모션 × 가격 모델 매핑

```
GTM 모션 확인 (하나 선택):
  PLG  → Freemium + usage-based 조합 우선
  SLG  → Flat-rate (seat) + negotiated enterprise tier
  CLG  → Hybrid (community free + paid power tools)
  DLG  → Outcome 또는 usage-based (데이터 기여 가치 연동)

복합 모션 (PLG + SLG 병행)?
  → PLG tier에는 UBP, SLG tier에는 flat/enterprise 계약
  → 두 개 가격 라인 유지 (self-serve vs sales-assisted)
```

---

## Step 4: Value Metric 선정

**3단계 선정 프로세스**:

```
1. 고객 언어로 성공을 표현하면?
   (예: "회의 시간 줄이기", "코드 리뷰 속도", "리드 전환율")

2. 그 성공 지표와 가장 비례하는 우리 제품 단위는?
   (회의 수, 리뷰 완료 건수, 분석된 리드 수)

3. 그 단위가 우리 COGS와 상관관계가 있는가?
   YES → UBP Value Metric으로 적합
   NO  → 단위 분리 (price unit ≠ cost unit → hybrid 필요)
```

---

## Step 5: LTV:CAC 현황 진단

```
LTV:CAC 계산:
  현재 ARPU = ?
  현재 Gross Margin = ?
  현재 Churn Rate (월간) = ?
  LTV = ARPU × GM% / Churn_Rate

  CAC = 최근 3개월 S&M 지출 / 최근 3개월 신규 고객 수

  LTV:CAC = ?
```

**판정**:
- < 1: 가격 모델 수정 전에 CAC 또는 Churn 해결이 우선
- 1–3: 가격 모델 검토 + 팽창(expansion) 메커니즘 추가
- 3–5: 현 가격 모델 유지 + 스케일 조건 확인
- > 5: 언더프라이싱 신호 → Van Westendorp PSM 또는 A/B 테스트 실행

---

## Step 6: 경쟁 가격 컨텍스트 파악

**수집 항목**:
```
□ 상위 3개 경쟁사 가격 모델 (flat / usage / hybrid?)
□ 각 경쟁사의 value metric (seats? API calls? outputs?)
□ 가격 범위 (entry / mid / enterprise tier)
□ 경쟁사 타겟 ICP vs 우리 ICP 차이점
```

**해석 원칙**:
- 경쟁사와 동일 ICP + 동일 value metric → 가격 밴드 내에서 포지셔닝
- 다른 ICP 또는 다른 value metric → 독립적 가격 결정 가능 (비교 불필요)
- 모든 경쟁사가 같은 모델 → 차별화 기회 또는 업계 수렴 신호

---

## 진단 출력 — 권장 모델 선택

진단 결과를 종합해 하나의 모델을 선택한다:

| 조건 조합 | 권장 모델 |
|---------|---------|
| PLG + AI + 예측 가능 사용량 | Usage-based (UBP) |
| SLG + B2B enterprise | Flat-rate per seat + negotiated |
| PLG + 바이럴 루프 | Freemium + UBP or hybrid upgrade |
| 높은 ROI 가시성 + 고신뢰 | Outcome-based |
| 복합 모션 or 불확실 | Hybrid (floor + usage/outcome overage) |
| 모든 지표 불명확 | **가격 모델 결정 연기**: 먼저 PMF 확인 후 revisit |

---

## Sources
- T1: 20260412-monetization-theory.md
- T4: 20260412-monetization-falsification.md
- Pricing I/O — SaaS Pricing Diagnostic Methodology
- OpenView — PLG Monetization Playbook 2025
- ChartMogul — LTV:CAC Measurement Guide

## Related
- [[projects/Ameva/research/20260412-monetization-theory|20260412-monetization-theory]]
- [[projects/Ameva/research/20260412-monetization-falsification|20260412-monetization-falsification]]
- [[projects/Ameva/research/20260412-monetization-playbook|20260412-monetization-playbook]]
