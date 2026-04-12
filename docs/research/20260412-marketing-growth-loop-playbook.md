# Viral Growth Loop Implementation Playbook (S1)
**corpus**: marketing_growth | **doc_id**: S1 | **layer**: L2  
**Date**: 2026-04-12 | **Status**: stable

---

## Purpose

루프 아키타입을 선택하고 실제로 구현하는 단계별 실행 가이드. D1(진단)에서 아키타입을 확인한 후 이 문서를 참조한다.

---

## Loop Selection Decision Tree

```
제품의 핵심 사용이 협업을 전제하는가?
  YES → PLG 임베딩 루프 (2B)
  NO  →

공유 없이 핵심 가치를 100% 달성하는가?
  YES → 인센티브 기반 Referral 루프 (2A)
  NO  → PLG 임베딩 루프 (2B)

사용자가 콘텐츠를 외부 플랫폼에 공유하는가?
  YES → UGC/Community 루프 (2D) 추가 고려

검색을 통해 발견되고 싶은가?
  YES → Content SEO 루프 (2C) 추가 고려

LTV > CAC가 확인되었는가?
  YES → Paid Reinvestment 루프 (2E) 고려
```

---

## 2A: Incentivized Referral Loop (Dropbox 모델)

**적합 제품**: 단독 사용 가능하지만 네트워크 효과로 더 유용해지는 제품 (스토리지, 문서, 도구)

### 구현 단계

**Phase 1: 인센티브 설계 (Week 1–2)**

| 항목 | 권장 | 피해야 할 것 |
|------|------|------------|
| 인센티브 유형 | 핵심 가치 직결 (스토리지, 기능 unlock) | 현금/포인트만 (디커플링 위험) |
| 방향성 | 양방향 (referrer + referee 모두 보상) | 단방향 (referrer만) |
| 보상 타이밍 | referee 첫 활성화 즉시 | 장기 딜레이 (30일+) |
| 보상 규모 | 가치 있지만 마진 허용 범위 내 | 너무 작음(무시됨) / 너무 큼(CAC 역전) |

양방향 인센티브 conversion lift: +25–50% (Stratrix 2025 benchmark).

**Phase 2: 진입점 배치 (Week 2–3)**

```
배치 우선순위 (높음 → 낮음):
1. Onboarding 완료 직후 (activation moment — 제품 가치를 막 경험한 순간)
2. 핵심 기능 첫 사용 직후 (aha moment)
3. 대시보드 상단 고정 배너
4. 이메일 시퀀스 (3일차, 7일차)

❌ 피해야 할 위치:
- 첫 화면 (가치 경험 전 → 거절)
- 모달 강제 (UX 마찰 증가)
- 결제 페이지 (주의 분산)
```

**Phase 3: 측정 설정 (Week 3)**

필수 추적 지표:
- Activation Rate (초대 완료율 / 새 사용자)
- K-factor = (월 초대 수 / MAU) × (수락률)
- Invitation Acceptance Rate (코호트별 추이)
- Virally-acquired 30d retention vs paid-acquired

건강 기준:
- Acceptance Rate: 최소 10%, 목표 20%+
- Virally-acquired retention: paid-acquired 동등 또는 우월 (warm introduction 효과)
- 4주 내 Acceptance Rate 20%+ 하락 → trust erosion 긴급 점검

---

## 2B: PLG Embedded Virality (Calendly/Figma 모델)

**적합 제품**: 사용 자체가 비사용자를 노출시키는 제품 (공유 링크, 협업 파일, 임베드 위젯)

### 구현 단계

**Phase 1: 바이럴 접점 감사 (Week 1)**

```
제품에서 비사용자가 만나는 모든 접점 목록:
□ 공유 URL (공개 링크인가, 로그인 요구인가?)
□ 이메일 알림 (비사용자도 받는가?)
□ 임베드/위젯 (외부 사이트에 삽입 가능한가?)
□ PDF/Export (브랜딩 포함인가?)
□ 초대 이메일 (비사용자가 클릭 시 어디로 가는가?)
```

비사용자 첫 경험 설계 원칙:
1. 로그인 전에 가치를 경험시킨다 (wall 이전에 aha moment)
2. "Powered by / Made with [제품명]" 브랜딩을 가치 노출 위치에 배치
3. CTA는 딱 하나 ("Try for free" — 계정 생성 마찰 최소화)

**Phase 2: 공유 워크플로우 통합 (Week 2–3)**

PLG virality 체크리스트:
- [ ] 핵심 액션(공유, 협업 초대, 링크 전송)이 주요 워크플로우에 embedded
- [ ] 공유 없이는 제품의 핵심 가치를 완전히 활용할 수 없음을 UX가 자연스럽게 유도
- [ ] 비사용자 랜딩 페이지가 즉시 가치를 보여줌 (사용 예시, 미리보기)
- [ ] 가입 → 첫 활성화까지 3 클릭 이내

