"""Experiment runner for hypothesis-vs-engineering comparison.

Runs both strategies on all debug tasks. Since strategies now use
deterministic evaluation (no random probability model),
each task is run exactly once per strategy.
"""
from dataclasses import dataclass, field
from experiments.hypothesis_validation.tasks import DebugTask, get_debug_tasks
from experiments.hypothesis_validation.strategies import (
    EngineeringStrategy,
    HypothesisStrategy,
    StrategyResult,
)


@dataclass
class TaskResult:
    task_id: str
    category: str
    engineering_result: StrategyResult | None = None
    hypothesis_result: StrategyResult | None = None


@dataclass
class ExperimentResult:
    task_results: list[TaskResult] = field(default_factory=list)
    max_attempts: int = 5


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
        tr = TaskResult(task_id=task.id, category=task.category)
        tr.engineering_result = eng.run(task, max_attempts)
        tr.hypothesis_result = hyp.run(task, max_attempts)
        result.task_results.append(tr)

    return result
