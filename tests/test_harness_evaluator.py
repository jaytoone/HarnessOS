"""harness_evaluator.py 테스트: 하네스 자체 평가 로직 검증."""
import json
from pathlib import Path
from unittest.mock import patch

import pytest

from harness_evaluator import (
    evaluate_harness,
    compare_runs,
    save_verdict,
    load_latest_verdict,
    HarnessVerdict,
    QualityThreshold,
    THRESHOLDS,
    _compute_score,
    _diagnose_context_memory,
    _diagnose_coding_failure,
)


# ── evaluate_harness 기본 동작 ─────────────────────────────────────────────────

def test_evaluate_harness_empty_steps() -> None:
    """스텝이 0개이면 passed=False, score=0.0."""
    data = {"experiment": "context_memory", "steps": []}
    verdict = evaluate_harness(data)
    assert verdict.passed is False
    assert verdict.score == 0.0
    assert verdict.total_steps == 0
    assert any("0개" in issue for issue in verdict.issues)


def test_evaluate_harness_all_success() -> None:
    """모든 스텝 성공 + 적정 시간이면 passed=True, 높은 score."""
    steps = [
        {"step": i, "status": "success", "duration_ms": 1000,
         "position": "front", "context_tokens": 1000}
        for i in range(1, 11)
    ]
    data = {"experiment": "context_memory", "steps": steps}
    verdict = evaluate_harness(data)
    assert verdict.passed is True
    assert verdict.score > 0.8
    assert verdict.success_rate == 1.0


def test_evaluate_harness_low_success_rate() -> None:
    """성공률이 기준 미달이면 이슈가 보고됨."""
    steps = [
        {"step": i, "status": "success" if i <= 3 else "failure",
         "duration_ms": 1000, "position": "front", "context_tokens": 1000}
        for i in range(1, 11)
    ]
    data = {"experiment": "context_memory", "steps": steps}
    verdict = evaluate_harness(data)
    assert verdict.success_rate == 0.3
    assert any("성공률" in issue for issue in verdict.issues)
    assert verdict.passed is False


def test_evaluate_harness_slow_duration() -> None:
    """평균 응답 시간 초과 시 이슈 보고."""
    steps = [
        {"step": i, "status": "success", "duration_ms": 50_000,
         "position": "front", "context_tokens": 1000}
        for i in range(1, 11)
    ]
    data = {"experiment": "context_memory", "steps": steps}
    verdict = evaluate_harness(data)
    assert any("응답 시간" in issue for issue in verdict.issues)


def test_evaluate_harness_insufficient_steps() -> None:
    """스텝 수 부족 시 이슈 보고."""
    steps = [
        {"step": 1, "status": "success", "duration_ms": 1000,
         "position": "front", "context_tokens": 1000}
    ]
    data = {"experiment": "context_memory", "steps": steps}
    verdict = evaluate_harness(data)
    assert any("스텝" in issue and "미달" in issue for issue in verdict.issues)


def test_evaluate_harness_unknown_experiment() -> None:
    """알 수 없는 실험 유형에도 기본 동작."""
    steps = [
        {"step": i, "status": "success", "duration_ms": 500}
        for i in range(1, 6)
    ]
    data = {"experiment": "unknown_exp", "steps": steps}
    verdict = evaluate_harness(data)
    assert verdict.experiment == "unknown_exp"
    assert verdict.success_rate == 1.0


def test_evaluate_harness_coding_failure_routes_to_diagnose() -> None:
    """evaluate_harness가 coding_failure 진단 경로를 통과한다 (line 134 커버)."""
    steps = [
        {"step": i, "status": "success", "duration_ms": 500}
        for i in range(1, 6)
    ]
    data = {"experiment": "coding_failure", "steps": steps, "summary": {}}
    verdict = evaluate_harness(data)
    assert verdict.experiment == "coding_failure"
    assert verdict.total_steps == 5


# ── context_memory 진단 ────────────────────────────────────────────────────────

