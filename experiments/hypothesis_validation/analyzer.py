"""Analyze hypothesis-vs-engineering experiment results.

Adapted for deterministic exec-based evaluation (no Monte Carlo).
Each task has exactly one engineering and one hypothesis result.
"""
from dataclasses import dataclass, field
from experiments.hypothesis_validation.runner import ExperimentResult, TaskResult


@dataclass
class CategoryStats:
    category: str
    eng_solved: int
    eng_total: int
    hyp_solved: int
    hyp_total: int
    eng_success_rate: float
    hyp_success_rate: float
    eng_avg_attempts: float
    hyp_avg_attempts: float
    advantage: float  # hyp_success_rate - eng_success_rate
    attempt_savings: float = 0.0  # eng_avg_attempts - hyp_avg_attempts


@dataclass
class TaskDetail:
    task_id: str
    category: str
    eng_solved: bool
    eng_attempts: int
    hyp_solved: bool
    hyp_attempts: int
    hypothesis_text: str = ""


@dataclass
class AnalysisReport:
    category_stats: list[CategoryStats] = field(default_factory=list)
    task_details: list[TaskDetail] = field(default_factory=list)
    overall_eng_success: float = 0.0
    overall_hyp_success: float = 0.0
    overall_eng_avg_attempts: float = 0.0
    overall_hyp_avg_attempts: float = 0.0
    best_advantage_category: str = ""
    best_advantage_value: float = 0.0
    hypothesis_first_accuracy: float = 0.0


def analyze_results(result: ExperimentResult) -> AnalysisReport:
    """Analyze experiment results and produce a report."""
    report = AnalysisReport()

    # Collect task details
    for tr in result.task_results:
        eng = tr.engineering_result
        hyp = tr.hypothesis_result
        hyp_text = ""
        if hyp and hyp.attempts:
            hyp_text = hyp.attempts[0].hypothesis or ""

        detail = TaskDetail(
            task_id=tr.task_id,
            category=tr.category,
            eng_solved=eng.solved if eng else False,
            eng_attempts=eng.total_attempts if eng else 0,
            hyp_solved=hyp.solved if hyp else False,
            hyp_attempts=hyp.total_attempts if hyp else 0,
            hypothesis_text=hyp_text,
        )
        report.task_details.append(detail)

    # Group by category
    by_category: dict[str, list[TaskResult]] = {}
    for tr in result.task_results:
        by_category.setdefault(tr.category, []).append(tr)

    total_eng_solved = 0
    total_hyp_solved = 0
    total_tasks = 0
    total_eng_attempts = 0
    total_hyp_attempts = 0
    total_first_correct = 0
    total_first_hypotheses = 0

    for cat in ["simple", "causal", "assumption"]:
        task_results = by_category.get(cat, [])
        eng_solved = 0
        hyp_solved = 0
        eng_attempts_sum = 0
        hyp_attempts_sum = 0
        count = len(task_results)

        for tr in task_results:
            eng = tr.engineering_result
            hyp = tr.hypothesis_result
            if eng and eng.solved:
                eng_solved += 1
            if hyp and hyp.solved:
                hyp_solved += 1
            eng_attempts_sum += eng.total_attempts if eng else 0
            hyp_attempts_sum += hyp.total_attempts if hyp else 0

            # First hypothesis accuracy
            if hyp and hyp.attempts:
                first = hyp.attempts[0]
                if first.hypothesis_correct is not None:
                    total_first_hypotheses += 1
                    if first.hypothesis_correct:
                        total_first_correct += 1

        eng_sr = eng_solved / count if count > 0 else 0.0
        hyp_sr = hyp_solved / count if count > 0 else 0.0
        eng_aa = eng_attempts_sum / count if count > 0 else 0.0
        hyp_aa = hyp_attempts_sum / count if count > 0 else 0.0

        stats = CategoryStats(
            category=cat,
            eng_solved=eng_solved,
            eng_total=count,
            hyp_solved=hyp_solved,
            hyp_total=count,
            eng_success_rate=eng_sr,
            hyp_success_rate=hyp_sr,
            eng_avg_attempts=eng_aa,
            hyp_avg_attempts=hyp_aa,
            advantage=hyp_sr - eng_sr,
            attempt_savings=eng_aa - hyp_aa,
        )
        report.category_stats.append(stats)

        total_eng_solved += eng_solved
        total_hyp_solved += hyp_solved
        total_tasks += count
        total_eng_attempts += eng_attempts_sum
        total_hyp_attempts += hyp_attempts_sum

    report.overall_eng_success = total_eng_solved / total_tasks if total_tasks > 0 else 0.0
    report.overall_hyp_success = total_hyp_solved / total_tasks if total_tasks > 0 else 0.0
    report.overall_eng_avg_attempts = total_eng_attempts / total_tasks if total_tasks > 0 else 0.0
    report.overall_hyp_avg_attempts = total_hyp_attempts / total_tasks if total_tasks > 0 else 0.0

    if report.category_stats:
        best = max(report.category_stats, key=lambda s: s.attempt_savings)
        report.best_advantage_category = best.category
        report.best_advantage_value = best.attempt_savings

    if total_first_hypotheses > 0:
        report.hypothesis_first_accuracy = total_first_correct / total_first_hypotheses

    return report


def format_report(report: AnalysisReport) -> str:
    """Format analysis report as readable text."""
    lines: list[str] = []
    lines.append("=== Hypothesis vs Engineering Experiment Results ===")
    lines.append("(Deterministic exec-based evaluation, no probability model)\n")

    lines.append(
        f"Overall:  Engineering={report.overall_eng_success:.1%} "
        f"(avg {report.overall_eng_avg_attempts:.1f} attempts)  "
        f"Hypothesis={report.overall_hyp_success:.1%} "
        f"(avg {report.overall_hyp_avg_attempts:.1f} attempts)\n"
    )

    lines.append(
        f"{'Category':<12} {'Eng':>6} {'Hyp':>6} {'Eng Att':>8} "
        f"{'Hyp Att':>8} {'Savings':>8}"
    )
    lines.append("-" * 55)
    for s in report.category_stats:
        lines.append(
            f"{s.category:<12} "
            f"{s.eng_solved}/{s.eng_total:>2}   "
            f"{s.hyp_solved}/{s.hyp_total:>2}   "
            f"{s.eng_avg_attempts:>7.1f} "
            f"{s.hyp_avg_attempts:>7.1f} "
            f"{s.attempt_savings:>+7.1f}"
        )

    lines.append("")
    lines.append("--- Per-Task Details ---")
    for d in report.task_details:
        eng_mark = "PASS" if d.eng_solved else "FAIL"
        hyp_mark = "PASS" if d.hyp_solved else "FAIL"
        lines.append(
            f"  {d.task_id} ({d.category}): "
            f"Eng={eng_mark} ({d.eng_attempts} att) | "
            f"Hyp={hyp_mark} ({d.hyp_attempts} att)"
        )
        if d.hypothesis_text:
            lines.append(f"    Hypothesis: {d.hypothesis_text}")

    lines.append("")
    lines.append(
        f"Best attempt savings category: {report.best_advantage_category} "
        f"({report.best_advantage_value:+.1f} attempts)"
    )
    lines.append(f"First hypothesis accuracy: {report.hypothesis_first_accuracy:.1%}")

    return "\n".join(lines)
