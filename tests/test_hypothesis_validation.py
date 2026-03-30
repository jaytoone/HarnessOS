"""Tests for hypothesis_validation experiment (exec-based, deterministic)."""
import unicodedata

from experiments.hypothesis_validation.tasks import get_debug_tasks, DebugTask
from experiments.hypothesis_validation.strategies import (
    EngineeringStrategy,
    HypothesisStrategy,
    StrategyResult,
    AttemptResult,
    ExperimentMetadata,
    _execute_attempt,
    ENGINEERING_ATTEMPTS,
    HYPOTHESIS_ATTEMPTS,
)
from experiments.hypothesis_validation.runner import (
    run_experiment,
    validate_experiment_config,
    to_harness_format,
    save_results,
    ExperimentResult,
    ConfigIssue,
)
from experiments.hypothesis_validation.analyzer import (
    analyze_results,
    format_report,
    AnalysisReport,
)


# --- Task structure tests ---


def test_get_debug_tasks_returns_9() -> None:
    tasks = get_debug_tasks()
    assert len(tasks) == 12


def test_tasks_have_all_categories() -> None:
    tasks = get_debug_tasks()
    categories = {t.category for t in tasks}
    assert categories == {"simple", "causal", "assumption"}


def test_tasks_have_4_per_category() -> None:
    tasks = get_debug_tasks()
    counts: dict[str, int] = {}
    for t in tasks:
        counts[t.category] = counts.get(t.category, 0) + 1
    assert counts == {"simple": 4, "causal": 4, "assumption": 4}


def test_all_tasks_have_test_cases() -> None:
    tasks = get_debug_tasks()
    for t in tasks:
        assert len(t.test_cases) >= 2, f"Task {t.id} has too few test cases"


# --- Code correctness tests (exec-based) ---


def _run_code(code: str, func_name: str):
    """Helper: compile code and extract the named function.

    Uses compile+exec on trusted test fixture strings (not user input).
    """
    ns: dict[str, object] = {}
    compiled = compile(code, "<test>", "exec")  # noqa: S102
    exec(compiled, ns)  # noqa: S102 -- trusted test fixture code only
    return ns[func_name]


def test_correct_code_passes_a1() -> None:
    task = [t for t in get_debug_tasks() if t.id == "A1"][0]
    fn = _run_code(task.correct_code, "find_max_subarray")
    assert fn([1, 3, 2, 5, 1], 2) == [2, 5]
    assert fn([5, 1, 1, 1, 9], 2) == [1, 9]
    assert fn([1], 2) == []


def test_buggy_code_fails_a1() -> None:
    task = [t for t in get_debug_tasks() if t.id == "A1"][0]
    fn = _run_code(task.buggy_code, "find_max_subarray")
    result = fn([5, 1, 1, 1, 9], 2)
    assert result != [1, 9]


def test_correct_code_passes_a2() -> None:
    task = [t for t in get_debug_tasks() if t.id == "A2"][0]
    fn = _run_code(task.correct_code, "is_palindrome")
    assert fn("racecar") is True
    assert fn("hello") is False


def test_buggy_code_fails_a2() -> None:
    task = [t for t in get_debug_tasks() if t.id == "A2"][0]
    fn = _run_code(task.buggy_code, "is_palindrome")
    assert fn("racecar") is not True


def test_correct_code_passes_a3() -> None:
    task = [t for t in get_debug_tasks() if t.id == "A3"][0]
    fn = _run_code(task.correct_code, "safe_divide")
    assert fn(10, 2) == 5.0
    assert fn(1, 0) is None


def test_buggy_code_fails_a3() -> None:
    import pytest
    task = [t for t in get_debug_tasks() if t.id == "A3"][0]
    fn = _run_code(task.buggy_code, "safe_divide")
    with pytest.raises(ZeroDivisionError):
        fn(1, 0)


def test_correct_code_passes_b1() -> None:
    task = [t for t in get_debug_tasks() if t.id == "B1"][0]
    fn = _run_code(task.correct_code, "remove_duplicates")
    assert fn([1, 2, 3, 2, 1]) == [1, 2, 3]
    assert fn([1, 1, 1, 1]) == [1]


