"""runner.py 비동기 오류 경로 테스트."""
import asyncio
import json
import pytest
from pathlib import Path
from unittest.mock import patch, AsyncMock, MagicMock

from runner import run_experiment_a, run_experiment_b, _save_results
from constants import CONTEXT_LENGTHS, POSITIONS, REPEATS, DEFAULT_MODEL


def _make_dashboard_mock():
    """Dashboard context manager mock."""
    mock = MagicMock()
    mock.__enter__ = MagicMock(return_value=mock)
    mock.__exit__ = MagicMock(return_value=False)
    mock.add_result = MagicMock()
    return mock


# ── _save_results ──────────────────────────────────────────────────────────────

def test_save_results_creates_json(tmp_path: Path) -> None:
    """_save_results가 올바른 JSON 파일을 생성한다."""
    with patch("runner.RESULTS_DIR", tmp_path):
        _save_results("test_exp", [{"step": 1, "status": "success"}])

    files = list(tmp_path.glob("test_exp_*.json"))
    assert len(files) == 1
    data = json.loads(files[0].read_text())
    assert data["experiment"] == "test_exp"
    assert len(data["steps"]) == 1
    assert data["summary"] == {}


def test_save_results_includes_summary(tmp_path: Path) -> None:
    """`summary` 인자가 있으면 JSON에 포함된다."""
    with patch("runner.RESULTS_DIR", tmp_path):
        _save_results("exp", [], summary={"total": 5, "success_rate": 1.0})

    files = list(tmp_path.glob("exp_*.json"))
    data = json.loads(files[0].read_text())
    assert data["summary"]["total"] == 5


def test_save_results_uses_default_model(tmp_path: Path) -> None:
    """결과 JSON의 model 필드가 DEFAULT_MODEL 상수와 일치한다."""
    with patch("runner.RESULTS_DIR", tmp_path):
        _save_results("exp", [])
    files = list(tmp_path.glob("exp_*.json"))
    data = json.loads(files[0].read_text())
    assert data["model"] == DEFAULT_MODEL


def test_save_results_ioerror_propagates(tmp_path: Path) -> None:
    """mkdir 실패 시 OSError가 전파된다."""
    readonly_dir = tmp_path / "readonly"
    readonly_dir.mkdir()
    readonly_dir.chmod(0o444)

    try:
        with patch("runner.RESULTS_DIR", readonly_dir / "sub"):
            with pytest.raises(OSError):
                _save_results("exp", [])
    finally:
        readonly_dir.chmod(0o755)


# ── run_experiment_a 오류 경로 ─────────────────────────────────────────────────

def test_run_experiment_a_propagates_evaluate_recall_error() -> None:
    """`evaluate_recall`이 ValueError를 던지면 run_experiment_a가 전파한다."""
    dash_mock = _make_dashboard_mock()

    with patch("runner.Dashboard", return_value=dash_mock), \
         patch("runner.CONTEXT_LENGTHS", [1_000]), \
         patch("runner.POSITIONS", ["front"]), \
         patch("runner.REPEATS", 1), \
         patch("runner.evaluate_recall", new_callable=AsyncMock,
               side_effect=ValueError("MINIMAX_API_KEY not set")):
        with pytest.raises(ValueError, match="MINIMAX_API_KEY"):
            asyncio.run(run_experiment_a())


def test_run_experiment_a_propagates_transport_error() -> None:
    """`evaluate_recall`이 RuntimeError를 던지면 전파된다."""
    import httpx
    dash_mock = _make_dashboard_mock()

    with patch("runner.Dashboard", return_value=dash_mock), \
         patch("runner.CONTEXT_LENGTHS", [1_000]), \
         patch("runner.POSITIONS", ["front"]), \
         patch("runner.REPEATS", 1), \
         patch("runner.evaluate_recall", new_callable=AsyncMock,
               side_effect=RuntimeError("connection failed")):
        with pytest.raises(RuntimeError, match="connection failed"):
            asyncio.run(run_experiment_a())


# ── run_experiment_b 오류 경로 ─────────────────────────────────────────────────

def test_run_experiment_b_propagates_openhands_error() -> None:
    """`run_openhands_task`가 예외를 던지면 run_experiment_b가 전파한다."""
    from experiments.coding_failure.tasks import CodingTask

    dash_mock = _make_dashboard_mock()
    fake_tasks = [CodingTask(step=1, prompt="write hello world", category="basic")]

    with patch("runner.Dashboard", return_value=dash_mock), \
         patch("runner.get_coding_tasks", return_value=fake_tasks), \
         patch("runner.run_openhands_task", new_callable=AsyncMock,
               side_effect=ConnectionError("openhands unreachable")):
        with pytest.raises(ConnectionError, match="openhands unreachable"):
            asyncio.run(run_experiment_b())


def test_run_experiment_b_saves_results_on_success(tmp_path: Path) -> None:
    """모든 태스크 성공 시 결과 파일이 저장된다."""
    from experiments.coding_failure.tasks import CodingTask
    from experiments.coding_failure.evaluator import StepResult

    dash_mock = _make_dashboard_mock()
    fake_tasks = [CodingTask(step=1, prompt="write hello world", category="basic")]
    fake_result = StepResult(step=1, status="success", context_tokens=500,
                             duration_ms=200, error=None)

    with patch("runner.Dashboard", return_value=dash_mock), \
         patch("runner.get_coding_tasks", return_value=fake_tasks), \
         patch("runner.run_openhands_task", new_callable=AsyncMock,
               return_value=fake_result), \
         patch("runner.RESULTS_DIR", tmp_path):
        asyncio.run(run_experiment_b())

    files = list(tmp_path.glob("coding_failure_*.json"))
    assert len(files) == 1
    data = json.loads(files[0].read_text())
    assert data["steps"][0]["status"] == "success"
