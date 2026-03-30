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
from constants import DebugTaskCategory, RESULTS_DIR
from experiments.hypothesis_validation.tasks import DebugTask, get_debug_tasks


@dataclass(frozen=True)
class LLMTaskResult:
    """Per-task LLM experiment result with pass@1 and attempt statistics."""

    task_id: str
    category: DebugTaskCategory
    trials: int
    engineering_results: list[LLMStrategyResult] = field(default_factory=list)
    hypothesis_results: list[LLMStrategyResult] = field(default_factory=list)

    @property
    def engineering_pass_at_1(self) -> float:
        """엔지니어링 전략의 pass@1 비율."""
        if not self.engineering_results:
            return 0.0
        return sum(1 for r in self.engineering_results if r.solved) / len(self.engineering_results)

    @property
    def hypothesis_pass_at_1(self) -> float:
        """가설 전략의 pass@1 비율."""
        if not self.hypothesis_results:
            return 0.0
        return sum(1 for r in self.hypothesis_results if r.solved) / len(self.hypothesis_results)

    @property
    def engineering_avg_attempts(self) -> float:
        """엔지니어링 전략의 성공한 시도 평균 횟수 (해결 없으면 inf)."""
        solved = [r for r in self.engineering_results if r.solved]
        if not solved:
            return float("inf")
        return sum(r.total_attempts for r in solved) / len(solved)

    @property
    def hypothesis_avg_attempts(self) -> float:
        """가설 전략의 성공한 시도 평균 횟수 (해결 없으면 inf)."""
        solved = [r for r in self.hypothesis_results if r.solved]
        if not solved:
            return float("inf")
        return sum(r.total_attempts for r in solved) / len(solved)

    @property
    def engineering_total_tokens(self) -> int:
        """엔지니어링 전략 전체 토큰 사용량 합계."""
        return sum(
            r.total_input_tokens + r.total_output_tokens
            for r in self.engineering_results
        )

    @property
    def hypothesis_total_tokens(self) -> int:
        """가설 전략 전체 토큰 사용량 합계."""
        return sum(
            r.total_input_tokens + r.total_output_tokens
            for r in self.hypothesis_results
        )


@dataclass(frozen=True)
class LLMExperimentResult:
    """Full LLM experiment result aggregating all task results."""

    task_results: list[LLMTaskResult] = field(default_factory=list)
    model: str = "claude-haiku-4-5-20251001"
    trials_per_task: int = 1
    max_attempts: int = 5
    run_timestamp: str = field(default_factory=lambda: datetime.now().isoformat())

    @property
    def engineering_overall_pass_rate(self) -> float:
        """전체 태스크에 대한 엔지니어링 전략의 평균 pass@1 비율."""
        if not self.task_results:
            return 0.0
        return sum(r.engineering_pass_at_1 for r in self.task_results) / len(
            self.task_results
        )

    @property
    def hypothesis_overall_pass_rate(self) -> float:
        """전체 태스크에 대한 가설 전략의 평균 pass@1 비율."""
        if not self.task_results:
            return 0.0
        return sum(r.hypothesis_pass_at_1 for r in self.task_results) / len(
            self.task_results
        )

    @property
    def engineering_total_tokens(self) -> int:
        """전체 태스크에 대한 엔지니어링 전략 토큰 사용량 합계."""
        return sum(r.engineering_total_tokens for r in self.task_results)

    @property
    def hypothesis_total_tokens(self) -> int:
        """전체 태스크에 대한 가설 전략 토큰 사용량 합계."""
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

    return LLMExperimentResult(
        model=model,
        trials_per_task=trials_per_task,
        max_attempts=max_attempts,
        task_results=[
            LLMTaskResult(
                task_id=task.id,
                category=task.category,
                trials=trials_per_task,
                engineering_results=[eng_strategy.run(task, max_attempts=max_attempts) for _ in range(trials_per_task)],
                hypothesis_results=[hyp_strategy.run(task, max_attempts=max_attempts) for _ in range(trials_per_task)],
            )
            for task in tasks
        ],
    )


def save_llm_results(result: LLMExperimentResult, output_dir: Path | None = None) -> Path:
    """Save LLM experiment results to JSON."""
    if output_dir is None:
        output_dir = RESULTS_DIR
    output_dir.mkdir(exist_ok=True)
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    path = output_dir / f"llm_hypothesis_validation_{ts}.json"

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
    return path
