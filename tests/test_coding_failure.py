import asyncio
from unittest.mock import patch, AsyncMock

from experiments.coding_failure.evaluator import (
    run_openhands_task, StepResult, detect_failure_inflection
)
from experiments.coding_failure.tasks import get_coding_tasks, CodingTask

def test_get_coding_tasks_returns_20() -> None:
    tasks = get_coding_tasks()
    assert len(tasks) == 20

def test_tasks_have_required_fields() -> None:
    tasks = get_coding_tasks()
    for t in tasks:
        assert isinstance(t.step, int)
        assert isinstance(t.prompt, str)
        assert t.step >= 1
        assert len(t.prompt) > 10

def test_task_difficulty_increases() -> None:
    tasks = get_coding_tasks()
    # 스텝 1-5: 단순 / 16-20: 복잡 (프롬프트 길이로 간접 측정)
    simple_avg = sum(len(t.prompt) for t in tasks[:5]) / 5
    complex_avg = sum(len(t.prompt) for t in tasks[15:]) / 5
    assert complex_avg > simple_avg

def test_detect_failure_inflection_consecutive() -> None:
    """연속 2회 실패 시 급증으로 판정."""
    results = [
        StepResult(step=i, status="success", context_tokens=i*1000, duration_ms=100, error=None)
        for i in range(1, 9)
    ]
    results.append(StepResult(9, "failure", 9000, 100, "error"))
    results.append(StepResult(10, "failure", 10000, 100, "error"))
    inflection = detect_failure_inflection(results)
    assert inflection == 9

def test_detect_failure_inflection_no_inflection() -> None:
    """실패가 없으면 None 반환."""
    results = [
        StepResult(step=i, status="success", context_tokens=i*1000, duration_ms=100, error=None)
        for i in range(1, 6)
    ]
    assert detect_failure_inflection(results) is None


def test_detect_failure_inflection_single_failure_not_inflection() -> None:
    """단독 실패 1회는 급증으로 판정하지 않음."""
    results = [
        StepResult(step=i, status="success", context_tokens=i*1000, duration_ms=100, error=None)
        for i in range(1, 5)
    ]
    results.append(StepResult(5, "failure", 5000, 100, "error"))
    results.append(StepResult(6, "success", 6000, 100, None))
    assert detect_failure_inflection(results) is None


def test_detect_failure_inflection_at_start() -> None:
    """첫 번째부터 연속 2회 실패 시 step=1 반환."""
    results = [
        StepResult(1, "failure", 1000, 100, "err1"),
        StepResult(2, "failure", 2000, 100, "err2"),
        StepResult(3, "success", 3000, 100, None),
    ]
    assert detect_failure_inflection(results) == 1


def test_detect_failure_inflection_empty_list() -> None:
    """빈 리스트는 None 반환."""
    assert detect_failure_inflection([]) is None