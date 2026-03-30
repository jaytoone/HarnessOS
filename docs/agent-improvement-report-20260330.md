# 자율 에이전트 인사이트 수집 및 LiveCode 개선 보고서

**일자**: 2026-03-30
**대상**: LiveCode / AutoCode 시스템

---

## 1. 수집된 인사이트 요약

### 1.1 AI 코딩의 발전단계 (bcho.tistory.com/1508)
- **Why Loop / How Loop 분리**: 기획(Why)과 구현(How)을 분리하여 AI 활용 수준을 정의
- **On the Loop 하네스**: 결과물이 아닌 "결과물을 만들어내는 시스템"을 개선하는 패러다임
- **Agent Flywheel**: AI가 테스트/실패를 통해 스스로 하네스를 보강하는 자가 진화 개념
- **교훈**: Amazon 사례 -- 통제되지 않은 AI가 프로덕션 코드를 수정하여 대형 장애 발생. 인간의 교차 검증이 필수

### 1.2 장기 실행 하네스 설계 (Anthropic 엔지니어링 블로그)
- **Generator/Evaluator 분리** (GAN 영감): 자기 평가 편향 해결의 핵심. 독립된 평가기를 회의적으로 튜닝하는 것이 생성기를 자기비판적으로 만드는 것보다 효과적
- **컨텍스트 리셋 vs 컴팩션**: 컨텍스트 불안(context anxiety) 해결을 위해 전체 리셋이 컴팩션보다 효과적
- **3-에이전트 아키텍처**: Planner(스펙 확장) + Generator(구현) + Evaluator(Playwright QA)
- **스프린트 계약(Sprint Contract)**: 코드 작성 전 "완료" 정의에 합의
- **핵심 원칙**: "모델이 향상되면 하네스 복잡도를 줄이되, 흥미로운 조합 공간은 이동할 뿐 줄지 않는다"

### 1.3 멀티 에이전트 워크플로우 (wikidocs.net -- 403, 제목 기반 추론)
- **아키텍트-개발자-리뷰어** 3역할 분담으로 수만 줄 프로젝트 유지
- 역할 분리를 통한 품질 제어가 핵심

### 1.4 Karpathy의 코드 에이전트 + AutoResearch (hada.io/27706)
- **병렬 에이전트 운영**: 10개 이상 에이전트를 동시에 20분 단위로 배분
- **사용자 숙련도가 병목**: 모델 능력이 아닌 MD 파일 지시사항, 메모리 구성이 성패 결정
- **프로그램 MD 메타 최적화**: 조직 전체를 마크다운으로 기술하고 코드로서 최적화
- **들쭉날쭉한(jagged) 지능**: RL로 검증 가능한 영역에서만 빠르게 개선, 비검증 영역은 정체

### 1.5 AutoResearchClaw (discuss.pytorch.kr)
- **23단계 완전 자율 파이프라인**: 연구 범위 설정부터 논문 작성까지
- **다중 에이전트 토론**: Innovator/Pragmatist/Contrarian 3-에이전트 가설 검증
- **자가 치유 실행**: 크래시 시 자율 복구, 가설 수정(Pivot/Refine) 자동 결정
- **MetaClaw 교차 실행 학습**: 실패 사례를 구조화된 "교훈"으로 저장, 30일 시간 감쇠, 견고성 18.3% 향상

### 1.6 Impeccable (hada.io/27750)
- **디자인 어휘/안티패턴 패키지**: AI 하네스의 프론트엔드 품질 향상용 스킬 패키지
- **20개 명령어 워크플로우**: audit -> normalize -> polish -> typeset
- **안티패턴 세트**: 흔한 LLM 디자인 오류(Inter 폰트, 카드 중첩 등) 차단
- **시사점**: 도메인별 품질 기준을 명시적으로 정의하고 에이전트에 주입하면 결과 품질 향상

### 1.7 속도를 늦춰야 빨라진다 (hada.io/27858)
- **System 1/2 프레임워크**: LLM은 본질적으로 System 1(패턴 매칭). System 2(분석적 판단)는 인간 영역
- **Thinking First 프로토콜**: AI에 작업을 넘기기 전 실제 원하는 것을 명확히 하는 시간 투자
- **프리모텀(Pre-mortem)**: 설계 확정 전 "무엇이 잘못될 수 있는가?" 질문
- **핵심**: 실행이 저렴해질수록 실행 이전의 의사결정이 더 중요해진다

---

## 2. LiveCode 적용 가능 개선사항 (우선순위별)

### P0 (즉시 구현) -- 이번 세션에서 구현 완료
1. **Harness Self-Evaluator 모듈** (`harness_evaluator.py`)
   - 실험 결과를 품질 기준과 대조하여 하네스 수준의 진단 수행
   - 교차 실행 비교(cross-run comparison)로 개선/퇴보 추이 추적
   - 구체적인 하네스 개선 제안(actionable feedback) 생성
   - 영감: Anthropic Generator/Evaluator 분리 + MetaClaw 교차 실행 학습

