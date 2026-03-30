"""LLM experiment runner — real Claude API calls.

Runs both LLM strategies (engineering vs hypothesis) on debug tasks.
Supports multiple trials per task for statistical validity (pass@k).
"""
import json
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path

from anthropic import Anthropic

from experiments.hypothesis_validation.llm_strategies import (
    LLMEngineeringStrategy,
    LLMHypothesisStrategy,
    LLMStrategyResult,
)
from experiments.hypothesis_validation.tasks import DebugTask, get_debug_tasks


@dataclass
class LLMTaskResult:
    task_id: str
    category: str
    trials: int
    engineering_results: list[LLMStrategyResult] = field(default_factory=list)
    hypothesis_results: list[LLMStrategyResult] = field(default_factory=list)

    @property
    def engineering_pass_at_1(self) -> float:
        if not self.engineering_results:
            return 0.0
        return sum(1 for r in self.engineering_results if r.solved) / len(self.engineering_results)

    @property
    def hypothesis_pass_at_1(self) -> float:
        if not self.hypothesis_results:
            return 0.0
        return sum(1 for r in self.hypothesis_results if r.solved) / len(self.hypothesis_results)

    @property
    def engineering_avg_attempts(self) -> float:
        solved = [r for r in self.engineering_results if r.solved]
        if not solved:
            return float("inf")
        return sum(r.total_attempts for r in solved) / len(solved)

    @property
    def hypothesis_avg_attempts(self) -> float:
        solved = [r for r in self.hypothesis_results if r.solved]
        if not solved:
            return float("inf")
        return sum(r.total_attempts for r in solved) / len(solved)

    @property
    def engineering_total_tokens(self) -> int:
        return sum(
            r.total_input_tokens + r.total_output_tokens
            for r in self.engineering_results
        )

    @property
    def hypothesis_total_tokens(self) -> int:
        return sum(
            r.total_input_tokens + r.total_output_tokens
            for r in self.hypothesis_results
        )


@dataclass
class LLMExperimentResult:
    task_results: list[LLMTaskResult] = field(default_factory=list)
    model: str = "claude-haiku-4-5-20251001"
    trials_per_task: int = 1
    max_attempts: int = 5
    run_timestamp: str = field(default_factory=lambda: datetime.now().isoformat())

    @property
    def engineering_overall_pass_rate(self) -> float:
        if not self.task_results:
            return 0.0
        return sum(r.engineering_pass_at_1 for r in self.task_results) / len(
            self.task_results
        )

    @property
    def hypothesis_overall_pass_rate(self) -> float:
        if not self.task_results:
            return 0.0
        return sum(r.hypothesis_pass_at_1 for r in self.task_results) / len(
            self.task_results
        )

    @property
    def engineering_total_tokens(self) -> int:
        return sum(r.engineering_total_tokens for r in self.task_results)

    @property
    def hypothesis_total_tokens(self) -> int:
        return sum(r.hypothesis_total_tokens for r in self.task_results)


def run_llm_experiment(
    tasks: list[DebugTask] | None = None,
    model: str = "claude-haiku-4-5-20251001",
    trials_per_task: int = 1,
    max_attempts: int = 5,
    client: Anthropic | None = None,
) -> LLMExperimentResult:
    """Run real LLM-based strategy comparison.

    Args:
        tasks: Tasks to run. Defaults to all 12 debug tasks.
        model: Claude model to use.
        trials_per_task: Number of independent trials per task (for pass@k).
        max_attempts: Max fix attempts per trial.
        client: Anthropic client (injectable for testing).
    """
    if tasks is None:
        tasks = get_debug_tasks()
    client = client or Anthropic()

    eng_strategy = LLMEngineeringStrategy(client=client, model=model)
    hyp_strategy = LLMHypothesisStrategy(client=client, model=model)

    result = LLMExperimentResult(
        model=model,
        trials_per_task=trials_per_task,
        max_attempts=max_attempts,
    )

    for task in tasks:
        task_result = LLMTaskResult(
            task_id=task.id,
            category=task.category,
            trials=trials_per_task,
        )

        for _ in range(trials_per_task):
            task_result.engineering_results.append(
                eng_strategy.run(task, max_attempts=max_attempts)
            )
            task_result.hypothesis_results.append(
                hyp_strategy.run(task, max_attempts=max_attempts)
            )

        result.task_results.append(task_result)

    return result


def save_llm_results(result: LLMExperimentResult, output_dir: str = "results") -> str:
    """Save LLM experiment results to JSON."""
    Path(output_dir).mkdir(exist_ok=True)
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    path = Path(output_dir) / f"llm_hypothesis_validation_{ts}.json"

    # Convert to serializable dict (skip complex nested objects, keep key stats)
    data = {
        "experiment": "llm_hypothesis_validation",
        "model": result.model,
        "trials_per_task": result.trials_per_task,
        "max_attempts": result.max_attempts,
        "run_timestamp": result.run_timestamp,
        "engineering_overall_pass_rate": result.engineering_overall_pass_rate,
        "hypothesis_overall_pass_rate": result.hypothesis_overall_pass_rate,
        "engineering_total_tokens": result.engineering_total_tokens,
        "hypothesis_total_tokens": result.hypothesis_total_tokens,
        "tasks": [
            {
                "task_id": tr.task_id,
                "category": tr.category,
                "engineering_pass_at_1": tr.engineering_pass_at_1,
                "hypothesis_pass_at_1": tr.hypothesis_pass_at_1,
                "engineering_avg_attempts": tr.engineering_avg_attempts,
                "hypothesis_avg_attempts": tr.hypothesis_avg_attempts,
                "engineering_total_tokens": tr.engineering_total_tokens,
                "hypothesis_total_tokens": tr.hypothesis_total_tokens,
            }
            for tr in result.task_results
        ],
    }
    def _finite(v: float) -> float | None:
        """Replace float infinity with None for RFC-compliant JSON output."""
        return None if v == float("inf") or v == float("-inf") else v

    for task_dict in data["tasks"]:
        task_dict["engineering_avg_attempts"] = _finite(task_dict["engineering_avg_attempts"])
        task_dict["hypothesis_avg_attempts"] = _finite(task_dict["hypothesis_avg_attempts"])

    path.write_text(json.dumps(data, indent=2))
    return str(path)
