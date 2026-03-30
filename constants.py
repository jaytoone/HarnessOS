"""LiveCode 실험 상수."""
from pathlib import Path
from typing import Literal

# 실험 식별자 타입
ExperimentName = Literal["context_memory", "coding_failure", "hypothesis_validation"]

# 가설 검증 실험 디버그 태스크 카테고리
DebugTaskCategory = Literal["simple", "causal", "assumption"]

# 전략 식별자 (결정론적 + LLM 포함)
StrategyName = Literal["engineering", "hypothesis", "llm_engineering", "llm_hypothesis"]

# 코딩 실패 실험 태스크 카테고리
CodingTaskCategory = Literal["simple", "multi_file", "refactor", "architecture"]

# OpenHands 태스크 실행 상태
TaskStatus = Literal["success", "failure", "timeout"]

# 비밀 코드 위치 타입
Position = Literal["front", "middle", "back"]
PositionOrUnknown = Literal["front", "middle", "back", "unknown"]

# 실험 A: 컨텍스트 길이 / 위치 / 반복 설정
CONTEXT_LENGTHS: list[int] = [1_000, 10_000, 50_000, 100_000]
POSITIONS: list[Position] = ["front", "middle", "back"]
REPEATS: int = 3

# 모델 식별자
DEFAULT_MODEL: str = "minimax/MiniMax-M2.5"

# 결과 저장 경로
RESULTS_DIR: Path = Path("results")
