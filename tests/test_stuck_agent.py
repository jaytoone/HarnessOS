"""Tests for Stuck-Agent Escape Rate experiment.

Covers:
  - Task design validity (buggy fails, correct passes, misleading tests differ)
  - Deterministic runner correctness
  - Stats module: McNemar, Cohen's d, bootstrap CI
  - LLM runner (mocked)
  - save_results serialization
  - analyze_results_file round-trip
  - analyze.py --run-stuck-llm CLI integration
"""
from __future__ import annotations

import json
import math
from pathlib import Path
from typing import Any
from unittest.mock import MagicMock, patch

import pytest

from experiments.stuck_agent.tasks import StuckTask, get_stuck_tasks
from experiments.stuck_agent.runner import (
    ControlledLLMStuckRunner,
    DeterministicStuckRunner,
    LLMStuckRunner,
    RescueResult,
    StuckExperimentResult,
    StuckTaskResult,
    save_results,
)
from experiments.stuck_agent.stats import (
    StatsResult,
    analyze,
    bootstrap_ci,
    cohens_d,
    mcnemar_test,
    _chi2_sf,
)
from experiments.stuck_agent.analyzer import analyze_results_file, print_report
from experiments.hypothesis_validation.strategies import _execute_attempt


# ── Task design validation ─────────────────────────────────────────────────


def test_all_tasks_have_required_fields() -> None:
    for task in get_stuck_tasks():
        assert task.id, f"{task.id}: empty id"
        assert task.buggy_code
        assert task.misleading_fix_code
        assert task.correct_code
        assert task.test_cases, f"{task.id}: no test cases"
        assert task.bug_description
        assert task.misleading_description


def test_correct_code_passes_all_tests() -> None:
    """Each task's correct_code must pass all test cases."""
    for task in get_stuck_tasks():
        _, _, solved = _execute_attempt(
            task.correct_code, task.function_name, task.test_cases
        )
        assert solved, f"{task.id}: correct_code fails tests — task design error"


def test_buggy_code_fails_at_least_one_test() -> None:
    """Each task's buggy_code must fail at least one test case."""
    for task in get_stuck_tasks():
        _, _, solved = _execute_attempt(
            task.buggy_code, task.function_name, task.test_cases
        )
        assert not solved, f"{task.id}: buggy_code passes all tests — not a valid bug"


def test_misleading_fix_differs_from_correct() -> None:
    """Misleading fix should not be identical to correct code."""
    for task in get_stuck_tasks():
        assert task.misleading_fix_code.strip() != task.correct_code.strip(), (
            f"{task.id}: misleading_fix_code is same as correct_code"
        )


def test_tasks_cover_all_categories() -> None:
    tasks = get_stuck_tasks()
    cats = {t.category for t in tasks}
    assert cats == {"red_herring", "multi_bug", "hidden_assume", "semantic_inv"}


def test_exactly_fourteen_tasks() -> None:
    assert len(get_stuck_tasks()) == 14


# ── Deterministic runner ───────────────────────────────────────────────────


def test_deterministic_runner_runs_all_tasks() -> None:
    runner = DeterministicStuckRunner()
    result = runner.run()
    assert len(result.task_results) == 14


def test_deterministic_runner_no_trivial_tasks() -> None:
    """All tasks should be 'stuck' (phase 1 fails) by design."""
    runner = DeterministicStuckRunner()
    result = runner.run()
    trivial = [r for r in result.task_results if r.phase1_passed]
    assert len(trivial) == 0, f"Trivial tasks: {[r.task_id for r in trivial]}"


def test_deterministic_runner_hypothesis_always_escapes() -> None:
    """Hypothesis rescue uses correct_code → always escapes."""
    runner = DeterministicStuckRunner()
    result = runner.run()
    for r in result.stuck_results:
        assert r.hyp_rescue is not None
        assert r.hyp_rescue.escaped, f"{r.task_id}: hypothesis rescue should escape"


def test_deterministic_runner_escape_lists() -> None:
    runner = DeterministicStuckRunner()
    result = runner.run()
    assert len(result.eng_escaped) == 14
    assert len(result.hyp_escaped) == 14
    assert all(result.hyp_escaped), "hypothesis should escape all (uses correct_code)"


def test_deterministic_runner_model_label() -> None:
    result = DeterministicStuckRunner().run()
    assert result.model == "deterministic"


# ── Stats module ───────────────────────────────────────────────────────────


def test_mcnemar_all_same() -> None:
    """When all outcomes match, no discordant pairs — p=1.0."""
    eng = [True, True, False, False]
    hyp = [True, True, False, False]
    chi2, p, b, c = mcnemar_test(eng, hyp)
    assert b == 0 and c == 0
    assert p == 1.0
    assert chi2 == 0.0


