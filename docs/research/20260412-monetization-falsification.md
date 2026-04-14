# SaaS / AI Monetization Falsification Criteria (T4)
**corpus**: monetization | **doc_id**: T4 | **layer**: L2  
**Date**: 2026-04-12 | **Status**: stable

---

## Purpose

이 문서는 monetization corpus의 **반증 기준 게이트**다. Corpus Pre-step에서 모든 수익화/가격 주장을 여기에 먼저 대조한다. 체크를 통과하지 못한 주장은 [UNCERTAIN] 또는 [CONFLICT] 태그로 표시한다.

---

## Hard Claims (HC) — 반드시 검증해야 하는 주장들

### HC-1: Usage-based pricing이 항상 더 낫다

**주장**: "AI 제품이니까 usage-based로 가야 한다"  
**반증 조건**: 아래 중 하나라도 해당하면 주장 기각

- 고객이 사용량을 예측하기 어렵다 → 가입 장벽 증가
- 단위 당 추론 비용이 가격의 3× 미만 → 마진 역전
- B2B 기업 고객이 연간 예산 편성 필요 → flat/hybrid가 현실적

→ Usage-based는 **선택지** 중 하나. GTM 모션 + COGS 구조 + 고객 예산 패턴 3가지를 먼저 확인.

---

### HC-2: 수익 증가 = 제품이 잘 되고 있다

**주장**: "매출이 오르고 있으니 가격 모델이 맞다"  
**반증 조건**:

- Gross Margin 확인 없이 매출 트렌드만 제시 → [INCOMPLETE]
- 고객 집중도 > 50% (상위 1–3개 고객이 매출 절반) → [CONCENTRATION_RISK]
- Net Revenue Retention (NRR) < 100% → 확장이 없고 이탈로 성장 중 → [CHURN_MASKED]

**함께 보고할 지표**: Gross Margin%, NRR, LTV:CAC, Payback Period

---

### HC-3: AI 제품은 높은 마진을 낼 수 있다

**주장**: "SaaS니까 80% 이상 마진을 기대한다"  
**반증 조건**:

- LLM 추론 비용이 COGS에 포함되었는가 확인
- AI-native 제품의 현실 gross margin: **50–65%** (전통 SaaS 75–85% 대비)
- Inference cost per output이 가격 책정에 반영되지 않으면 → [MARGIN_ILLUSION]

→ 80%+ margin은 AI 제품에서 [OVERCONFIDENT] — "future infrastructure improvement에 의존하는 목표"로 처리.

---

### HC-4: 경쟁사 가격 복사

**주장**: "경쟁사가 $49/month이니 우리도 비슷하게 가자"  
**반증 조건**:

- 경쟁사의 Value Metric이 같은가? (그들은 seats, 우리는 API calls일 수 있음)
- 우리의 COGS 구조가 경쟁사와 같은가?
- 우리의 고객 세그먼트와 ICP가 같은가?

→ 경쟁사 가격 복사는 Value Metric 미정의 + ICP 미확인 = [PREMATURE_PRICING]

---

### HC-5: Freemium이 성장을 보장한다

**주장**: "무료 티어를 만들면 바이럴/PLG로 성장한다"  
**반증 조건**:

- 바이럴 루프(K-factor)가 제품 워크플로우에 embedded되어 있는가?
- 무료 → 유료 전환 경로(paywall moment)가 명확한가?
- 무료 사용자당 infra + support 비용이 정량화되었는가?

→ 루프 없는 Freemium = [CHARITY_TIER_RISK]. 사전에 단위 경제 계산 필수.

---

### HC-6: Outcome-based pricing은 혁신적이다

**주장**: "결과 기반 가격이 고객 친화적이다 — 성공하면 받는 구조"  
**반증 조건**:

- 결과(Outcome)를 계약서에 명확히 정의할 수 있는가?
- Attribution 문제 해결됨 — 우리 제품의 기여도가 측정 가능한가?
- 고객이 결과 측정에 동의하고 데이터 공유에 동의하는가?

→ Attribution 불명확 + 단기 내 검증 불가능 시 → [ARCHITECTURE_MISMATCH]

---

### HC-7: 가격 인상 = 고객 이탈

**주장**: "가격을 올리면 기존 고객이 떠난다"  
**반증 조건**:

- NPS + CSAT 없이 이 주장은 [ASSUMPTION]
- "Underpriced" 신호 확인: LTV:CAC > 5, 고객이 ROI를 쉽게 산출, 대안 없음
- Van Westendorp PSM이나 A/B pricing test 없이 단정 → [UNTESTED]

→ 데이터 없는 가격 동결 = 잠재 수익 포기일 수 있음.

---

## Confidence Calibration Rules

| 주장 유형 | 신뢰도 조건 | 태그 |
|---------|-----------|------|
| Usage-based = right choice | GTM + COGS 미확인 | [PREMATURE — model not selected] |
| Gross margin 80%+ for AI | Inference cost 미포함 | [UNCERTAIN — AI COGS not factored] |
| Freemium drives growth | Viral loop 미설계 | [RISKY — no loop architecture] |
| Outcome-based will work | Attribution 미해결 | [CONFLICT — attribution gap] |
| Price elasticity assumption | No pricing test data | [ASSUMPTION — needs validation] |

---

## Sycophancy Gate (Corpus Pre-step 적용)

주장이 다음 패턴에 해당하면 즉시 교정:

1. **Usage-based 기본 선택** → "GTM 모션 + COGS + 고객 예산 패턴 확인 후 선택. UBP가 맞을 수도 있지만 자동 디폴트 아님."
2. **AI = 높은 마진** → "LLM-native 현실 gross margin은 50–65%. 80%는 인프라 비용 미반영 추정."
3. **Freemium = PLG** → "Freemium은 PLG 모션 중 하나. K-factor embedded + 명확한 paywall moment가 선제 조건."
4. **경쟁사 가격 복사** → "Value Metric + COGS + ICP 3가지 먼저 확인. 숫자 복사는 전략 아님."
5. **가격 인상 = 이탈** → "NRR + NPS + 대안 현황 데이터 없이 이 가정은 [UNTESTED]."

---

## Sources
- T1: 20260412-monetization-theory.md
- OpenView — SaaS Pricing Benchmark 2025
- a16z AI SaaS Unit Economics (2025)
- Paddle SaaS Monetization Trends 2026
- Pricing I/O — Value Metric + Freemium analysis

## Related
- [[projects/Entity/research/20260412-monetization-theory|20260412-monetization-theory]]
- [[projects/Entity/research/20260412-monetization-diagnostic|20260412-monetization-diagnostic]]
- [[projects/Entity/research/20260411-wtp-falsification-criteria|20260411-wtp-falsification-criteria]]
