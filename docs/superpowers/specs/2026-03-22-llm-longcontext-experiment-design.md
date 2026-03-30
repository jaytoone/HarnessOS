# LLM 장기 컨텍스트 실험 시스템 설계

**날짜**: 2026-03-22
**프로젝트**: AutoCode
**목적**: Claude Code(설계·지휘) + OpenHands(자율 실행) 조합으로 LLM 장기 컨텍스트 한계 실험

---

## 1. 목표

### 실험 A: 기억력 저하 측정 (Lost-in-the-Middle)
컨텍스트 길이가 증가함에 따라 LLM이 앞 내용을 얼마나 정확하게 recall하는지 측정.

### 실험 B: 코딩 작업 실수 시점 측정
OpenHands 에이전트가 장기 코딩 작업 중 어느 시점(스텝/토큰 수)부터 실수가 급증하는지 관찰.

---

## 2. 기술 스택

- **LLM**: MiniMax M2.5 (OpenHands 연동)
- **실험 실행기**: Python (`runner.py`)
- **실시간 대시보드**: Python `rich` 라이브러리
- **결과 저장**: JSON (results/ 디렉토리)
- **에이전트 실행 환경**: OpenHands (Docker, localhost:3000)

---

## 3. 프로젝트 구조

```
AutoCode/
├── experiments/
│   ├── context_memory/         # 실험 A: 기억력 저하
│   │   ├── tasks.py            # recall 태스크 생성기
│   │   └── evaluator.py        # 정답 평가 로직
│   └── coding_failure/         # 실험 B: 코딩 실수 시점
│       ├── tasks.py            # 단계별 코딩 태스크 생성기
│       └── evaluator.py        # 코드 실행/검증 로직
├── runner.py                   # 실험 실행기 (OpenHands API 호출)
├── dashboard.py                # 실시간 터미널 대시보드 (rich)
├── results/                    # JSON 실험 결과 저장
│   └── .gitkeep
├── requirements.txt
└── README.md
```

---

## 4. 실험 상세 설계

### 실험 A: 기억력 저하 측정

**방식**: 문서 내 특정 위치에 정보를 삽입하고, 컨텍스트 전체를 LLM에 제공한 후 recall 질문

**컨텍스트 길이 단계**:
- 1K 토큰
- 10K 토큰
- 50K 토큰
- 100K 토큰

**정보 삽입 위치**:
- 앞부분 (처음 10%)
- 중간부분 (45~55%)
- 뒷부분 (마지막 10%)

**측정 지표**:
- 위치별 recall 정확도 (%)
- 응답 시간 (ms)
- 컨텍스트 길이별 정확도 곡선

**예시 태스크**:
```
[컨텍스트 삽입] "비밀 코드는 ALPHA-7734 입니다."
... (패딩 텍스트 N 토큰) ...
[질문] "앞에서 언급된 비밀 코드는 무엇인가요?"
```

---

### 실험 B: 코딩 실수 시점 측정

**방식**: OpenHands에게 점진적으로 복잡한 코딩 작업을 부여, 스텝별 성공/실패 추적

**단계별 태스크**:
| 스텝 | 태스크 | 예상 성공률 |
|------|--------|------------|
| 1-5  | 단순 함수 작성 (단일 파일) | ~100% |
| 6-10 | 여러 파일 수정, 의존성 추가 | ~80% |
| 11-15 | 기존 코드 리팩토링 | ~60% |
| 16-20 | 아키텍처 변경, 인터페이스 수정 | ~40% |

**측정 지표**:
- 스텝별 성공/실패
- 실패 유형 분류 (컴파일 오류, 논리 오류, 컨텍스트 망각 등)
- 실패 급증 시점의 컨텍스트 토큰 수
- 총 소요 시간

---

## 5. 실시간 대시보드 UI

