# VALUE GAP 의사결정 플레이북 — 13회 연구 종합

**Date**: 2026-04-11
**Method**: live-inf iter 14/∞ — 전체 종합
**Synthesizes**: iter 1-13 전체 (이론 → 검증 → 제품 → 실행)
**Read time**: 10분
**Purpose**: Career Mirror MVP build/no-build 의사결정 + 첫 6개월 실행 계획

---

## 핵심 주장 (1분 버전)

1. **WTP는 정체성 갭 해소 비용이다.** 사람이 "되고 싶은 나"와 "지금의 나" 사이의 거리를 인식하는 순간, 그 거리를 줄여주는 제품에 대한 지불의사가 발생한다. 기능적 효용이 아니라 정체성 위협이 프리미엄 가격의 근원이다.
2. **갭은 5단계 계층(L1-L5)으로 구분된다.** 소셜 소속감(L1) → 단순 위임(L2) → 정체성 위임(L3) → 아는 미지(L4) → 모르는 미지(L5). 상위 레벨일수록 WTP가 높고 비탄력적이다.
3. **갭 공개 순간이 곧 판매다.** 제품 피처를 설명하는 것보다 "당신이 몰랐던 갭"을 보여주는 것이 더 강력한 전환 도구다. 공개 이후의 모든 과정은 이행(fulfillment)이다.
4. **사회적 가시성은 독립 드라이버가 아니라 증폭기다.** 기능적 갭이 타인에게 보이는 정도가 WTP를 곱한다. 단, L1(소셜 포지션)만은 독립적으로 WTP를 생성한다.
5. **지속가능한 WTP와 순간적 WTP는 분리된다.** 착취적 설계는 순간 WTP를 극대화하지만 장기 WTP를 훼손한다. 건강한 제품은 "각 세션 후 사용자가 더 유능해진다."

**기존 이론과의 차이 (1문장)**: JTBD는 "어떤 일을 해결하나"를 묻지만, VALUE GAP은 "어떤 정체성 위협을 해소하나"를 묻는다 — 동일 기능의 제품이 갭 공개 프레이밍만으로 2-3배 WTP 차이를 만든다고 예측한다.

**가장 중요한 통찰**: 소비자는 자신이 모르는 것을 쇼핑할 수 없다. 따라서 가장 강력한 마케팅은 피처 설명이 아니라 갭 공개다.

### 수요 공식 (v2, 최종)

```
Gap_Intensity     = Functional_Gap + Social_Position_Gap
D(WTP)_instant    = [Gap_Intensity x Attainability] x [Social_Amplifier]
D(WTP)_sustainable = D(WTP)_instant x Ethical_Coefficient
```

- **Functional_Gap**: 제품 없이는 해결 불가능한 기능적/인식론적 격차
- **Social_Position_Gap**: 소속/지위/인정 관련 사회적 격차 (L1의 독립 WTP 설명)
- **Attainability**: 고객 자신의 변화 없이 제품이 갭을 닫는 정도 (높을수록 WTP 상승)
- **Social_Amplifier**: 기능적 갭이 중요한 타인에게 보이는 정도 (신호 전달 계수)
- **Ethical_Coefficient**: 장기 잉여 할인 인자 (0,1]. 착취적 설계일수록 0에 수렴

### 이론의 적용 범위 (iter 11 확정)

VALUE GAP은 다음 세 조건을 **모두** 충족하는 구매에만 적용된다:
1. **고관여**: 구매 전 비교/탐색 행동이 있고, 결과가 자아 평가에 영향
2. **정체성 인접**: "이 제품을 쓰는 나는 어떤 사람인가?"가 의미 있는 질문
3. **비독점 시장**: 대안이 존재

적용 밖: 생필품 보충, 충동 구매, 순수 상품재, 제도적 조달, 중독/강박 구매

---

## 이론 신뢰도 평가

