import time
import asyncio
from dataclasses import dataclass
import httpx

OPENHANDS_URL = "http://localhost:3000"
POLL_INTERVAL = 2.0
MAX_WAIT_SEC = 300  # 5분 타임아웃

@dataclass
class StepResult:
    step: int
    status: str  # "success" | "failure" | "timeout"
    context_tokens: int
    duration_ms: int
    error: str | None

async def run_openhands_task(step: int, prompt: str) -> StepResult:
    """OpenHands에 태스크 전송 후 trajectory 폴링으로 결과 수집."""
    start = time.monotonic()

    async with httpx.AsyncClient(timeout=30.0) as client:
        # 대화 생성
        resp = await client.post(
            f"{OPENHANDS_URL}/api/conversations",
            json={"initial_user_msg": prompt, "conversation_trigger": "gui"},
        )
        resp.raise_for_status()
        conversation_id = resp.json()["conversation_id"]

        # trajectory 폴링
        elapsed = 0.0
        last_event_count = 0
        stable_count = 0

        while elapsed < MAX_WAIT_SEC:
            await asyncio.sleep(POLL_INTERVAL)
            elapsed += POLL_INTERVAL

            traj_resp = await client.get(
                f"{OPENHANDS_URL}/api/conversations/{conversation_id}/trajectory"
            )
            if traj_resp.status_code != 200:
                continue

            events = traj_resp.json().get("trajectory", [])
            if len(events) == last_event_count:
                stable_count += 1
                if stable_count >= 3:  # 6초간 새 이벤트 없으면 완료
                    break
            else:
                stable_count = 0
                last_event_count = len(events)

        duration_ms = int((time.monotonic() - start) * 1000)

        # 결과 분석
        if elapsed >= MAX_WAIT_SEC:
            return StepResult(step, "timeout", 0, duration_ms, "timeout exceeded")

        # 마지막 이벤트에서 오류 감지
        error_msg = None
        for event in reversed(events):
            content = str(event.get("observation", "") or event.get("action", ""))
            if any(kw in content.lower() for kw in ["error", "exception", "traceback", "failed"]):
                error_msg = content[:200]
                break

        status = "failure" if error_msg else "success"
        context_tokens = sum(len(str(e)) // 4 for e in events)  # 근사치

        return StepResult(step, status, context_tokens, duration_ms, error_msg)

def detect_failure_inflection(results: list[StepResult]) -> int | None:
    """
    실패 급증 시점(스텝 번호) 반환.
    조건: 연속 2회 실패 OR 구간(5스텝) 실패율이 이전 구간 대비 2배 이상.
    """
    # 조건 1: 연속 2회 실패
    for i in range(1, len(results)):
        if results[i].status == "failure" and results[i-1].status == "failure":
            return results[i-1].step

    # 조건 2: 구간 실패율 2배 이상
    if len(results) >= 10:
        prev_failures = sum(1 for r in results[:5] if r.status == "failure")
        for start in range(5, len(results) - 4):
            window = results[start:start+5]
            curr_failures = sum(1 for r in window if r.status == "failure")
            if prev_failures > 0 and curr_failures >= prev_failures * 2:
                return window[0].step
            prev_failures = curr_failures

    return None