```
┌─ LLM 장기 컨텍스트 실험 ──────────────────────────┐
│ 실험: B - 코딩 실수 시점  모델: MiniMax-M2.5        │
│ 현재 스텝: 8/20    컨텍스트: 45,230 tokens          │
│ ████████░░░░░░░░░░░░ 40%                            │
├─ 성공률 현황 ────────────────────────────────────────┤
│ 스텝  1- 5:  ██████████ 100% (5/5)                  │
│ 스텝  6-10:  ████████░░  80% (3/4, 진행중)           │
│ 스텝 11-15:  ░░░░░░░░░░   -  (미시작)                │
├─ 최근 로그 ──────────────────────────────────────────┤
│ [08] SUCCESS  함수 리팩토링 완료  | 45,230 tok        │
│ [07] FAILURE  파일 참조 오류      | 38,104 tok        │
│ [06] SUCCESS  API 엔드포인트 추가 | 31,882 tok        │
└─────────────────────────────────────────────────────┘
```

---

## 6. OpenHands 연동 방식

### 6.1 대화 생성 (실제 API 스키마 기준)

```python
POST http://localhost:3000/api/conversations
Content-Type: application/json

{
  "initial_user_msg": "<태스크 프롬프트>",
  "conversation_trigger": "gui"
}

Response: {"status": "ok", "conversation_id": "<id>"}
```

### 6.2 결과 수집

OpenHands는 WebSocket 기반 실시간 이벤트 스트리밍을 사용.
REST 폴링으로는 대화 메타데이터만 조회 가능:

```python
GET http://localhost:3000/api/conversations/{conversation_id}
# → status, 기본 정보

GET http://localhost:3000/api/conversations/{conversation_id}/trajectory
# → 에이전트 실행 전체 이력 (actions + observations)
```

**실용적 구현 전략**: trajectory 폴링 (1초 간격) → 마지막 이벤트 기준 완료 판정

### 6.3 실험 A (기억력 측정)의 LLM 호출 경로

실험 A는 OpenHands 에이전트 경유가 아닌 **MiniMax API 직접 호출** 방식 사용:
- OpenHands는 코딩 에이전트이므로 순수 recall 테스트에 부적합
- MiniMax API (`https://api.minimax.io/v1/chat/completions`) 직접 호출
- 실험 B만 OpenHands 에이전트 경유

---

## 7. 결과 저장 포맷

```json
{
  "experiment": "coding_failure",
  "model": "minimax/MiniMax-M2.5",
  "timestamp": "2026-03-22T10:00:00Z",
  "steps": [
    {
      "step": 1,
      "task": "단순 함수 작성",
      "status": "success",
      "context_tokens": 1240,
      "duration_ms": 3200,
      "error": null
    }
  ],
  "summary": {
    "total_steps": 20,
    "success_rate": 0.75,
    "failure_inflection_step": 11,
    "failure_inflection_tokens": 42000
  }
}
```

---

## 8. 성공 기준

- [ ] 실험 A: 4가지 컨텍스트 길이 × 3가지 위치 × n=3 반복 = 36개 데이터포인트 수집
- [ ] 실험 B: 20스텝 완주, 실패 급증 시점 특정
  - **실패 급증 판정**: 연속 2회 실패 또는 해당 구간(5스텝) 실패율이 이전 구간 대비 2배 이상
- [ ] 실시간 대시보드: rich 라이브러리로 1초 갱신 주기 동작 확인
- [ ] 결과 JSON 자동 저장 (results/ 디렉토리)
- [ ] OpenHands trajectory API로 결과 수집 성공

## 9. 전제 조건 및 제약

- **MiniMax M2.5 컨텍스트 윈도우**: 공식 100K 토큰. 실험 A의 최대 100K 범위 내.
- **실험 A 반복 횟수**: 각 조건당 n=3 (통계적 노이즈 최소화)
- **실험 B 태스크 생성**: 각 스텝은 이전 스텝 결과물 위에 누적 (컨텍스트 자연 증가)
- **패딩 텍스트**: tiktoken 또는 문자 수 기반 근사치로 토큰 수 제어

---

## 10. 역할 분담

| 역할 | 도구 | 작업 |
|------|------|------|
| 설계·지휘 | Claude Code | 스펙 작성, 실험 설계, 결과 분석 |
| 자율 실행 | OpenHands (MiniMax M2.5) | 실험 코드 작성·실행, 태스크 수행 |
| 공유 저장소 | `/home/jayone/Project/AutoCode` | 양쪽 모두 접근 |
