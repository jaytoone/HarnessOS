# Viral Growth Diagnostic Protocol (D1)
**corpus**: marketing_growth | **doc_id**: D1 | **layer**: L2  
**Date**: 2026-04-12 | **Status**: stable

---

## Purpose

Viral growth 상황 진단을 위한 구조화된 인터뷰/분석 프로토콜. 제품의 현재 루프 상태를 빠르게 파악하고 우선순위 개입 지점을 식별한다.

**사용 시점**: 
- 신규 제품의 viral growth 전략 설계 전
- 기존 루프가 기대보다 낮은 성과를 낼 때
- K-factor 최적화 우선순위 결정 시

---

## Stage 1: 루프 기반 진단 (5문항)

### Q1 — 루프 아키타입 식별
"현재 제품에서 신규 사용자가 유입되는 경로를 모두 나열하세요."

**분류 기준**:
- 사용자가 직접 초대 → viral/referral 루프 
- 제품 사용 자체가 배포 (캘린더 링크, 공유 문서) → PLG 임베딩 루프
- 사용자 행동이 검색 인덱스 생성 → Content SEO 루프
- 사용자가 콘텐츠를 만들어 외부 공유 → UGC/community 루프
- 유료 획득 → LTV > CAC 여부 확인 → paid reinvestment 루프

**진단 결과 없음**: 루프 아키타입이 명확하지 않으면 바이럴 설계 전에 아키타입 결정이 선행.

---

### Q2 — Activation Rate 측정 현황
"신규 사용자 중 [핵심 공유 액션]을 완료하는 비율은 얼마입니까? 이 지표를 추적하고 있습니까?"

**핵심 공유 액션 예시**:
- Dropbox: 폴더 공유
- Calendly: 미팅 링크 전송
- Figma: 파일 협업자 초대
- 일반 SaaS: "초대하기" 또는 "팀 추가" 클릭

**벤치마크**:
- Activation Rate < 5% → 루프 자체가 작동 안 함 (루프 재설계 고려)
- 5–20% → 개선 여지 큼 (onboarding 개선, 트리거 위치 최적화)
- > 20% → healthy (K-factor 및 cycle time 최적화로 이동)

---

### Q3 — K-factor 현재값
"(초대 수 / MAU) × (초대 수락률)을 계산할 수 있습니까?"

**계산 가이드**:
```
K = (월 평균 초대 수 / 월 활성 사용자) × (초대 수락 후 신규 가입 / 총 초대 수)
```

**데이터 없는 경우**: 이 시점에서 K-factor 최적화보다 측정 인프라 구축이 우선.

---

### Q4 — Cycle Time 측정
"초대 발송에서 초대받은 사람의 첫 활성화(activation)까지 평균 소요 시간은?"

**기준값**:
- < 24시간: 매우 빠른 루프 (B2C messaging 수준)
- 1–7일: 정상 범위 (B2C SaaS)
- 7–21일: B2B SaaS 일반적
- > 21일: cycle time 단축 개입 필요

**단축 레버**: 초대 이메일 타이밍, 초대받은 사람의 onboarding 단계 수, 가치 경험까지의 클릭 수.

---

### Q5 — 신뢰도 지표 (Trust Signal)
"최근 4주 코호트에서 초대 수락률 추이가 어떻습니까?"

**해석**:
- 수락률 감소 없음: 루프 건강
- 수락률 10–20% 하락: 주의 (초대 빈도, 타겟팅 품질 점검)
- 수락률 > 20% 하락: trust erosion — 루프 메커니즘 긴급 점검

**연결 지표**: 바이럴 획득 사용자 30일 리텐션 vs 유료 획득 사용자 비교 (바이럴 품질 벤치마크).

---

## Stage 2: 루프 아키타입별 추가 진단

### 2A — Viral/Referral 루프 (Dropbox 모델)

