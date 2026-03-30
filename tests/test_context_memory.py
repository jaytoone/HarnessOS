import asyncio
from unittest.mock import patch, AsyncMock, MagicMock

import httpx
import pytest

from experiments.context_memory.evaluator import evaluate_recall, call_minimax, RecallResult
from experiments.context_memory.tasks import build_recall_prompt, count_tokens

def test_build_recall_prompt_contains_secret() -> None:
    prompt, answer = build_recall_prompt(
        context_tokens=1000,
        position="front",
        secret="ALPHA-7734"
    )
    assert "ALPHA-7734" in prompt
    assert answer == "ALPHA-7734"

def test_build_recall_prompt_token_count_approximate() -> None:
    prompt, _ = build_recall_prompt(context_tokens=1000, position="middle", secret="TEST-0001")
    tokens = count_tokens(prompt)
    # 허용 오차 20%
    assert 800 <= tokens <= 1200

def test_positions_place_secret_correctly() -> None:
    for position in ["front", "middle", "back"]:
        prompt, answer = build_recall_prompt(
            context_tokens=500, position=position, secret="XYZ-9999"
        )
        assert "XYZ-9999" in prompt
        assert answer == "XYZ-9999"

def test_evaluate_recall_success() -> None:
    """LLM이 정답을 맞춘 경우 is_correct=True."""
    with patch("experiments.context_memory.evaluator.call_minimax") as mock:
        mock.return_value = "ALPHA-7734"
        result = asyncio.run(evaluate_recall(
            prompt="...비밀 코드는 ALPHA-7734...",
            expected="ALPHA-7734",
            context_tokens=1000,
        ))
    assert result.is_correct is True
    assert result.context_tokens == 1000

def test_evaluate_recall_failure() -> None:
    """LLM이 오답을 반환한 경우 is_correct=False."""
    with patch("experiments.context_memory.evaluator.call_minimax") as mock:
        mock.return_value = "WRONG-0000"
        result = asyncio.run(evaluate_recall(
            prompt="...비밀 코드는 ALPHA-7734...",
            expected="ALPHA-7734",
            context_tokens=1000,
        ))
    assert result.is_correct is False


def test_call_minimax_raises_on_missing_api_key(monkeypatch: pytest.MonkeyPatch) -> None:
    """MINIMAX_API_KEY 미설정 시 ValueError 발생."""
    monkeypatch.delenv("MINIMAX_API_KEY", raising=False)
    with pytest.raises(ValueError, match="MINIMAX_API_KEY"):
        asyncio.run(call_minimax("test prompt"))


def test_call_minimax_retries_on_429(monkeypatch: pytest.MonkeyPatch) -> None:
    """429 응답 시 재시도 후 성공."""
    monkeypatch.setenv("MINIMAX_API_KEY", "test-key")
    call_count = 0

    def make_mock_response(status_code: int, body: dict) -> MagicMock:
        mock_resp = MagicMock()
        mock_resp.status_code = status_code
        mock_resp.json.return_value = body
        mock_resp.raise_for_status.return_value = None  # 429 path skips raise_for_status
        return mock_resp

    async def mock_post(*args: object, **kwargs: object) -> MagicMock:
        nonlocal call_count
        call_count += 1
        if call_count == 1:
            return make_mock_response(429, {})
        return make_mock_response(200, {"choices": [{"message": {"content": "ANSWER"}}]})

    with patch("httpx.AsyncClient.post", side_effect=mock_post):
        with patch("asyncio.sleep", new_callable=AsyncMock):
            result = asyncio.run(call_minimax("test", _retries=2))
    assert result == "ANSWER"
    assert call_count == 2


def test_evaluate_recall_case_insensitive() -> None:
    """대소문자 무관하게 정답 인식."""
    with patch("experiments.context_memory.evaluator.call_minimax") as mock:
        mock.return_value = "alpha-7734"
        result = asyncio.run(evaluate_recall(
            prompt="...", expected="ALPHA-7734", context_tokens=500,
        ))
    assert result.is_correct is True


def test_call_minimax_retries_on_transport_error(monkeypatch: pytest.MonkeyPatch) -> None:
    """TransportError 발생 시 재시도 후 성공."""
    monkeypatch.setenv("MINIMAX_API_KEY", "test-key")
    call_count = 0

    async def mock_post(*args: object, **kwargs: object) -> MagicMock:
        nonlocal call_count
        call_count += 1
        if call_count == 1:
            raise httpx.TransportError("network error")
        mock_resp = MagicMock()
        mock_resp.status_code = 200
        mock_resp.raise_for_status.return_value = None
        mock_resp.json.return_value = {"choices": [{"message": {"content": "RESULT"}}]}
        return mock_resp

    with patch("httpx.AsyncClient.post", side_effect=mock_post), \
         patch("asyncio.sleep", new_callable=AsyncMock):
        result = asyncio.run(call_minimax("prompt", _retries=2))

    assert result == "RESULT"
    assert call_count == 2


def test_build_recall_prompt_invalid_position() -> None:
    """알 수 없는 position 입력 시 ValueError 발생."""
    from experiments.context_memory.tasks import build_recall_prompt
    with pytest.raises(ValueError, match="Unknown position"):
        build_recall_prompt(context_tokens=500, position="left")


def test_call_minimax_exhausts_retries_raises(monkeypatch: pytest.MonkeyPatch) -> None:
    """재시도를 모두 소진하면 마지막 예외가 전파된다."""
    monkeypatch.setenv("MINIMAX_API_KEY", "test-key")

    async def mock_post(*args: object, **kwargs: object) -> None:
        raise httpx.TransportError("always fails")

    with patch("httpx.AsyncClient.post", side_effect=mock_post), \
         patch("asyncio.sleep", new_callable=AsyncMock):
        with pytest.raises(httpx.TransportError, match="always fails"):
            asyncio.run(call_minimax("prompt", _retries=2))