| 구성요소 | 신뢰도 | 근거 |
|---|---|---|
| L1-L5 진단 계층 | **HIGH** | iter 4 한국 제품 감사에서 비자명한 진단 생성 (퍼블리/리멤버/클래스101). 설명력 확인 |
| 갭 공개 = 판매 | **HIGH** | Schwartz(1966) 문제 인식 세그멘테이션의 정체성 재프레이밍. 구조적으로 타당 |
| Anti-빠짐 윤리 기준 | **HIGH** | "세션 후 더 유능해지는가?" Fogg/Noggle 이중 테스트. 명확하고 실행 가능 |
| 수요 공식 (v2) | **MEDIUM** | 내부 모순 3개를 iter 9에서 수정했으나 경험적 검증 0건. 공식 자체는 미검증 |
| Social_Amplifier 곱셈 구조 | **LOW** | iter 7 실험 설계만 존재, 실행 0. 곱셈인지 덧셈인지 미확인 |
| ICP: 정체성 이동성 기준 | **MEDIUM** | 이론적으로 타당하나 인터뷰 0건. 실제 ICP가 이 기준으로 구분되는지 미확인 |
| L5 > L3 WTP 예측 | **LOW** | VALUE GAP의 가장 차별적 예측이나 데이터 0. "모르는 갭이 아는 갭보다 값지다"는 미검증 |

### 의사결정자가 알아야 할 약점

1. **인터뷰 0건** — 13회 반복 동안 단 한 명의 잠재 고객과도 대화하지 않았다. 이론의 내부 일관성만 다듬은 상태.
2. **자기 확인 루프** — 자체 프레임워크로 공개 제품을 분석하고 부합을 "검증"으로 표시한 것은 순환 논증 (iter 8 지적).
3. **"모든 수요의 특수 사례" 주장은 철회됨** — iter 11에서 스코프를 고관여 + 정체성 인접 + 비독점 시장으로 제한.

---

## Career Mirror MVP: Go/Pause/Kill 기준

### Career Mirror 제품 개요

사용자의 커리어 히스토리를 입력하면, 동일 아웃컴에 도달한 사람들의 궤적과 비교하여 **사용자가 스스로 진단할 수 없었던 발산점 3개**를 자동 공개. 발산점 라벨은 무료, 인과 분석과 닫기 경로는 유료(29,000원/월). 6개 아웃컴 카테고리: 시리즈A+ 창업가, 월 500만+ 프리랜서, 테크리드/CTO, 독립 컨설턴트, 크리에이터, 사내→외부 전환.

### 현재 상태 (연구 기준)

- 이론 프레임워크: v2 완성, 내부 모순 해소, 반증 기준 명문화
- 제품 설계: MVP spec 완성 (8-10주 빌드, 29,000원/월), PLG 메커니즘 설계
- 실행 계획: 시드 코호트 90명 모집 전략, 인터뷰 프로토콜, DM 스크립트 준비
- ICP 기준: 정체성 이동성 (고용 형태가 아닌 외부 가시적 아웃풋 + 이직 자신감 + 외부 인정)
- **미완**: 고객 인터뷰 0건, 시드 데이터 0건, 코드 0줄
- **핵심 리스크**: 시드 코호트 n=10/카테고리는 호로스코프 수준 — 최소 n=15 필요 (iter 12 확인)

### Go 조건 (모두 충족 시 즉시 빌드)

| # | 조건 | 측정 방법 | Yes/No |
|---|---|---|---|
| G1 | L4-L5 ICP 5명 이상 인터뷰 완료 | iter 10 프로토콜 Q1-Q13 실행, 녹취 존재 | [ ] |
| G2 | 인터뷰에서 identity gap 양성 반응 (Q4+Q5+Q8) 60% 이상 | 양성 = 구체적 갭 서술 + 감정 반응 관찰 | [ ] |
| G3 | 시드 코호트 60명 이상 확보 (4개+ 카테고리 각 12명+) | 스크리닝 SQ1-SQ5 통과 + 아웃컴 확인 완료 | [ ] |
| G4 | 빠짐 감사 점수 4 이하 (Safe zone) | iter 13 프레임워크 7개 항목 채점 | [ ] |
| G5 | 갭 시각화 목업에 대한 자발적 "더 보고 싶다" 반응 3명+ | 인터뷰 중 목업 제시 후 행동 관찰 | [ ] |

