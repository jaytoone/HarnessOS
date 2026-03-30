"""analyze.py 결과 분석 스크립트 테스트."""
import json
import pytest
from pathlib import Path
from unittest.mock import patch

from analyze import analyze_context_memory, analyze_coding_failure, main


def _write_result(path: Path, experiment: str, steps: list, summary: dict | None = None) -> Path:
    data = {
        "experiment": experiment,
        "model": "test/model",
        "timestamp": "2026-01-01T00:00:00",
        "steps": steps,
        "summary": summary or {},
    }
    result_path = path / f"{experiment}_20260101_000000.json"
    result_path.write_text(json.dumps(data))
    return result_path


def test_analyze_context_memory_success_rate(capsys: pytest.CaptureFixture) -> None:
    """context_memory 분석: 성공률 정확히 출력."""
    steps = [
        {"status": "success", "position": "front", "context_tokens": 1_000},
        {"status": "failure", "position": "back", "context_tokens": 10_000},
    ]
    analyze_context_memory({"steps": steps})
    out = capsys.readouterr().out
    assert "2회" in out
    assert "1/2" in out
    assert "50.0%" in out


def test_analyze_context_memory_empty(capsys: pytest.CaptureFixture) -> None:
    """빈 steps일 때 no steps 출력."""
    analyze_context_memory({"steps": []})
    out = capsys.readouterr().out
    assert "no steps" in out


def test_analyze_coding_failure_with_inflection(capsys: pytest.CaptureFixture) -> None:
    """실패 급증 시점이 있으면 출력."""
    steps = [{"status": "success"}]
    summary = {"failure_inflection_step": 7, "failure_inflection_tokens": 50_000}
    analyze_coding_failure({"steps": steps, "summary": summary})
    out = capsys.readouterr().out
    assert "스텝 7" in out
    assert "50000" in out


def test_analyze_coding_failure_no_inflection(capsys: pytest.CaptureFixture) -> None:
    """실패 급증 없으면 '감지되지 않음' 출력."""
    analyze_coding_failure({"steps": [{"status": "success"}], "summary": {}})
    out = capsys.readouterr().out
    assert "감지되지 않음" in out


def test_analyze_coding_failure_empty(capsys: pytest.CaptureFixture) -> None:
    """빈 steps일 때 no steps 출력."""
    analyze_coding_failure({"steps": [], "summary": {}})
    out = capsys.readouterr().out
    assert "no steps" in out


def test_main_no_results_dir(tmp_path: Path, capsys: pytest.CaptureFixture) -> None:
    """결과 디렉터리 없으면 안내 메시지 출력 후 종료."""
    with patch("analyze.RESULTS_DIR", tmp_path / "nonexistent"):
        with pytest.raises(SystemExit) as exc:
            main()
    assert exc.value.code == 0
    assert "결과 파일 없음" in capsys.readouterr().out


def test_main_unknown_experiment_type(tmp_path: Path, capsys: pytest.CaptureFixture) -> None:
    """알 수 없는 experiment 타입은 스텝 수만 출력."""
    _write_result(tmp_path, "custom_experiment", [{"status": "success"}])
    with patch("analyze.RESULTS_DIR", tmp_path):
        main()
    out = capsys.readouterr().out
    assert "스텝 수" in out


def test_main_analyzes_all_files(tmp_path: Path, capsys: pytest.CaptureFixture) -> None:
    """main()이 RESULTS_DIR의 모든 JSON 파일을 분석한다."""
    _write_result(tmp_path, "context_memory", [
        {"status": "success", "position": "front", "context_tokens": 1_000},
    ])
    _write_result(tmp_path, "coding_failure", [
        {"status": "failure"},
    ], summary={"failure_inflection_step": None, "failure_inflection_tokens": None})

    with patch("analyze.RESULTS_DIR", tmp_path):
        main()

    out = capsys.readouterr().out
    assert "2개 파일" in out
    assert "context_memory" in out
    assert "coding_failure" in out


