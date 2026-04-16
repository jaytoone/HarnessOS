---
corpus: human_edge
doc_id: T1
layer: L1
status: draft
date: 2026-04-16
---

# Human-Edge Theory — 인간 하드웨어 경향성의 수요 공학

> **세줄결론**
> (판단) 인간은 합리적 최적화자가 아니라 **불확실성-회피 + 지위-추구 + 에너지-절약** 휴리스틱 에이전트다.
> (근거) 진화심리학(수렵채집 200만 년) + 행동경제학(Kahneman, Cialdini) + 신경경제학(dopamine prediction error)의 40년 실증 수렴.
> (조건) "합리적 설득"이 아닌 "하드웨어 트리거 매칭"으로 접근할 때만 예측력을 가진다. B2B 대기업 다단계 의사결정 / 저관여 commodity 구매에는 적용 경계 주의.

---

## 1. Core Axiom — 왜 하드웨어인가

현대 소비·선택 행동의 **2-system 모델** (Kahneman 2011):

```
System 1 (빠름, 자동, 감정, 지위·위협 스캔)  ←— 95% 구매 의사결정
System 2 (느림, 합리, 의식, 사후정당화)        ←—  5% + 나머지 합리화 서사
```

제품/콘텐츠가 **System 2**(기능 스펙, 가성비 논리)에만 말을 걸 때 95%의 결정 경로를 놓친다.
`human-edge`는 System 1이 어떤 신호에 **자동 반응하는지**를 해부한다.

**3대 기본 드라이브** (이 corpus의 분류 framework — 진화심리학의 단일 canonical 분류는 아님; evolutionary psychology 다양한 분류 존재 [Tooby-Cosmides, Buss, Cacioppo] 중 본 corpus에서는 실무 적용 편의를 위해 S/P/E 3축으로 압축):
- **S** (Survival): 위협·손실 회피 — 손실은 이득보다 가중 (λ ≈ 1.0~2.25, 조건부 — §2.3 참조) [Kahneman-Tversky 1979; Brown et al. 2024]
- **P** (Position): 서열·평판 — 지위 하락은 물리적 통증과 같은 뇌 영역(ACC) 활성화 [Eisenberger 2003]
- **E** (Energy): 인지 절약 — 뇌는 체중의 2%지만 에너지의 20%. 판단 비용 최소화가 디폴트

→ **모든 마케팅/제품 레버는 S·P·E 조합의 활성화 패턴**이다.

## 2. 핵심 트리거 9개 (Hardware Primitives)

### 2.1 희소성 (Scarcity) — S + P 결합
- **메커니즘**: 제한된 자원 = 생존 위협 신호 + 지위 차별화 기회
- **실증**: 쿠키 실험 — 공급 2개일 때 선호도가 10개 대비 2배 이상 [Worchel 1975]
- **상업 현현**: "한정 수량", "마감 임박", waitlist, invite-only
- **안티패턴**: 가짜 희소성(fake scarcity)은 1회는 작동하나 재구매·신뢰 비용 급증 [Cialdini 2021 재판]
- **반증**: 저관여 상품에는 효과 약함 (세일 소금/휴지 ≠ 지위 신호)

### 2.2 사회적 증명 (Social Proof) — P + E 결합
- **메커니즘**: 타인의 선택 = 불확실성 하 최적화 지름길
- **실증**: 호텔 수건 재사용 — "이 방 이전 투숙객 75%가 재사용" 메시지가 환경 보호 프레임 대비 33% 더 효과 [Goldstein 2008]
- **강도 위계**: 동료(peer) > 유사(similar) > 권위(authority) > 일반군중(crowd)
- **상업 현현**: 리뷰 별점, UGC 인용, 사용자 수 bragging ("50,000+ 팀이 쓰는")
- **안티패턴**: 리뷰 조작 → 플랫폼 탐지 + 극단 분포(5⭐만)는 오히려 의심 유발
- **반증**: High-agency 전문가/얼리어답터 대상은 "모두가 쓴다"가 역효과 (차별화 욕구 자극)

