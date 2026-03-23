import os
import time
import asyncio
from dataclasses import dataclass
import httpx

MINIMAX_API_URL = "https://api.minimax.io/v1/chat/completions"
MINIMAX_MODEL = "MiniMax-M2.5"

@dataclass
class RecallResult:
    is_correct: bool
    expected: str
    got: str
    context_tokens: int
    position: str
    duration_ms: int

async def call_minimax(prompt: str) -> str:
    """MiniMax API 직접 호출, 응답 텍스트 반환."""
    api_key = os.environ.get("MINIMAX_API_KEY", "")
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
    }
    payload = {
        "model": MINIMAX_MODEL,
        "messages": [{"role": "user", "content": prompt}],
        "max_tokens": 50,
        "temperature": 0.0,
    }
    async with httpx.AsyncClient(timeout=120.0) as client:
        resp = await client.post(MINIMAX_API_URL, json=payload, headers=headers)
        resp.raise_for_status()
        data = resp.json()
        return data["choices"][0]["message"]["content"].strip()

async def evaluate_recall(
    prompt: str,
    expected: str,
    context_tokens: int,
    position: str = "unknown",
) -> RecallResult:
    start = time.monotonic()
    got = await call_minimax(prompt)
    duration_ms = int((time.monotonic() - start) * 1000)
    is_correct = expected.upper() in got.upper()
    return RecallResult(
        is_correct=is_correct,
        expected=expected,
        got=got,
        context_tokens=context_tokens,
        position=position,
        duration_ms=duration_ms,
    )