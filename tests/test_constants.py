"""constants.py 값 불변성 및 타입 검증."""
from constants import CONTEXT_LENGTHS, POSITIONS, REPEATS, DEFAULT_MODEL


def test_context_lengths_ascending() -> None:
    assert CONTEXT_LENGTHS == sorted(CONTEXT_LENGTHS)
    assert all(x > 0 for x in CONTEXT_LENGTHS)


def test_positions_complete() -> None:
    assert set(POSITIONS) == {"front", "middle", "back"}


def test_repeats_positive() -> None:
    assert REPEATS >= 1


def test_default_model_nonempty() -> None:
    assert isinstance(DEFAULT_MODEL, str) and len(DEFAULT_MODEL) > 0


def test_results_dir_is_path() -> None:
    from constants import RESULTS_DIR
    from pathlib import Path
    assert isinstance(RESULTS_DIR, Path)
    assert str(RESULTS_DIR) == "results"
