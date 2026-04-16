---
corpus: human_edge
doc_id: V1
layer: L3
status: draft
date: 2026-04-16
---

# Human-Edge Experiment V1 — Pain of Payment × Mental Accounting A/B

> **세줄결론**
> (판단) 결제 친화 + 분리 계좌 프레임의 **2×2 factorial A/B**로 human-edge 레버가 자사 시장에서 재현되는지 검증한다.
> (근거) Prelec-Loewenstein(1998) Red-and-Black 수용 + Thaler(1985) mental accounting — 실험실 ES 0.4~0.6, 실거래 ES 기대 0.15~0.35.
> (조건) 표본 n ≥ 각 셀 400 (power 0.8, α 0.05, 최소검출 효과 0.20); 4주 기간; 단일 가격대 제품(주거 고정요인); 사전 등록(pre-registration) 필수.

---

## 1. 목적과 가설

**1차 가설** (H1):
- Pain of Payment 감소(원클릭 결제) + Mental Accounting 분리 프레임(투자 계좌 프레임) **교호 효과**가 있다.
- 두 레버 단독보다 조합 시 CR↑ > 단독 합 (superadditive).

**H0**: 두 요인이 독립 효과만 가진다 (additive 또는 무효).

**2차 가설** (탐색적):
- 집단주의 KR 세그먼트에서 "우리 구성원의 투자 프레임"이 개인 투자 프레임보다 강하다.
- Pain 감소 효과가 고가(>50k KRW) 제품에서 저가보다 크다.

## 2. 2×2 Factorial Design

| Cell | Pain of Payment | Mental Accounting Frame |
|------|:---------------:|:-----------------------:|
| A (control)  | 표준 (3-step 결제) | 없음 ("가격 29,000원") |
| B (pain↓)    | 원클릭 결제 (저장 카드 1-tap) | 없음 |
| C (frame)    | 표준 | 투자 프레임 ("나에게 투자 29,000원 — 6개월 할부 월 4,833원") |
| D (both)     | 원클릭 | 투자 프레임 |

**측정 outcome**:
- Primary: 구매 전환율 (CR) = 결제 완료 / 결제 페이지 도달
- Secondary:
  - AOV (평균 결제액)
  - Time-to-decision (페이지 진입 → 결제 버튼 클릭)
  - 7일 후 환불률
  - 30일 재구매율

## 3. 표본 / Power Analysis

```
가정:
  baseline CR (Cell A) = 15%
  최소 검출 효과 = 3%p (15% → 18%, 상대 20%↑)
  α = 0.05, power = 0.80, 2-tailed

n per cell = 2 × [(z_α/2 + z_β)² × p̄ × (1-p̄)] / effect²
           = 2 × [(1.96 + 0.84)² × 0.165 × 0.835] / 0.03²
           ≈ 2 × 7.84 × 0.138 / 0.0009
           ≈ 2 × 1204
           ≈ 약 400 per cell
```
- **표본 min**: 4 × 400 = 1,600 페이지 방문 (결제 페이지 도달 기준)
- **기간**: 주 400 방문 × 4주 = 1,600 (트래픽 확보 가능해야 실행)
- **랜덤 할당**: 세션 기반 hash(user_id % 4) → Cell A/B/C/D 균등 분산

## 4. 사전 등록 (Pre-registration) — T4-HC 강제 준수

실험 시작 **전에** 다음을 잠금:
1. 1차·2차 가설 문구 고정 (HARKing 방지)
2. 측정 지표 precision / 측정 기간 / 제외 기준 (bot / refund / 연속 동일 IP 등)
3. Statistical analysis plan:
   - Primary: 2-way ANOVA (Pain × Frame) on CR
   - Interaction effect p < 0.05 → H1 지지
   - Multiple comparison: Bonferroni (6 pairwise)
4. 조기 중단 조건: 각 셀 n ≥ 300 + p < 0.01 → 조기 성공 가능
5. 중간 peeking 금지 (주 1회 점검 OK, 가설 변경 금지)

## 5. Confounding 통제

T4 §3 alternative explanations 대응:

| 위협 | 통제 |
|---|---|
| Quality Signal | 동일 제품, 동일 가격, 동일 가치 설명 — 포장만 A/B/C/D |
| Selection | 랜덤 할당, 세션 hash 기반 |
| Expectation | double-blind 불가(UI 차이 보임) → 대신 pre-registered 지표만 집계 |
| Novelty (Hawthorne) | 관찰 알림 없음 (사용자 inform 없음, 윤리 규정 허용 범위 내) |

## 6. 윤리 · 규제 체크

- KR 개인정보보호법 + GDPR: 세션 hash 익명화, 개인 식별 정보 분석 금지
- 2024 KR 소비자법 개정: "투자 프레임"이 오인 유도 소지 검토 — "투자"가 금융상품 투자로 해석 가능한 맥락 피함
- [X-GROUNDED: wtp.D3] Ethical_Coefficient audit — 실험 자체가 사용자 후회 유발하지 않음 확인
- 취소/환불 UX 4개 셀 모두 동일 (Q12 중립)

## 7. Acceptance Criteria (corpus.human_edge promotion 조건)

**실험 결과가 다음 만족하면 T4 HC 통과 + corpus.human_edge 전체 draft→stable 승격 권고**:

| 결과 | 해석 | 후속 |
|---|---|---|
| 셀 D CR ≥ 셀 A CR × 1.25 AND interaction p < 0.05 | H1 강하게 지지 | T1/D1/S1 stable 승격 + V2 (다른 primitive 조합) 후속 |
| 셀 D CR > 셀 A CR + 3%p AND interaction p < 0.10 | H1 약하게 지지 | T1 stable, D1/S1 draft 유지 + 추가 V2 필요 |
| Pain 단독 OR Frame 단독만 유의, interaction 무효 | additive model | primitive 독립 가정 유지 |
| 모든 셀 차이 무효 (p > 0.05) | **현 시장 replication 실패** | T4 §4 Dead-zone 업데이트 — 해당 세그먼트에서 primitive 무효 기록, draft 유지 |

## 8. 실행 체크리스트 (4주 타임라인)

```
Week 0 (준비):
  [ ] Pre-registration 문서 잠금 (OSF 또는 사내 timestamped)
  [ ] 4개 셀 UI 변형 퍼블리싱 (QA 완료)
  [ ] 트래픽 할당 로직 테스트 (hash 분산 균등 확인)
  [ ] 집계 대시보드 준비 (일별 누적, 셀별 CR)
  [ ] IRB/내부 승인 (해당 시)

Week 1-4 (실행):
  [ ] 주 1회 peek (가설 변경 금지, sample size 모니터만)
  [ ] Data quality 체크 (bot, 중복, refund 제외)

Week 5 (분석):
  [ ] Pre-registered analysis 실행 (2-way ANOVA, Bonferroni)
  [ ] 결과 리포트: CR 매트릭스 + interaction plot + CI
  [ ] Acceptance 매트릭스로 해석 → 승격 결정
```

## 9. V1-HC (실험 설계 자체 sycophancy checks)

| ID | 질문 |
|---|---|
| V1-HC-1 | n per cell 계산이 **실제 달성 가능한 트래픽**에 기반했는가? (exaggerated n 금지) |
| V1-HC-2 | Pre-registration 없이 실행하지 않았는가? HARKing 유혹 차단했는가? |
| V1-HC-3 | Interaction effect 검정이 적절한 통계 방법(2-way ANOVA, GLM)을 사용하는가? |
| V1-HC-4 | "투자 프레임" 문구가 규제 위반(오인 유도) 가능성 없는가? — 법무 검토 완료? |
| V1-HC-5 | 조기 중단 조건에서 Peeking 오류(과도한 중간 검정) 방지되는가? |
| V1-HC-6 | 실패 결과(무효)도 T4 업데이트로 **자산화** 되는가, 서랍 속으로 사라지지 않는가? |
| V1-HC-7 | WEIRD 표본인가 KR 실거래인가? 표본 특성 reporting 포함? |

## 10. 후속 실험 로드맵 (V2~V4)

V1 결과 기반 다음 실험:
- **V2**: Scarcity × Social Proof 교호효과 (재고 카운터 × 리뷰 노출)
- **V3**: Loss Aversion × Anchoring 교호효과 (환불 보장 × 3단 가격 티어)
- **V4**: Commitment × Meta-Insight 순서 효과 (진단 전 vs 후 계단 효율성)

각 V는 pre-registered 2×2 factorial + 동일 HC 체크리스트.

---
- [T1] 20260416-human-edge-theory.md — 2.3 Loss Aversion, 3.2 Spending Pockets (실험 배경)
- [T4] 20260416-human-edge-falsification.md — §3 Alternative Explanations, §4 Dead-zone (설계 제약)
- [D1] 20260416-human-edge-diagnostic.md — Q10 Spending Pocket (실험 조작 변수와 연결)
- [S1] 20260416-human-edge-playbook.md — Revenue 단계 Anchoring × Loss Aversion 교호 가설 (V3 후속)
- [X-GROUNDED: wtp.V1] 20260411-wtp-social-amplifier-experiment-v2.md — Social Amplifier 실험 프로토콜 교차
- [X-GROUNDED: monetization.D1] 20260412-monetization-diagnostic.md — Pain of Payment 가격 진단 연결

## References
- Prelec, D., & Loewenstein, G. (1998). The Red and the Black: Mental Accounting of Savings and Debt. *Marketing Science* 17.
- Thaler, R. (1985). Mental Accounting and Consumer Choice. *Marketing Science* 4.
- Gelman, A., & Loken, E. (2014). The Statistical Crisis in Science (on pre-registration / garden of forking paths). *American Scientist* 102.
- Simmons, J., Nelson, L., & Simonsohn, U. (2011). False-Positive Psychology. *Psychological Science* 22.

## Related
- [[projects/Entity/research/20260416-human-edge-falsification|20260416-human-edge-falsification]]
- [[projects/Entity/research/20260416-human-edge-theory|20260416-human-edge-theory]]
- [[projects/Entity/research/20260416-human-edge-playbook|20260416-human-edge-playbook]]
- [[projects/Entity/research/20260416-human-edge-diagnostic|20260416-human-edge-diagnostic]]
- [[projects/Entity/research/20260411-wtp-social-amplifier-experiment-v2|20260411-wtp-social-amplifier-experiment-v2]]
- [[projects/Entity/research/20260412-monetization-theory|20260412-monetization-theory]]
- [[projects/Entity/research/20260412-monetization-diagnostic|20260412-monetization-diagnostic]]
- [[projects/Entity/research/20260412-monetization-falsification|20260412-monetization-falsification]]
