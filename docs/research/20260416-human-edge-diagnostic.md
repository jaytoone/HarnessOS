---
corpus: human_edge
doc_id: D1
layer: L2
status: draft
date: 2026-04-16
---

# Human-Edge Diagnostic — 13-문항 제품/랜딩페이지 감사 체크리스트

> **세줄결론**
> (판단) 임의 제품·랜딩페이지·광고 크리에이티브에 13문항을 적용해 9 primitives의 결여·과잉·악용을 수치화할 수 있다.
> (근거) 각 문항은 [T1] 9 primitives + System 1/2 기층에 1:1 매핑되며, 관측 가능한 artifact(버튼 문구·가격 표기·CTA 배치)로 scoring.
> (조건) 사전 정보: 제품 카테고리(고관여 vs 저관여), 타겟 세그먼트(개인주의 vs 집단주의), 문화 시장(KR/US/JP). 이 3정보 없으면 HC-3/HC-6 보정 불가.

---

## 사용법

**입력**: 감사 대상 1개 자산 (랜딩페이지 URL / 제품 페이지 / 광고 / 이메일 시퀀스 / 구독 플로우).
**출력**: `[HUMAN_EDGE_AUDIT]` 13-문항 점수 (0/0.5/1) + 종합 점수 + 3대 우선 수정 포인트.

**scoring rubric**:
- `1.0` = 명확히 존재하고 올바르게 적용됨
- `0.5` = 부분적 / 형식만 있음 / 약하게 적용
- `0.0` = 부재 또는 역효과 적용 (다크패턴 포함)

**종합 점수 공식**:
```
raw_score = sum(Q1..Q13) / 13                        # 0.00 ~ 1.00
dark_penalty = 0.15 × count(dark_pattern_flagged)    # Q7, Q9, Q12 다크 플래그 수
final_score = max(0, raw_score − dark_penalty)       # 다크패턴 강한 페이지는 구조적 감점
```

**해석 구간**:
- `≥ 0.75` STRONG — S1 레버 대부분 활성화
- `0.50 ~ 0.74` ADEQUATE — 2~3개 primitives 누락, 전환율 향상 여지 있음
- `0.25 ~ 0.49` WEAK — S2만 자극하는 스펙 중심 페이지, 구조 재설계 필요
- `< 0.25` CRITICAL — S1 트리거 거의 없음 또는 다크패턴 의존

---

## 13-문항 체크리스트

각 문항: `질문 / 어디를 보라(관측 포인트) / 1.0 기준 / 0.5 기준 / 0.0 기준 / 매핑([T1])`

---

### Q1. Scarcity — 희소성 신호가 **실재하고 검증 가능한가**?
- **관측**: 재고 카운터 / 마감 타이머 / "N명 남음" / invite-only 문구 / waitlist 숫자
- **1.0**: 실제 제약(재고·시간·초대권) 존재하며 수치 검증 가능 (e.g., "10/100 seats")
- **0.5**: 희소성 문구만 있고 검증 불가 ("한정 수량", "곧 마감" — 숫자 없음)
- **0.0**: 희소성 신호 전무 / 가짜 희소성 (타이머 리셋 탐지 등)
- **매핑**: [T1 §2.1 Scarcity] / HC-1 Cialdini 재탕 주의
- **DARK FLAG**: 가짜 희소성 (타이머 영구 리셋, 가짜 "sold out") → `Q1 = 0.0 + dark_pattern_flagged`

---

### Q2. Social Proof — 동료·유사 사용자 증명이 **강도 위계에 맞게** 배치되었는가?
- **관측**: 리뷰 수·평점 / 구체 고객사 로고 / UGC 캡처 / "N명이 사용 중" / 사례 스토리
- **1.0**: peer 또는 similar 레벨 증명 ("당신 같은 개발자 500명 사용" / 같은 업종 로고) + 구체 UGC
- **0.5**: 일반 crowd 증명만 ("전 세계 10만 명") 또는 권위 증명만 (고위 직함 coverage)
- **0.0**: 리뷰·UGC·사용자수 표시 전무
- **매핑**: [T1 §2.2 Social Proof] / HC-2 단일실험 일반화 주의
- **주의**: 2020s 메타분석은 peer > authority. 권위만 강조하는 페이지는 0.5 상한.