def test_buggy_code_fails_b1() -> None:
    task = [t for t in get_debug_tasks() if t.id == "B1"][0]
    fn = _run_code(task.buggy_code, "remove_duplicates")
    result = fn([1, 1, 1, 1])
    assert result != [1]


def test_correct_code_passes_b2() -> None:
    task = [t for t in get_debug_tasks() if t.id == "B2"][0]
    fn = _run_code(task.correct_code, "make_multipliers")
    multipliers = fn(4)
    assert [m(3) for m in multipliers] == [0, 3, 6, 9]


def test_buggy_code_fails_b2() -> None:
    task = [t for t in get_debug_tasks() if t.id == "B2"][0]
    fn = _run_code(task.buggy_code, "make_multipliers")
    multipliers = fn(4)
    results = [m(3) for m in multipliers]
    assert results == [9, 9, 9, 9]


def test_correct_code_passes_c1() -> None:
    task = [t for t in get_debug_tasks() if t.id == "C1"][0]
    fn = _run_code(task.correct_code, "count_unique_chars")
    assert fn("hello") == 4
    assert fn("e\u0301") == 1


def test_buggy_code_fails_c1() -> None:
    task = [t for t in get_debug_tasks() if t.id == "C1"][0]
    fn = _run_code(task.buggy_code, "count_unique_chars")
    assert fn("e\u0301") == 2


# --- _execute_attempt tests ---


def test_execute_attempt_correct_code() -> None:
    code = "def add(a, b):\n    return a + b\n"
    cases = [
        {"input": {"a": 1, "b": 2}, "expected": 3},
        {"input": {"a": 0, "b": 0}, "expected": 0},
    ]
    passed, total, solved = _execute_attempt(code, "add", cases)
    assert passed == 2
    assert total == 2
    assert solved is True


def test_execute_attempt_wrong_code() -> None:
    code = "def add(a, b):\n    return a - b\n"
    cases = [
        {"input": {"a": 1, "b": 2}, "expected": 3},
    ]
    passed, total, solved = _execute_attempt(code, "add", cases)
    assert passed == 0
    assert total == 1
    assert solved is False


def test_execute_attempt_syntax_error() -> None:
    code = "def add(a, b)\n    return a + b\n"  # missing colon
    cases = [{"input": {"a": 1, "b": 2}, "expected": 3}]
    passed, total, solved = _execute_attempt(code, "add", cases)
    assert passed == 0
    assert solved is False


def test_execute_attempt_runtime_error() -> None:
    code = "def div(a, b):\n    return a / b\n"
    cases = [{"input": {"a": 1, "b": 0}, "expected": None}]
    passed, total, solved = _execute_attempt(code, "div", cases)
    assert passed == 0
    assert solved is False


def test_execute_attempt_multipliers_check() -> None:
    """Test the special 'multipliers' check for B2."""
    code = "def make_multipliers(n):\n    return [lambda x, i=i: x * i for i in range(n)]\n"
    cases = [{"input": {"n": 4}, "expected_check": "multipliers"}]
    passed, total, solved = _execute_attempt(code, "make_multipliers", cases)
    assert passed == 1
    assert solved is True


# --- Strategy tests ---


def test_engineering_strategy_returns_valid_result() -> None:
    task = get_debug_tasks()[0]
    eng = EngineeringStrategy()
    result = eng.run(task, max_attempts=5)
    assert isinstance(result, StrategyResult)
    assert result.strategy == "engineering"
    assert result.task_id == task.id
    assert result.total_attempts >= 1


def test_hypothesis_strategy_returns_valid_result() -> None:
    task = get_debug_tasks()[0]
    hyp = HypothesisStrategy()
    result = hyp.run(task, max_attempts=5)
    assert isinstance(result, StrategyResult)
    assert result.strategy == "hypothesis"
    assert result.task_id == task.id
    for a in result.attempts:
        assert a.hypothesis is not None
        assert a.hypothesis_correct is not None


