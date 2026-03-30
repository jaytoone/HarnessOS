"""constants.py 값 불변성 및 타입 검증."""
from constants import CONTEXT_LENGTHS, POSITIONS, REPEATS, DEFAULT_MODEL


def test_context_lengths_ascending() -> None:
    """CONTEXT_LENGTHS가 오름차순 양수 리스트다."""
    assert CONTEXT_LENGTHS == sorted(CONTEXT_LENGTHS)
    assert all(x > 0 for x in CONTEXT_LENGTHS)


def test_positions_complete() -> None:
    """POSITIONS가 front/middle/back 세 값을 포함한다."""
    assert set(POSITIONS) == {"front", "middle", "back"}


def test_repeats_positive() -> None:
    """REPEATS가 1 이상의 양수다."""
    assert REPEATS >= 1


def test_default_model_nonempty() -> None:
    """DEFAULT_MODEL이 비어 있지 않은 문자열이다."""
    assert isinstance(DEFAULT_MODEL, str) and len(DEFAULT_MODEL) > 0


def test_results_dir_is_path() -> None:
    """RESULTS_DIR이 Path('results') 인스턴스다."""
    from constants import RESULTS_DIR
    from pathlib import Path
    assert isinstance(RESULTS_DIR, Path)
    assert str(RESULTS_DIR) == "results"
