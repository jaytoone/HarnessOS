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