**판정**: 5/5 YES = 즉시 빌드 시작

### Pause 조건 (검증 후 빌드)

다음 상황이면 빌드 시작하지 말고 추가 검증 실행:

| 조건 | 해결 방법 | 예상 소요 |
|---|---|---|
| G1-G2 미달: 인터뷰 부족 또는 양성 반응 < 60% | iter 10 프로토콜로 추가 인터뷰 10명 실행 | 2-3주 |
| G3 미달: 시드 코호트 60명 미달 | iter 12 채널 매트릭스 Phase 2 실행 | 3-4주 |
| G4 미달: 빠짐 감사 점수 5+ (Warning zone) | 제품 설계 수정 후 재감사 | 1주 |
| G5 미달: 목업 무반응 | 갭 시각화 UI/카피 재설계 후 재테스트 | 1-2주 |

**판정**: 3-4/5 YES = Pause 상태, 미달 항목 해결 후 재평가

### Kill 조건 (빌드 중단)

다음 중 하나라도 실현되면 Career Mirror MVP를 중단한다:

| Kill 신호 | 근거 (iter 11 반증 기준) | 판단 기준 |
|---|---|---|
| K1: 인터뷰 10명 중 갭 인식 보고 30% 미만 | F-2: 갭 비인식 구매의 체계적 관찰 | 10명 중 3명 미만이 정체성 갭 서술 |
| K2: L5 제품 설명에 대한 WTP가 L3보다 낮음 | F-3: L-레벨 위계 역전 | 인터뷰 내 PSM 비교에서 역전 관찰 |
| K3: "이미 내 갭을 안다" 반응이 70%+ | VALUE GAP L5 전제 붕괴 — unknown-unknown 부재 | 자가 진단 충분, 외부 도구 불필요 |
| K4: 시드 코호트 30명 이상 확보 불가 (8주 이내) | 콜드 스타트 실패 — ICP 접근성 부재 | 모집 실행 후 전환율 < 3% |
| K5: 빠짐 감사 점수 7+ (Danger zone) | 제품이 구조적으로 의존성 유발 | 설계 수정 후에도 점수 미개선 |

**판정**: 2/5 이하 YES (Go 조건) = KILL. 또는 K1-K5 중 하나 실현 = KILL.

### Kill 후 보존되는 것

Career Mirror를 Kill해도 VALUE GAP 이론 자체는 폐기하지 않는다. 보존 대상:
- L1-L5 진단 렌즈 (다른 제품 형태에 적용 가능)
- 갭 공개 = 판매 통찰 (마케팅 프레임으로 범용 활용)
- Anti-빠짐 윤리 기준 (모든 구독 제품에 적용 가능)
- 인터뷰/코호트 데이터 (다른 제품 아이디어의 기반)

폐기 대상: Career Mirror 특유의 궤적 비교 알고리즘, 시각화 UI, 6개 아웃컴 카테고리

---

## 첫 6개월 실행 순서

### Week 1-2: 고객 발견 인터뷰

- **Action**: iter 10 프로토콜로 ICP 5-10명 인터뷰 실행
- **채널**: LinkedIn 콜드 DM (일 20건), Disquiet 게시, 오프라인 커피챗
- **측정**: Q4/Q5/Q8 양성 반응률, 자발적 갭 서술 빈도
- **Decision Gate**: 양성 반응 60%+ → 다음 단계. 30% 미만 → K1 Kill 검토
- **Kill**: 10명 인터뷰 후 정체성 갭 서술 3명 미만 = Career Mirror 중단

### Week 3-4: 시드 코호트 Phase 1 모집