---

### Q3. Loss Aversion — 얻음보다 잃음 프레임이 **최소 1곳 이상** 사용되었는가?
- **관측**: "놓치면 / 잃어버리면 / 지금 안 하면" 문구, 환불보장(risk reversal), 무료체험 종료 알림
- **1.0**: Loss frame 문구 + risk reversal(환불/보장) + endowment 유도(체험중 탈퇴 차단)
- **0.5**: Loss frame 문구만 있고 risk reversal 없음 (또는 그 반대)
- **0.0**: 전부 gain frame ("얻으세요/추가됩니다") + 환불 보장 미표시
- **매핑**: [T1 §2.3 Loss Aversion] / HC-3 한국 시장 2.25× 직접 이식 주의

---

### Q4. Anchoring — 가격 앵커가 **3단 구조 또는 정가 비교**로 배치되었는가?
- **관측**: 가격 티어 테이블 (3단 권장) / MSRP vs "지금 가격" / "다른 서비스 $X 대비" 비교
- **1.0**: 3단 가격 티어 + 중앙값이 "추천"으로 강조 (decoy effect) 또는 명확 정가-할인가 비교
- **0.5**: 2단 가격만 또는 앵커 없는 단일 가격 (비교 문구만 있음)
- **0.0**: 가격만 달랑 표시, 비교 기준점 전무
- **매핑**: [T1 §2.4 Anchoring]
- **주의**: 앵커가 너무 극단적이면 오히려 불신 → 1.0 기준에서 감점 0.2

---

### Q5. Reciprocity — 구매 이전 "선물" 가치가 **계산 티 나지 않게** 제공되는가?
- **관측**: 무료 리포트 / 템플릿 / 1회 무료 컨설팅 / 가이드북 / 커뮤니티 무료 접근
- **1.0**: 진짜 유용한 무료 콘텐츠 (유료 수준 퀄리티) + 바로 제공 (이메일 submit 없이)
- **0.5**: 무료 콘텐츠는 있으나 이메일 입력 강제 (gated) 또는 피상적 (1페이지 PDF)
- **0.0**: "선물" 제공 전무 또는 "free trial 시작해보세요" 수준 (거래 인센티브)
- **매핑**: [T1 §2.5 Reciprocity] / HC-5 다크패턴 경계 — gated=약한 0.5까지만

---

### Q6. Commitment — Micro-commit 계단이 **점증하는 구조**로 설계되었는가?
- **관측**: 가입 플로우 step 수 / 정체성 선언 UI ("당신은 ___인가요?") / 마이크로 액션 (한 번에 "저장"/"즐겨찾기"/"투표")
- **1.0**: 3~5단 점증 계단 (email → profile → preference → trial → payment), 각 단계 유익 제공
- **0.5**: 2단만 있거나 계단은 있으나 첫 단계부터 카드 요구
- **0.0**: One-shot 결제만 (calendar booking 없이 바로 구매) 또는 commitment 없이 콜드 CTA
- **매핑**: [T1 §2.6 Commitment] / HC-6 KR/JP 집단주의 — "혼자 선언" 허들 고려

---

### Q7. Novelty — 새로움 레버가 **지속 가능하고 피로 안 주는** 방식인가?
- **관측**: "새 기능" 뱃지 빈도 / 업데이트 changelog / 개인화 추천 리프레시
- **1.0**: 의미 있는 업데이트 월 1~2회 + 개인화된 신규 ("당신이 저번에 X 봤으니 Y는 어때요")
- **0.5**: 업데이트는 있으나 일반화된 "새로운 기능들!" 푸시 (개인화 없음)
- **0.0**: 신규 노출 전무 (정체) OR 과도한 고지 (일 1회 이상 "NEW!" 푸시) — 후자는 DARK FLAG
- **매핑**: [T1 §2.7 Novelty-Seeking]
- **DARK FLAG**: 과도한 novelty 피로 강제 → `dark_pattern_flagged`

---