| 진단 항목 | 질문 |
|---------|------|
| 인센티브 구조 | 양방향 인센티브(referrer + referee)인가, 단방향인가? |
| 인센티브 연결성 | 인센티브가 핵심 가치(스토리지, 기능)에 연결되어 있는가, 현금/포인트인가? |
| 초대 마찰 | 초대 완료까지 몇 번의 클릭이 필요한가? |
| 인지 시점 | 사용자가 초대 기능을 언제 처음 보는가? (onboarding 중 vs 이후) |

**양방향 인센티브 효과**: +25–50% conversion lift (Stratrix benchmark).

---

### 2B — PLG 임베딩 루프 (Calendly/Figma 모델)

| 진단 항목 | 질문 |
|---------|------|
| 공유 필수성 | 공유 없이 제품의 핵심 가치를 100% 달성 가능한가? |
| 비사용자 접점 | 비사용자가 제품 URL/파일을 받을 때 어떤 경험을 하는가? |
| 전환 마찰 | 비사용자 → 가입 → 첫 활성화까지 단계 수 |
| 바이럴 브랜딩 | "Powered by / Sent via [제품명]" 노출이 있는가? |

**핵심 체크**: 공유가 협업의 부산물이 아니라 협업의 전제조건이어야 한다.

---

### 2C — Content SEO 루프

| 진단 항목 | 질문 |
|---------|------|
| 인덱싱 가능 콘텐츠 | 사용자 행동이 public URL을 생성하는가? |
| 검색 의도 매칭 | 생성된 콘텐츠가 실제 검색 쿼리와 매칭되는가? |
| 롱테일 규모 | 사용자가 생성하는 콘텐츠의 다양성이 충분한가? |
| 크롤링 허용 | robots.txt가 UGC 페이지 인덱싱을 허용하는가? |

---

## Stage 3: 개입 우선순위 결정 프레임워크

```
Activation Rate < 10%?
  → YES: Loop 재설계 또는 onboarding 개선이 먼저 (K-factor 작업 보류)
  → NO: 다음 단계

K-factor 미측정?
  → YES: 측정 인프라 구축이 먼저
  → NO: 다음 단계

K < 0.3?
  → YES: 아키타입 재선택 검토 (현재 루프가 제품에 맞지 않을 수 있음)
  → K = 0.3–0.7: Cycle time 단축 (가장 ROI 높음)
  → K > 0.7: Trust signal 모니터링 + 신규 채널 보강

Invitation acceptance rate 하락 중?
  → YES: loop 추출 패턴 긴급 점검 (trust restoration 우선)
  → NO: 정상 운영 모드
```

---

## Stage 4: 측정 대시보드 체크리스트

배포 전 반드시 설정해야 하는 지표:

- [ ] Activation Rate (루프 트리거 액션 완료율)
- [ ] K-factor (코호트별, 월별)
- [ ] Viral Cycle Time (초대 → 신규 활성화 평균 소요일)
- [ ] Invitation Acceptance Rate (코호트별 추이)
- [ ] Virally-acquired 30-day retention (vs paid-acquired)
- [ ] Sharing Rate (MAU 중 공유자 비율 — 목표: 15–40%)

**주의**: 위 6개 지표 없이 K-factor 최적화를 시작하면 개선 방향을 알 수 없다.

---

## 빠른 진단 (5분 버전)

3가지만 먼저 확인:
1. 어떤 루프 아키타입인가? (5 archetypes 중 1개 선택)
2. Activation Rate를 측정하고 있는가?
3. 초대 수락률이 하락하고 있는가?

이 3가지 답이 없으면 K-factor 수치 논의는 시기상조다.

---

## Sources
- T1: 20260412-marketing-growth-theory.md
- T4: 20260412-marketing-growth-falsification.md
- Stratrix — Viral Growth Dashboard targets
- OpenView 2024 PLG benchmark (activation tracking 34% only)
- CraftUp — Growth Loop diagnostic templates

## Related
- [[projects/Entity/research/20260412-marketing-growth-falsification|20260412-marketing-growth-falsification]]
- [[projects/Entity/research/20260412-marketing-growth-theory|20260412-marketing-growth-theory]]
- [[projects/Entity/research/20260412-marketing-growth-corpus-draft|20260412-marketing-growth-corpus-draft]]
