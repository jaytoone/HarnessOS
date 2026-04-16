---
corpus: human_edge
doc_id: S1
layer: L2
status: draft
date: 2026-04-16
---

# Human-Edge Playbook — 9 Primitives × AARRR 전환 퍼널 블루프린트

> **세줄결론**
> (판단) 9 primitives를 AARRR 5단계에 **중복 없이** 분산 배치해야 전환 CR ≥ 25~40% 구조가 만들어진다.
> (근거) 단계별 유저 의사결정 비용이 달라 — Awareness 단계에 Loss Aversion을 쏘면 거부감, Retention 단계에 Scarcity를 쓰면 바이럴 동력 손상.
> (조건) 제품 카테고리(고관여 / 저관여), 비즈니스 모델(구독 / 일회성), 타겟 문화(개인주의 / 집단주의) — 3변수로 프리셋 선택.

---

## 1. 9 × AARRR 레버리지 매트릭스

각 primitive가 **어느 단계에 가장 레버리지가 큰가** (●=주력 ○=보조 —=기피):

| Primitive                | A Awareness | A Activation | R Retention | R Revenue | R Referral |
|--------------------------|:-----------:|:------------:|:-----------:|:---------:|:----------:|
| 2.1 Scarcity             | ●           | ○            | —           | ○         | —          |
| 2.2 Social Proof         | ●           | ●            | ○           | ●         | ●          |
| 2.3 Loss Aversion        | —           | ○            | ●           | ●         | —          |
| 2.4 Anchoring            | ○           | —            | —           | ●         | —          |
| 2.5 Reciprocity          | ●           | ●            | ○           | —         | ●          |
| 2.6 Commitment           | ○           | ●            | ●           | ○         | —          |
| 2.7 Novelty              | ●           | ○            | ●           | —         | ○          |
| 2.8 Meta-Insight         | ●           | ●            | ○           | ○         | ●          |
| 2.9 Status Signaling     | ○           | —            | ●           | ○         | ●          |

**원칙** (why this shape):
- **Awareness**: 정보 과잉 → E(에너지 절약) 레버 우위 (Social Proof / Reciprocity / Novelty / Meta-Insight 가벼운 무료 훅)
- **Activation**: "아하 모먼트"까지 마찰 최소화 → Commitment 계단 + Meta-Insight 개인화 결과물
- **Retention**: 반복 사용 트리거 → Novelty + Status + Loss Aversion(이탈 비용)
- **Revenue**: 가격 수용 순간 → Anchoring + Social Proof(리뷰) + Loss Aversion(환불 보장)
- **Referral**: 지위·관계 자본 → Status + Meta-Insight 공유 + Reciprocity + Social Proof

**기피 셀 주의**:
- Awareness × Loss Aversion: 첫 인상에 "놓치면 후회" 프레임 = 광고 회피 자극
- Activation × Anchoring: 신규 사용자가 기준점이 없어 앵커 효과 미약
- Retention × Scarcity: 반복 유저에게 마감 반복은 피로 + 신뢰 손상
- Referral × Loss Aversion: 손실 프레임으로 추천 유도 = 관계 손상 리스크

## 2. 단계별 블루프린트 (3 시나리오)

### Scenario A — B2B SaaS (고관여, 구독, 개인주의 혹은 팀)

```
A [Awareness]       → Social Proof (팀 로고 + "개발팀 X명이 사용") + Reciprocity (오픈소스 툴 / 가이드) + Meta-Insight (무료 diagnostic)
A [Activation]      → Commitment 3단 (email → workspace → connect_integration → first_value) + Meta-Insight (팀 분석 리포트)
R [Retention]       → Novelty (주간 인사이트 리포트 개인화) + Status (팀 내 활동 리더보드)
R [Revenue]         → Anchoring (3단 가격 Team/Business/Enterprise) + Social Proof (도입 사례 ROI) + Loss Aversion (무료→유료 전환 시 데이터 이관 리스크 최소화 보장)
R [Referral]        → Status (팀 레벨 뱃지 공개) + Meta-Insight (팀 리포트 공유 UX) + Reciprocity (친구 초대 시 양쪽 크레딧)
```

**Anti-pattern 시그널**:
- Hero section에 기능 스펙만 나열 → [Awareness Social Proof 부족]
- Trial 기간 중 결제 정보 요구 → [Activation Commitment 과도 점프]
- 가격 티어 단일 → [Revenue Anchoring 부재]

### Scenario B — D2C Consumer (저~중관여, 일회성, 집단주의 KR 전형)