def test_analyze_hypothesis_validation_output(capsys: pytest.CaptureFixture) -> None:
    """hypothesis_validation 분석: 전략별 해결 수 및 이점 출력."""
    from analyze import analyze_hypothesis_validation
    data = {
        "steps": [{"status": "success"}] * 18,
        "summary": {
            "task_count": 9,
            "engineering_solved": 9,
            "hypothesis_solved": 9,
            "engineering_avg_attempts": 1.6,
            "hypothesis_avg_attempts": 1.0,
        },
    }
    analyze_hypothesis_validation(data)
    out = capsys.readouterr().out
    assert "9개" in out
    assert "1.6" in out
    assert "1.0" in out
    assert "이점" in out


def test_analyze_hypothesis_validation_empty(capsys: pytest.CaptureFixture) -> None:
    from analyze import analyze_hypothesis_validation
    analyze_hypothesis_validation({"steps": [], "summary": {}})
    out = capsys.readouterr().out
    assert "no steps" in out


def test_analyze_llm_hypothesis_output(capsys: pytest.CaptureFixture) -> None:
    """LLM 실험 결과 분석: pass@1 및 토큰 차이 출력."""
    from analyze import analyze_llm_hypothesis
    data = {
        "model": "claude-haiku-4-5-20251001",
        "trials_per_task": 3,
        "engineering_overall_pass_rate": 0.889,
        "hypothesis_overall_pass_rate": 1.0,
        "engineering_total_tokens": 10000,
        "hypothesis_total_tokens": 12000,
        "tasks": [{}],
    }
    analyze_llm_hypothesis(data)
    out = capsys.readouterr().out
    assert "claude-haiku" in out
    assert "88.9%" in out
    assert "100.0%" in out
    assert "+2,000" in out or "2000" in out


def test_analyze_llm_hypothesis_empty_tasks(capsys: pytest.CaptureFixture) -> None:
    from analyze import analyze_llm_hypothesis
    analyze_llm_hypothesis({"tasks": []})
    out = capsys.readouterr().out
    assert "no tasks" in out


def test_main_hypothesis_validation_type(tmp_path: Path, capsys: pytest.CaptureFixture) -> None:
    """main()이 hypothesis_validation 타입을 올바르게 처리한다."""
    data = {
        "experiment": "hypothesis_validation",
        "model": "test",
        "timestamp": "2026-01-01T00:00:00",
        "steps": [{"status": "success"}] * 18,
        "summary": {
            "task_count": 9, "engineering_solved": 9, "hypothesis_solved": 9,
            "engineering_avg_attempts": 1.6, "hypothesis_avg_attempts": 1.0,
        },
    }
    path = tmp_path / "hypothesis_validation_20260101_000000.json"
    path.write_text(json.dumps(data))
    with patch("analyze.RESULTS_DIR", tmp_path):
        main()
    out = capsys.readouterr().out
    assert "9개" in out


def test_main_llm_hypothesis_type(tmp_path: Path, capsys: pytest.CaptureFixture) -> None:
    """main()이 llm_hypothesis_validation 파일을 올바르게 처리한다."""
    data = {
        "experiment": "llm_hypothesis_validation",
        "model": "claude-haiku-4-5-20251001",
        "timestamp": "2026-01-01T00:00:00",
        "steps": [],
        "summary": {},
        "trials_per_task": 1,
        "engineering_overall_pass_rate": 0.9,
        "hypothesis_overall_pass_rate": 1.0,
        "engineering_total_tokens": 5000,
        "hypothesis_total_tokens": 6000,
        "tasks": [{}],
    }
    path = tmp_path / "llm_hypothesis_validation_20260101_000000.json"
    path.write_text(json.dumps(data))
    with patch("analyze.RESULTS_DIR", tmp_path):
        main()
    out = capsys.readouterr().out
    assert "claude-haiku" in out
