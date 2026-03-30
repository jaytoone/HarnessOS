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
            main([])
    assert exc.value.code == 0
    assert "결과 파일 없음" in capsys.readouterr().out


def test_main_unknown_experiment_type(tmp_path: Path, capsys: pytest.CaptureFixture) -> None:
    """알 수 없는 experiment 타입은 스텝 수만 출력."""
    _write_result(tmp_path, "custom_experiment", [{"status": "success"}])
    with patch("analyze.RESULTS_DIR", tmp_path):
        main([])
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
        main([])

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


def test_analyze_hypothesis_validation_by_category(capsys: pytest.CaptureFixture) -> None:
    """by_category 있으면 카테고리별 breakdown 출력."""
    from analyze import analyze_hypothesis_validation
    data = {
        "steps": [{"status": "success"}] * 18,
        "summary": {
            "task_count": 9,
            "engineering_solved": 9,
            "hypothesis_solved": 9,
            "engineering_avg_attempts": 1.6,
            "hypothesis_avg_attempts": 1.0,
            "by_category": {
                "simple": {"engineering_avg_attempts": 1.0, "hypothesis_avg_attempts": 1.0, "attempt_savings": 0.0},
                "causal": {"engineering_avg_attempts": 1.7, "hypothesis_avg_attempts": 1.0, "attempt_savings": 0.7},
                "assumption": {"engineering_avg_attempts": 2.0, "hypothesis_avg_attempts": 1.0, "attempt_savings": 1.0},
            },
        },
    }
    analyze_hypothesis_validation(data)
    out = capsys.readouterr().out
    assert "카테고리별" in out
    assert "simple" in out
    assert "causal" in out
    assert "assumption" in out
    assert "+1.0" in out


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
        main([])
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
        main([])
    out = capsys.readouterr().out
    assert "claude-haiku" in out


# --- show_harness_trend tests ---


def test_show_harness_trend_dir_exists_no_eval_files(tmp_path: Path, capsys: pytest.CaptureFixture) -> None:
    """디렉터리는 있지만 *_eval_*.json 파일이 없으면 '기록 없음' 출력."""
    from analyze import show_harness_trend
    with patch("harness_evaluator.HARNESS_EVAL_DIR", tmp_path):
        show_harness_trend(None)
    out = capsys.readouterr().out
    assert "없음" in out


def test_show_harness_trend_no_directory(tmp_path: Path, capsys: pytest.CaptureFixture) -> None:
    """harness_eval 디렉터리 없으면 안내 메시지."""
    from analyze import show_harness_trend
    with patch("harness_evaluator.HARNESS_EVAL_DIR", tmp_path / "nonexistent"):
        show_harness_trend()
    out = capsys.readouterr().out
    assert "없음" in out


def test_show_harness_trend_with_two_runs(tmp_path: Path, capsys: pytest.CaptureFixture) -> None:
    """2회 실행 기록 → 추이 출력."""
    import json
    from analyze import show_harness_trend

    # 두 개의 평가 파일 생성
    for i, score in enumerate([0.7, 0.9]):
        data = {
            "experiment": "test_exp",
            "passed": score > 0.8,
            "score": score,
            "success_rate": score,
            "avg_duration_ms": 1000.0,
            "total_steps": 5,
            "issues": [],
            "suggestions": [],
            "timestamp": f"2026-03-30T0{i}:00:00",
        }
        (tmp_path / f"test_exp_eval_2026033{i}.json").write_text(json.dumps(data))

    with patch("harness_evaluator.HARNESS_EVAL_DIR", tmp_path):
        show_harness_trend("test_exp")

    out = capsys.readouterr().out
    assert "test_exp" in out
    assert "0.700" in out or "0.7" in out
    assert "0.900" in out or "0.9" in out
    assert "↑" in out or "improving" in out


def test_show_harness_trend_no_matching_exp(tmp_path: Path, capsys: pytest.CaptureFixture) -> None:
    """지정한 실험 기록 없으면 '없음' 출력."""
    from analyze import show_harness_trend
    with patch("harness_evaluator.HARNESS_EVAL_DIR", tmp_path):
        show_harness_trend("nonexistent_exp")
    out = capsys.readouterr().out
    assert "없음" in out