```
A [Awareness]       → Scarcity (한정판/기간) + Social Proof (UGC 캡처 + 리뷰 별점) + Novelty (이번 주 신상)
A [Activation]      → Reciprocity (첫 구매 쿠폰) + Commitment (원클릭 회원 + wishlist)
R [Retention]       → Novelty (주간 신상 알림) + Loss Aversion (쿠폰 만료 D-day) + Social Proof (친구들 최근 구매)
R [Revenue]         → Anchoring (정가-세일가) + Loss Aversion (무료배송 임계 + 환불 정책) + Social Proof (구매자 리뷰)
R [Referral]        → Reciprocity (친구 추천 양쪽 크레딧) + Status (인플루언서 등급) + Social Proof (친구 활동 알림)
```

**KR 특수 보정 (집단주의 레버 가중)**:
- Q6 Commitment 계단에 "혼자 선언" 대신 "친구랑 같이" 레이어 (동시 가입 프로모션)
- Q9 Status는 "티어/배지"보다 "내 그룹 안에서 위치" 프레임이 효과 높음
- Q5 Reciprocity는 "개인 선물"보다 "우리 회원에게만" 프레임이 수용력 높음

### Scenario C — Community/Knowledge Product (고관여, 구독 + UGC, 하이브리드)

```
A [Awareness]       → Meta-Insight (진단 퀴즈 "당신은 어떤 타입") + Social Proof (멤버 활동 피드 공개) + Reciprocity (무료 월간 리포트)
A [Activation]      → Commitment (프로필 작성 → 관심사 선택 → 첫 글 작성) + Novelty (온보딩 주간 챌린지)
R [Retention]       → Status (기여 레벨 + 뱃지) + Novelty (주간 큐레이션) + Loss Aversion (활동 streak)
R [Revenue]         → Anchoring (무료/프리미엄 2단) + Status (프리미엄 전용 인사이더 배지) + Social Proof (프리미엄 멤버 수 공개)
R [Referral]        → Status (초대 가능 슬롯 — 프리미엄만) + Meta-Insight (내가 읽은 월간 리포트 공유)
```

## 3. 발화 예시 (레이어별 카피 패턴)

### Awareness — Social Proof × Novelty
- ❌ "AI 기반 생산성 플랫폼, 지금 시작하세요"
- ✅ "이번 주 2,847팀이 새로 시작 — 특히 시리즈 A 스타트업 PM들이 쓰는 방식"

### Activation — Commitment × Meta-Insight
- ❌ "회원가입 하시고 시작해주세요 (14개 필드)"
- ✅ "1분 진단: 당신의 팀 생산성 타입은? → 결과는 이메일만 입력하면 즉시"

### Retention — Novelty × Status
- ❌ "새로운 기능이 추가되었습니다"
- ✅ "이번 주 당신이 쓰지 않은 3개 기능 — 비슷한 사용자들이 가장 많이 쓴 것부터"

### Revenue — Anchoring × Loss Aversion
- ❌ "Pro 플랜: 월 $29"
- ✅ "현재 Free → Pro 전환 시: 작업 히스토리 90일 → 무제한 + 팀 초대 + $199 상당 템플릿 (취소 30일 내 전액 환불)"

### Referral — Status × Meta-Insight
- ❌ "친구를 초대하고 $10 받으세요"
- ✅ "당신의 2026 생산성 리포트 — 팀원 3명에게 공유하면 premium 2개월 추가 (초대받은 분에게도)"

## 4. Kill Switch — 언제 레버를 빼야 하는가

| 신호 | 제거할 레버 | 이유 |
|---|---|---|
| 환불율 > 15% | Scarcity 강도 낮춤 | 충동구매 유도 후 후회 |
| NPS 하락 + 지원 티켓 "취소 어려움" | 전체 Loss Aversion | "빠짐"(dependency) 감지 |
| 바이럴 K-factor 하락 | 과도한 Novelty | 피로 누적 + 업데이트 불신 |
| 브랜드 검색량 감소 + SNS 조롱 | Status Signaling 공개 강도 | 조용한 럭셔리 층 이탈 |
| 이메일 unsubscribe 급증 | Reciprocity 빈도 | 선물이 "광고 가장"으로 간파 |
| 유료 전환 rate 하락 | Anchoring 극단치 | 비현실 앵커로 전체 불신 |

## 5. 측정 지표 (각 primitive당 primary metric)

| Primitive | 측정 |
|---|---|
| Scarcity | 클릭률 (첫 노출 10분 내 CTR) |
| Social Proof | 체류 시간 + scroll depth at proof section |
| Loss Aversion | 환불 보장 문구 노출 후 결제 완료율 |
| Anchoring | 중간 티어 선택 비율 (decoy 성공률) |
| Reciprocity | 무료 가치 소비 후 후속 액션 전환율 |
| Commitment | 계단 단계별 drop-off 차이 |
| Novelty | 재방문 7일 retention |
| Meta-Insight | 진단/리포트 공유 rate |
| Status Signaling | 뱃지/티어 획득 후 engagement 증감 |

## 6. Scope Gate

