from experiments.coding_failure.tasks import get_coding_tasks, CodingTask
from unittest.mock import patch, AsyncMock
from experiments.coding_failure.evaluator import (
    run_openhands_task, StepResult, detect_failure_inflection
)
import asyncio

def test_get_coding_tasks_returns_20():
    tasks = get_coding_tasks()
    assert len(tasks) == 20

def test_tasks_have_required_fields():
    tasks = get_coding_tasks()
    for t in tasks:
        assert isinstance(t.step, int)
        assert isinstance(t.prompt, str)
        assert t.step >= 1
        assert len(t.prompt) > 10

def test_task_difficulty_increases():
    tasks = get_coding_tasks()
    # 스텝 1-5: 단순 / 16-20: 복잡 (프롬프트 길이로 간접 측정)
    simple_avg = sum(len(t.prompt) for t in tasks[:5]) / 5
    complex_avg = sum(len(t.prompt) for t in tasks[15:]) / 5
    assert complex_avg > simple_avg

def test_detect_failure_inflection_consecutive():
    """연속 2회 실패 시 급증으로 판정."""
    results = [
        StepResult(step=i, status="success", context_tokens=i*1000, duration_ms=100, error=None)
        for i in range(1, 9)
    ]
    results.append(StepResult(9, "failure", 9000, 100, "error"))
    results.append(StepResult(10, "failure", 10000, 100, "error"))
    inflection = detect_failure_inflection(results)
    assert inflection == 9

def test_detect_failure_inflection_no_inflection():
    """실패가 없으면 None 반환."""
    results = [
        StepResult(step=i, status="success", context_tokens=i*1000, duration_ms=100, error=None)
        for i in range(1, 6)
    ]
    assert detect_failure_inflection(results) is None