# SaaS / AI Monetization Execution Playbook (S1)
**corpus**: monetization | **doc_id**: S1 | **layer**: L2  
**Date**: 2026-04-12 | **Status**: stable

---

## Purpose

D1 진단 이후 선택된 가격 모델을 실제로 구현하는 0–90일 실행 가이드.

---

## 모델별 구현 가이드

### Model A: Usage-Based Pricing (UBP)

**Phase 1: Metering Infrastructure (Week 1–3)**

```
□ 과금 단위(value metric) 확정 → 코드에 계측(instrumentation) 삽입
□ 사용량 집계 파이프라인 구축 (real-time 또는 daily batch)
□ 고객 대시보드: 본인 사용량 실시간 확인 가능
□ Alert 시스템: 예상 초과 비용 알림 → "bill shock" 방지
□ 월간 cap 옵션: 고정 상한액 설정 가능 (선택적)
```

**Phase 2: Tier 설계 (Week 2–3)**

| Tier | 특징 | 비고 |
|------|------|------|
| 무료 크레딧 | 월 N 단위 무료 | onboarding + 바이럴 루프 지원 |
| Pay-as-you-go | 단위당 $X | 자동 결제 필수 |
| Committed use | 볼륨 할인 (10–30%) | 연간 계약 옵션 |
| Enterprise | 커스텀 계약 | SLG 트랙 진입 |

**건강 지표**:
- Monthly Revenue Volatility: 20% 이내
- Usage Predictability Score: 상위 50% 고객의 실제 vs 예측 편차 < 15%
- Bill Shock Rate: < 2% (월 예상 대비 50% 초과 청구 발생 고객 비율)

---

### Model B: Flat-Rate / Seat Pricing

**Phase 1: Tier 설계 (Week 1–2)**

```
Starter / Growth / Business / Enterprise
각 티어 포함 기능 목록 확정:
  □ 핵심 기능은 Growth 이상에서만 (Starter = hook, not product)
  □ 팀/협업 기능 잠금 → upgrade trigger
  □ API 접근 = Business 이상 (개발자 segment 분리)
```

**Phase 2: Annual vs Monthly 가격 격차 설계 (Week 2)**

```
연간 할인율 권장: 15–25%
  - 너무 낮은 할인(<10%): 연간 전환 인센티브 부족
  - 너무 높은 할인(>30%): 현금흐름 개선은 되나 마진 희생
```

**Phase 3: Enterprise Sales Motion (Week 3+)**

```
□ 커스텀 계약 가능 여부 + 최소 ARR 기준 설정
□ Security review, SSO, SLA = Enterprise 전용
□ Annual commitment = discount + professional services 번들
```

---

### Model C: Hybrid (Floor + Overage)

**Floor 설계 원칙**:
- Floor = 최소 usage × unit price (고객이 항상 지불하는 기준선)
- Overage = Floor 초과분 × 단위 가격 (usually 10–20% lower than base rate)
- Floor는 고객에게 "예산 예측 가능성" 제공
- Overage는 성장 고객에게 자연스러운 확장 경로

```
Floor 설정 기준:
  현재 median customer 사용량의 70–80% → 대부분 overage 없음
  상위 20% 고객이 overage → NRR 자연 확장 엔진
```

**측정 지표**:
- Overage Revenue % of Total: 15–30% 목표 (너무 낮으면 floor 과대, 너무 높으면 unpredictability)
- NRR (Net Revenue Retention): 목표 > 110%

---

### Model D: Freemium + Paid Upgrade

**Phase 1: Free Tier 경계 설정 (Week 1–2)**

```
Free tier 설계 원칙:
  □ 핵심 가치 경험 가능 (aha moment 도달)
  □ 협업/팀 기능 = Paid 전용 (natural upgrade trigger)
  □ 사용량 cap = 고객의 "아 이건 더 필요해" 순간에 도달
  □ Free tier infra 비용 < 예상 conversion revenue ÷ 전환 기간
```

**Phase 2: Paywall Moment 설계 (Week 2–3)**

```
최적 paywall 배치:
  1. 협업 초대 시 (팀원 추가 클릭)
  2. 사용량 한도 도달 직후
  3. 고급 분석/export 클릭 시
  ❌ 가입 즉시 (가치 경험 전 paywall = 이탈)
  ❌ 매 세션 팝업 (UX 마찰 → trust erosion)
```

**Phase 3: Conversion 측정 (Week 3+)**

- Free → Paid conversion rate (목표: B2B PLG 5–10%)
- Time-to-convert (중앙값): 14–30일이 건강한 범위
- Upgrade trigger event (어떤 액션 직후 전환이 가장 많은가?)

---

## 0–90일 타임라인

| Phase | 기간 | 목표 | 성공 지표 |
|-------|------|------|---------|
| 진단 + 모델 선택 | Week 1–2 | D1 진단 완료 → 모델 확정 | Value metric 정의, COGS 측정 |
| Metering / Tier 설계 | Week 2–4 | 과금 인프라 구축 | 사용량 추적 live |
| 가격 발표 + Pilot | Week 4–6 | 소규모 코호트에 신규 가격 적용 | 전환율, 이탈 없음 확인 |
| 전면 적용 | Week 6–8 | 전체 신규 사용자 적용 | MRR / NRR 측정 시작 |
| 최적화 | Week 8–12 | Tier 구성 + paywall 위치 A/B | conversion lift 확인 |
| 리뷰 | Month 3 | LTV:CAC + NRR 첫 코호트 데이터 | 모델 유지 or 전환 판단 |

---

## 가격 변경 전 Anti-Pattern 체크리스트

- [ ] LTV:CAC 데이터 없이 가격 인상 추진? → 먼저 측정
- [ ] 경쟁사 가격 그대로 복사? → Value Metric 확인 필수
- [ ] UBP 도입 전 Bill Shock 방지 메커니즘 없음? → cap/alert 구현 선행
- [ ] Freemium 론칭 전 viral loop 미설계? → K-factor 먼저 확인
- [ ] Outcome-based 도입 전 attribution 모델 미정? → 계약 정의 먼저

---

## Sources
- T1: 20260412-monetization-theory.md
- D1: 20260412-monetization-diagnostic.md
- T4: 20260412-monetization-falsification.md
- OpenView PLG Monetization Playbook 2025
- Paddle SaaS Monetization Trends 2026
- Reforge — Pricing Motion Design Templates

## Related
- [[projects/Ameva/research/20260412-monetization-theory|20260412-monetization-theory]]
- [[projects/Ameva/research/20260412-monetization-diagnostic|20260412-monetization-diagnostic]]
- [[projects/Ameva/research/20260412-monetization-falsification|20260412-monetization-falsification]]
- [[projects/Ameva/research/20260412-marketing-growth-loop-playbook|20260412-marketing-growth-loop-playbook]]
- [[projects/Ameva/research/20260412-marketing-growth-diagnostic|20260412-marketing-growth-diagnostic]]
- [[projects/Ameva/research/20260412-marketing-growth-theory|20260412-marketing-growth-theory]]
- [[projects/Ameva/research/20260412-marketing-growth-falsification|20260412-marketing-growth-falsification]]
- [[projects/Ameva/research/20260412-marketing-growth-corpus-draft|20260412-marketing-growth-corpus-draft]]
