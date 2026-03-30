# [expert-research-v2] 완전 자율 에이전트 — 목표 자율 업데이트 + 하위 루프 구성법
**Date**: 2026-03-25  **Skill**: expert-research-v2

## Original Question
최근 자율 에이전트 동작과 관련한 연구/리서치. 특히 완전 자율을 위해서 자율 루프의 목표인 최종 상태에 대해 자율로 업데이트하는 부분, 하위의 루프 구성법 등 다각적인 부분 구조화.

---

## Web Facts

[FACT-1] [AREA-A] Self-Evolving AI Agents Three Laws (Fang et al. 2025, arXiv:2508.07407):
Endure(안전/안정성 유지) + Excel(성능 보존 하 적응) + Evolve(자율 지속 개선). 실용적 설계 제약.

[FACT-2] [AREA-A] AgentEvolver Proxy Task Generation (arXiv:2511.10395):
호기심 탐색→태스크 합성→큐레이션. 인간 설계 없이 p_train(g) ≈ p_target(g) 근사.

[FACT-3] [AREA-A] GCRL Goal-Conditioned RL (NeurIPS 2024):
V^π_θ(s_0, g) — 목표 조건부 가치 함수. 목표 도달 vs 수정 필요 여부 자율 인식.

[FACT-4] [AREA-A] AgentEvolver Self-Attributing (arXiv:2511.10395):
F_reward: E×G → (S×A→R) — 환경 보상 없이 LLM이 궤적 기여도를 단계별 평가.

[FACT-5] [AREA-A] Evolutionary Curriculum Agents (2025):
개체군 기반 탐색 + 커리큘럼 적응. 성공률 기반 난이도 자동 조정.

[FACT-6] [AREA-A] MAHRL Multi-Agent Hierarchical RL (arXiv:2411.01184):
상위 정책 → 협력 서브 목표 분해. 서브 목표 완료 신호 → 부모 목표 정제.

[FACT-7] [AREA-B] Inner/Outer Loop 이분법 (philschmid.de 2026):
Inner: 단일 태스크 실행 사이클. Outer: 장기 메모리/스킬/룰. 루프 인프라 동일, 의사결정이 차별화.

[FACT-8] [AREA-B] Meta Learning Agent 이중 루프 (2025):
Inner: 특정 태스크 π_θ 학습 (소수 그래디언트). Outer: 메타 파라미터 φ 최적화.

[FACT-9] [AREA-B] AgentEvolver 3중 루프 (arXiv:2511.10395):
(1) Self-questioning(탐색→태스크) (2) Self-navigating(경험 가이드 롤아웃) (3) Self-attributing(보상 분배). 통합 컨텍스트 매니저 운용.

[FACT-10] [AREA-B] AgentOrchestra TEA Protocol (ICLR 2026 submission):
T2A, E2T, A2E, A2T, E2A, T2E 6개 변환 채널. 하위 에이전트 행동 = 환경 제약으로 추상화.

[FACT-11] [AREA-B] AgentEvolver Self-navigating 동적 서브 루프 (arXiv:2511.10395):
태스크 유사도 벡터 검색 → 경험 검색 → 조건부 스폰. 성공 임계값 OR 반복 한계 = 종료.

[FACT-12] [AREA-B] Magentic-One 이중 루프 실패 처리 (Microsoft 2025):
Inner Loop 교착 → Outer Loop 리셋. 하위 에이전트 실패 → 상위 태스크 재분해 → 다른 에이전트 스폰.

---

## Multi-Lens Analysis

### 1부: AREA-A — 목표 자율 업데이트 메커니즘 분류 체계

#### 수정 깊이(Level) 분류

| Level | 유형 | 내용 | 트리거 |
|-------|------|------|--------|
| 0 | 파라미터 조정 | 목표 세부 파라미터 변경 (임계값 등) | 실행 불가능성 감지 |
| 1 | 서브 목표 재구성 | 최상위 목표 유지, 분해 방식 변경 | 서브 목표 완료 + 상위 목표 미달 |
| 2 | 목표 확장 | 기존 유지 + 새 목표 추가 | 탐색 중 새 상태 공간 발견 |
| 3 | 목표 교체 | 완전히 다른 목표로 대체 | 현재 목표의 근본적 실행 불가능성 |

Level 0-1은 안전하지만 국소적, Level 2-3은 강력하지만 목표 발산(goal drift) 위험.