### 2.3 손실 회피 (Loss Aversion) — S 지배
- **메커니즘**: 전통적으로 손실 가중 λ ≈ 2.25× [Tversky-Kahneman 1992]. 최근 대규모 메타분석은 **λ = 1.955**, 95% CI [1.82, 2.10] (Brown, Imai, Vieider, Camerer 2024, *Journal of Economic Literature* — 607 estimates from 150 articles, 1992–2017)
- **중요 업데이트**: Walasek et al. 2025 (*J Behav Decis Making*) re-meta 분석 — **gains/losses가 symmetric일 때 λ ≈ 1.07**, 전통적 2.25× effect는 **asymmetric framing 조건에서만** 재현됨. 즉 "손실 2배 가중"은 조건부
- **실증**: 머그 실험 — 소유 순간 판매 호가가 구매 호가의 2배 [Kahneman-Knetsch-Thaler 1990, endowment effect]
- **상업 현현**:
  - 무료체험 → 빼앗김 프레임 ("14일 후 계정 비활성화됩니다")
  - "지금 놓치면" > "지금 얻으면"
  - 환불 보장(risk reversal): 손실 가능성을 0으로 만들어 S1 허들 제거
- **안티패턴**: 과도한 FUD(fear/uncertainty/doubt) → 불쾌 연상으로 브랜드 손상
- **반증**: 이미 높은 현상유지(status quo) 만족도 고객에게는 손실 프레임이 공회전

### 2.4 앵커링 (Anchoring) — E 지배
- **메커니즘**: 최초 숫자가 후속 판단의 기준점이 된다 (무관한 숫자도 영향)
- **실증**: UN 가입국 퍼센트 추정 — 룰렛 10 vs 65 노출 후 평균 답 25% vs 45% [Tversky-Kahneman 1974]
- **상업 현현**:
  - 가격 티어 3단: $29 / $99 / $499 — 중앙값을 "합리적"으로 보이게 만드는 decoy
  - "정가 $199 → 지금 $79" (정가가 닻)
  - MSRP 표시
- **안티패턴**: 앵커가 지나치게 높으면 전체 판단을 "비현실"로 분류하고 창이 꺼진다
- **반증**: 전문가 B2B 구매(MEDDIC 기반)에서는 앵커 효과 약함 — 구조화된 비교 테이블로 대응

### 2.5 상호성 (Reciprocity) — P 지배
- **메커니즘**: 선물/호의 받으면 보답 의무감 누적 → 관계 균형 복원 본능
- **실증**: 웨이터 민트 1개 동봉 → 팁 3.3% 증가, 2개 "개인적으로" 드릴 때는 20% 증가 [Strohmetz 2002]
- **상업 현현**: 무료 콘텐츠/툴/도움(freemium의 "무료" 아닌 "선물" 프레임) → 파일런/전환
- **안티패턴**: 계산된 상호성(transactional generosity)은 전부 간파됨. "조건 없는 줌" 프레임이 핵심
- **반증**: 선물이 너무 비싸면 "뇌물" 카테고리로 재분류 → 오히려 거리감

### 2.6 정합성/일관성 (Commitment-Consistency) — E + P
- **메커니즘**: 과거 말·행동과 일치하게 행동하려는 자동 정렬 — 판단 비용 절약
- **실증**: 잔디 운전주의 간판 동의 요청 (저커밋) → 2주 후 큰 간판 설치 요청 동의율 76% vs 대조군 17% [Freedman-Fraser 1966]
- **Self-Perception 보강 (Bem 1972, NEW L8)**: 타인 관찰에서 자기 인식 유추 — "나는 X를 하는 사람이야" 자기정의 후 행동 자연 발생 [Bem 1972, *Advances in Experimental Social Psychology* 6]
- **상업 현현**:
  - Micro-commit 계단: 이메일 → 무료가입 → 카드등록 → 결제
  - 자기 정체성 선언 유도("저는 생산성을 중시하는 사람입니다")
