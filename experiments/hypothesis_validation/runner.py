"""Experiment runner for hypothesis-vs-engineering comparison.

Runs both strategies on all debug tasks. Since strategies now use
deterministic evaluation (no random probability model),
each task is run exactly once per strategy.

Pipeline:
  validate_experiment_config()  ← pre-mortem (P1-2)
  run_experiment()               ← deterministic execution
  save_results()                 ← persist to results/ JSON
  to_harness_format()            ← convert for harness evaluator
  evaluate_harness()             ← optional auto-quality-check
"""
import json
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Any

from constants import RESULTS_DIR

from experiments.hypothesis_validation.strategies import (
    EngineeringStrategy,
    HypothesisStrategy,
    StrategyResult,
    _execute_attempt,
)
from experiments.hypothesis_validation.tasks import DebugTask, get_debug_tasks


@dataclass(frozen=True)
class ConfigIssue:
    """A configuration validation issue for a specific task."""

    task_id: str
    issue: str


@dataclass(frozen=True)
class TaskResult:
    """Paired engineering and hypothesis strategy results for a single task."""

    task_id: str
    category: str
    engineering_result: StrategyResult | None = None
    hypothesis_result: StrategyResult | None = None


@dataclass
class ExperimentResult:
    task_results: list[TaskResult] = field(default_factory=list)
    max_attempts: int = 5


# ---------------------------------------------------------------------------
# Pre-mortem validation (P1-2)
# ---------------------------------------------------------------------------


def validate_experiment_config(
    tasks: list[DebugTask] | None = None,
) -> list[ConfigIssue]:
    """Pre-mortem check: validate tasks before running the experiment.

    Checks:
    - Each task has at least one test case
    - Each task's correct_code actually passes all test cases
    - Each task's buggy_code fails at least one test case

    Returns a list of ConfigIssues (empty = all clear).
    """
    if tasks is None:
        tasks = get_debug_tasks()

    issues: list[ConfigIssue] = []

    for task in tasks:
        if not task.test_cases:
            issues.append(ConfigIssue(task.id, "no test cases defined"))
            continue

        # Correct code must pass all tests
        _, _, correct_passes = _execute_attempt(
            task.correct_code, task.function_name, task.test_cases
        )
        if not correct_passes:
            issues.append(
                ConfigIssue(task.id, "correct_code fails test cases — task definition error")
            )

        # Buggy code should fail at least one test
        passed, total, buggy_all_pass = _execute_attempt(
            task.buggy_code, task.function_name, task.test_cases
        )
        if buggy_all_pass:
            issues.append(
                ConfigIssue(
                    task.id,
                    f"buggy_code passes all {total} tests — bug may not be testable",
                )
            )

    return issues


# ---------------------------------------------------------------------------
# Core runner
# ---------------------------------------------------------------------------


def run_experiment(
    tasks: list[DebugTask] | None = None,
    max_attempts: int = 5,
) -> ExperimentResult:
    """Run both strategies on all tasks.

    Each task is run once per strategy (deterministic -- no Monte Carlo needed).
    """
    if tasks is None:
        tasks = get_debug_tasks()

    eng = EngineeringStrategy()
    hyp = HypothesisStrategy()
    result = ExperimentResult(max_attempts=max_attempts)

    for task in tasks:
        result.task_results.append(TaskResult(
            task_id=task.id,
            category=task.category,
            engineering_result=eng.run(task, max_attempts),
            hypothesis_result=hyp.run(task, max_attempts),
        ))

    return result


# ---------------------------------------------------------------------------
# Harness format bridge
# ---------------------------------------------------------------------------


