# OSS AI Agent Tools 2026 — HarnessOS Integration Assessment

## Source
- **Video**: 7 new open source AI tools you need right now
- **URL**: https://www.youtube.com/watch?v=Xn-gtHDsaPY
- **Absorbed via**: /inhale trending_tools — Fireship (2026-03-12)
- **Relevance**: 10.0/10 (skill_selection)

## Core Idea
2026년 초 AI 에이전트 생태계에서 급부상한 7개 오픈소스 도구 분석.
공통 패턴: (1) 에이전트를 "whip into shape" 하는 제어 레이어,
(2) 고도로 효율적인 에이전트 실행 인프라, (3) 특정 도메인 특화 에이전트 툴킷.

## HarnessOS Integration Assessment

### 도구 분류 프레임워크
```
HarnessOS 관점의 통합 우선순위:

Priority 1 (즉시 통합 가능):
  - 에이전트 제어/모니터링 레이어 → CTX 또는 Safety Triad에 연결
  - 경량 평가 도구 → execution_reward oracle로 사용

Priority 2 (실험 후 통합):
  - 메모리 관리 도구 → omc-episode-memory와 통합
  - 도구 선택 라우터 → skill_patcher.py와 통합

Priority 3 (참고/벤치마크용):
  - 특정 도메인 특화 도구 → 경쟁 분석 대상
```

### 평가 기준 (HarnessOS 적합성)

| 기준 | 가중치 | 설명 |
|------|--------|------|
| live-inf 호환성 | 40% | 무한 루프 내에서 호출 가능한가 |
| 의존성 경량화 | 25% | 추가 패키지 최소화 |
| Python 인터페이스 | 20% | `subprocess` 또는 직접 import |
| 오픈소스 라이선스 | 15% | MIT/Apache2 필수 |

### 실제 적용 후보

**1. 에이전트 형상화(shaping) 도구**
- HarnessOS 연결점: `evolution_safety.py`의 Safety Triad를 외부 검증기로 교체 가능
- 통합 방식: `SafetyTriad.external_validator = ExternalTool()`
- 위험도: 낮음 (optional layer)

**2. 실행 추적 도구**
- HarnessOS 연결점: `.omc/evolution-registry.jsonl`의 상태 추적 보강
- 통합 방식: registry writer를 외부 추적 도구로 대체
- 위험도: 중간 (기존 registry 포맷 변경 필요)

**3. 경량 벤치마크 도구**
- HarnessOS 연결점: `execution_reward`의 oracle 함수 대체
- 통합 방식: `oracle = ExternalBenchmark(task_type=...)`
- 위험도: 낮음 (oracle 인터페이스만 맞추면 됨)

### Next Steps
1. Fireship 영상 전체 시청 후 7개 도구 목록 확정
2. 각 도구에 대해 위 평가 기준 스코어링
3. Priority 1 도구 1개 선택 → `skill_patcher.py`에 통합 프로토타입

### Trade-offs

| 통합 방식 | 장점 | 단점 |
|-----------|------|------|
| 직접 임포트 | 빠른 실행 | 의존성 추가 |
| subprocess 래핑 | 격리 보장 | 지연 증가 |
| HTTP API | 언어 무관 | 네트워크 의존 |

**권장**: subprocess 래핑으로 시작 (live-inf 내 안전성 우선)