### P1 (다음 세션)
2. **Pre-mortem 단계 통합**: runner.py 실행 전에 실험 설정을 사전 검증하는 `validate_experiment_config()` 함수 추가. "속도를 늦춰야 빨라진다" 원칙 적용
3. **컨텍스트 리셋 메커니즘**: 장기 실행 실험에서 컨텍스트 불안을 방지하기 위한 실험 단계별 클린 핸드오프 구현

### P2 (중기)
4. **다중 평가자 토론 시스템**: AutoResearchClaw의 Innovator/Pragmatist/Contrarian 패턴을 실험 결과 해석에 적용. 단일 평가 기준이 아닌 다각도 분석
5. **하네스 안티패턴 세트**: Impeccable 스타일로, 흔한 실험 설계 오류(너무 적은 반복, 불균형한 난이도 등)를 명시적으로 정의하고 자동 감지

### P3 (장기)
6. **Agent Flywheel**: 실험 결과 -> 하네스 평가 -> 하네스 자동 조정 -> 재실험의 자가 진화 루프
7. **프로그램 MD 메타 최적화**: 실험 구성(태스크 목록, 프롬프트, 기준)을 마크다운으로 기술하고, 결과에 기반한 구성 자동 최적화

---

## 3. 구현 내용

### 3.1 신규 파일: `harness_evaluator.py`

**개요**: 실험 하네스 자체의 품질을 평가하고 개선 피드백을 생성하는 모듈.

**핵심 구성요소**:
- `QualityThreshold`: 실험 유형별 합격 기준 (성공률, 응답 시간, 최소 스텝 수)
- `HarnessVerdict`: 평가 판정 결과 (pass/fail, 종합 점수, 이슈, 제안)
- `evaluate_harness()`: 실험 결과 JSON을 받아 하네스 품질 평가
- `_diagnose_context_memory()`: 위치별 성공률 편차, 긴 컨텍스트 성능 저하 진단
- `_diagnose_coding_failure()`: 카테고리별 분석, 실패 급증 조기 발생 검사
- `compare_runs()`: 두 실행 결과 비교하여 개선/퇴보 추이 반환
- `save_verdict()` / `load_latest_verdict()`: 평가 결과 영속화 및 교차 실행 학습

**설계 영감**:
- Anthropic의 Generator/Evaluator 분리: 생성(실험 실행)과 평가(하네스 품질)를 독립적으로 수행
- MetaClaw의 교차 실행 학습: 이전 평가 결과를 로드하여 추이를 비교
- "속도를 늦춰야 빨라진다": 실행 결과를 바로 사용하지 않고, 하네스 수준의 메타 검증 단계를 추가

### 3.2 신규 파일: `tests/test_harness_evaluator.py`
- 20개 테스트 케이스
- 기본 동작, 실험 유형별 진단, 점수 계산, 교차 실행 비교, 저장/로드 검증
- 기존 테스트 패턴(pytest, unittest.mock, dataclass fixture) 준수

### 3.3 수정 파일: `pytest.ini`
- `--cov=harness_evaluator` 추가하여 커버리지 측정 대상에 포함

### 3.4 검증 결과
- 전체 83개 테스트 통과
- 코드 커버리지: 99.77% (기준 95% 충족)

---

## 4. TODO / 진행 현황

### 완료 (2026-03-30 세션)
- [x] `validate_experiment_config()` Pre-mortem 함수 구현 (P1-2) — `experiments/hypothesis_validation/runner.py`
- [x] runner.py에 harness_evaluator 통합 — `to_harness_format()` bridge + `hypothesis_validation` threshold 추가
- [x] harness 자동 평가: `evaluate_harness()` → score=1.0 달성
- [x] 가설 실험 LLM API 계층 구현 — `llm_strategies.py`, `llm_runner.py` (pass@k, 토큰 추적)
- [x] analyze.py hypothesis/LLM 실험 분석 지원
- [x] C3 재설계 (cached_fibonacci → collect_unique): 실제 버그를 테스트로 검출 가능
- [x] 177 tests / 99.47% coverage

### 미완료 (향후 세션)
- [ ] 컨텍스트 리셋 메커니즘 설계 및 구현 (P1-3) — 장기 실험 대상
- [ ] compare_runs CLI 대시보드 (예: `python analyze.py --harness-trend`) (P1-5)
- [ ] 다중 평가자 토론 시스템 프로토타입 (P2-4)
- [ ] 하네스 안티패턴 세트 정의 및 자동 감지 로직 (P2-5)
- [ ] 실제 LLM 실험 실행 및 결과 기록 (ANTHROPIC_API_KEY 필요, 비용 발생)
- [ ] Agent Flywheel 아키텍처 설계 문서 작성 (P3-6)
