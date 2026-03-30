"""Context-memory recall evaluator using MiniMax API."""
import asyncio
import os
import time
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

async def call_minimax(prompt: str, *, _retries: int = 2) -> str:
    """MiniMax API 직접 호출, 응답 텍스트 반환. 429/5xx 시 최대 _retries회 재시도."""
    api_key = os.environ.get("MINIMAX_API_KEY", "")
    if not api_key:
        raise ValueError("MINIMAX_API_KEY environment variable is not set")
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
    last_exc: Exception = RuntimeError("unreachable")
    async with httpx.AsyncClient(timeout=120.0) as client:
        for attempt in range(_retries + 1):
            try:
                resp = await client.post(MINIMAX_API_URL, json=payload, headers=headers)
                if resp.status_code == 429 and attempt < _retries:
                    await asyncio.sleep(2 ** attempt)
                    continue
                resp.raise_for_status()
                data = resp.json()
                content: str = data["choices"][0]["message"]["content"]
                return content.strip()
            except (httpx.HTTPStatusError, httpx.TransportError) as exc:
                last_exc = exc
                if attempt < _retries:
                    await asyncio.sleep(2 ** attempt)
    raise last_exc

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