**Phase 3: 루프 모니터링 (Week 4+)**

```
virality_rate = (공유 링크를 통한 신규 가입) / (공유 링크를 클릭한 비사용자)
목표: > 15%

invited_activation_rate = (링크 클릭 후 첫 활성화) / (링크 클릭)
목표: > 30% (warm context — 이미 제품을 본 상태)
```

---

## 2C: Content SEO Loop

**적합 제품**: 사용자 행동이 검색 인덱싱 가능한 공개 페이지를 생성하는 제품

### 구현 단계

```
Step 1: 인덱싱 가능 콘텐츠 유형 확인
  - 사용자 프로필 페이지 (공개 URL?)
  - 생성 결과물 (공개 링크로 공유 가능?)
  - 커뮤니티 Q&A, 리뷰, 포스트

Step 2: SEO 기술 설정
  - robots.txt: UGC 페이지 크롤링 허용
  - Canonical URL 설정 (중복 콘텐츠 방지)
  - Open Graph 태그 (소셜 공유 미리보기)
  - 구조화 데이터 (Schema.org)

Step 3: 롱테일 키워드 전략
  - 사용자가 생성하는 콘텐츠의 자연어 제목이 실제 검색 쿼리와 매칭되는지 확인
  - 매칭 안 됨 → 제목 템플릿 또는 SEO-friendly 기본 구조 제공

Step 4: Loop 측정
  - Organic search → 랜딩 → 가입 퍼널 추적
  - 콘텐츠 생성량 vs 신규 유입 상관관계 확인
```

---

## 2D: UGC / Community Loop

**주의**: UGC 루프는 플랫폼 수준 콘텐츠 모더레이션 투자가 선행되어야 한다.

### 핵심 설계 원칙

1. **공유 마찰 최소화**: 콘텐츠 생성 → 외부 공유 → 바이럴 노출까지 2클릭 이내
2. **공유 인센티브 내재화**: 공유가 작성자에게 가치를 준다 (조회수, 팔로워, 인정)
3. **플랫폼 브랜딩**: 공유된 콘텐츠에서 제품 출처가 명확히 보임
4. **중재 인프라**: 스팸/abuse 필터링 없이 성장하면 trust erosion → 루프 붕괴

---

## 2E: Paid Reinvestment Loop

**전제 조건**: LTV > CAC가 코호트 데이터로 검증된 상태에서만 진입.

```
Loop mechanics:
  유료 광고 → 신규 사용자 획득
  → 높은 retention + LTV 실현
  → 잉여 마진으로 다음 광고 코호트 자금 조달
  → CAC 효율 개선 (데이터 축적 → 타겟팅 개선)

측정 지표:
  - CAC 추이 (목표: 하락 또는 안정)
  - LTV:CAC ratio (최소 3:1 유지)
  - Payback period (12개월 이내 권장)
```

---

## 루프 보강 전략 (Multi-Loop)

단일 루프로 시작하되, K > 0.5 달성 후 보조 루프를 추가한다:

```
Primary (항상 먼저): Referral 또는 PLG 임베딩 루프
↓ K > 0.5 달성
Secondary (보강): Content SEO 루프 (검색 트래픽 추가)
↓ MAU > 1,000
Tertiary (선택): UGC 루프 (콘텐츠 플라이휠)
```

**⚠️ Anti-pattern**: 여러 루프를 동시에 런칭하면 측정과 최적화가 불가능하다.  
한 번에 하나, K > 0.3 확인 후 다음 루프로 이동.

---

## 실행 타임라인 (0–90일)

| Phase | 기간 | 목표 | 성공 지표 |
|-------|------|------|---------|
| 측정 인프라 | Week 1–2 | 6개 핵심 지표 대시보드 구축 | Activation Rate, K-factor 실측 |
| 루프 선택 + 설계 | Week 2–3 | 아키타입 선택 + 인센티브/UX 설계 | D1 진단 완료, 아키타입 확정 |
| MVP 배포 | Week 3–5 | 루프 첫 배포 | 초대 수락 첫 케이스 |
| 최적화 | Week 5–12 | Activation Rate 최적화 | K-factor > 0.3 달성 |
| 확장 | Month 3+ | Cycle time 단축 + 보조 루프 검토 | K > 0.5, Acceptance Rate 안정 |

---

## Sources
- T1: 20260412-marketing-growth-theory.md
- D1: 20260412-marketing-growth-diagnostic.md
- T4: 20260412-marketing-growth-falsification.md
- Stratrix — Component 2 (viral mechanics), Component 4 (cycle time), Components 7-8 (trust)
- CraftUp — Growth Loop implementation templates (November 2025)
- Dropbox case: GrowthHackers / Brands at Play (3,900% growth, 35% referral signups)