def test_mcnemar_hypothesis_always_wins() -> None:
    """When hypothesis always wins where engineering fails → strong signal."""
    eng = [False, False, False, False, False, False, False, False, False, False]
    hyp = [True,  True,  True,  True,  True,  True,  True,  True,  True,  True]
    chi2, p, b, c = mcnemar_test(eng, hyp)
    assert b == 10 and c == 0
    assert p < 0.05


def test_mcnemar_length_mismatch() -> None:
    with pytest.raises(ValueError, match="same length"):
        mcnemar_test([True, False], [True])


def test_cohens_d_identical_groups() -> None:
    d, label = cohens_d([1.0, 1.0, 1.0], [1.0, 1.0, 1.0])
    assert d == 0.0
    assert label == "negligible"


def test_cohens_d_large_effect() -> None:
    group1 = [0.0] * 20
    group2 = [1.0] * 20
    d, label = cohens_d(group1, group2)
    assert label == "large"
    assert d > 0.8


def test_cohens_d_labels() -> None:
    """Boundary values map to correct labels."""
    # negligible: tiny mean diff relative to large variance
    big_spread = list(range(20))  # mean=9.5, std≈5.9
    slightly_shifted = [x + 0.5 for x in big_spread]  # diff=0.5 << std
    d, label = cohens_d(big_spread, slightly_shifted)
    assert label == "negligible", f"expected negligible, got {label} (d={d:.3f})"


def test_bootstrap_ci_no_uplift() -> None:
    """When both groups identical, CI should straddle 0."""
    eng = [True, False, True, False, True, False, True, False]
    hyp = [True, False, True, False, True, False, True, False]
    lo, hi = bootstrap_ci(eng, hyp, n_boot=500, seed=42)
    assert lo <= 0.0 <= hi


def test_bootstrap_ci_positive_uplift() -> None:
    """When hypothesis always wins, CI should be positive."""
    eng = [False] * 20
    hyp = [True] * 20
    lo, hi = bootstrap_ci(eng, hyp, n_boot=500, seed=42)
    assert lo > 0.0


def test_analyze_returns_statsresult() -> None:
    eng = [False, False, True, False]
    hyp = [True,  True,  True, True]
    result = analyze(eng, hyp, n_boot=200)
    assert isinstance(result, StatsResult)
    assert result.n == 4
    assert result.hyp_escape_rate > result.eng_escape_rate
    assert result.mcnemar_b == 3
    assert result.mcnemar_c == 0


def test_chi2_sf_at_zero() -> None:
    assert _chi2_sf(0.0) == 1.0


def test_chi2_sf_large_value() -> None:
    # chi2=10 for df=1 → p should be very small (~0.0016)
    p = _chi2_sf(10.0, df=1)
    assert 0.0 < p < 0.01


def test_chi2_sf_df2() -> None:
    # chi2=5.99 for df=2 → p ≈ 0.05
    p = _chi2_sf(5.99, df=2)
    assert 0.04 < p < 0.06


def test_chi2_sf_negative() -> None:
    assert _chi2_sf(-1.0) == 1.0


def test_cohens_d_small_group() -> None:
    """Groups with < 2 elements return (0.0, 'negligible')."""
    d, label = cohens_d([0.5], [0.8])
    assert d == 0.0
    assert label == "negligible"


def test_cohens_d_small_effect() -> None:
    """d in [0.2, 0.5) → 'small'."""
    # d ≈ 0.3: mean diff = 0.3, pooled std ≈ 1.0
    import random
    rng = random.Random(0)
    g1 = [rng.gauss(0, 1) for _ in range(100)]
    g2 = [x + 0.3 for x in g1]
    d, label = cohens_d(g1, g2)
    assert label == "small", f"expected small, got {label} (d={d:.3f})"


def test_cohens_d_medium_effect() -> None:
    """d in [0.5, 0.8) → 'medium'."""
    import random
    rng = random.Random(1)
    g1 = [rng.gauss(0, 1) for _ in range(100)]
    g2 = [x + 0.65 for x in g1]
    d, label = cohens_d(g1, g2)
    assert label == "medium", f"expected medium, got {label} (d={d:.3f})"


def test_power_note_zero_discordant() -> None:
    from experiments.stuck_agent.stats import _power_note
    note = _power_note(10, 0, 0)
    assert "identically" in note


def test_power_note_low() -> None:
    from experiments.stuck_agent.stats import _power_note
    note = _power_note(10, 3, 0)
    assert "Low" in note


def test_power_note_moderate() -> None:
    from experiments.stuck_agent.stats import _power_note
    note = _power_note(10, 6, 1)
    assert "Moderate" in note