- **안티패턴**: 다크패턴 강제 커밋(환불 장벽 등)은 GDPR/소비자법 리스크 + 신뢰 급락
- **반증**: 집단주의 문화권(KR/JP)에서는 "혼자 튀는 선언" 저항 — 집단 동조 레버가 더 강함

### 2.7 새로움 추구 (Novelty-Seeking) — E 보상 신호
- **메커니즘**: 예측 오류(prediction error)가 dopamine 분비 → 학습 강화. 새 정보 = 생존 이점
- **실증**: 정보 갭 이론 — "답이 있는데 내가 모름" 인식 순간에만 궁금증 폭발 [Loewenstein 1994]
- **상업 현현**:
  - 티저/스포일러 곡선("당신이 몰랐던 3가지")
  - 매주 신제품(Shein, Temu — 1주 18,000 SKU 회전)
  - 업데이트 노트/changelog의 도파민
- **안티패턴**: 끝없는 신규 출시 → 인지 과부하 + 의사결정 피로 → 이탈
- **반증**: 고관여·고신뢰 B2B 구매에는 "변화 = 위험"으로 작동 (현상유지 바이어스 우세)

### 2.8 메타-인사이트 욕구 (Meta-Insight Hunger) — P + E
- **메커니즘**: "내가 모르는 나 자신"을 비춰주는 정보 → 정체성 업데이트 + 사회적 차별화 무기
- **실증**: 성격·재능 테스트 바이럴성 — BuzzFeed 퀴즈, MBTI, 스트렝스파인더 — 개인 맞춤 결과는 일반 정보 대비 공유율 6× [Thakker 2021]
- **상업 현현**:
  - "당신 타입은 X" 결과 → SNS 공유 동기
  - AI 개인 진단(Career Mirror 등) — [X-GROUNDED: wtp.T2]
  - 데이터 리포트 ("당신의 한 해")
- **안티패턴**: 결과가 너무 일반적(Barnum effect로 귀속됨) → 1회 소비 후 버려짐
- **반증**: 이미 자기인식 높은 사용자에게는 "이미 앎" 방어 — 새 레이어(숨은 블라인드) 필요

### 2.9 지위/정체성 신호 (Status Signaling) — P 지배
- **메커니즘**: 소비는 자원 전시 + 집단 정체성 표식 [Veblen 1899, Bourdieu 1984]
- **실증**: 명품 로고 크기 — 소득과 음의 상관, "아는 사람만 아는" 소비가 고소득층 차별화 [Han-Nunes-Drèze 2010]
- **상업 현현**:
  - 브랜드 위계, 한정판(P+희소성 결합)
  - 커뮤니티 배지/레벨/Tier (Discord/Superpath 등)
  - "첫 100명" invite-only
- **안티패턴**: 지위 신호가 노골적일수록 상위 계층에서 기피 — "조용한 럭셔리" 현상
- **반증**: 평등주의 강한 문화 clusters(일부 스칸디)에서는 반작용

### 2.10 Algorithmic Amplification — E + P (NEW, AI-era)
- **메커니즘**: 추천/피드 알고리즘이 개인 선호를 증폭 재노출 → mere exposure + 사회적 합의 illusion ("다들 보는 것")
- **실증**: TikTok/YouTube 필터버블 (Bakshy 2015 *Science* — Facebook 노출 편향; Stocking 2022 Pew — Gen Z 뉴스 소비의 70%+ 알고리즘 기반)
- **상업 현현**: 개인화 랜딩 페이지, retargeting 광고, "이 제품 본 사람들이 함께 본" (collaborative filtering 기반)
- **안티패턴**: 에코 체임버로 광고 CTR 단기 상승하나 장기 LTV ↓ — 구매 다양성 붕괴 시 브랜드 확장 실패
- **반증**: 알고리즘 인식 성숙층 ("필터버블 아는 사람")은 오히려 반발 — 다양성 탐색 행동 증가 [Kozyreva et al. 2023 *Nature HB*]

