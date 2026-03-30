"""coding_failure/evaluator.py 오류 경로 테스트."""
import asyncio
from unittest.mock import patch, AsyncMock, MagicMock

import httpx
import pytest

from experiments.coding_failure.evaluator import (
    _create_conversation,
    _analyze_events,
    run_openhands_task,
    detect_failure_inflection,
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


def test_analyze_events_no_finish_no_error_returns_success() -> None:
    """finish 없고 에러 키워드도 없으면 awaiting_user_input으로 간주해 success 반환."""
    events = [{"action": "cmd", "observation": "Task done, waiting for input"}]
    status, err = _analyze_events(events)
    assert status == "success"
    assert err is None


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


# ── _poll_until_done ──────────────────────────────────────────────────────────

from experiments.coding_failure.evaluator import _poll_until_done, TERMINAL_STATES


def test_poll_until_done_returns_events_on_terminal_state() -> None:
    """터미널 상태 감지 시 events 및 상태명 반환."""
    events = [
        {"action": "agent_state_changed", "extras": {"agent_state": "finished"}}
    ]
    mock_resp = MagicMock()
    mock_resp.status_code = 200
    mock_resp.json.return_value = {"trajectory": events}

    call_count = 0

    async def mock_get(*a, **kw):
        nonlocal call_count
        call_count += 1
        return mock_resp

    async def run():
        async with httpx.AsyncClient() as client:
            with patch.object(client, "get", side_effect=mock_get), \
                 patch("asyncio.sleep", new_callable=AsyncMock):
                return await _poll_until_done(client, "cid-1")

    result_events, state = asyncio.run(run())
    assert state == "finished"
    assert result_events == events


def test_poll_until_done_skips_non_200_response() -> None:
    """비-200 응답은 무시하고 이후 200 응답에서 완료 감지."""
    events = [
        {"action": "agent_state_changed", "extras": {"agent_state": "finished"}}
    ]
    call_count = 0

    async def mock_get(*a, **kw):
        nonlocal call_count
        call_count += 1
        m = MagicMock()
        if call_count == 1:
            m.status_code = 503
        else:
            m.status_code = 200
            m.json.return_value = {"trajectory": events}
        return m

    async def run():
        async with httpx.AsyncClient() as client:
            with patch.object(client, "get", side_effect=mock_get), \
                 patch("asyncio.sleep", new_callable=AsyncMock):
                return await _poll_until_done(client, "cid-2")

    _, state = asyncio.run(run())
    assert state == "finished"
    assert call_count == 2


def test_poll_until_done_ignores_connect_error() -> None:
    """ConnectError는 무시하고 다음 폴링 시도."""
    events = [
        {"action": "agent_state_changed", "extras": {"agent_state": "error"}}
    ]
    call_count = 0

    async def mock_get(*a, **kw):
        nonlocal call_count
        call_count += 1
        if call_count == 1:
            raise httpx.ConnectError("down")
        m = MagicMock()
        m.status_code = 200
        m.json.return_value = {"trajectory": events}
        return m

    async def run():
        async with httpx.AsyncClient() as client:
            with patch.object(client, "get", side_effect=mock_get), \
                 patch("asyncio.sleep", new_callable=AsyncMock):
                return await _poll_until_done(client, "cid-3")

    _, state = asyncio.run(run())
    assert state == "error"


def test_poll_until_done_extracts_state_from_change_agent_state() -> None:
    """change_agent_state 액션도 터미널 상태로 인식."""
    events = [
        {"action": "change_agent_state", "extras": {"agent_state": "stopped"}}
    ]
    mock_resp = MagicMock()
    mock_resp.status_code = 200
    mock_resp.json.return_value = {"trajectory": events}

    async def run():
        async with httpx.AsyncClient() as client:
            with patch.object(client, "get", new_callable=AsyncMock, return_value=mock_resp), \
                 patch("asyncio.sleep", new_callable=AsyncMock):
                return await _poll_until_done(client, "cid-4")

    _, state = asyncio.run(run())
    assert state == "stopped"


def test_poll_until_done_timeout_when_max_wait_exceeded() -> None:
    """MAX_WAIT_SEC 초과 시 ([], 'timeout') 반환."""
    import experiments.coding_failure.evaluator as ev_mod

    async def mock_get(*a, **kw):
        m = MagicMock()
        m.status_code = 200
        m.json.return_value = {"trajectory": []}
        return m

    async def run():
        async with httpx.AsyncClient() as client:
            with patch.object(client, "get", side_effect=mock_get), \
                 patch("asyncio.sleep", new_callable=AsyncMock), \
                 patch.object(ev_mod, "MAX_WAIT_SEC", 6.0), \
                 patch.object(ev_mod, "POLL_INTERVAL", 3.0):
                return await _poll_until_done(client, "cid-timeout")

    events, state = asyncio.run(run())
    assert state == "timeout"
    assert events == []


# ── run_openhands_task 성공/타임아웃/에러 상태 ─────────────────────────────────

def test_run_openhands_task_success_path() -> None:
    """정상 완료(finished) 시 StepResult(success) 반환."""
    events = [{"action": "finish"}]
    with patch(
        "experiments.coding_failure.evaluator._create_conversation",
        new_callable=AsyncMock,
        return_value="cid-ok",
    ), patch(
        "experiments.coding_failure.evaluator._poll_until_done",
        new_callable=AsyncMock,
        return_value=(events, "finished"),
    ):
        result = asyncio.run(run_openhands_task(1, "do it"))

    assert result.status == "success"
    assert result.step == 1
    assert result.error is None


def test_run_openhands_task_timeout_returns_timeout_result() -> None:
    """폴링 타임아웃 시 StepResult(timeout) 반환."""
    with patch(
        "experiments.coding_failure.evaluator._create_conversation",
        new_callable=AsyncMock,
        return_value="cid-timeout",
    ), patch(
        "experiments.coding_failure.evaluator._poll_until_done",
        new_callable=AsyncMock,
        return_value=([], "timeout"),
    ):
        result = asyncio.run(run_openhands_task(2, "slow task"))

    assert result.status == "timeout"
    assert result.error == "agent timeout"


def test_run_openhands_task_agent_error_state_overrides_status() -> None:
    """final_state=error 이면 _analyze_events 결과와 무관하게 failure 반환."""
    events = [{"action": "finish"}]  # _analyze_events would say "success"
    with patch(
        "experiments.coding_failure.evaluator._create_conversation",
        new_callable=AsyncMock,
        return_value="cid-err",
    ), patch(
        "experiments.coding_failure.evaluator._poll_until_done",
        new_callable=AsyncMock,
        return_value=(events, "error"),
    ):
        result = asyncio.run(run_openhands_task(3, "bad task"))

    assert result.status == "failure"
    assert result.error == "agent reached error state"


# ── detect_failure_inflection: window 비율 로직 ───────────────────────────────

def test_detect_failure_inflection_window_rate_doubling() -> None:
    """이전 구간 대비 실패율 2배 이상 시 해당 구간 첫 스텝 반환."""
    # steps 1-5: 1 failure (rate=1), steps 6-10: 2 failures (rate=2 = 2x)
    results = []
    for i in range(1, 6):
        status = "failure" if i == 3 else "success"
        results.append(StepResult(i, status, i * 1000, 100, None))
    for i in range(6, 11):
        status = "failure" if i in (7, 9) else "success"
        results.append(StepResult(i, status, i * 1000, 100, None))

    inflection = detect_failure_inflection(results)
    assert inflection == 6


def test_detect_failure_inflection_window_no_prev_failures_skips() -> None:
    """이전 구간 실패가 0이면 window 비율 로직 스킵 → None."""
    # steps 1-5: all success (prev_failures=0), steps 6-10: isolated failures (not consecutive)
    statuses = ["success"] * 5 + ["failure", "success", "failure", "success", "success"]
    results = [
        StepResult(i + 1, statuses[i], (i + 1) * 1000, 100, None)
        for i in range(10)
    ]
    # prev_failures=0 → rate check skipped; no consecutive failures → None
    inflection = detect_failure_inflection(results)
    assert inflection is None