def test_diagnose_context_memory_position_variance() -> None:
    """위치별 성공률 편차가 크면 이슈 보고."""
    steps = [
        {"status": "success", "position": "front", "context_tokens": 1000},
        {"status": "success", "position": "front", "context_tokens": 1000},
        {"status": "failure", "position": "middle", "context_tokens": 1000},
        {"status": "failure", "position": "middle", "context_tokens": 1000},
    ]
    issues: list[str] = []
    suggestions: list[str] = []
    _diagnose_context_memory(steps, issues, suggestions)
    assert any("편차" in issue for issue in issues)


def test_diagnose_context_memory_long_context_degradation() -> None:
    """긴 컨텍스트에서 성능 저하가 심하면 제안 생성."""
    steps = [
        {"status": "success", "position": "front", "context_tokens": 1000},
        {"status": "success", "position": "front", "context_tokens": 1000},
        {"status": "failure", "position": "front", "context_tokens": 100_000},
        {"status": "failure", "position": "front", "context_tokens": 100_000},
    ]
    issues: list[str] = []
    suggestions: list[str] = []
    _diagnose_context_memory(steps, issues, suggestions)
    assert any("저하" in s for s in suggestions)


# ── coding_failure 진단 ────────────────────────────────────────────────────────

def test_diagnose_coding_failure_low_category() -> None:
    """특정 카테고리 성공률이 매우 낮으면 이슈 보고."""
    steps = [
        {"status": "failure", "category": "architecture"},
        {"status": "failure", "category": "architecture"},
        {"status": "failure", "category": "architecture"},
    ]
    issues: list[str] = []
    suggestions: list[str] = []
    _diagnose_coding_failure(steps, {}, issues, suggestions)
    assert any("architecture" in issue for issue in issues)


def test_diagnose_coding_failure_early_inflection() -> None:
    """실패 급증이 조기 발생하면 이슈 보고."""
    steps = [{"status": "success"} for _ in range(20)]
    summary = {"failure_inflection_step": 3}
    issues: list[str] = []
    suggestions: list[str] = []
    _diagnose_coding_failure(steps, summary, issues, suggestions)
    assert any("30%" in issue for issue in issues)


# ── 점수 계산 ──────────────────────────────────────────────────────────────────

def test_compute_score_perfect() -> None:
    """완벽한 조건에서 score=1.0."""
    threshold = QualityThreshold(min_success_rate=0.7, max_avg_duration_ms=30_000, min_steps=5)
    score = _compute_score(1.0, 10_000, 10, threshold)
    assert score == 1.0


def test_compute_score_zero_success() -> None:
    """성공률 0이면 score가 낮음."""
    threshold = QualityThreshold(min_success_rate=0.7, max_avg_duration_ms=30_000, min_steps=5)
    score = _compute_score(0.0, 10_000, 10, threshold)
    assert score < 0.5


def test_compute_score_no_threshold() -> None:
    """threshold가 None이어도 계산 가능."""
    score = _compute_score(0.8, 20_000, 10, None)
    assert 0.0 <= score <= 1.0


# ── compare_runs ───────────────────────────────────────────────────────────────

def test_compare_runs_improving() -> None:
    """점수가 향상되면 trend=improving."""
    prev = HarnessVerdict("exp", True, 0.5, 0.6, 5000, 10)
    curr = HarnessVerdict("exp", True, 0.8, 0.9, 4000, 10)
    result = compare_runs(curr, prev)
    assert result["trend"] == "improving"
    assert result["delta_score"] > 0


def test_compare_runs_regressing() -> None:
    """점수가 하락하면 trend=regressing."""
    prev = HarnessVerdict("exp", True, 0.8, 0.9, 5000, 10)
    curr = HarnessVerdict("exp", False, 0.4, 0.3, 8000, 10)
    result = compare_runs(curr, prev)
    assert result["trend"] == "regressing"
    assert result["delta_score"] < 0


def test_compare_runs_stable() -> None:
    """점수 변화가 미미하면 trend=stable."""
    prev = HarnessVerdict("exp", True, 0.75, 0.8, 5000, 10)
    curr = HarnessVerdict("exp", True, 0.77, 0.82, 4800, 10)
    result = compare_runs(curr, prev)
    assert result["trend"] == "stable"


# ── save/load verdict ──────────────────────────────────────────────────────────