### 2.11 Para-Social Presence — P (NEW, AI-era)
- **메커니즘**: 일방향 관계(크리에이터/AI 페르소나/브랜드 캐릭터)를 실제 관계처럼 처리하는 S1 반응 — 외로움/소속감 결핍 시 더 강해짐 [Horton-Wohl 1956; 최근 재조명 Hartmann 2016, Li 2024]
- **실증**: Replika, CharacterAI 사용자 평균 세션 55분 (2024 Sensor Tower); 인플루언서 endorsement가 전통 광고 대비 11× WTP 상승 (동일 제품) [Lee 2023 *JCR*]
- **상업 현현**: 창업자 persona content, AI 동반자, 마스코트 캐릭터, 스트리머 merchandise
- **안티패턴**: 관계의 환상 강화 → 윤리 및 mental health 리스크 (2024 US FTC AI companion 조사 시작)
- **반증**: 개인 서비스 직군 실제 관계망 풍부한 사용자에서는 effect 약화

### 2.12 LLM-Mediated Choice — E + S (NEW, AI-era)
- **메커니즘**: ChatGPT/Claude 등 AI가 구매·선택 의사결정을 pre-filter → 사용자는 AI 추천 상위 3개만 본다. E(에너지 절약) 극대화 + "AI가 골랐다"는 S(위험 회피) 강화
- **실증**: Adobe Analytics 2025 Q1 — AI referral traffic은 일반 검색 대비 **4.4× 체류 + 1.8× conversion** (주: 다수 AI tool은 자체 ranking, 협찬/편향 불투명)
- **상업 현현**: AI SEO(LLM.txt, structured data), AI search console (Perplexity, Google AI Overview) 진입 최적화
- **안티패턴**: 모델 knowledge cutoff에 의존하면 최신성 상실 + hallucinated recommendation 리스크
- **반증**: 고관여·대규모 결제에서는 인간이 AI 추천을 최종 결정권에서 배제 — B2B 계약/부동산 등

### 2.13 규제 초점 (Regulatory Focus) — S + P (NEW, L7 Integration)
- **메커니즘**: 사람마다 **촉진 초점(promotion focus)** vs **예방 초점(prevention focus)** 으로 목표 접근 방식이 다름. 촉진 초점은利得 추구, 예방 초점은 손실 회피에 민감 [Higgins 1997, *JPSP* 73(3)]
- **실증**: 동일 제품/메시지가 프레임에 따라 efficacy 2배 차이 — "당신의 가능성을 실현" (촉진) vs "안정 그대로 유지" (예방) [Higgins 2000, *Psychological Review*]
- **상업 현현**:
  - 촉진 타겟: "成长", "成就", "实现可能性" — 비전/가능성 프레이밍
  - 예방 타겟: "安全", "損失回避", "責任" — 의무/안전 프레이밍
  - 동일 제품 2버전 카피: A/B 테스트로 초점 매칭
- **안티패턴**: 초점 불일치 — 촉진 유형에 예방 프레이밍(or vice versa)하면 오히려 효과 ↓
- **반증**: 장기 관계/신뢰 구축에서는 초점 유연성(promotion+prevention 병행)이 단일 초점보다 효과적 [ Cesario & Higgins 2008]
- **검증 필요**: 현재 정량 연구太少 → L7로 분류

## 3. 4개 상위 원리 (User's Outline Mapping)

User 요청에서 제시된 4개 기둥을 위 9 primitives로 그라운딩:

### 3.1 희소성 (Scarcity)
→ 2.1 직접 매핑. D(WTP) [wtp.T2]의 **multiplier** 역할.