def to_harness_format(result: ExperimentResult) -> dict[str, Any]:
    """Convert ExperimentResult to the harness_evaluator step format.

    Maps each (task, strategy) pair to a harness "step" so that
    evaluate_harness() can assess experiment quality automatically.
    """
    steps: list[dict[str, Any]] = []

    eng_solved = 0
    hyp_solved = 0
    eng_total_attempts = 0
    hyp_total_attempts = 0
    task_count = len(result.task_results)

    # Single pass: build steps and accumulate overall + per-category stats
    by_category: dict[str, dict[str, Any]] = {}
    for tr in result.task_results:
        cat = tr.category
        if cat not in by_category:
            by_category[cat] = {
                "eng_attempts": [], "hyp_attempts": [],
                "eng_solved": 0, "hyp_solved": 0, "count": 0,
            }
        entry = by_category[cat]
        entry["count"] += 1

        if tr.engineering_result is not None:
            eng_r = tr.engineering_result
            steps.append({
                "task_id": tr.task_id,
                "category": cat,
                "strategy": "engineering",
                "status": "success" if eng_r.solved else "failure",
                "attempts": eng_r.total_attempts,
                "duration_ms": 0,  # deterministic — no wall-clock time
            })
            if eng_r.solved:
                eng_solved += 1
                eng_total_attempts += eng_r.total_attempts
                entry["eng_solved"] += 1
                entry["eng_attempts"].append(eng_r.total_attempts)

        if tr.hypothesis_result is not None:
            hyp_r = tr.hypothesis_result
            steps.append({
                "task_id": tr.task_id,
                "category": cat,
                "strategy": "hypothesis",
                "status": "success" if hyp_r.solved else "failure",
                "attempts": hyp_r.total_attempts,
                "duration_ms": 0,
            })
            if hyp_r.solved:
                hyp_solved += 1
                hyp_total_attempts += hyp_r.total_attempts
                entry["hyp_solved"] += 1
                entry["hyp_attempts"].append(hyp_r.total_attempts)

    category_stats: dict[str, dict[str, Any]] = {}
    for cat, entry in by_category.items():
        eng_avg_cat = (
            sum(entry["eng_attempts"]) / len(entry["eng_attempts"])
            if entry["eng_attempts"] else 0.0
        )
        hyp_avg_cat = (
            sum(entry["hyp_attempts"]) / len(entry["hyp_attempts"])
            if entry["hyp_attempts"] else 0.0
        )
        category_stats[cat] = {
            "count": entry["count"],
            "engineering_solved": entry["eng_solved"],
            "hypothesis_solved": entry["hyp_solved"],
            "engineering_avg_attempts": round(eng_avg_cat, 2),
            "hypothesis_avg_attempts": round(hyp_avg_cat, 2),
            "attempt_savings": round(eng_avg_cat - hyp_avg_cat, 2),
        }

    summary: dict[str, Any] = {
        "task_count": task_count,
        "engineering_solved": eng_solved,
        "hypothesis_solved": hyp_solved,
        "engineering_avg_attempts": (
            eng_total_attempts / eng_solved if eng_solved else 0.0
        ),
        "hypothesis_avg_attempts": (
            hyp_total_attempts / hyp_solved if hyp_solved else 0.0
        ),
        "by_category": category_stats,
    }

    return {
        "experiment": "hypothesis_validation",
        "steps": steps,
        "summary": summary,
    }


def save_results(
    result: ExperimentResult,
    output_dir: Path | None = None,
    model: str = "deterministic",
) -> tuple[Path, dict[str, Any]]:
    """Persist ExperimentResult to a JSON file in results/.

    The saved format matches what analyze.py expects for hypothesis_validation:
    {experiment, model, timestamp, steps, summary}.

    Args:
        result: The experiment result to save.
        output_dir: Directory to save to (defaults to RESULTS_DIR).
        model: Label for the 'model' field (deterministic for researcher-coded runs).

    Returns:
        (path, data) — path to saved JSON file and the harness-format data dict.
        Returning data avoids a redundant to_harness_format() call in callers.
    """
    if output_dir is None:
        output_dir = RESULTS_DIR
    output_dir.mkdir(parents=True, exist_ok=True)

    data = to_harness_format(result)
    data["model"] = model
    data["timestamp"] = datetime.now().isoformat()

    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    path = output_dir / f"hypothesis_validation_{ts}.json"
    path.write_text(json.dumps(data, indent=2))
    return path, data
