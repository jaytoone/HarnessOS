"""Shared pytest fixtures for AutoCode tests."""
import pytest
from unittest.mock import MagicMock


@pytest.fixture
def dashboard_mock() -> MagicMock:
    """Context-manager Dashboard mock with add_result stub."""
    mock = MagicMock()
    mock.__enter__ = MagicMock(return_value=mock)
    mock.__exit__ = MagicMock(return_value=False)
    mock.add_result = MagicMock()
    return mock


@pytest.fixture
def single_step_patches():
    """Patch CONTEXT_LENGTHS/POSITIONS/REPEATS to a single minimal step."""
    from unittest.mock import patch
    import contextlib

    @contextlib.contextmanager
    def _patches():
        with patch("runner.CONTEXT_LENGTHS", [1_000]), \
             patch("runner.POSITIONS", ["front"]), \
             patch("runner.REPEATS", 1):
            yield

    return _patches
