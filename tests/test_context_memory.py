import pytest
from experiments.context_memory.tasks import build_recall_prompt, count_tokens
from unittest.mock import patch, AsyncMock
from experiments.context_memory.evaluator import evaluate_recall, RecallResult
import asyncio

def test_build_recall_prompt_contains_secret():
    prompt, answer = build_recall_prompt(
        context_tokens=1000,
        position="front",
        secret="ALPHA-7734"
    )
    assert "ALPHA-7734" in prompt
    assert answer == "ALPHA-7734"

def test_build_recall_prompt_token_count_approximate():
    prompt, _ = build_recall_prompt(context_tokens=1000, position="middle", secret="TEST-0001")
    tokens = count_tokens(prompt)
    # 허용 오차 20%
    assert 800 <= tokens <= 1200

def test_positions_place_secret_correctly():
    for position in ["front", "middle", "back"]:
        prompt, answer = build_recall_prompt(
            context_tokens=500, position=position, secret="XYZ-9999"
        )
        assert "XYZ-9999" in prompt
        assert answer == "XYZ-9999"

def test_evaluate_recall_success():
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

def test_evaluate_recall_failure():
    """LLM이 오답을 반환한 경우 is_correct=False."""
    with patch("experiments.context_memory.evaluator.call_minimax") as mock:
        mock.return_value = "WRONG-0000"
        result = asyncio.run(evaluate_recall(
            prompt="...비밀 코드는 ALPHA-7734...",
            expected="ALPHA-7734",
            context_tokens=1000,
        ))
    assert result.is_correct is False