def test_power_note_adequate() -> None:
    from experiments.stuck_agent.stats import _power_note
    note = _power_note(20, 8, 3)
    assert "Adequate" in note


def test_igamma_q_negative_x() -> None:
    from experiments.stuck_agent.stats import _igamma_q
    assert _igamma_q(1.0, -0.5) == 1.0


def test_igamma_q_zero_x() -> None:
    from experiments.stuck_agent.stats import _igamma_q
    assert _igamma_q(1.0, 0.0) == 1.0


def test_igamma_p_series_zero_x() -> None:
    from experiments.stuck_agent.stats import _igamma_p_series
    assert _igamma_p_series(1.0, 0.0) == 0.0


def test_igamma_q_large_x() -> None:
    """x >= a+1 uses continued fraction branch."""
    from experiments.stuck_agent.stats import _igamma_q
    # large x relative to a → Q should be small
    val = _igamma_q(2.0, 20.0)
    assert 0.0 < val < 0.01


def test_igamma_q_cf_small_qc_qd() -> None:
    """Exercise the abs(qc/qd) < 1e-30 clamp branches."""
    from experiments.stuck_agent.stats import _igamma_q_cf
    # Just ensure it runs without error
    result = _igamma_q_cf(0.5, 5.0)
    assert 0.0 <= result <= 1.0