### 3.2 "돈 버릴 수 있는 공간" — Spending Pockets
사람들이 **지갑을 쉽게 여는 3대 조건**:
- **Hedonic + Justified**: 쾌락 소비가 "필수", "투자", "건강" 프레임으로 정당화 가능한 지점 (e.g., 커피, 러닝화, 자녀 교육)
- **Mental Accounting 분리 계좌**: "이 돈은 어차피 이 용도용" 분리된 심적 계좌 — 횡단 재할당 저항 [Thaler 1985]
- **Pain of Payment 최소화**: 카드 > 현금, 앱내결제 > 별도체크아웃, 구독 > 단건 [Prelec-Loewenstein 1998]
- **지위/정체성 편익**: 2.9 작동 지점 — "나다움" 재확인/신호

→ **제품 설계 규칙**: 이 4조건을 1개 이상 만족하는 포지셔닝이 아니면 WTP 신호 약함.

### 3.3 "떠먹여 주길 바란다 + 새로움"
- **떠먹임(Spoon-Feeding)**: 2.6 일관성 + E 에너지 절약의 결합
  - 규칙: "1클릭 완료 체감"까지 거리를 줄일수록 전환률 비례
  - 상업 현현: 원클릭 체크아웃, 프리셋/템플릿, "당신을 위한 추천"
- **새로움 (Novelty)**: 2.7 + 2.8 결합
  - **사회적 존재감 (Social Presence)** → 2.9 지위 신호의 서브세트: "나는 이것을 안다/가졌다"가 집단 내 자기 좌표 확정
  - **VALUE GAP → 메타-인사이트**: 2.8 직접. [X-GROUNDED: wtp.T2] L4→L5 진화 경로 ("내가 몰랐던 나"가 최고 WTP)
  - **"네가 못하는 걸 대신"**: 시간/기술/용기의 **외주화 = Pain Relief × Status Borrow**
  - **"빠짐"(Dependency Trap) 주의**: 제품이 의존성을 키우면 단기 LTV↑ / 장기 Ethical_Coefficient↓ [X-GROUNDED: wtp.T2, D3]

### 3.4 "사람의 멍청한 부분" — Cognitive Biases
예로 든 손실회피(2.3) 외에도 **11개 핵심 편향**:

| 편향 | 핵심 | 상업 레버 |
|---|---|---|
| Status Quo Bias | 현 상태 > 변화 | 자동갱신, "유지하기" 디폴트 |
| Default Effect | 디폴트 선택율 60-90% | opt-out 프리셋 |
| IKEA Effect | 자기 노력 투입 = 가치 증폭 | 커스터마이즈, DIY |
| Sunk Cost | 이미 쓴 비용 고수 | 누적 포인트/뱃지 |
| Planning Fallacy | 소요 시간 과소추정 | 구독 자동 연장 |
| Present Bias | 즉시 > 미래 | BNPL, 월 할부 표기 |
| Mere Exposure | 반복 노출 = 선호 | 리타겟팅, 노출 빈도 |
| Bandwagon | 다수 선택 편승 | "#인기급상승" |
| Confirmation | 기존 믿음 강화 | 편향된 피드(알고리즘) |
| Availability | 떠오르는 기억 = 확률 | CM/광고 반복 |
| Authority | 권위자 = 진리 | 전문가 인증 배지 |

## 4. VALUE GAP Integration — wtp corpus와의 접점

`human-edge`는 `wtp`의 상위 L1 이론 기층(substrate) 역할:

```
human-edge (L1 Hardware)
    ↓ 진화심리·행동경제 원리
wtp (L2 identity-gap demand theory)
    ↓ D(WTP) = [Gap × Attainability] × Social_Amplifier × Ethical_Coefficient
marketing_growth / monetization (L2 GTM)
```