def test_hypothesis_attempts_have_hypotheses() -> None:
    """Every attempt in hypothesis strategy includes a hypothesis declaration."""
    task = get_debug_tasks()[3]  # B1: causal
    hyp = HypothesisStrategy()
    result = hyp.run(task, max_attempts=5)
    for attempt in result.attempts:
        assert isinstance(attempt.hypothesis, str)
        assert len(attempt.hypothesis) > 0


def test_engineering_no_hypotheses() -> None:
    """Engineering attempts should have no hypothesis."""
    task = get_debug_tasks()[0]
    eng = EngineeringStrategy()
    result = eng.run(task, max_attempts=5)
    for attempt in result.attempts:
        assert attempt.hypothesis is None


def test_strategy_results_are_deterministic() -> None:
    """Same task should produce same result on multiple runs."""
    task = get_debug_tasks()[4]  # B2
    eng = EngineeringStrategy()
    r1 = eng.run(task)
    r2 = eng.run(task)
    assert r1.solved == r2.solved
    assert r1.total_attempts == r2.total_attempts


def test_attempt_result_has_test_counts() -> None:
    """AttemptResult should contain tests_passed and tests_total."""
    task = get_debug_tasks()[0]
    eng = EngineeringStrategy()
    result = eng.run(task)
    for a in result.attempts:
        assert a.tests_total > 0
        if a.success:
            assert a.tests_passed == a.tests_total


# --- Runner tests ---


def test_run_experiment_returns_valid_structure() -> None:
    tasks = get_debug_tasks()[:2]
    result = run_experiment(tasks=tasks, max_attempts=3)
    assert isinstance(result, ExperimentResult)
    assert len(result.task_results) == 2
    assert result.max_attempts == 3
    for tr in result.task_results:
        assert tr.engineering_result is not None
        assert tr.hypothesis_result is not None


def test_run_experiment_default_tasks() -> None:
    result = run_experiment(max_attempts=5)
    assert len(result.task_results) == 12


def test_all_tasks_solved_by_both_strategies() -> None:
    """Both strategies should solve all 12 tasks (within max_attempts)."""
    result = run_experiment(max_attempts=10)
    for tr in result.task_results:
        assert tr.engineering_result is not None
        assert tr.engineering_result.solved, f"Eng failed on {tr.task_id}"
        assert tr.hypothesis_result is not None
        assert tr.hypothesis_result.solved, f"Hyp failed on {tr.task_id}"


# --- Analyzer tests ---


def test_analyze_results_produces_report() -> None:
    result = run_experiment(max_attempts=5)
    report = analyze_results(result)
    assert isinstance(report, AnalysisReport)
    assert len(report.category_stats) == 3
    assert report.overall_eng_success >= 0
    assert report.overall_hyp_success >= 0
    assert report.best_advantage_category in {"simple", "causal", "assumption"}


def test_analyze_results_has_task_details() -> None:
    result = run_experiment(max_attempts=5)
    report = analyze_results(result)
    assert len(report.task_details) == 12
    for d in report.task_details:
        assert d.task_id
        assert d.category in {"simple", "causal", "assumption"}


def test_hypothesis_fewer_attempts_on_causal() -> None:
    """Hypothesis should need fewer attempts on causal tasks."""
    result = run_experiment(max_attempts=10)
    report = analyze_results(result)
    causal = [s for s in report.category_stats if s.category == "causal"][0]
    assert causal.hyp_avg_attempts <= causal.eng_avg_attempts


def test_hypothesis_fewer_attempts_on_assumption() -> None:
    """Hypothesis should need fewer attempts on assumption tasks."""
    result = run_experiment(max_attempts=10)
    report = analyze_results(result)
    assumption = [s for s in report.category_stats if s.category == "assumption"][0]
    assert assumption.hyp_avg_attempts <= assumption.eng_avg_attempts


