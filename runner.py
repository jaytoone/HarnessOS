#!/usr/bin/env python3
"""
LLM 장기 컨텍스트 실험 실행기.
Usage:
  python runner.py --exp a   # 실험 A: 기억력 저하
  python runner.py --exp b   # 실험 B: 코딩 실수 시점
"""
import argparse
import asyncio
import json
from datetime import datetime
from typing import Any

from dotenv import load_dotenv
load_dotenv()

from constants import CONTEXT_LENGTHS, POSITIONS, REPEATS, DEFAULT_MODEL, RESULTS_DIR, ExperimentName
from dashboard import Dashboard, DashboardState
from experiments.context_memory.tasks import build_recall_prompt
from experiments.context_memory.evaluator import evaluate_recall
from experiments.coding_failure.tasks import get_coding_tasks
from experiments.coding_failure.evaluator import run_openhands_task, detect_failure_inflection, StepResult


async def run_experiment_a() -> None:
    """실험 A: Lost-in-the-Middle 기억력 저하 측정."""
    total = len(CONTEXT_LENGTHS) * len(POSITIONS) * REPEATS
    state = DashboardState(experiment="A - 기억력 저하", total_steps=total)
    all_results: list[dict[str, Any]] = []
    step = 0

    with Dashboard(state) as dash:
        for ctx_len in CONTEXT_LENGTHS:
            for position in POSITIONS:
                for rep in range(REPEATS):
                    step += 1
                    prompt, expected = build_recall_prompt(
                        context_tokens=ctx_len, position=position
                    )
                    result = await evaluate_recall(
                        prompt=prompt,
                        expected=expected,
                        context_tokens=ctx_len,
                        position=position,
                    )
                    row: dict[str, Any] = {
                        "step": step,
                        "context_tokens": ctx_len,
                        "position": position,
                        "repeat": rep + 1,
                        "status": "success" if result.is_correct else "failure",
                        "expected": result.expected,
                        "got": result.got,
                        "duration_ms": result.duration_ms,
                        "task": f"{ctx_len}tok/{position}/rep{rep+1}",
                    }
                    all_results.append(row)
                    dash.add_result(row)

    _save_results("context_memory", all_results)
    print(f"\n실험 A 완료: {sum(1 for r in all_results if r['status']=='success')}/{total} 성공")


async def run_experiment_b() -> None:
    """실험 B: OpenHands 코딩 실수 시점 측정."""
    tasks = get_coding_tasks()
    state = DashboardState(experiment="B - 코딩 실수 시점", total_steps=len(tasks))
    all_results: list[dict[str, Any]] = []

    with Dashboard(state) as dash:
        for task in tasks:
            result = await run_openhands_task(task.step, task.prompt)
            row: dict[str, Any] = {
                "step": result.step,
                "status": result.status,
                "context_tokens": result.context_tokens,
                "duration_ms": result.duration_ms,
                "error": result.error,
                "task": task.prompt[:60],
                "category": task.category,
            }
            all_results.append(row)
            dash.add_result(row)

    step_results = [
        StepResult(
            step=r["step"],
            status=r["status"],
            context_tokens=r["context_tokens"],
            duration_ms=r["duration_ms"],
            error=r["error"],
        )
        for r in all_results
    ]
    inflection = detect_failure_inflection(step_results)

    summary: dict[str, Any] = {
        "total_steps": len(tasks),
        "success_rate": sum(1 for r in all_results if r["status"] == "success") / len(tasks),
        "failure_inflection_step": inflection,
        "failure_inflection_tokens": next(
            (r["context_tokens"] for r in all_results if r["step"] == inflection), None
        ) if inflection else None,
    }
    _save_results("coding_failure", all_results, summary=summary)
    print(f"\n실험 B 완료. 실패 급증 시점: 스텝 {inflection}")


def _save_results(name: ExperimentName, steps: list[dict[str, Any]], summary: dict[str, Any] | None = None) -> None:
    """결과를 RESULTS_DIR/{name}_{timestamp}.json 으로 저장. summary 없으면 빈 dict."""
    RESULTS_DIR.mkdir(exist_ok=True)
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    path = RESULTS_DIR / f"{name}_{ts}.json"
    data: dict[str, Any] = {
        "experiment": name,
        "model": DEFAULT_MODEL,
        "timestamp": datetime.now().isoformat(),
        "steps": steps,
        "summary": summary or {},
    }
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2))
    print(f"결과 저장: {path}")


def main() -> None:
    """CLI 진입점: --exp 인자로 실험 A(기억력) 또는 B(코딩실수)를 선택해 실행."""
    parser = argparse.ArgumentParser(description="LLM 장기 컨텍스트 실험")
    parser.add_argument("--exp", choices=["a", "b"], required=True, help="실험 선택: a=기억력, b=코딩실수")
    args = parser.parse_args()

    if args.exp == "a":
        asyncio.run(run_experiment_a())
    else:
        asyncio.run(run_experiment_b())


if __name__ == "__main__":  # pragma: no cover
    main()