def test_show_harness_trend_all_experiments(tmp_path: Path, capsys: pytest.CaptureFixture) -> None:
    """experiment 인자 없으면 모든 실험 표시."""
    import json
    from analyze import show_harness_trend

    for exp in ["exp_a", "exp_b"]:
        data = {
            "experiment": exp, "passed": True, "score": 0.8,
            "success_rate": 0.8, "avg_duration_ms": 0, "total_steps": 5,
            "issues": [], "suggestions": [], "timestamp": "2026-03-30T00:00:00",
        }
        (tmp_path / f"{exp}_eval_20260330.json").write_text(json.dumps(data))

    with patch("harness_evaluator.HARNESS_EVAL_DIR", tmp_path):
        show_harness_trend(None)

    out = capsys.readouterr().out
    assert "exp_a" in out
    assert "exp_b" in out


def test_main_harness_trend_flag(tmp_path: Path, capsys: pytest.CaptureFixture) -> None:
    """--harness-trend 플래그가 show_harness_trend를 호출한다."""
    from analyze import main
    with patch("harness_evaluator.HARNESS_EVAL_DIR", tmp_path / "no"):
        main(["--harness-trend"])
    out = capsys.readouterr().out
    assert "없음" in out or "추이" in out


# --- run_hypothesis_pipeline tests ---


def test_run_hypothesis_pipeline_success(tmp_path: Path, capsys: pytest.CaptureFixture) -> None:
    """run_hypothesis_pipeline() 성공 경로: 4단계 출력 및 파일 생성."""
    from analyze import run_hypothesis_pipeline
    with patch("experiments.hypothesis_validation.runner.RESULTS_DIR", tmp_path), \
         patch("harness_evaluator.HARNESS_EVAL_DIR", tmp_path):
        run_hypothesis_pipeline()
    out = capsys.readouterr().out
    assert "1/4" in out
    assert "2/4" in out
    assert "3/4" in out
    assert "4/4" in out
    assert "PASS" in out or "FAIL" in out
    # Formatted report includes category table
    assert "simple" in out
    assert "assumption" in out
    # At least one result file should exist
    json_files = list(tmp_path.glob("*.json"))
    assert json_files


def test_run_hypothesis_pipeline_config_failure(tmp_path: Path, capsys: pytest.CaptureFixture) -> None:
    """설정 검증 실패 시 sys.exit(1) 호출."""
    from analyze import run_hypothesis_pipeline
    from experiments.hypothesis_validation.runner import ConfigIssue
    fake_issue = ConfigIssue(task_id="Z1", issue="test failure")
    with patch(
        "experiments.hypothesis_validation.runner.validate_experiment_config",
        return_value=[fake_issue],
    ):
        with pytest.raises(SystemExit) as exc:
            run_hypothesis_pipeline()
    assert exc.value.code == 1
    out = capsys.readouterr().out
    assert "검증 실패" in out


def test_main_run_flag(tmp_path: Path, capsys: pytest.CaptureFixture) -> None:
    """--run 플래그가 run_hypothesis_pipeline을 호출한다."""
    from analyze import main
    with patch("analyze.run_hypothesis_pipeline") as mock_run:
        main(["--run"])
    mock_run.assert_called_once()


def test_run_hypothesis_pipeline_with_issues(tmp_path: Path, capsys: pytest.CaptureFixture) -> None:
    """하네스 verdict에 issue/suggestion 있을 때 해당 줄 출력."""
    import json
    from analyze import run_hypothesis_pipeline
    from harness_evaluator import HarnessVerdict

    fake_verdict = HarnessVerdict(
        experiment="hypothesis_validation",
        passed=False,
        score=0.6,
        success_rate=0.6,
        avg_duration_ms=0.0,
        total_steps=12,
        issues=["성공률 낮음"],
        suggestions=["태스크 난이도 조정"],
    )
    with patch("experiments.hypothesis_validation.runner.RESULTS_DIR", tmp_path), \
         patch("harness_evaluator.HARNESS_EVAL_DIR", tmp_path), \
         patch("harness_evaluator.evaluate_harness", return_value=fake_verdict):
        run_hypothesis_pipeline()
    out = capsys.readouterr().out
    assert "성공률 낮음" in out
    assert "태스크 난이도 조정" in out