### Q8. Meta-Insight — 사용자가 "나를 더 알게 되는" 순간을 **제공**하는가?
- **관측**: 진단 퀴즈 / 개인 리포트 / "당신의 X 점수" / 타입 분류 결과
- **1.0**: 개인화된 인사이트 결과물 + 공유 가능 형식 (스크린샷/링크) + 2차 액션 연결
- **0.5**: 퀴즈는 있으나 결과가 일반적 (Barnum — 누구에게나 맞는 말) 또는 공유 UX 없음
- **0.0**: 자기 성찰 트리거 전무 (순수 기능 구매 페이지)
- **매핑**: [T1 §2.8 Meta-Insight Hunger] / `wtp.T2` L4→L5 진화 경로

---

### Q9. Status Signaling — 소비·사용이 **사회적 신호로 작동**하는가?
- **관측**: 공개 뱃지 / Tier 시스템 / 기여자 리스트 / 프로덕트 로고 공개 워크스페이스 / "첫 N명" / 레퍼럴 크레딧
- **1.0**: 공개 뱃지/Tier + 상대비교 가능 UI + 타겟 세그먼트에 맞는 신호 강도 (조용한 럭셔리 vs 과시)
- **0.5**: Status 레버는 있으나 세그먼트 miscalibration (과시형을 조용한 럭셔리 층에 적용 등)
- **0.0**: Status 신호 전무 또는 노골적 과시 강요 (사용자 불편)
- **매핑**: [T1 §2.9 Status Signaling] / HC-6 문화 보정
- **DARK FLAG**: 강제 공개(프라이버시 침해 수준) → `dark_pattern_flagged`

---

### Q10. Spending Pocket Alignment — 가격 프레임이 **4조건 중 최소 2개** 만족하는가?
- **관측**: 정당화 프레임(투자·건강·필수·교육) / 분리 계좌 유도(B2B 경비 vs 개인 돈) / 결제 마찰 최소(원클릭) / 정체성 편익
- **1.0**: 4조건 중 3개 이상 명확 ("B2B 경비처리 가능 + 1클릭 결제 + 투자 프레임")
- **0.5**: 2조건 만족
- **0.0**: 0~1조건 — 순수 기능 구매, 지갑 열 프레임 부재
- **매핑**: [T1 §3.2 Spending Pockets] / `wtp.T2` D(WTP) 공식

---

### Q11. Spoon-Feeding — 핵심 가치까지 **"1클릭 체감 거리"**인가?
- **관측**: 첫 가치 전달까지 클릭 수 / 프리셋·템플릿 제공 / AI 자동 설정 / "바로 시작" 버튼
- **1.0**: 가입 후 3클릭 이내 첫 "아하 모먼트" 도달 + 프리셋/템플릿 기본 제공
- **0.5**: 5~7클릭 또는 수동 설정 많음, 가이드는 있음
- **0.0**: 가치 전달까지 많은 셋업 필요 (유저가 직접 조립) — DIY 감성이 오히려 IKEA Effect로 긍정 작동하는 전문가 타겟 제외 시 감점
- **매핑**: [T1 §3.3 Spoon-Feeding]

---

### Q12. Ethical Coefficient — "빠짐"(의존성 유도) 신호가 **없는가**?
- **관측**: 취소 UX 찾기 난이도 / 환불 프로세스 / "삭제하면 이 데이터 다 사라집니다" 공포 프레임 / 강제 자동 갱신 (명시 부족)
- **1.0**: 1클릭 취소 UX + 명확 환불 정책 + 자동 갱신 사전 명시 + 데이터 내보내기 지원
- **0.5**: 취소는 되지만 3클릭 이상 필요 또는 자동 갱신 알림이 작은 글씨로만
- **0.0**: 취소 장벽(고객센터 전화 강요) / 환불 불가 / 공포 프레임 (삭제 후 복구 불가 협박)
- **매핑**: [T1 §4 Ethical_Coefficient] / `wtp.D3` audit / HC-5 규제 리스크
- **DARK FLAG**: Q12 < 1.0 이면 강한 감점 (장기 부메랑 리스크) → `dark_pattern_flagged` (0.0일 때만)

---

### Q13. System 1 vs System 2 Balance — 페이지 상단 60%가 **S1 트리거 중심**인가?
- **관측**: 위에서부터 스크롤 60% 지점 스크린샷 / 첫 화면 hero section
- **1.0**: Hero section이 S1 트리거 (감정·사회 증명·지위·희소성) 중심 + 스펙은 아래 중첩
- **0.5**: Hero section이 S1/S2 혼합 (절반 스펙, 절반 감정)
- **0.0**: Hero부터 스펙·기능 나열 (e.g., "AI-powered 3-pipeline orchestration with hybrid RAG")
- **매핑**: [T1 §1 Core Axiom — 2-system model]
- **주의**: B2B deep-tech는 S2-heavy가 오히려 맞음 → 세그먼트 보정 후 1.0 재평가