def test_simple_tasks_have_zero_advantage() -> None:
    """Research finding: simple bugs show no advantage for hypothesis approach."""
    result = run_experiment(max_attempts=10)
    report = analyze_results(result)
    simple = [s for s in report.category_stats if s.category == "simple"][0]
    assert simple.eng_avg_attempts == simple.hyp_avg_attempts, (
        "Simple bugs should take equal attempts for both strategies"
    )


def test_assumption_advantage_greater_than_causal() -> None:
    """Research finding: assumption bugs benefit MORE from hypothesis than causal bugs."""
    result = run_experiment(max_attempts=10)
    report = analyze_results(result)
    causal = [s for s in report.category_stats if s.category == "causal"][0]
    assumption = [s for s in report.category_stats if s.category == "assumption"][0]
    causal_savings = causal.eng_avg_attempts - causal.hyp_avg_attempts
    assumption_savings = assumption.eng_avg_attempts - assumption.hyp_avg_attempts
    assert assumption_savings >= causal_savings, (
        "Assumption bugs should show >= advantage over causal bugs for hypothesis strategy"
    )


def test_to_harness_format_includes_category_breakdown() -> None:
    """to_harness_format summary includes by_category with correct keys."""
    result = run_experiment(max_attempts=5)
    data = to_harness_format(result)
    by_cat = data["summary"]["by_category"]
    assert set(by_cat.keys()) == {"simple", "causal", "assumption"}
    for cat_data in by_cat.values():
        assert "count" in cat_data
        assert "engineering_avg_attempts" in cat_data
        assert "hypothesis_avg_attempts" in cat_data
        assert "attempt_savings" in cat_data
    assert by_cat["simple"]["attempt_savings"] == 0.0


def test_format_report_contains_categories() -> None:
    result = run_experiment(max_attempts=5)
    report = analyze_results(result)
    text = format_report(report)
    assert "simple" in text
    assert "causal" in text
    assert "assumption" in text
    assert "Engineering" in text
    assert "Hypothesis" in text


def test_format_report_contains_per_task_details() -> None:
    result = run_experiment(max_attempts=5)
    report = analyze_results(result)
    text = format_report(report)
    assert "A1" in text
    assert "B2" in text
    assert "C1" in text
    assert "Hypothesis:" in text


# --- Metadata tests ---


def test_experiment_metadata_fields() -> None:
    meta = ExperimentMetadata()
    assert meta.simulation_type == "researcher_coded_attempts"
    assert "researcher" in meta.limitation
    assert "real_LLM" in meta.what_this_does_not_prove


# --- Attempt coverage tests ---


def test_all_tasks_have_engineering_attempts() -> None:
    tasks = get_debug_tasks()
    for t in tasks:
        assert t.id in ENGINEERING_ATTEMPTS, f"Missing eng attempts for {t.id}"
        assert len(ENGINEERING_ATTEMPTS[t.id]) >= 1


def test_all_tasks_have_hypothesis_attempts() -> None:
    tasks = get_debug_tasks()
    for t in tasks:
        assert t.id in HYPOTHESIS_ATTEMPTS, f"Missing hyp attempts for {t.id}"
        assert len(HYPOTHESIS_ATTEMPTS[t.id]) >= 1


# --- validate_experiment_config tests ---


def test_validate_config_all_clear_with_real_tasks() -> None:
    issues = validate_experiment_config()
    assert issues == [], f"Expected no issues, got: {issues}"


def test_validate_config_detects_no_test_cases() -> None:
    bad_task = DebugTask(
        id="X1",
        category="simple",
        function_name="foo",
        buggy_code="def foo(): return 0",
        correct_code="def foo(): return 1",
        bug_description="wrong return",
        test_cases=[],
    )
    issues = validate_experiment_config([bad_task])
    assert any("no test cases" in i.issue for i in issues)
    assert issues[0].task_id == "X1"


def test_validate_config_detects_wrong_correct_code() -> None:
    bad_task = DebugTask(
        id="X2",
        category="simple",
        function_name="add",
        buggy_code="def add(a, b): return a - b",
        correct_code="def add(a, b): return a - b",  # same as buggy = still wrong
        bug_description="wrong op",
        test_cases=[{"input": {"a": 1, "b": 2}, "expected": 3}],
    )
    issues = validate_experiment_config([bad_task])
    assert any("correct_code fails" in i.issue for i in issues)


