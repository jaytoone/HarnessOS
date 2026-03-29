"""coding_failure/evaluator.py 오류 경로 테스트."""
import asyncio
import pytest
import httpx
from unittest.mock import patch, AsyncMock, MagicMock

from experiments.coding_failure.evaluator import (
    _create_conversation,
    _analyze_events,
    run_openhands_task,
    StepResult,
)


def _mock_resp(status_code: int, body: dict) -> MagicMock:
    m = MagicMock()
    m.status_code = status_code
    m.json.return_value = body
    if status_code >= 400:
        m.raise_for_status.side_effect = httpx.HTTPStatusError(
            "error", request=MagicMock(), response=m
        )
    else:
        m.raise_for_status.return_value = None
    return m


# ── _create_conversation ──────────────────────────────────────────────────────

def test_create_conversation_success() -> None:
    """정상 응답 시 conversation_id 반환."""
    mock_resp = _mock_resp(200, {"conversation_id": "abc-123"})

    async def run():
        async with httpx.AsyncClient() as client:
            with patch.object(client, "post", new_callable=AsyncMock, return_value=mock_resp):
                return await _create_conversation(client, "hello")

    assert asyncio.run(run()) == "abc-123"


def test_create_conversation_retries_on_429() -> None:
    """429 응답 후 재시도하여 성공."""
    call_count = 0

    async def mock_post(*a, **kw):
        nonlocal call_count
        call_count += 1
        if call_count == 1:
            return _mock_resp(429, {})
        return _mock_resp(200, {"conversation_id": "retry-ok"})

    async def run():
        async with httpx.AsyncClient() as client:
            with patch.object(client, "post", side_effect=mock_post), \
                 patch("asyncio.sleep", new_callable=AsyncMock):
                return await _create_conversation(client, "test", _retries=2)

    result = asyncio.run(run())
    assert result == "retry-ok"
    assert call_count == 2


def test_create_conversation_raises_after_retries_exhausted() -> None:
    """재시도 소진 후 HTTPStatusError 전파."""
    async def mock_post(*a, **kw):
        return _mock_resp(500, {})

    async def run():
        async with httpx.AsyncClient() as client:
            with patch.object(client, "post", side_effect=mock_post), \
                 patch("asyncio.sleep", new_callable=AsyncMock):
                await _create_conversation(client, "test", _retries=1)

    with pytest.raises(httpx.HTTPStatusError):
        asyncio.run(run())


def test_create_conversation_raises_on_transport_error() -> None:
    """TransportError 재시도 소진 시 전파."""
    async def mock_post(*a, **kw):
        raise httpx.ConnectError("refused")

    async def run():
        async with httpx.AsyncClient() as client:
            with patch.object(client, "post", side_effect=mock_post), \
                 patch("asyncio.sleep", new_callable=AsyncMock):
                await _create_conversation(client, "test", _retries=1)

    with pytest.raises(httpx.ConnectError):
        asyncio.run(run())


# ── _analyze_events ───────────────────────────────────────────────────────────

def test_analyze_events_empty_returns_failure() -> None:
    assert _analyze_events([]) == ("failure", "no events")


def test_analyze_events_finish_action_returns_success() -> None:
    events = [{"action": "finish"}]
    status, err = _analyze_events(events)
    assert status == "success"
    assert err is None


def test_analyze_events_error_keyword_returns_failure() -> None:
    events = [{"action": "cmd", "observation": "Traceback: error occurred"}]
    status, err = _analyze_events(events)
    assert status == "failure"
    assert err is not None


# ── run_openhands_task 통합 ───────────────────────────────────────────────────

def test_run_openhands_task_create_failure_returns_failure_result() -> None:
    """_create_conversation 실패 시 StepResult(failure) 반환 (예외 전파 안 함)."""
    with patch(
        "experiments.coding_failure.evaluator._create_conversation",
        new_callable=AsyncMock,
        side_effect=httpx.ConnectError("refused"),
    ):
        result = asyncio.run(run_openhands_task(3, "do stuff"))

    assert result.step == 3
    assert result.status == "failure"
    assert "create failed" in (result.error or "")
