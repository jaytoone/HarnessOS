# AutoCode - LLM 장기 컨텍스트 실험

## 개요
MiniMax M2.5를 대상으로 장기 컨텍스트 한계를 측정하는 실험 시스템.

## 실험 종류

### 실험 A: 기억력 저하 (Lost-in-the-Middle)
- 컨텍스트 길이: 1K / 10K / 50K / 100K 토큰
- 정보 위치: 앞 / 중간 / 뒤
- 각 조건 3회 반복 → 총 36 데이터포인트

### 실험 B: 코딩 실수 시점
- OpenHands 에이전트로 20단계 코딩 태스크 수행
- 실패 급증 시점 자동 감지

## 실행

```bash
# 환경 설정
pip install -r requirements.txt
source ~/.claude/env/shared.env  # MINIMAX_API_KEY 로드

# 실험 A 실행
python runner.py --exp a

# 실험 B 실행 (OpenHands localhost:3000 필요)
python runner.py --exp b
```

## 결과
`results/` 디렉토리에 JSON 저장됨.