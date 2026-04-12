# Viral Growth / K-factor Falsification Criteria (T4)
**corpus**: marketing_growth | **doc_id**: T4 | **layer**: L2  
**Date**: 2026-04-12 | **Status**: stable

---

## Purpose

이 문서는 marketing_growth corpus의 **반증 기준 게이트**다. Corpus Pre-step에서 모든 viral growth 주장을 여기에 먼저 대조한다. 체크를 통과하지 못한 주장은 [UNCERTAIN] 또는 [CONFLICT] 태그로 표시한다.

---

## Hard Claims (HC) — 반드시 검증해야 하는 주장들

### HC-1: K > 1.0 달성 가능성

**주장**: "우리 제품은 K > 1.0을 달성할 수 있다"  
**반증 조건**: 아래 중 하나라도 해당하면 주장 기각

- 제품이 단독 사용 가능 (협업 필수 아님)
- 공유가 핵심 워크플로우에 포함되지 않음
- 현재 invitations_per_user < 3 AND conversion_rate < 0.3

**현실 기준**: 99th percentile 제품만 K > 1.0. 계획 목표로 설정 시 [OVERCONFIDENT] 처리.

---

### HC-2: Activation Rate 미측정 상태에서 K-factor 최적화

**주장**: "K-factor를 높이면 성장이 가속된다"  
**반증 조건**: activation rate를 별도 지표로 측정하지 않는 경우 → [PREMATURE OPTIMIZATION]

- Activation Rate = 신규 사용자 중 루프 트리거 액션을 완료한 비율
- 이것이 먼저 측정·최적화되지 않으면 K-factor 개선 효과는 희석됨

---

### HC-3: 고립된 초대량 (High invite volume, low acceptance)

**주장**: "초대 1000건을 보냈으니 viral loop가 작동한다"  
**반증 조건**: 초대 수락률(invitation acceptance rate)이 아래 기준 미달 시 → loop 품질 저하 신호

- 초대 수락률 < 10% (최소 건강 기준)
- 수락률이 4코호트 이내 20%+ 하락 → trust erosion 확정

**항상 함께 보고할 지표**: (1) 수락률, (2) 바이럴 획득 사용자 30일 리텐션, (3) 코호트별 K-factor 추이

---

### HC-4: Product-Led Loop (임베딩 바이럴) 강제 적용

**주장**: "우리는 Figma/Calendly처럼 PLG 임베딩 바이럴을 적용하겠다"  
**반증 조건**:
- 제품의 핵심 사용 시나리오가 단독 완결 (collaborators 없어도 가치 완전)
- 공유 없이 핵심 목적 달성 가능

→ 이 경우 embedded virality = [ARCHITECTURE MISMATCH]. 대신: 인센티브 기반 referral loop (Dropbox 모델) 권장.

---

### HC-5: 단일 출처 K-factor 벤치마크 절대화

**주장**: "Slack K = 8.5이므로 우리도 높은 K를 기대할 수 있다"  
**반증 조건**: Slack K ≈ 8.5 및 Facebook K ≈ 7은 Arfadia 단일 출처, 1차 소스 미확인.

- 이 수치를 계획 기준선으로 사용 시 [OVERCONFIDENT]
- 사용 가능한 표현: "directional upper bound" 또는 "reported peak K (single source)"

---

### HC-6: 루프 아키타입 없이 "바이럴" 사용

**주장**: "마케팅을 바이럴하게 만들겠다"  
**반증 조건**: 어떤 루프 아키타입(viral/referral, PLG, content SEO, UGC, paid reinvestment)인지 명시되지 않은 경우

→ 아키타입 미명시 = 실행 불가능한 계획. 반드시 5 archetypes 중 하나로 매핑.

---

### HC-7: 루프 벤치마크 산업 세그먼트 혼합

**주장**: "cycle time 2–14일이 업계 표준이다"  
**반증 조건**: B2C와 B2B를 혼합해 단일 기준으로 적용하는 경우

- B2C 메시징: 수시간–1일
- B2C 소비자 앱: 2–5일  
- B2B SaaS: 7–21일

세그먼트 명시 없이 사용 시 [CONTEXT MISSING] 처리.

---

## Confidence Calibration Rules

| 주장 유형 | 신뢰도 조건 | 태그 |
|---------|-----------|------|
| K-factor 수치 인용 | 단일 출처만 존재 | [DIRECTIONAL — single source] |
| "viral 성공 사례" | 어떤 루프 아키타입인지 미명시 | [UNCERTAIN — archetype?] |
| PLG 성과 지표 | vendor 데이터 (자사 도구 홍보 동기 존재) | [VENDOR DATA — use cautiously] |
| AI-native viral 주장 | 2024 단일 연구, fast-moving domain | [EMERGING — low sample] |

---

## Sycophancy Gate (Corpus Pre-step 적용)

주장이 다음 패턴에 해당하면 즉시 교정:

1. **K > 1.0 목표 설정** → "K > 1.0은 99th percentile. 계획 기준은 K = 0.3–0.7 CAC 감소 효과."
2. **PLG 임베딩 강제** → "공유가 핵심 워크플로우가 아닌 제품에 PLG 적용은 <2% share CTR로 실패."
3. **초대량 집착** → "초대 수락률과 바이럴 획득 리텐션을 함께 측정하지 않으면 loop 품질 판단 불가."
4. **Slack/Facebook 벤치마크 절대화** → "단일 출처 directional 수치. 계획 기준선으로 사용 금지."
5. **Activation rate 미측정** → "K-factor 최적화보다 activation rate 측정·개선이 우선 순서."

---

## Sources
- T1: 20260412-marketing-growth-theory.md (내부 이론 문서)
- MetricHQ Viral Coefficient benchmarks
- Stratrix — Viral Growth Strategy (components 7-8, trust metrics)
- CraftUp Growth Loop Examples (November 2025)
- arXiv 반증 방법론: wtp T4(20260411-wtp-falsification-criteria.md) 구조 참조

## Related
- [[projects/Entity/research/20260412-marketing-growth-theory|20260412-marketing-growth-theory]]
- [[projects/Entity/research/20260412-marketing-growth-corpus-draft|20260412-marketing-growth-corpus-draft]]
- [[projects/Entity/research/20260411-wtp-falsification-criteria|20260411-wtp-falsification-criteria]]
- [[projects/Entity/research/20260412-marketing-growth-diagnostic|20260412-marketing-growth-diagnostic]]
- [[projects/Entity/research/20260328-omc-live-infinite-loop-architecture-research|20260328-omc-live-infinite-loop-architecture-research]]