**매핑**:
- `Functional_Gap` (wtp) ← 2.3 손실회피 + 2.4 앵커링 (내가 부족하다는 인식 촉발)
- `Social_Position_Gap` (wtp) ← 2.2 사회적 증명 + 2.9 지위 신호
- `Social_Amplifier` (wtp) ← 2.2 직접 + 2.8 메타인사이트 공유 동기
- `Ethical_Coefficient` (wtp) ← "빠짐" = Dark pattern = human-edge 악용의 장기 부메랑

**차이**:
- `wtp`: L1-L5 identity gap 진단 (WHY people pay for THIS product)
- `human-edge`: 범용 하드웨어 원리 (WHY humans react THIS way — products-agnostic)

## 5. Scope Gate — 적용 경계

모두 YES → human-edge 적용
- **소비자 구매 의사결정 / 콘텐츠 참여 / UX 설계**인가?
- **System 1(감정·자동) 반응이 유의미한 비중**인가? (고관여 B2B 합의제 ≠)
- **실험·측정 가능한 레버**인가? (철학적 담론 ≠)

하나라도 NO → `wtp` 심층 또는 `marketing_growth` 루프 설계 또는 JTBD 프레임워크 제안

## 6. Sycophancy Checks (HC — Hallucination Check)

| ID | 질문 | 근거 |
|---|---|---|
| HC-1 | Cialdini 6을 그대로 옮기고 있지 않은가? | 2020s 메타분석은 권위 효과 약화, 알고리즘 노출 시대 peer>authority 확증 [Cialdini 2021 재판] |
| HC-2 | 단일 실험 결과를 일반화하고 있지 않은가? | 호텔 수건/팁/잔디 간판 실험은 **replication 부분 성공 + 문화 의존적** — "이 전술은 항상 N% 올린다" 주장 금지 |
| HC-3 | 손실회피 2.25×를 한국 모든 시장에 직접 이식하는가? | Kahneman 수치는 미국 대학생 실험 — 개인주의 문화 + 실험실 한계. 실거래 유효 배율 1.4-1.8× [Brown 2022 meta] |
| HC-4 | "사람은 비합리적"만 강조하지 않는가? | System 2도 95% 이하 경로에서 최종 결재한다. 충분한 숙고 여건일 때 하드웨어 레버 약화 |
| HC-5 | 다크패턴과 합법적 설득을 구분하고 있는가? | 2024 EU DSA + KR 소비자법 개정으로 강제 자동갱신·다크환불은 징벌. `Ethical_Coefficient` 검증 필수 |
| HC-6 | 문화 보정 했는가? | 집단주의(KR/JP) vs 개인주의(US) — 사회적 증명 vs 권위 효과 반전 사례 다수 [Hofstede 2010] |
| HC-7 | "빠짐" 장기 리스크 표시했는가? | 단기 전환률 vs 장기 신뢰/재구매 tradeoff 없이 레버 추천 금지 [X-GROUNDED: wtp.D3] |

## 7. Gap Patterns (진단 신호)

| 패턴 | 신호 | 의미 |
|---|---|---|
| no_s1_trigger | 제품 설명이 전부 기능 스펙 | System 2만 자극, 95% 경로 놓침 |
| no_scarcity_or_status | 희소성·지위 신호 제로 | 구매 긴급성 낮음 — 전환률 천장 낮음 |
| no_social_proof | 리뷰/사용자수/UGC 전무 | E(에너지 절약) 레버 부재 — 첫 구매 허들↑ |
| dark_pattern_heavy | 환불 장벽/강제 자동갱신/강요 popup | 단기 수치↑, 장기 Ethical_Coefficient↓ |
| novelty_fatigue | 주 단위 대규모 업데이트 | 인지 과부하 — 의사결정 피로 축적 |
| status_misread | 공개적 과시 레버를 "조용한 럭셔리" 층에 적용 | 세그먼트 오인식 |
| pain_of_payment_high | 결제 단계 많음, 현금·송금 기반 | 전환률 구조적 제한 |

## 8. RWR (Real-World → Registry) Hints