- **Action**: 6개 아웃컴 카테고리별 시드 모집 시작 (목표 60명, 이상 90명)
- **채널**: LinkedIn + Disquiet + 글또/AWSKRUG (iter 12 매트릭스 상위 3개)
- **스크리닝**: SQ1-SQ5 실행, 3/5+ Yes만 통과
- **Decision Gate**: 2주 내 30명+ 확보 → 계속. 15명 미만 → 모집 전략 수정
- **Kill**: 4주 누적 30명 미만 = K4 실현, 중단 검토

### Week 5-8: MVP 빌드 Phase 1 + 시드 데이터 입력

- **Action**: 온보딩 폼 + 갭 계산 엔진 + 정적 시각화 (iter 5 Week 1-5 범위)
- **병행**: 시드 코호트 데이터 입력 계속, Phase 2 모집 (부족 카테고리)
- **Decision Gate**: Week 8에 시드 50명+ AND 프로토타입 동작 → 다음 단계
- **Kill**: 빠짐 감사 재실행, 점수 5+ → 설계 수정 필수

### Week 9-16: MVP 빌드 Phase 2 + 알파 테스트

- **Action**: 페이월 통합 + 공유 잠금 해제 + PQL 감지 (iter 5 Week 6-10)
- **알파 테스트**: 시드 코호트 중 10-15명에게 제품 사용 → 갭 시각화 반응 관찰
- **측정**: Aha Moment 활성화율 (목표 60%+), 블러 호버율, 7일 재방문율
- **Decision Gate**: 활성화율 40%+ → 유료 전환 테스트. 20% 미만 → 갭 시각화 재설계
- **Kill**: 알파 15명 중 유료 전환 의사 0명 = 제품-시장 적합 실패

### Week 17-24: 유료 전환 + Social_Amplifier 검증

- **Action**: 29,000원/월 유료 전환 개방, 공유 메커니즘 활성화
- **측정**: 유료 전환율 (목표 5%+), 공유 통한 신규 유입 (바이럴 계수)
- **Social_Amplifier 자연 실험**: 공유 기능 사용자 vs 미사용자 WTP 비교
- **Decision Gate**: 유료 전환 5%+ AND 월 MRR 100만원+ → 스케일
- **Kill**: 24주차 유료 사용자 10명 미만 = 사업 모델 재검토

### 6개월 요약 테이블

| 기간 | 핵심 활동 | Go/Kill Gate | Kill 조건 |
|---|---|---|---|
| W1-2 | 인터뷰 5-10명 | 갭 양성 60%+ | 양성 < 30% |
| W3-4 | 시드 모집 60명 | 30명+ 확보 | 4주 후 30명 미만 |
| W5-8 | 빌드 Phase 1 | 시드 50명 + 프로토타입 | 빠짐 감사 5+ |
| W9-16 | 빌드 Phase 2 + 알파 | 활성화율 40%+ | 유료 의사 0명 |
| W17-24 | 유료 전환 | 전환율 5%+, MRR 100만+ | 유료 10명 미만 |

### 예산 주의사항 (iter 8 경고)

iter 7의 실험 예산(12만원)은 3-5배 과소 추정되었다 (iter 8 지적). 시드 코호트 모집에서도 동일 리스크 존재:
- LinkedIn InMail 비용: 건당 약 1,000-2,000원
- 인터뷰 참여 인센티브: 커피 기프티콘 5,000원/명 x 10명 = 50,000원
- 시드 모집 인센티브: 궤적 분석 리포트 (무료, 제품 가치 교환)
- **현실적 6개월 예산**: 50-100만원 (마케팅/인센티브), 개발 비용 별도

---

## 연구 지도 (Where to go deep)

