"""AutoCode 실험 상수."""
from __future__ import annotations
from pathlib import Path

# 실험 A: 컨텍스트 길이 / 위치 / 반복 설정
CONTEXT_LENGTHS: list[int] = [1_000, 10_000, 50_000, 100_000]
POSITIONS: list[str] = ["front", "middle", "back"]
REPEATS: int = 3

# 모델 식별자
DEFAULT_MODEL: str = "minimax/MiniMax-M2.5"

# 결과 저장 경로
RESULTS_DIR: Path = Path("results")