---

## 점수 집계 예시

```
| Q  | 요소          | Score | Dark |
|----|---------------|-------|------|
| Q1 | Scarcity      | 0.5   |      |
| Q2 | Social Proof  | 1.0   |      |
| Q3 | Loss Aversion | 1.0   |      |
| Q4 | Anchoring     | 0.5   |      |
| Q5 | Reciprocity   | 0.5   |      |
| Q6 | Commitment    | 1.0   |      |
| Q7 | Novelty       | 0.5   |      |
| Q8 | Meta-Insight  | 0.0   |      |
| Q9 | Status        | 0.5   |      |
| Q10| Spending Pkt  | 0.5   |      |
| Q11| Spoon-Feed    | 1.0   |      |
| Q12| Ethical Coef  | 0.5   |      |
| Q13| S1/S2 Balance | 0.5   |      |
|----|---------------|-------|------|
| raw_score = 8.0 / 13 = 0.615                 |
| dark_penalty = 0.15 × 0 = 0                  |
| final_score = 0.615 → ADEQUATE              |
| Top 3 수정 포인트:                           |
|   1. Q8 Meta-Insight (0.0) — 진단 퀴즈 추가  |
|   2. Q1 Scarcity (0.5) — 실재 카운터로 업그레이드 |
|   3. Q4 Anchoring (0.5) — 3단 티어로 재구성  |
```

## 13-문항 레버리지 매트릭스 (수정 우선순위 판단)

| 현재 점수 | 수정 난이도 (LOW=H / MID=M / HIGH=L) | 우선순위 |
|---|---|---|
| Q1, Q3, Q4 (가격·희소성·손실) | LOW — 카피·가격 표기 변경 | ★★★ 먼저 |
| Q5, Q7, Q11 (선물·새로움·1클릭) | MID — 자산 제작 / 플로우 수정 | ★★ |
| Q2, Q9, Q8 (증명·지위·메타인사이트) | HIGH — UGC 수집 / 시스템 구축 | ★ (장기) |
| Q10, Q13 (지갑·S1 균형) | MID — 포지셔닝 재구성 | ★★ |
| Q6, Q12 (커밋·윤리) | LOW~MID — 플로우 재설계 | ★★★ 먼저 |

## Scope Gate (감사 적용 경계)

모두 YES → D1 적용:
- 대상이 **웹/앱 화면 또는 이메일·광고 크리에이티브**인가?
- 타겟이 **System 1 반응 비중 높은 의사결정**인가? (고관여 B2B deep-tech 제외)
- 문화 맥락(KR/US/JP 등)과 세그먼트(개인주의 vs 집단주의) 정보를 **알고 있는가**?

하나라도 NO → 적용 중단. 대체:
- B2B 복잡 의사결정 → MEDDIC / Challenger Sale 프레임
- 제품 구조·포지셔닝 수준 진단 → `wtp.D1` + `monetization.D1`
- 순수 UX 접근성 진단 → WCAG / HIG 기준

## Sycophancy Checks (D1 전용 — T1 보완)

| ID | 질문 |
|---|---|
| D1-HC-1 | 13문항 점수를 **합산만** 하고 다크 플래그 패널티를 빠트리지 않았는가? |
| D1-HC-2 | 문화 보정 없이 KR 페이지에 US 기준 (loss aversion 2.25×) 직접 적용하지 않았는가? |
| D1-HC-3 | B2B deep-tech에 S1 중심 Q13 점수를 그대로 적용해 0.0 주지 않았는가? |
| D1-HC-4 | 세그먼트 miscalibration을 간과 — 조용한 럭셔리 타겟에 과시형 Q9 기대치 적용하지 않았는가? |
| D1-HC-5 | 다크패턴(Q7/Q9/Q12)을 "고급 설득 기법"으로 포장하지 않았는가? |
| D1-HC-6 | 13문항이 **관측 가능 증거**(버튼/문구/플로우)에 근거했는가, LLM의 "느낌"으로 매겼는가? |
| D1-HC-7 | 우선순위 3 제안이 **레버리지 매트릭스**(현재점수 × 수정난이도) 기준인가, 단순 최저점 기준인가? |