| 필요한 결정 | 읽을 문서 | 핵심 섹션 |
|---|---|---|
| VALUE GAP 이론 기초 이해 | [wtp-demand-genesis-theory.md](20260411-wtp-demand-genesis-theory.md) | 섹션 2: L1-L5 계층, 섹션 5: 통합 공식 |
| 이론 v2 수정 사항 확인 | [wtp-theory-v2.md](20260411-wtp-theory-v2.md) | 수정 1-3 전체, 수정된 공식 |
| ICP 정의 및 정체성 이동성 기준 | [wtp-theory-v2.md](20260411-wtp-theory-v2.md) | 수정 3: ICP 제외 기준 정제 |
| 기존 이론과 비교 (JTBD 등) | [wtp-jtbd-comparison.md](20260411-wtp-jtbd-comparison.md) | 전체 |
| 한국 제품에 적용한 사례 | [wtp-korean-product-audit.md](20260411-wtp-korean-product-audit.md) | 제품별 L-레벨 진단 |
| 고객 인터뷰 방법 | [wtp-interview-protocol.md](20260411-wtp-interview-protocol.md) | Q1-Q13 질문 + 프로빙 가이드 |
| 제품 설계 (MVP 빌드 스펙) | [wtp-career-mirror-mvp.md](20260411-wtp-career-mirror-mvp.md) | Core Loop, 갭 공개 순간, MVP 빌드 스코프 |
| 제품 설계 패턴 일반 | [wtp-product-design-patterns.md](20260411-wtp-product-design-patterns.md) | pricing tiers, activation hooks |
| 빠짐 감사 (윤리 체크) | [wtp-bbaijjim-audit-framework.md](20260411-wtp-bbaijjim-audit-framework.md) | 7개 감사 항목 + 채점 기준 |
| 시드 코호트 모집 실행 | [wtp-seed-cohort-strategy.md](20260411-wtp-seed-cohort-strategy.md) | 섹션 3: 채널 매트릭스, 섹션 4: DM 스크립트 |
| 이론의 한계와 반증 기준 | [wtp-falsification-criteria.md](20260411-wtp-falsification-criteria.md) | 섹션 2: F-1~F-7, 섹션 3: 스코프 경계 |
| Social_Amplifier 실험 설계 | [wtp-social-amplifier-experiment.md](20260411-wtp-social-amplifier-experiment.md) | 전체 |
| 자기 비판 (메타-리뷰) | [wtp-meta-review.md](20260411-wtp-meta-review.md) | 섹션 1: 내부 모순, 섹션 2: 과잉주장 |

---

## 가장 중요한 미답 질문 (연구가 해결 못 한 것)

### 1. L5(모르는 미지) 갭이 실제로 L3보다 높은 WTP를 생성하는가?

VALUE GAP의 가장 차별적이고 반직관적인 예측이다. "자신이 뭘 모르는지 모르는" 상태가 "뭘 모르는지 아는" 상태보다 더 큰 지불의사를 만든다는 주장. 이것이 맞으면 Career Mirror의 핵심 가치 제안이 성립한다. 틀리면 제품이 "그냥 또 하나의 커리어 진단 도구"가 된다.

**최소 검증 방법**: 인터뷰 10명에게 L3 제품 설명 (커리어 코칭)과 L5 제품 설명 (unknown gap 발견)을 순차 제시하고 PSM으로 WTP 비교. 2주 내 실행 가능.

### 2. 한국 지식 노동자의 "정체성 이동성"이 실제로 WTP와 상관하는가?

iter 9에서 ICP 기준을 고용 형태에서 정체성 이동성으로 교체했지만, 이것이 실제로 WTP를 예측하는지 데이터가 없다. 직장인 중에서도 외부 가시성이 있는 사람(연구자, 컨설턴트)이 없는 사람보다 Career Mirror에 돈을 쓸지는 미확인.

**최소 검증 방법**: 스크리닝 SQ1-SQ5 점수와 "Career Mirror에 월 29,000원 내겠는가?" 응답의 상관 분석. 30명이면 통계적 유의성 확보 가능.

### 3. 갭 시각화가 실제로 구매 전환을 촉발하는가, 아니면 호기심만 유발하는가?

"갭 공개 = 판매"는 이론적으로 타당하지만, 궤적 비교 시각화를 본 사용자가 실제로 지갑을 여는지는 별개 문제다. 무료 갭 공개와 유료 상세 사이의 전환 장벽이 얼마나 높은지, 갭을 보여주는 것만으로 충분한지 아니면 해결 경로까지 제시해야 하는지 미확인.