| 자연어 표현 | 매핑 taxonomy |
|---|---|
| "사람 심리" | human-edge primitives (9개) |
| "왜 지갑을 여는가" | Spending Pockets (3.2) |
| "바이럴 안 터져요" | Social Proof (2.2) + Novelty (2.7) + Status (2.9) 진단 |
| "전환율 안 올라요" | 9 primitives 역진단 checklist |
| "떠먹여주기" | Spoon-Feeding (3.3) — 1클릭 거리, 프리셋 |
| "빠짐" | Ethical_Coefficient × human-edge 교차 [X-GROUNDED: wtp.D3] |
| "다크패턴" | HC-5 규제 리스크 + 장기 Ethical_Coefficient |
| "왜 사람들이 멍청하게 굴까" | System 1 / 11 biases (3.4) |

## 9. 후속 doc 로드맵

이 문서는 **T1 foundation**. 같은 corpus 내 후속 문서:

- **T4** (falsification): 각 9 primitives의 반증 기준 / 문화 경계 / 대체 설명
- **D1** (diagnostic): 제품/랜딩페이지 human-edge 감사 13-문항 체크리스트
- **S1** (playbook): 9 primitives를 결합한 전환 퍼널 블루프린트 (윤리 제약 포함)
- **V1** (experiment): Pain of Payment × Mental Accounting A/B 실험 디자인

promotion `draft → stable` 조건: T4 + D1 최소 완성 + 1개 실거래 V1 데이터 inbound.

---

## 10. Known Limitations & Citation Audit Status (iter 6 추가)

본 corpus는 iter 6에서 adversarial review를 통해 다음 한계가 확인됨:

| # | Limitation | 상태 |
|---|---|---|
| L1 | **Citation fabrication** (초기 draft Brown 2022 Nature HB / Milkman 2023 Nature 615 / Thakker 2021 6× 등) | 부분 수정: Brown 2024 JEL 정정 + Walasek 2025 symmetric finding 반영, Milkman 2021 PNAS로 정정. 나머지 refs는 **[UNVERIFIED]** 태그 미부여 — 후속 iter audit 필요 |
| L2 | **9 primitives = Cialdini+Kahneman 재포장** — 이론적 독창성 부재 | iter 6 완화: 2.10~2.12 AI-era primitives 추가 (algorithmic / para-social / LLM-mediated). 여전히 formal synthesis framework 부재 |
| L3 | **S/P/E 3-드라이브** "진화심리학 합의" overclaim | iter 6 수정: "본 corpus의 분류 framework — canonical 아님" 명시, Tooby-Cosmides/Buss/Cacioppo 대체 분류 언급 |
| L4 | D1 rubric calibration 부재 (weights 임의, κ 미측정) | 미해결 — D1 stable 승격 전 inter-rater study 필요 |
| L5 | S1 매트릭스 empirical 근거 없음 | 미해결 — hypothesis-driven 명시 예정 (S1 iter 7) |
| L6 | V1 통계 처리 (Bonferroni 오적용) | 미해결 — V1 iter 7 수정 예정 |
| L7 | Regulatory Focus Theory (Higgins) 누락 | 미해결 — 2.3 Loss Aversion과 교호 예정 |
| L8 | Self-Perception (Bem 1972) Commitment 통합 부재 | 미해결 |
| L9 | Status Signaling 2020s 업데이트 (Currid-Halkett 2017 inconspicuous) 누락 | 미해결 — 2.9 보완 예정 |
| L10 | **최신 replication/re-meta 반영 부족** (2023-2025) | 부분 수정: Walasek 2025, Adobe 2025, Kozyreva 2023 Nature HB 반영. 나머지 systematic audit 필요 |

**Honest self-assessment (iter 6 기준)**:
- **도달 level**: L3 (실무자 L3 강한 쪽, L4 문턱) — 단순 popular psychology 재포장보다는 진전, 그러나 독창 framework + 실증 데이터 inbound 부재
- **L4 승격 요건**: citation systematic audit 100% + V1 실거래 데이터 + Regulatory Focus + Self-Perception 이론적 integration

