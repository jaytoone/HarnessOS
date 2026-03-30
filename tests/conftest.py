"""Shared pytest fixtures for LiveCode tests."""
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