**최소 검증 방법**: 갭 시각화 목업(Figma/정적 HTML)을 인터뷰 대상자에게 보여주고 "상세를 보려면 29,000원"이라고 했을 때 반응 관찰. 5명이면 정성적 신호 확보.

---

## 의사결정 체크리스트 (최종)

- [ ] VALUE GAP L4-L5 ICP를 5명 이상 인터뷰했는가?
- [ ] 인터뷰에서 identity gap (Q4, Q5, Q8) 양성 반응 60%+를 얻었는가?
- [ ] 시드 코호트 60명 이상 확보했는가 (4개+ 아웃컴 카테고리, 각 12명+)?
- [ ] 빠짐 감사 점수 4 이하 (Safe zone)?
- [ ] 갭 시각화 목업에 대한 자발적 "더 보고 싶다" 반응 3명+?

**판정 기준**:
- **4-5/5 YES = GO** — MVP 빌드 시작
- **3/5 YES = PAUSE** — 미달 항목 검증 후 재평가
- **2/5 이하 = KILL** — Career Mirror 중단, 이론은 보존하되 다른 제품 형태 탐색

---

- [iter 1] [20260411-wtp-demand-genesis-theory.md](20260411-wtp-demand-genesis-theory.md) — VALUE GAP 기초 이론
- [iter 2] [20260411-wtp-product-design-patterns.md](20260411-wtp-product-design-patterns.md) — 제품 설계 패턴
- [iter 3] [20260411-wtp-one-pager.md](20260411-wtp-one-pager.md) — 전략 원페이저
- [iter 4] [20260411-wtp-korean-product-audit.md](20260411-wtp-korean-product-audit.md) — 한국 제품 감사
- [iter 5] [20260411-wtp-career-mirror-mvp.md](20260411-wtp-career-mirror-mvp.md) — Career Mirror MVP 설계
- [iter 6] [20260411-wtp-jtbd-comparison.md](20260411-wtp-jtbd-comparison.md) — JTBD 비교 분석
- [iter 7] [20260411-wtp-social-amplifier-experiment.md](20260411-wtp-social-amplifier-experiment.md) — Social Amplifier 실험
- [iter 8] [20260411-wtp-meta-review.md](20260411-wtp-meta-review.md) — 메타-리뷰 (자기 비판)
- [iter 9] [20260411-wtp-theory-v2.md](20260411-wtp-theory-v2.md) — Theory v2 (모순 수정)
- [iter 10] [20260411-wtp-interview-protocol.md](20260411-wtp-interview-protocol.md) — 인터뷰 프로토콜
- [iter 11] [20260411-wtp-falsification-criteria.md](20260411-wtp-falsification-criteria.md) — 반증 기준
- [iter 12] [20260411-wtp-seed-cohort-strategy.md](20260411-wtp-seed-cohort-strategy.md) — 시드 코호트 전략
- [iter 13] [20260411-wtp-bbaijjim-audit-framework.md](20260411-wtp-bbaijjim-audit-framework.md) — 빠짐 감사 프레임워크

## Related
- [[projects/Entity/research/20260411-wtp-career-mirror-pricing|20260411-wtp-career-mirror-pricing]]
- [[projects/Entity/research/20260411-wtp-seed-cohort-strategy|20260411-wtp-seed-cohort-strategy]]
- [[projects/Entity/research/20260411-wtp-demand-genesis-theory|20260411-wtp-demand-genesis-theory]]
- [[projects/Entity/research/20260411-wtp-bbaijjim-audit-framework|20260411-wtp-bbaijjim-audit-framework]]
- [[projects/Entity/research/20260411-wtp-interview-protocol|20260411-wtp-interview-protocol]]
- [[projects/Entity/research/20260411-wtp-product-design-patterns|20260411-wtp-product-design-patterns]]
- [[projects/Entity/research/20260411-wtp-falsification-criteria|20260411-wtp-falsification-criteria]]
- [[projects/Entity/research/20260411-wtp-korean-product-audit|20260411-wtp-korean-product-audit]]
