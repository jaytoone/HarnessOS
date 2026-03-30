# LiveCode - LLM 실험 시스템

## 개요
LLM 에이전트의 디버깅 전략과 장기 컨텍스트 한계를 측정하는 실험 시스템.

---

## 실험 C: 가설 기반 vs 엔지니어링 디버깅 (주력 실험)

**핵심 가설**: "가설 기반 사고(원인 → 검증)는 엔지니어링 사고(패턴 매칭 → 재시도)에 비해 어려운 버그에서 시도 횟수를 줄인다."

**결과 요약** (12 태스크, 3개 카테고리):

| 카테고리 | Eng 평균 시도 | Hyp 평균 시도 | 절약 |
|---------|-------------|-------------|------|
| Simple  | 1.0         | 1.0         | 0.0  |
| Causal  | 1.75        | 1.0         | +0.75 |
| Assumption | 2.0      | 1.0         | +1.0  |

- 가설 정확도(첫 번째 가설이 맞을 확률): **100%**
- 실행 방법 (단일 명령):

```bash
python3 analyze.py --run
```

**상세 연구 문서**: `docs/research/20260330-hypothesis-experiment-results.md`

---

## 실험 A: 기억력 저하 (Lost-in-the-Middle)
- 컨텍스트 길이: 1K / 10K / 50K / 100K 토큰
- 정보 위치: 앞 / 중간 / 뒤
- 각 조건 3회 반복 → 총 36 데이터포인트

```bash
python3 runner.py --exp a
```

## 실험 B: 코딩 실수 시점
- OpenHands 에이전트로 20단계 코딩 태스크 수행
- 실패 급증 시점 자동 감지

```bash
python3 runner.py --exp b  # OpenHands localhost:3000 필요
```

---

## 결과 분석

```bash
# 모든 결과 파일 요약
python3 analyze.py

# 실험 C 전체 파이프라인 (실행 + 분석 + 하네스 평가)
python3 analyze.py --run

# 실험 C LLM 버전 (실제 Claude API 호출, ANTHROPIC_API_KEY 필요)
export ANTHROPIC_API_KEY=sk-ant-...
python3 analyze.py --run-llm

# 하네스 평가 추이 (cross-run)
python3 analyze.py --harness-trend
```

결과 JSON: `results/` | 하네스 평가: `harness_eval/`

## 테스트

```bash
python3 -m pytest  # 214 tests, 100% coverage
```