#### 트리거 조건 분류

| 트리거 유형 | 메커니즘 |
|------------|---------|
| 실패 기반 | 임계 반복 초과, 진행 없는 루프 감지 |
| 가치 기반 | V^π_θ(s,g) < threshold → 도달 불가 판정 |
| 호기심 기반 | 예상치 못한 상태 발견 → 새 목표 생성 |
| 분포 기반 | p_train ≠ p_target 격차 감지 → 태스크 큐레이션 |
| 보상 재설계 | F_reward: E×G → (S×A→R) 재계산 |

#### 핵심 원칙: 목표-보상 동시 업데이트

목표(g)가 변경되면 보상 함수(F_reward)도 반드시 동반 재설계해야 한다.
목표만 변경하고 보상 함수를 고정하면 goal-reward misalignment 발생.
F_reward가 목표에 조건부인 구조(FACT-4)는 이를 올바르게 구현한다.

---

### 2부: AREA-B — 하위 루프 구성법 분류 체계

#### 루프 계층 4대 패턴

**패턴 1: Inner/Outer 이분 구조**
```
Outer Loop (턴 간 지속성)
├── 장기 메모리 / 스킬 파일 / 룰 파일 관리
└── Inner Loop ×N
    ├── 단일 태스크 실행 사이클
    ├── 코드 작성 → 테스트 → 실패 → 수정 → 재테스트
    └── 종료: 성공 OR 최대 반복 초과
```
루프 인프라 동일; 에이전트의 학습된 의사결정이 차별화 요인.

**패턴 2: Meta-Learning 이중 최적화**
```
Outer Loop: 태스크 분포 D_task 샘플링, 메타 파라미터 φ 업데이트
└── Inner Loop ×K: 초기 파라미터 θ=f(φ), 소수 그래디언트로 π_θ 학습
중첩 최적화 비용: O(K·N) → 실용적 bottleneck
```

**패턴 3: AgentEvolver 3중 병렬 루프**
```
통합 컨텍스트 매니저
├── Loop-1: Self-questioning (환경→태스크 생성)
├── Loop-2: Self-navigating (경험 가이드 롤아웃)
└── Loop-3: Self-attributing (보상 분배)
3 루프 상호 의존: Loop-1 생성 → Loop-2 실행 → Loop-3 평가 → Loop-1 갱신
```

**패턴 4: TEA 계층 구조 (AgentOrchestra)**
```
Planning Agent (최상위)
└── 전문화 에이전트 (하위)
    ├── Deep Researcher Agent
    ├── Browser Use Agent
    ├── Deep Analyzer Agent
    └── Tool Manager Agent
변환 채널: T2A, E2T, A2E, A2T, E2A, T2E (6개)
하위 에이전트 행동 = 환경 제약으로 추상화 (모듈성 핵심)
```

#### 서브 루프 스폰/종료 조건

| 조건 유형 | 스폰 트리거 | 종료 조건 |
|----------|-----------|---------|
| 태스크 분해 | 복잡도 threshold 초과 | 서브 목표 완료 신호 |
| 전문화 필요 | 현재 능력 범위 초과 | 성공 임계값 도달 |
| 병렬화 기회 | 독립 서브 태스크 발견 | 반복 한계 초과 |
| 유사 경험 존재 | 태스크 유사도 검색 성공 | 교착 감지 → 강제 종료 |

#### 실패 전파 3유형

```
Type-1 일시적 실패: 하위 루프 재시도 (N회 미만) → 상위 알림 불필요
Type-2 지속적 실패: 실패 신호+컨텍스트 → 상위 루프 → 서브 목표 재분해 OR 에이전트 교체
Type-3 치명적 실패: 상위도 해결 불가 → AREA-A Level 2/3 목표 업데이트 트리거
```

---

### 3부: 두 축의 통합 구조