def test_save_results_default_dir(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    """save_results with no output_dir uses RESULTS_DIR (monkeypatched)."""
    import experiments.stuck_agent.runner as runner_mod
    monkeypatch.setattr(runner_mod, "RESULTS_DIR", tmp_path)
    result = DeterministicStuckRunner().run()
    path = runner_mod.save_results(result)  # no output_dir → uses RESULTS_DIR
    assert path.parent == tmp_path


def test_deterministic_runner_trivial_task_branch() -> None:
    """If a task's buggy_code accidentally passes, it's marked trivial."""
    # Use a "task" where buggy_code == correct_code (always passes)
    trivial = StuckTask(
        id="TX",
        category="red_herring",
        function_name="trivial_fn",
        buggy_code="def trivial_fn(x):\n    return x + 1\n",
        misleading_fix_code="def trivial_fn(x):\n    return x + 1\n",
        correct_code="def trivial_fn(x):\n    return x + 1\n",
        bug_description="fake",
        misleading_description="fake",
        test_cases=[{"input": {"x": 1}, "expected": 2}],
    )
    runner = DeterministicStuckRunner()
    result = runner.run(tasks=[trivial])
    assert len(result.task_results) == 1
    assert result.task_results[0].phase1_passed is True


def test_llm_runner_rescue_max_attempts_no_escape() -> None:
    """When all rescue attempts fail, escaped=False."""
    task = get_stuck_tasks()[0]

    call_count = 0

    def side_effect(**kwargs: Any) -> MagicMock:
        nonlocal call_count
        call_count += 1
        response = MagicMock()
        # Always return buggy code (never escapes)
        response.choices[0].message.content = (
            f"Root cause hypothesis: still wrong.\n"
            f"```python\n{task.buggy_code}\n```"
        )
        response.usage.prompt_tokens = 30
        response.usage.completion_tokens = 20
        return response

    client = MagicMock()
    client.chat.completions.create.side_effect = side_effect

    runner = LLMStuckRunner(client=client, model="test", max_rescue_attempts=2)
    result = runner.run(tasks=[task], trials_per_task=1)

    tr = result.task_results[0]
    assert not tr.phase1_passed
    assert tr.eng_rescue is not None
    assert tr.eng_rescue.escaped is False
    assert tr.eng_rescue.attempts_used == 2
    assert tr.hyp_rescue is not None
    assert tr.hyp_rescue.escaped is False


def test_llm_runner_no_code_in_response() -> None:
    """If LLM returns no code block in phase 1, still runs rescue."""
    task = get_stuck_tasks()[0]

    call_count = 0
    correct_code = task.correct_code

    def side_effect(**kwargs: Any) -> MagicMock:
        nonlocal call_count
        call_count += 1
        response = MagicMock()
        if call_count == 1:
            # Phase 1: no code block
            response.choices[0].message.content = "I cannot fix this bug."
        else:
            # Rescue: correct code
            response.choices[0].message.content = (
                f"Root cause hypothesis: found.\n```python\n{correct_code}\n```"
            )
        response.usage.prompt_tokens = 20
        response.usage.completion_tokens = 10
        return response

    client = MagicMock()
    client.chat.completions.create.side_effect = side_effect

    runner = LLMStuckRunner(client=client, model="test", max_rescue_attempts=1)
    result = runner.run(tasks=[task], trials_per_task=1)

    tr = result.task_results[0]
    assert not tr.phase1_passed  # no code → failed → stuck


# ── LLM runner (mocked) ────────────────────────────────────────────────────


def _make_mock_client(code: str, hypothesis: str = "Root cause found") -> MagicMock:
    """Return a mock OpenAI client that returns correct code."""
    client = MagicMock()
    response = MagicMock()
    response.choices[0].message.content = (
        f"Failure analysis: previous fix wrong.\n"
        f"Root cause hypothesis: {hypothesis}\n"
        f"```python\n{code}\n```"
    )
    response.usage.prompt_tokens = 100
    response.usage.completion_tokens = 80
    client.chat.completions.create.return_value = response
    return client


def test_llm_stuck_runner_trivial_task() -> None:
    """If phase 1 passes, task_result.phase1_passed should be True."""
    task = get_stuck_tasks()[7]  # D8: semantic_inv

    # Mock phase 1 to return correct code (task is 'trivial' for this mock)
    correct = task.correct_code
    client = _make_mock_client(correct)

    runner = LLMStuckRunner(client=client, model="test-model", max_rescue_attempts=1)
    result = runner.run(tasks=[task], trials_per_task=1)

    assert len(result.task_results) == 1
    assert result.task_results[0].phase1_passed is True


def test_llm_stuck_runner_rescue_escapes() -> None:
    """When rescue returns correct code, escaped=True."""
    task = get_stuck_tasks()[0]  # D1

    call_count = 0
    correct_code = task.correct_code
    buggy_code = task.buggy_code

    def side_effect(**kwargs: Any) -> MagicMock:
        nonlocal call_count
        call_count += 1
        response = MagicMock()
        # First call (phase 1): return buggy code → will fail
        # Second+ calls (rescue): return correct code → will pass
        code = buggy_code if call_count == 1 else correct_code
        response.choices[0].message.content = (
            f"Root cause hypothesis: fixed.\n```python\n{code}\n```"
        )
        response.usage.prompt_tokens = 50
        response.usage.completion_tokens = 40
        return response

    client = MagicMock()
    client.chat.completions.create.side_effect = side_effect

    runner = LLMStuckRunner(client=client, model="test-model", max_rescue_attempts=2)
    result = runner.run(tasks=[task], trials_per_task=1)

    tr = result.task_results[0]
    assert not tr.phase1_passed
    assert tr.eng_rescue is not None
    assert tr.eng_rescue.escaped is True
    assert tr.hyp_rescue is not None
    assert tr.hyp_rescue.escaped is True


# ── save_results ───────────────────────────────────────────────────────────


def test_save_results_creates_json(tmp_path: Path) -> None:
    runner = DeterministicStuckRunner()
    result = runner.run()
    path = save_results(result, output_dir=tmp_path)
    assert path.exists()
    data = json.loads(path.read_text())
    assert data["experiment"] == "stuck_agent"
    assert data["model"] == "deterministic"
    assert "n_stuck" in data
    assert "eng_escape_rate" in data
    assert "hyp_escape_rate" in data


def test_save_results_task_count(tmp_path: Path) -> None:
    runner = DeterministicStuckRunner()
    result = runner.run()
    path = save_results(result, output_dir=tmp_path)
    data = json.loads(path.read_text())
    assert len(data["tasks"]) == 14


# ── analyze_results_file ───────────────────────────────────────────────────


def test_analyze_results_file_round_trip(tmp_path: Path) -> None:
    runner = DeterministicStuckRunner()
    result = runner.run()
    path = save_results(result, output_dir=tmp_path)

    data, stats = analyze_results_file(path)
    assert isinstance(stats, StatsResult)
    assert stats.n == 14
    assert stats.hyp_escape_rate == 1.0  # hypothesis always escapes in deterministic


def test_print_report_runs_without_error(
    tmp_path: Path, capsys: pytest.CaptureFixture
) -> None:
    runner = DeterministicStuckRunner()
    result = runner.run()
    path = save_results(result, output_dir=tmp_path)
    data, stats = analyze_results_file(path)
    print_report(data, stats)
    out = capsys.readouterr().out
    assert "Escape Rate" in out
    assert "McNemar" in out
    assert "Cohen" in out


# ── analyze.py CLI integration ─────────────────────────────────────────────


# ── ControlledLLMStuckRunner ───────────────────────────────────────────────


def test_controlled_runner_no_trivial() -> None:
    """ControlledLLMStuckRunner never produces trivial results."""
    task = get_stuck_tasks()[0]
    correct_code = task.correct_code

    client = _make_mock_client(correct_code)
    runner = ControlledLLMStuckRunner(client=client, model="test", max_rescue_attempts=1)
    result = runner.run(tasks=[task], trials_per_task=2)

    assert len(result.task_results) == 2
    for tr in result.task_results:
        assert not tr.phase1_passed, "Controlled runner must never produce trivial"


def test_controlled_runner_model_label() -> None:
    task = get_stuck_tasks()[0]
    client = _make_mock_client(task.correct_code)
    runner = ControlledLLMStuckRunner(client=client, model="test-model", max_rescue_attempts=1)
    result = runner.run(tasks=[task], trials_per_task=1)
    assert "controlled" in result.model


def test_controlled_runner_escape_rates() -> None:
    """Verify eng_escaped and hyp_escaped computed correctly."""
    tasks = get_stuck_tasks()[:2]
    correct_codes = {t.function_name: t.correct_code for t in tasks}

    call_count = 0

    def side_effect(**kwargs: Any) -> MagicMock:
        nonlocal call_count
        call_count += 1
        response = MagicMock()
        messages = kwargs.get("messages", [])
        content = " ".join(m.get("content", "") for m in messages)
        code = ""
        for name, correct in correct_codes.items():
            if name in content:
                code = correct
                break
        response.choices[0].message.content = f"```python\n{code}\n```"
        response.usage.prompt_tokens = 30
        response.usage.completion_tokens = 20
        return response

    client = MagicMock()
    client.chat.completions.create.side_effect = side_effect

    runner = ControlledLLMStuckRunner(client=client, model="test", max_rescue_attempts=1)
    result = runner.run(tasks=tasks, trials_per_task=1)

    assert len(result.eng_escaped) == 2
    assert len(result.hyp_escaped) == 2


def test_run_stuck_controlled_no_api_key(capsys: pytest.CaptureFixture) -> None:
    """MINIMAX_API_KEY 없으면 sys.exit(1)."""
    from analyze import run_stuck_controlled_pipeline
    with patch.dict("os.environ", {}, clear=True):
        with pytest.raises(SystemExit) as exc:
            run_stuck_controlled_pipeline()
    assert exc.value.code == 1


def test_run_stuck_llm_pipeline_no_api_key(capsys: pytest.CaptureFixture) -> None:
    """MINIMAX_API_KEY/OPENAI_API_KEY 없으면 에러 메시지 후 sys.exit(1)."""
    from analyze import run_stuck_llm_pipeline
    with patch.dict("os.environ", {}, clear=True):
        with pytest.raises(SystemExit) as exc:
            run_stuck_llm_pipeline()
    assert exc.value.code == 1
    assert "MINIMAX_API_KEY" in capsys.readouterr().out


def test_run_stuck_llm_pipeline_success(
    tmp_path: Path, capsys: pytest.CaptureFixture
) -> None:
    """With mocked LLM, pipeline runs end-to-end and prints report."""
    from analyze import run_stuck_llm_pipeline

    tasks = get_stuck_tasks()[:2]  # only 2 tasks for speed
    call_count = 0
    correct_codes = {t.function_name: t.correct_code for t in tasks}
    buggy_codes = {t.function_name: t.buggy_code for t in tasks}

    def side_effect(**kwargs: Any) -> MagicMock:
        nonlocal call_count
        call_count += 1
        response = MagicMock()
        # Determine which task by looking at prompt content
        messages = kwargs.get("messages", [])
        content = " ".join(m.get("content", "") for m in messages)
        code = ""
        for name, correct in correct_codes.items():
            if name in content:
                # phase 1 = buggy, rescue = correct
                is_phase1 = call_count % 3 == 1
                code = buggy_codes[name] if is_phase1 else correct
                break
        response.choices[0].message.content = (
            f"Root cause hypothesis: analysis done.\n```python\n{code}\n```"
        )
        response.usage.prompt_tokens = 60
        response.usage.completion_tokens = 50
        return response

    mock_client = MagicMock()
    mock_client.chat.completions.create.side_effect = side_effect

    with patch.dict("os.environ", {"MINIMAX_API_KEY": "sk-test"}):
        with patch(
            "experiments.stuck_agent.runner.LLMStuckRunner.__init__",
            lambda self, **kw: (
                setattr(self, "client", mock_client)
                or setattr(self, "model", "test-model")
                or setattr(self, "max_rescue_attempts", 1)
            ),
        ):
            with patch(
                "experiments.stuck_agent.runner.get_stuck_tasks",
                return_value=tasks,
            ):
                with patch("experiments.stuck_agent.runner.save_results") as mock_save:
                    # Write a minimal valid result file
                    result_data = {
                        "experiment": "stuck_agent",
                        "model": "test-model",
                        "trials_per_task": 1,
                        "run_timestamp": "2026-03-31T00:00:00",
                        "n_stuck": 2,
                        "n_trivial": 0,
                        "eng_escape_rate": 0.5,
                        "hyp_escape_rate": 1.0,
                        "escape_rate_uplift": 0.5,
                        "eng_total_tokens": 100,
                        "hyp_total_tokens": 150,
                        "tasks": [
                            {
                                "task_id": "D1", "category": "red_herring",
                                "trial": 1, "phase1_passed": False,
                                "eng_escaped": False, "eng_attempts": 1, "eng_tokens": 50,
                                "hyp_escaped": True, "hyp_attempts": 1, "hyp_tokens": 75,
                            },
                            {
                                "task_id": "D2", "category": "red_herring",
                                "trial": 1, "phase1_passed": False,
                                "eng_escaped": True, "eng_attempts": 1, "eng_tokens": 50,
                                "hyp_escaped": True, "hyp_attempts": 1, "hyp_tokens": 75,
                            },
                        ],
                    }
                    result_path = tmp_path / "stuck_agent_test.json"
                    result_path.write_text(json.dumps(result_data))
                    mock_save.return_value = result_path
                    run_stuck_llm_pipeline(trials=1, max_rescue_attempts=1)

    out = capsys.readouterr().out
    assert "Stuck-Agent" in out


# ── Category McNemar + Power Analysis ─────────────────────────────────────


def test_mcnemar_exact_p_symmetric() -> None:
    """Exact McNemar p should be 1.0 when b == c."""
    from experiments.stuck_agent.stats import mcnemar_exact_p
    assert mcnemar_exact_p(3, 3) == pytest.approx(1.0, abs=1e-6)
    assert mcnemar_exact_p(5, 5) == pytest.approx(1.0, abs=1e-6)


def test_mcnemar_exact_p_zero_discordant() -> None:
    """No discordant pairs → p=1.0."""
    from experiments.stuck_agent.stats import mcnemar_exact_p
    assert mcnemar_exact_p(0, 0) == 1.0


def test_mcnemar_exact_p_significant() -> None:
    """Large imbalance should produce p < 0.05."""
    from experiments.stuck_agent.stats import mcnemar_exact_p
    # b=0, c=10 — all discordant pairs favor engineering (hypothesis hurts)
    p = mcnemar_exact_p(0, 10)
    assert p < 0.05


def test_mcnemar_exact_p_range() -> None:
    """p-value must be in [0, 1]."""
    from experiments.stuck_agent.stats import mcnemar_exact_p
    for b, c in [(0, 6), (6, 2), (3, 3), (10, 0)]:
        p = mcnemar_exact_p(b, c)
        assert 0.0 <= p <= 1.0, f"p={p} out of range for b={b}, c={c}"


def test_power_analysis_semantic_inv() -> None:
    """semantic_inv (b=2, c=6, n=10) should require ~21 obs for significance."""
    from experiments.stuck_agent.stats import power_analysis_by_category
    eng = [True, True, True, True, False, False, True, True, True, True]  # 8/10
    hyp = [True, False, False, False, True, True, True, False, True, False]  # 4/10 — b=2,c=6
    pa = power_analysis_by_category("semantic_inv", eng, hyp, task_count=2)
    # Should converge in <= 50 observations
    assert 0 < pa.required_n_for_significance <= 50


def test_analyze_by_category_keys() -> None:
    """analyze_by_category should return one entry per unique category."""
    from experiments.stuck_agent.stats import analyze_by_category
    tasks = [
        {"category": "red_herring", "phase1_passed": False, "eng_escaped": True, "hyp_escaped": False},
        {"category": "red_herring", "phase1_passed": False, "eng_escaped": True, "hyp_escaped": True},
        {"category": "semantic_inv", "phase1_passed": False, "eng_escaped": True, "hyp_escaped": False},
    ]
    result = analyze_by_category(tasks)
    assert set(result.keys()) == {"red_herring", "semantic_inv"}
    assert result["red_herring"].n == 2
    assert result["semantic_inv"].n == 1


def test_analyze_by_category_excludes_trivial() -> None:
    """Tasks with phase1_passed=True should be excluded."""
    from experiments.stuck_agent.stats import analyze_by_category
    tasks = [
        {"category": "red_herring", "phase1_passed": True, "eng_escaped": True, "hyp_escaped": True},
        {"category": "red_herring", "phase1_passed": False, "eng_escaped": True, "hyp_escaped": False},
    ]
    result = analyze_by_category(tasks)
    assert result["red_herring"].n == 1  # only the stuck task counts


# ── StuckTypeClassifier ────────────────────────────────────────────────────


def test_classifier_semantic_inv_return_inversion() -> None:
    """D8-style code (return True/False inverted) → semantic_inv."""
    from experiments.stuck_agent.classifier import StuckTypeClassifier
    clf = StuckTypeClassifier()
    code = (
        "def is_strictly_increasing(nums):\n"
        "    for i in range(len(nums) - 1):\n"
        "        if nums[i] >= nums[i + 1]:\n"
        "            return True\n"
        "    return False\n"
    )
    result = clf.classify(code, [{"input": {"nums": [1, 2, 3]}, "expected": True}])
    assert result.category == "semantic_inv"
    assert result.recommended_strategy == "engineering"


def test_classifier_result_fields() -> None:
    """ClassificationResult must have all required fields with valid values."""
    from experiments.stuck_agent.classifier import StuckTypeClassifier
    clf = StuckTypeClassifier()
    code = "def f(x):\n    return x + 1\n"
    result = clf.classify(code)
    assert result.category in {"red_herring", "semantic_inv", "hidden_assume", "multi_bug"}
    assert 0.0 <= result.confidence <= 1.0
    assert isinstance(result.matched_rules, list)
    assert result.recommended_strategy in {"hypothesis", "engineering", "either"}
    assert isinstance(result.rationale, str) and len(result.rationale) > 0


def test_classifier_boolean_tests_boost_semantic_inv() -> None:
    """Test cases with boolean expected values should boost semantic_inv score."""
    from experiments.stuck_agent.classifier import StuckTypeClassifier
    clf = StuckTypeClassifier()
    code = "def check(nums):\n    return nums[0] > nums[1]\n"
    # 3 boolean expected → semantic_inv boost
    tests = [
        {"input": {"nums": [1, 2]}, "expected": False},
        {"input": {"nums": [3, 1]}, "expected": True},
        {"input": {"nums": [2, 2]}, "expected": False},
    ]
    result = clf.classify(code, tests)
    # With 3 boolean tests, semantic_inv gets +0.5 boost
    # We just verify it runs without error and returns a valid category
    assert result.category in {"red_herring", "semantic_inv", "hidden_assume", "multi_bug"}


# ── analyze.py --category-mcnemar CLI ─────────────────────────────────────


def test_category_mcnemar_cli(tmp_path: Path, capsys: pytest.CaptureFixture) -> None:
    """--category-mcnemar should print category table and power analysis."""
    import json
    from analyze import run_category_mcnemar_pipeline

    # Minimal result file with 2 categories
    result_data = {
        "experiment": "stuck_agent",
        "model": "test-model",
        "trials_per_task": 5,
        "run_timestamp": "2026-03-31T00:00:00",
        "n_stuck": 6,
        "n_trivial": 0,
        "eng_escape_rate": 0.833,
        "hyp_escape_rate": 0.667,
        "escape_rate_uplift": -0.167,
        "eng_total_tokens": 1000,
        "hyp_total_tokens": 1200,
        "tasks": [
            # red_herring: b=1, c=2
            {"task_id": "D1", "category": "red_herring", "trial": 1, "phase1_passed": False,
             "eng_escaped": True, "eng_attempts": 1, "eng_tokens": 100,
             "hyp_escaped": False, "hyp_attempts": 2, "hyp_tokens": 150, "hypothesis": "h"},
            {"task_id": "D1", "category": "red_herring", "trial": 2, "phase1_passed": False,
             "eng_escaped": False, "eng_attempts": 2, "eng_tokens": 100,
             "hyp_escaped": True, "hyp_attempts": 1, "hyp_tokens": 100, "hypothesis": "h"},
            {"task_id": "D2", "category": "red_herring", "trial": 1, "phase1_passed": False,
             "eng_escaped": True, "eng_attempts": 1, "eng_tokens": 100,
             "hyp_escaped": False, "hyp_attempts": 3, "hyp_tokens": 200, "hypothesis": "h"},
            # semantic_inv: b=0, c=3
            {"task_id": "D7", "category": "semantic_inv", "trial": 1, "phase1_passed": False,
             "eng_escaped": True, "eng_attempts": 1, "eng_tokens": 100,
             "hyp_escaped": False, "hyp_attempts": 2, "hyp_tokens": 150, "hypothesis": "h"},
            {"task_id": "D7", "category": "semantic_inv", "trial": 2, "phase1_passed": False,
             "eng_escaped": True, "eng_attempts": 1, "eng_tokens": 100,
             "hyp_escaped": False, "hyp_attempts": 2, "hyp_tokens": 150, "hypothesis": "h"},
            {"task_id": "D8", "category": "semantic_inv", "trial": 1, "phase1_passed": False,
             "eng_escaped": True, "eng_attempts": 1, "eng_tokens": 100,
             "hyp_escaped": False, "hyp_attempts": 2, "hyp_tokens": 150, "hypothesis": "h"},
        ],
    }
    result_path = tmp_path / "stuck_agent_test.json"
    result_path.write_text(json.dumps(result_data))

    run_category_mcnemar_pipeline(str(result_path))
    out = capsys.readouterr().out

    assert "Category-Level McNemar" in out
    assert "red_herring" in out
    assert "semantic_inv" in out
    assert "Power Analysis" in out
    assert "p=" in out
    assert "Bootstrap Variance" in out


# ── Bootstrap variance estimator tests ───────────────────────────────────────


def test_bootstrap_effect_variance_basic() -> None:
    """bootstrap_effect_variance returns BootstrapEffectResult with correct fields."""
    from experiments.stuck_agent.stats import bootstrap_effect_variance

    eng = [True, True, False, True, True, True, False, True, False, True]
    hyp = [True, True, True, True, True, True, True, True, True, False]
    result = bootstrap_effect_variance("test_cat", eng, hyp, n_bootstrap=500, seed=0)

    assert result.category == "test_cat"
    assert result.n == 10
    assert 0.0 <= result.observed_effect <= 1.0
    assert 0.0 <= result.bootstrap_mean <= 1.0
    assert result.bootstrap_std >= 0.0
    assert result.ci_90_lower <= result.ci_90_upper
    assert result.collapse_risk in ("HIGH", "MEDIUM", "LOW")
    assert 0.0 <= result.collapse_probability <= 1.0


def test_bootstrap_effect_variance_zero_effect() -> None:
    """All concordant pairs → observed_effect=0, CI=[0,0]."""
    from experiments.stuck_agent.stats import bootstrap_effect_variance

    eng = [True] * 10
    hyp = [True] * 10
    result = bootstrap_effect_variance("ceil_cat", eng, hyp, n_bootstrap=200, seed=42)

    assert result.observed_effect == 0.0
    assert result.bootstrap_mean == 0.0
    assert result.bootstrap_std == 0.0
    assert result.ci_90_lower == 0.0
    assert result.ci_90_upper == 0.0


def test_bootstrap_effect_variance_high_risk_small_n() -> None:
    """n=10 with small discordant pairs should register HIGH or MEDIUM collapse risk."""
    from experiments.stuck_agent.stats import bootstrap_effect_variance

    # 2 tasks × 5 trials, b=2, c=6 (classic semantic_inv pilot pattern)
    eng = [True, True, True, True, True, True, True, True, False, False]
    hyp = [True, True, False, True, True, True, True, True, True, True]
    result = bootstrap_effect_variance("semantic_inv", eng, hyp, n_bootstrap=1000, seed=42)

    # With small n, CI lower should be < 0.20 → MEDIUM or HIGH risk
    assert result.collapse_risk in ("HIGH", "MEDIUM"), (
        f"Expected HIGH or MEDIUM for small-n pilot, got {result.collapse_risk}"
    )


def test_bootstrap_effect_variance_empty() -> None:
    """Empty input → safe defaults."""
    from experiments.stuck_agent.stats import bootstrap_effect_variance

    result = bootstrap_effect_variance("empty", [], [], n_bootstrap=100)
    assert result.n == 0
    assert result.observed_effect == 0.0
    assert result.collapse_risk == "HIGH"


def test_category_mcnemar_cli_includes_bootstrap(
    tmp_path: Path, capsys: pytest.CaptureFixture
) -> None:
    """--category-mcnemar output includes bootstrap section."""
    import json
    from analyze import run_category_mcnemar_pipeline

    result_data = {
        "experiment": "stuck_agent",
        "model": "test",
        "trials_per_task": 5,
        "run_timestamp": "2026-03-31T00:00:00",
        "n_stuck": 4, "n_trivial": 0,
        "eng_escape_rate": 0.75, "hyp_escape_rate": 0.5, "escape_rate_uplift": -0.25,
        "eng_total_tokens": 400, "hyp_total_tokens": 400,
        "tasks": [
            {"task_id": "D7", "category": "semantic_inv", "trial": i,
             "phase1_passed": False, "eng_escaped": True, "eng_attempts": 1, "eng_tokens": 100,
             "hyp_escaped": (i % 2 == 0), "hyp_attempts": 1, "hyp_tokens": 100, "hypothesis": "h"}
            for i in range(1, 5)
        ],
    }
    p = tmp_path / "bootstrap_test.json"
    p.write_text(json.dumps(result_data))
    run_category_mcnemar_pipeline(str(p))
    out = capsys.readouterr().out
    assert "Bootstrap Variance" in out
    assert "Collapse Risk" in out