적용 조건 (모두 YES):
- 제품이 **AARRR 루프**를 가지고 있는가? (일회성 단건 ≠ 적용)
- 타겟이 **System 1 반응 비중** 높은가? (고관여 B2B deep-tech는 SLG/MEDDIC 우선)
- 3변수(카테고리 / 모델 / 문화) 알고 있는가?

하나라도 NO → [monetization.S1] 또는 [marketing_growth.S1] 교차 라우팅.

## 7. Sycophancy Checks (S1 전용)

| ID | 질문 |
|---|---|
| S1-HC-1 | 9 primitives를 **모든 단계에 전부** 뿌리지 않았는가? (기피 셀 존재 — 과잉은 피로) |
| S1-HC-2 | 3 시나리오(B2B/D2C/Community) 중 맞지 않는 프리셋을 강제 적용하지 않았는가? |
| S1-HC-3 | KR 타겟에 US 카피 그대로 직역하지 않았는가? (집단주의 보정 미반영) |
| S1-HC-4 | Kill Switch 조건을 가정에 기초하지 않고 **실측 지표**로 설정했는가? |
| S1-HC-5 | 다크패턴(강제 자동갱신, 취소 장벽)을 "Loss Aversion 활용"으로 포장하지 않았는가? |
| S1-HC-6 | [T1/D1] cross-grounding 없이 S1만 단독 인용하고 있지 않는가? |
| S1-HC-7 | 단일 성공 사례(Slack/Notion)를 일반법칙으로 외삽하지 않았는가? |

## 8. Gap Patterns

| 패턴 | 신호 | 수정 |
|---|---|---|
| all_stages_same_lever | 모든 단계에 Scarcity만 | primitive 5~7개 분산 재배치 |
| funnel_no_meta | Meta-Insight 레버 전무 | Awareness·Referral에 진단 레이어 추가 |
| referral_loss_pressure | Referral에 Loss 프레임 | 관계 자산 손상 위험 — Status/Reciprocity 전환 |
| activation_anchor_waste | Activation 단계에 가격 앵커 | Anchor는 Revenue 단계로 이동 |
| kill_switch_missing | Kill switch 지표 부재 | 6개 최소 설정 강제 |

## 9. RWR

- "전환 퍼널 만들어야" → Scenario A/B/C 중 선택 → 매트릭스 적용
- "우리 활성화가 낮음" → Activation 컬럼 재설계 (Commitment + Meta-Insight)
- "유지가 안 됨" → Retention 컬럼 재설계 (Novelty + Status + Loss Aversion)
- "리퍼럴 동력 없음" → Referral 컬럼 재설계 (Status + Meta-Insight 공유 + Reciprocity)
- "인도네시아 시장인데" → S1-HC-3 문화 보정 (집단주의/인플루언서 가중)
- "가격 안 먹힘" → Revenue 컬럼 (Anchoring 3단 + Social Proof 사례 + Loss Aversion 환불보장)

---
- [T1] 20260416-human-edge-theory.md — 9 primitives 원리
- [D1] 20260416-human-edge-diagnostic.md — 13-문항 감사 (S1 배포 전후 진단 기준)
- [X-GROUNDED: wtp.S1] 20260411-wtp-seed-cohort-strategy.md — cohort 설계 교차
- [X-GROUNDED: marketing_growth.S1] 20260412-marketing-growth-loop-playbook.md — viral loop archetype
- [X-GROUNDED: monetization.S1] 20260412-monetization-playbook.md — pricing 플레이북 (Revenue 컬럼 교차)

---

### Note: Empirical Caveats (L5)
- **현재 매트릭스**: 이론 기반 권고 (AARRR × primitive 상관관계)
- **검증 필요**: 실거래 A/B 테스트 3건 이상 → 권고 재검증
- **제한**: 동일 카테고리 내 재현 ≠ 타 카테고리 일반화 가능
- **실행**: Phase V1 실험 완료 후 매트릭스 업데이트 필수

## Related
- [[projects/Entity/research/20260412-marketing-growth-corpus-draft|20260412-marketing-growth-corpus-draft]]
- [[projects/Entity/research/20260412-marketing-growth-loop-playbook|20260412-marketing-growth-loop-playbook]]
- [[projects/Entity/research/20260412-marketing-growth-diagnostic|20260412-marketing-growth-diagnostic]]
- [[projects/Entity/research/20260416-human-edge-diagnostic|20260416-human-edge-diagnostic]]
- [[projects/Entity/research/20260412-marketing-growth-theory|20260412-marketing-growth-theory]]
- [[projects/Entity/research/20260416-human-edge-theory|20260416-human-edge-theory]]
- [[projects/Entity/research/20260412-monetization-theory|20260412-monetization-theory]]
- [[projects/Entity/research/20260412-monetization-playbook|20260412-monetization-playbook]]