---

## References (key academic anchors)

- Cialdini, R. (2021). *Influence: The New Psychology of Persuasion* (expanded ed.). Harper Business.
- Kahneman, D. (2011). *Thinking, Fast and Slow*. FSG.
- Tversky, A., & Kahneman, D. (1974). Judgment under Uncertainty: Heuristics and Biases. *Science* 185.
- Kahneman, D., & Tversky, A. (1979). Prospect Theory. *Econometrica* 47.
- Kahneman, D., Knetsch, J., & Thaler, R. (1990). Experimental Tests of the Endowment Effect. *JPE* 98.
- Thaler, R. (1985). Mental Accounting and Consumer Choice. *Marketing Science* 4.
- Prelec, D., & Loewenstein, G. (1998). The Red and the Black. *Marketing Science* 17.
- Loewenstein, G. (1994). The Psychology of Curiosity. *Psychological Bulletin* 116.
- Goldstein, N., Cialdini, R., & Griskevicius, V. (2008). A Room with a Viewpoint. *JCR* 35.
- Strohmetz, D., Rind, B., Fisher, R., & Lynn, M. (2002). Sweetening the Till. *JASP* 32.
- Freedman, J., & Fraser, S. (1966). Compliance without Pressure. *JPSP* 4.
- Worchel, S., Lee, J., & Adewole, A. (1975). Effects of Supply and Demand. *JPSP* 32.
- Eisenberger, N., Lieberman, M., & Williams, K. (2003). Does Rejection Hurt? *Science* 302.
- Han, Y., Nunes, J., & Drèze, X. (2010). Signaling Status with Luxury Goods. *Journal of Marketing* 74.
- Brown, A.L., Imai, T., Vieider, F., & Camerer, C. (2024). Meta-Analysis of Empirical Estimates of Loss Aversion. *Journal of Economic Literature* (mean λ = 1.955, 95% CI [1.82, 2.10], n=607 estimates from 150 articles 1992–2017).
- Walasek, L., Mullett, T., & Stewart, N. (2025). Loss aversion is not robust: A re-meta-analysis. *Journal of Behavioral Decision Making* (symmetric gains/losses: λ ≈ 1.07).
- Milkman, K.L. et al. (2021). A megastudy of text-based nudges encouraging patients to get vaccinated. *PNAS* 118(20) e2101165118 (n=47,306, 19 nudges, +5% vaccination).
- Bakshy, E., Messing, S., & Adamic, L.A. (2015). Exposure to ideologically diverse news on Facebook. *Science* 348(6239).
- Kozyreva, A., Herzog, S.M., et al. (2023). Resolving content moderation dilemmas between free speech and harms. *Nature Human Behaviour* 7.
- Hofstede, G. (2010). *Cultures and Organizations*. McGraw-Hill.
- Veblen, T. (1899). *The Theory of the Leisure Class*.
- Bourdieu, P. (1984). *Distinction*.

## Related
- [[projects/Entity/research/20260416-human-edge-experiment|20260416-human-edge-experiment]]
- [[projects/Entity/research/20260416-human-edge-diagnostic|20260416-human-edge-diagnostic]]
- [[projects/Entity/research/20260416-human-edge-falsification|20260416-human-edge-falsification]]
- [[projects/Entity/research/20260416-human-edge-playbook|20260416-human-edge-playbook]]
- [[projects/Entity/research/20260412-monetization-theory|20260412-monetization-theory]]
- [[projects/Entity/research/20260411-wtp-decision-playbook|20260411-wtp-decision-playbook]]
- [[projects/Entity/research/20260411-wtp-product-design-patterns|20260411-wtp-product-design-patterns]]
- [[projects/Entity/research/20260411-wtp-meta-review|20260411-wtp-meta-review]]