## Gap Patterns (D1 진단 시그널)

| 패턴 | 신호 | 수정 방향 |
|---|---|---|
| all_system_2 | Q13=0.0 + Q1/Q3 대부분 0.0 | Hero section 전면 재구성, 감정/희소성 레이어 추가 |
| dark_dominant | dark_pattern_flagged ≥ 2 | 규제 리스크 + 신뢰 손상 — 즉시 수정 |
| weak_spoon | Q11=0.0 + Q6=0.0 | Onboarding flow 리설계, 프리셋/템플릿 도입 |
| vanity_signal | Q2=1.0 + Q8=0.0 + Q9=1.0 | 증명은 있으나 사용자 자신 성찰 없음 — 퀴즈·리포트 도입 |
| pay_friction | Q10=0.0 + Q11=0.5 | 결제 단계 + 정당화 프레임 동시 개선 |
| status_misfit | Q9=0.5 + 타겟=조용한럭셔리 | 노골 과시 UI 제거, 인사이더 신호로 전환 |

## RWR (자연어 → D1 진단 매핑)

- "전환율 낮아요" → 전체 13문항 + Gap Pattern 매칭
- "랜딩 페이지 점검" → Q1/Q2/Q4/Q13 우선
- "가격 페이지 봐줘" → Q4/Q10/Q12 집중
- "결제 이탈 많음" → Q6/Q11/Q12 (+ pay_friction pattern)
- "바이럴 안 퍼짐" → Q8/Q9/Q2 (+ 실제 UGC·공유 UX 점검)
- "다크패턴 있나" → Q7/Q9/Q12 + dark_pattern_flagged 집계

## Output Template (audit 결과 포맷)

```
[HUMAN_EDGE_AUDIT]
target: <URL / page_name>
segment: <ICP> | culture: <KR/US/JP> | involvement: <high/low>

scores:
  Q1..Q13: [0.5, 1.0, 1.0, 0.5, 0.5, 1.0, 0.5, 0.0, 0.5, 0.5, 1.0, 0.5, 0.5]
raw_score: 0.615
dark_penalty: 0.00 (flagged: [])
final_score: 0.615 → ADEQUATE

top_3_fix:
  1. [Q8 Meta-Insight] 0.0 → 진단 퀴즈 섹션 추가, 개인 리포트 결과 공유 UX — 난이도 HIGH
  2. [Q1 Scarcity]    0.5 → 재고 카운터 또는 waitlist 숫자 실재화 — 난이도 LOW
  3. [Q6 Commitment]  — 1.0 유지, 추가 최적화 불요

gap_patterns_detected: [vanity_signal]
cultural_notes: KR segment — Q6 저커밋 계단에 "혼자 튀기 어색함" 완화 필요 (집단 증명 동반)

sycophancy_check: D1-HC-1..7 PASS
related: [T1] human-edge-theory / [wtp.D3] bbaijjim audit (Ethical_Coefficient 교차)
```

---
- [T1] 20260416-human-edge-theory.md — 9 primitives + user outline mapping
- [X-GROUNDED: wtp.T2] 20260411-wtp-theory-v2.md — D(WTP) 공식, L1-L5 identity gap
- [X-GROUNDED: wtp.D3] 20260411-wtp-bbaijjim-audit-framework.md — Ethical_Coefficient audit
- [X-GROUNDED: monetization.D1] 20260412-monetization-diagnostic.md — 가격 모델 진단 (Q4/Q10 교차)

## Related
- [[projects/Entity/research/20260416-human-edge-theory|20260416-human-edge-theory]]
- [[projects/Entity/research/20260411-wtp-bbaijjim-audit-framework|20260411-wtp-bbaijjim-audit-framework]]
- [[projects/Entity/research/20260412-monetization-theory|20260412-monetization-theory]]
- [[projects/Entity/research/20260412-monetization-diagnostic|20260412-monetization-diagnostic]]
- [[projects/Entity/research/20260412-marketing-growth-corpus-draft|20260412-marketing-growth-corpus-draft]]