def test_validate_config_detects_bug_not_testable() -> None:
    bad_task = DebugTask(
        id="X3",
        category="simple",
        function_name="add",
        buggy_code="def add(a, b): return a + b",  # correct code as buggy
        correct_code="def add(a, b): return a + b",
        bug_description="no bug",
        test_cases=[{"input": {"a": 1, "b": 2}, "expected": 3}],
    )
    issues = validate_experiment_config([bad_task])
    assert any("buggy_code passes" in i.issue for i in issues)


def test_validate_config_returns_list_of_config_issues() -> None:
    issues = validate_experiment_config()
    assert isinstance(issues, list)
    for issue in issues:
        assert isinstance(issue, ConfigIssue)


# --- to_harness_format tests ---


def test_to_harness_format_structure() -> None:
    result = run_experiment(tasks=get_debug_tasks()[:3], max_attempts=5)
    data = to_harness_format(result)
    assert data["experiment"] == "hypothesis_validation"
    assert isinstance(data["steps"], list)
    assert isinstance(data["summary"], dict)


def test_to_harness_format_step_count() -> None:
    """3 tasks × 2 strategies = 6 steps."""
    result = run_experiment(tasks=get_debug_tasks()[:3], max_attempts=5)
    data = to_harness_format(result)
    assert len(data["steps"]) == 6


def test_to_harness_format_step_fields() -> None:
    result = run_experiment(tasks=get_debug_tasks()[:1], max_attempts=5)
    data = to_harness_format(result)
    for step in data["steps"]:
        assert "task_id" in step
        assert "strategy" in step
        assert step["strategy"] in {"engineering", "hypothesis"}
        assert step["status"] in {"success", "failure"}
        assert "attempts" in step


def test_to_harness_format_summary_keys() -> None:
    result = run_experiment(max_attempts=5)
    data = to_harness_format(result)
    summary = data["summary"]
    assert "task_count" in summary
    assert "engineering_solved" in summary
    assert "hypothesis_solved" in summary
    assert "engineering_avg_attempts" in summary
    assert "hypothesis_avg_attempts" in summary


def test_to_harness_format_all_tasks_success() -> None:
    """All 9 tasks solved → all steps should be success."""
    result = run_experiment(max_attempts=10)
    data = to_harness_format(result)
    assert all(s["status"] == "success" for s in data["steps"])


def test_to_harness_format_feeds_into_harness_evaluator() -> None:
    """Output of to_harness_format should pass evaluate_harness without error."""
    from harness_evaluator import evaluate_harness
    result = run_experiment(max_attempts=5)
    data = to_harness_format(result)
    verdict = evaluate_harness(data)
    assert verdict.experiment == "hypothesis_validation"
    assert verdict.score >= 0.0
    assert verdict.total_steps == 24  # 12 tasks × 2 strategies


# --- hypothesis_validation harness diagnosis tests ---


def test_harness_evaluator_hypothesis_validation_threshold() -> None:
    """Both strategies solve all tasks → should pass harness threshold."""
    from harness_evaluator import evaluate_harness, THRESHOLDS
    assert "hypothesis_validation" in THRESHOLDS
    result = run_experiment(max_attempts=10)
    data = to_harness_format(result)
    verdict = evaluate_harness(data)
    assert verdict.passed is True


def test_harness_evaluator_hypothesis_low_success_rate() -> None:
    """Inject low success rate → harness should flag it."""
    from harness_evaluator import evaluate_harness
    data = {
        "experiment": "hypothesis_validation",
        "steps": [
            {"task_id": "A1", "category": "simple", "strategy": "engineering",
             "status": "failure", "attempts": 5, "duration_ms": 0},
            {"task_id": "A1", "category": "simple", "strategy": "hypothesis",
             "status": "failure", "attempts": 5, "duration_ms": 0},
        ] * 5,  # 10 steps all failing
        "summary": {"engineering_avg_attempts": 0.0, "hypothesis_avg_attempts": 0.0},
    }
    verdict = evaluate_harness(data)
    assert verdict.passed is False
    assert any("성공률" in issue for issue in verdict.issues)


