"""Coding-failure evaluator: OpenHands task execution and result analysis."""
import asyncio
import time
from dataclasses import dataclass
from typing import Any

import httpx

OPENHANDS_URL = "http://localhost:3000"
POLL_INTERVAL = 3.0
MAX_WAIT_SEC = 360  # 6분 타임아웃

TERMINAL_STATES = {"finished", "error", "stopped", "awaiting_user_input"}

@dataclass
class StepResult:
    step: int
    status: str  # "success" | "failure" | "timeout"
    context_tokens: int
    duration_ms: int
    error: str | None


async def _create_conversation(
    client: httpx.AsyncClient, prompt: str, *, _retries: int = 2
) -> str:
    """OpenHands 대화 세션 생성. 429/TransportError 시 지수 백오프로 최대 _retries회 재시도."""
    last_exc: Exception = RuntimeError("unreachable")
    for attempt in range(_retries + 1):
        try:
            resp = await client.post(
                f"{OPENHANDS_URL}/api/conversations",
                json={"initial_user_msg": prompt, "conversation_trigger": "gui"},
                timeout=30.0,
            )
            if resp.status_code == 429 and attempt < _retries:
                await asyncio.sleep(2 ** attempt)
                continue
            resp.raise_for_status()
            data: dict[str, str] = resp.json()
            return data["conversation_id"]
        except (httpx.HTTPStatusError, httpx.TransportError) as exc:
            last_exc = exc
            if attempt < _retries:
                await asyncio.sleep(2 ** attempt)
    raise last_exc


async def _poll_until_done(client: httpx.AsyncClient, cid: str) -> tuple[list[dict[str, Any]], str]:
    """
    trajectory 폴링. agent_state_changed 이벤트로 완료 감지.
    반환: (events, final_agent_state)
    """
    elapsed = 0.0
    last_state = "loading"

    while elapsed < MAX_WAIT_SEC:
        await asyncio.sleep(POLL_INTERVAL)
        elapsed += POLL_INTERVAL

        try:
            resp = await client.get(
                f"{OPENHANDS_URL}/api/conversations/{cid}/trajectory",
                timeout=httpx.Timeout(30.0, read=60.0),
            )
        except (httpx.ReadTimeout, httpx.ConnectError):
            continue

        if resp.status_code != 200:
            continue

        data: dict[str, list[dict[str, Any]]] = resp.json()
        events = data.get("trajectory", [])

        # agent_state_changed 이벤트에서 최신 상태 추출
        for ev in reversed(events):
            action = ev.get("action", "") or ev.get("observation", "")
            if action in ("agent_state_changed", "change_agent_state"):
                state = ev.get("extras", {}).get("agent_state", "")
                if state:
                    last_state = state
                    break

        if last_state in TERMINAL_STATES:
            return events, last_state

    return [], "timeout"


def _analyze_events(events: list[dict[str, Any]]) -> tuple[str, str | None]:
    """events에서 success/failure 판정."""
    if not events:
        return "failure", "no events"

    # 마지막 finish 이벤트 확인
    for ev in reversed(events):
        action = ev.get("action", "")
        if action == "finish":
            return "success", None

    # error 키워드 탐색
    for ev in reversed(events):
        content = str(ev.get("observation", "") or ev.get("content", "") or "")
        if any(kw in content.lower() for kw in ["error", "exception", "traceback", "failed", "exit code 1"]):
            return "failure", content[:200]

    # finish 없이 awaiting_user_input → 태스크 완료로 간주
    return "success", None


async def run_openhands_task(step: int, prompt: str) -> StepResult:
    """OpenHands에 태스크 전송 → trajectory 폴링 → 결과 반환."""
    start = time.monotonic()

    async with httpx.AsyncClient() as client:
        try:
            cid = await _create_conversation(client, prompt)
        except Exception as e:
            return StepResult(step, "failure", 0,
                             int((time.monotonic()-start)*1000), f"create failed: {e}")

        events, final_state = await _poll_until_done(client, cid)

    duration_ms = int((time.monotonic() - start) * 1000)

    if final_state == "timeout":
        return StepResult(step, "timeout", 0, duration_ms, "agent timeout")

    context_tokens = sum(len(str(e)) // 4 for e in events)
    status, error = _analyze_events(events)

    # error 상태면 실패
    if final_state == "error":
        status = "failure"
        if not error:
            error = "agent reached error state"

    return StepResult(step, status, context_tokens, duration_ms, error)


def detect_failure_inflection(results: list[StepResult]) -> int | None:
    """
    실패 급증 시점(스텝 번호) 반환.
    조건: 연속 2회 실패 OR 구간(5스텝) 실패율이 이전 구간 대비 2배 이상.
    """
    for i in range(1, len(results)):
        if results[i].status != "success" and results[i-1].status != "success":
            return results[i-1].step

    if len(results) >= 10:
        prev_failures = sum(1 for r in results[:5] if r.status != "success")
        for start in range(5, len(results) - 4):
            window = results[start:start+5]
            curr_failures = sum(1 for r in window if r.status != "success")
            if prev_failures > 0 and curr_failures >= prev_failures * 2:
                return window[0].step
            prev_failures = curr_failures

    return None
