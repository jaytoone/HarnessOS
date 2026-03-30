#!/usr/bin/env python3
"""실험 결과 JSON 파일 분석 및 요약 리포트 출력."""
import json
import sys
from pathlib import Path
from constants import RESULTS_DIR


def analyze_context_memory(data: dict) -> None:
    steps = data["steps"]
    total = len(steps)
    if total == 0:
        print("  (no steps)")
        return

    success = sum(1 for s in steps if s["status"] == "success")
    print(f"  총 {total}회 | 성공 {success}/{total} ({success/total*100:.1f}%)")

    by_position: dict[str, list[bool]] = {}
    by_ctx: dict[int, list[bool]] = {}
    for s in steps:
        pos = s.get("position", "unknown")
        ctx = s.get("context_tokens", 0)
        hit = s["status"] == "success"
        by_position.setdefault(pos, []).append(hit)
        by_ctx.setdefault(ctx, []).append(hit)

    print("  위치별 정확도:")
    for pos in sorted(by_position):
        hits = by_position[pos]
        print(f"    {pos:8s}: {sum(hits)}/{len(hits)} ({sum(hits)/len(hits)*100:.0f}%)")

    print("  컨텍스트 길이별 정확도:")
    for ctx in sorted(by_ctx):
        hits = by_ctx[ctx]
        label = f"{ctx:,}tok"
        print(f"    {label:10s}: {sum(hits)}/{len(hits)} ({sum(hits)/len(hits)*100:.0f}%)")


def analyze_coding_failure(data: dict) -> None:
    steps = data["steps"]
    total = len(steps)
    if total == 0:
        print("  (no steps)")
        return

    success = sum(1 for s in steps if s["status"] == "success")
    print(f"  총 {total}회 | 성공 {success}/{total} ({success/total*100:.1f}%)")

    summary = data.get("summary", {})
    if summary.get("failure_inflection_step"):
        print(f"  실패 급증 시점: 스텝 {summary['failure_inflection_step']}"
              f" ({summary.get('failure_inflection_tokens', '?')} 토큰)")
    else:
        print("  실패 급증 시점: 감지되지 않음")


def analyze_hypothesis_validation(data: dict) -> None:
    steps = data["steps"]
    total = len(steps)
    if total == 0:
        print("  (no steps)")
        return

    summary = data.get("summary", {})
    eng_solved = summary.get("engineering_solved", "?")
    hyp_solved = summary.get("hypothesis_solved", "?")
    task_count = summary.get("task_count", total // 2)
    eng_avg = summary.get("engineering_avg_attempts", 0.0)
    hyp_avg = summary.get("hypothesis_avg_attempts", 0.0)

    print(f"  태스크 {task_count}개 | Engineering: {eng_solved}/{task_count} 해결 (평균 {eng_avg:.1f} 시도)")
    print(f"               Hypothesis:  {hyp_solved}/{task_count} 해결 (평균 {hyp_avg:.1f} 시도)")
    if eng_avg > 0 and hyp_avg > 0:
        savings = eng_avg - hyp_avg
        print(f"  Hypothesis 이점: {savings:+.1f} 시도 절약 ({savings/eng_avg*100:.0f}% 효율)")


def analyze_llm_hypothesis(data: dict) -> None:
    tasks = data.get("tasks", [])
    if not tasks:
        print("  (no tasks)")
        return

    model = data.get("model", "?")
    trials = data.get("trials_per_task", 1)
    eng_pass = data.get("engineering_overall_pass_rate", 0.0)
    hyp_pass = data.get("hypothesis_overall_pass_rate", 0.0)
    eng_tok = data.get("engineering_total_tokens", 0)
    hyp_tok = data.get("hypothesis_total_tokens", 0)

    print(f"  모델: {model}  |  trial/task: {trials}")
    print(f"  Engineering pass@1: {eng_pass:.1%}  |  토큰: {eng_tok:,}")
    print(f"  Hypothesis  pass@1: {hyp_pass:.1%}  |  토큰: {hyp_tok:,}")
    if eng_tok > 0 and hyp_tok > 0:
        tok_diff = hyp_tok - eng_tok
        print(f"  토큰 오버헤드 (Hypothesis): {tok_diff:+,} ({tok_diff/eng_tok*100:+.1f}%)")


def main() -> None:
    paths = sorted(RESULTS_DIR.glob("*.json")) if RESULTS_DIR.exists() else []

    if not paths:
        print(f"결과 파일 없음: {RESULTS_DIR}/")
        sys.exit(0)

    print(f"=== 실험 결과 분석 ({len(paths)}개 파일) ===\n")

    for path in paths:
        data = json.loads(path.read_text())
        exp = data.get("experiment", "unknown")
        ts = data.get("timestamp", "?")[:16]
        model = data.get("model", "?")
        print(f"[{path.name}]")
        print(f"  실험: {exp}  모델: {model}  시각: {ts}")

        if "context_memory" in exp:
            analyze_context_memory(data)
        elif "coding_failure" in exp:
            analyze_coding_failure(data)
        elif "llm_hypothesis" in exp or "llm_hypothesis_validation" in path.name:
            analyze_llm_hypothesis(data)
        elif "hypothesis_validation" in exp:
            analyze_hypothesis_validation(data)
        else:
            print(f"  스텝 수: {len(data.get('steps', []))}")
        print()


if __name__ == "__main__":  # pragma: no cover
    main()