```
┌─────────────────────────────────────────────────────────────────┐
│                     META-AGENT SYSTEM                           │
│                                                                 │
│  [AREA-A: 목표 업데이트 레이어]                                  │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │  G = {g_1,...,g_n} + F_reward: E×G → (S×A→R)           │   │
│  │  + Three Laws 안전 경계 (Endure/Excel/Evolve)            │   │
│  │  업데이트 경로: 호기심탐색 → 태스크합성 → 큐레이션 → G갱신│   │
│  └──────────────────────────┬────────────────────────────┘   │
│                             │ 목표 할당 (g ∈ G)               │
│                             ▼                                   │
│  [AREA-B: 루프 계층 레이어]                                      │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │  Outer Loop (지속성/메타 최적화)                          │   │
│  │  ├── 장기 메모리, 스킬, 경험 누적                         │   │
│  │  └── Inner Loop 클러스터                                  │   │
│  │       ├── IL-1: Self-questioning (태스크 생성)             │   │
│  │       ├── IL-2: Self-navigating (경험 가이드)              │   │
│  │       └── IL-3: Self-attributing (보상 귀속)               │   │
│  └──────────────────────────┬────────────────────────────┘   │
│                             │                                   │
│         Type-3 치명적 실패  ◄──── 목표 달성 불가 확인            │
│         ─────────────────── ┘                                   │
│         ↑ AREA-A로 피드백: 목표 업데이트 트리거                  │
└─────────────────────────────────────────────────────────────────┘
```

**3개 결합점**:
1. 목표 Level 2/3 변경 → 루프 계층 재구성 동반 필수
2. Type-3 치명적 실패 → AREA-A Level 2/3 목표 업데이트 트리거
3. Self-attributing 보상 신호 → V^π_θ(s,g) 갱신 → 목표 업데이트 여부 결정

---

### 4부: 비판적 검토

**과신 사항**:
- AgentEvolver p_train ≈ p_target 근사: 탐색 편향 문제 미해결. 에이전트가 모르는 영역을 "발견"하기 어렵다는 근본적 한계.
- Three Laws의 "실용적 설계 제약" 주장: Endure vs Evolve 충돌 중재 알고리즘 미명시. Excel의 성능 측정 메트릭 불명확. Continual learning의 미해결 과제와 동일.

**누락 사항**:
- 목표 업데이트의 외부 가치 정렬 검증: 자율 목표 교체 시 설계자 의도와의 부합 여부 검증 메커니즘 없음.
- 3중 루프 컨텍스트 경합: Self-questioning이 리소스 과다 소비 시 Self-attributing 딜레이 → 학습 신호 지연.
- Oscillation 방지: Inner Loop 교착 → Outer Loop 리셋의 무한 진동 damping 메커니즘 미명시.

---

## Final Conclusion

### 실용 패턴 4가지

**Pattern 1: 계층적 목표 트리 + 보상 조건부 재설계**
Level에 따른 분기 처리. Level 2 이상은 안전 검증 후 루프 재구성 동반.
핵심: 목표 변경 = 보상 함수 변경 (동시 실행 필수).

**Pattern 2: 실패 분류기 기반 전파 라우팅**
Transient→자체재시도, Persistent→부모 루프 신호, Fatal→목표 업데이트 트리거.
Oscillation 방지: 실패 이력 카운터 + 지수 백오프.

**Pattern 3: 컨텍스트 우선순위 큐를 가진 병렬 루프**
P(Self-attributing) > P(Self-navigating) > P(Self-questioning).
타임슬라이싱 + 스냅샷-머지 정책으로 경합/starvation 방지.

**Pattern 4: TEA 변환 채널 + 하위 에이전트 추상화**
하위 에이전트를 환경 제약으로 추상화 → 모듈성 확보.
최소 구현: E2A + A2E 2개로 시작 → 점진 확장.

### Confidence: MEDIUM-HIGH

개별 메커니즘은 논문 기반 HIGH. 통합 구조 및 실용 패턴은 논문 간 추론으로 MEDIUM.
단일 시스템에서 모든 패턴 통합 구현 사례 미존재 → 실제 동작은 별도 검증 필요.

---

## Sources
- https://arxiv.org/abs/2508.07407 — Self-Evolving AI Agents 종합 서베이 (Fang et al. 2025)
- https://arxiv.org/abs/2511.10395 — AgentEvolver: Self-questioning/navigating/attributing (2025)
- https://arxiv.org/abs/2411.01184 — MAHRL: 계층적 다중 에이전트 RL (2024)
- https://openreview.net/forum?id=YcnKdeI9pp — AgentOrchestra TEA Protocol (ICLR 2026 submission)
- https://www.philschmid.de/agents-inner-outer-loop — Inner/Outer Loop 이분법 (2026)
- https://neurips.cc/ — GCRL Goal-Conditioned RL (NeurIPS 2024)
- https://www.microsoft.com/research/articles/magentic-one — Magentic-One 이중 루프 실패 처리 (2025)