def test_save_verdict_creates_json(tmp_path: Path) -> None:
    """save_verdict가 JSON 파일을 생성."""
    verdict = HarnessVerdict(
        experiment="context_memory",
        passed=True,
        score=0.9,
        success_rate=0.95,
        avg_duration_ms=2000,
        total_steps=10,
        issues=[],
        suggestions=[],
    )
    with patch("harness_evaluator.HARNESS_EVAL_DIR", tmp_path):
        path = save_verdict(verdict)
    assert path.exists()
    data = json.loads(path.read_text())
    assert data["experiment"] == "context_memory"
    assert data["score"] == 0.9
    assert data["passed"] is True


def test_load_latest_verdict_found(tmp_path: Path) -> None:
    """저장된 verdict를 load_latest_verdict로 로드."""
    verdict = HarnessVerdict(
        experiment="coding_failure",
        passed=False,
        score=0.4,
        success_rate=0.3,
        avg_duration_ms=10_000,
        total_steps=5,
        issues=["low rate"],
        suggestions=["fix it"],
    )
    with patch("harness_evaluator.HARNESS_EVAL_DIR", tmp_path):
        save_verdict(verdict)
        loaded = load_latest_verdict("coding_failure")

    assert loaded is not None
    assert loaded.experiment == "coding_failure"
    assert loaded.score == 0.4
    assert loaded.issues == ["low rate"]


def test_load_latest_verdict_not_found(tmp_path: Path) -> None:
    """파일이 없으면 None 반환."""
    with patch("harness_evaluator.HARNESS_EVAL_DIR", tmp_path):
        loaded = load_latest_verdict("nonexistent")
    assert loaded is None


def test_load_latest_verdict_no_directory() -> None:
    """디렉토리 자체가 없으면 None 반환."""
    with patch("harness_evaluator.HARNESS_EVAL_DIR", Path("/tmp/nonexistent_dir_xyz")):
        loaded = load_latest_verdict("anything")
    assert loaded is None


def test_hypothesis_validation_small_attempt_difference_suggestion() -> None:
    """When eng/hyp attempts are similar, harness suggests adding harder tasks."""
    from harness_evaluator import evaluate_harness
    data = {
        "experiment": "hypothesis_validation",
        "steps": [
            {"task_id": f"A{i}", "category": "simple", "strategy": "engineering",
             "status": "success", "attempts": 1, "duration_ms": 0}
            for i in range(9)
        ] + [
            {"task_id": f"A{i}", "category": "simple", "strategy": "hypothesis",
             "status": "success", "attempts": 1, "duration_ms": 0}
            for i in range(9)
        ],
        "summary": {
            "engineering_avg_attempts": 1.1,
            "hypothesis_avg_attempts": 1.0,
        },
    }
    verdict = evaluate_harness(data)
    assert any("attempt 차이" in s for s in verdict.suggestions)


def test_hypothesis_validation_single_category_suggestion() -> None:
    """단일 카테고리만 있으면 외적 타당도 제안."""
    from harness_evaluator import evaluate_harness
    steps = [
        {"task_id": f"A{i}", "category": "simple", "strategy": s,
         "status": "success", "attempts": 1, "duration_ms": 0}
        for i in range(5) for s in ("engineering", "hypothesis")
    ]
    data = {
        "experiment": "hypothesis_validation",
        "steps": steps,
        "summary": {"task_count": 5, "engineering_avg_attempts": 1.5, "hypothesis_avg_attempts": 1.0},
    }
    verdict = evaluate_harness(data)
    assert any("카테고리" in s for s in verdict.suggestions)


def test_hypothesis_validation_too_few_tasks_issue() -> None:
    """태스크 수 < 5이면 통계적 유의성 이슈 플래그."""
    from harness_evaluator import evaluate_harness
    steps = [
        {"task_id": f"T{i}", "category": "causal", "strategy": s,
         "status": "success", "attempts": 1, "duration_ms": 0}
        for i in range(3) for s in ("engineering", "hypothesis")
    ]
    data = {
        "experiment": "hypothesis_validation",
        "steps": steps,
        "summary": {"task_count": 3, "engineering_avg_attempts": 1.5, "hypothesis_avg_attempts": 1.0},
    }
    verdict = evaluate_harness(data)
    assert any("통계적 유의성" in issue for issue in verdict.issues)