def test_hypothesis_first_attempt_solves_all_tasks() -> None:
    """Hypothesis strategy's first (and only) attempt should solve every task."""
    tasks = get_debug_tasks()
    hyp = HypothesisStrategy()
    for t in tasks:
        result = hyp.run(t, max_attempts=1)
        assert result.solved, (
            f"Hyp failed on {t.id} with 1 attempt: "
            f"{result.attempts[0].tests_passed}/{result.attempts[0].tests_total}"
        )


# --- Strategy edge case: max_attempts truncation ---


def test_engineering_max_attempts_break_and_unsolved() -> None:
    """Engineering: when len(attempts) > max_attempts, break triggered → unsolved return."""
    # C1 has 4 engineering attempts; capping at 3 forces the break path
    task = [t for t in get_debug_tasks() if t.id == "C1"][0]
    eng = EngineeringStrategy()
    result = eng.run(task, max_attempts=3)
    assert result.solved is False
    assert result.total_attempts == 3  # only 3 attempts ran, break on 4th


def test_hypothesis_max_attempts_zero_break() -> None:
    """Hypothesis: max_attempts=0 triggers break on first iteration → empty/unsolved."""
    task = get_debug_tasks()[0]  # A1
    hyp = HypothesisStrategy()
    result = hyp.run(task, max_attempts=0)
    assert result.solved is False
    assert result.total_attempts == 0


# --- Full pipeline integration test ---


def test_full_pipeline_validate_run_harness(tmp_path) -> None:
    """End-to-end: validate_config → run_experiment → to_harness_format → evaluate_harness → save_verdict."""
    from harness_evaluator import evaluate_harness, save_verdict

    # Pre-mortem: all tasks must be testable
    issues = validate_experiment_config()
    assert issues == [], f"Config issues: {issues}"

    # Run deterministic experiment
    result = run_experiment(max_attempts=5)
    assert len(result.task_results) == 12

    # Convert to harness format and evaluate
    data = to_harness_format(result)
    verdict = evaluate_harness(data)
    assert verdict.passed is True
    assert verdict.score >= 0.9

    # Persist verdict (should not raise)
    from unittest.mock import patch
    with patch("harness_evaluator.HARNESS_EVAL_DIR", tmp_path):
        path = save_verdict(verdict)
    assert path.exists()
    import json
    saved = json.loads(path.read_text())
    assert saved["experiment"] == "hypothesis_validation"
    assert saved["passed"] is True


def test_save_results_writes_json(tmp_path) -> None:
    """save_results() persists experiment to a loadable JSON file and returns (path, data)."""
    import json
    result = run_experiment(max_attempts=5)
    path, returned_data = save_results(result, output_dir=tmp_path)
    assert path.exists()
    data = json.loads(path.read_text())
    assert data["experiment"] == "hypothesis_validation"
    assert data["model"] == "deterministic"
    assert "timestamp" in data
    assert len(data["steps"]) == 24  # 12 tasks × 2 strategies
    assert "by_category" in data["summary"]
    # returned_data matches saved JSON (avoids redundant to_harness_format call in callers)
    assert returned_data["experiment"] == data["experiment"]
    assert returned_data["steps"] == data["steps"]


def test_save_results_default_dir(tmp_path, monkeypatch) -> None:
    """save_results() defaults to RESULTS_DIR when output_dir is None."""
    import json
    from experiments.hypothesis_validation import runner as runner_mod
    monkeypatch.setattr(runner_mod, "RESULTS_DIR", tmp_path)
    result = run_experiment(max_attempts=5)
    path, _ = save_results(result)
    assert path.parent == tmp_path
    data = json.loads(path.read_text())
    assert data["experiment"] == "hypothesis_validation"
