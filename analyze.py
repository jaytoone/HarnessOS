#!/usr/bin/env python3
"""실험 결과 JSON 파일 분석 및 요약 리포트 출력.

Usage:
  python analyze.py                      # 모든 실험 결과 출력
  python analyze.py --run                # 결정론적 가설 검증 실험 실행 및 분석
  python analyze.py --harness-trend      # 하네스 평가 추이 (cross-run)
  python analyze.py --harness-trend context_memory  # 특정 실험 추이
"""
import argparse
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

    by_category = summary.get("by_category", {})
    if by_category:
        print("  카테고리별 breakdown:")
        for cat in sorted(by_category):
            cs = by_category[cat]
            eng_c = cs.get("engineering_avg_attempts", 0.0)
            hyp_c = cs.get("hypothesis_avg_attempts", 0.0)
            savings_c = cs.get("attempt_savings", 0.0)
            print(
                f"    {cat:10s}: Eng={eng_c:.1f} Hyp={hyp_c:.1f} "
                f"(절약 {savings_c:+.1f})"
            )


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


def show_harness_trend(experiment: str | None = None) -> None:
    """하네스 평가 결과 추이 출력 (cross-run comparison)."""
    from harness_evaluator import HARNESS_EVAL_DIR, HarnessVerdict, compare_runs

    if not HARNESS_EVAL_DIR.exists():
        print(f"하네스 평가 결과 없음: {HARNESS_EVAL_DIR}/")
        print("  먼저 실험을 실행하고 evaluate_harness()로 평가하세요.")
        return

    # 실험 유형 결정
    if experiment:
        pattern = f"{experiment}_eval_*.json"
        exp_names = [experiment]
    else:
        # 모든 실험 유형 자동 감지
        all_files = list(HARNESS_EVAL_DIR.glob("*_eval_*.json"))
        exp_names_set: set[str] = set()
        for f in all_files:
            parts = f.stem.split("_eval_")
            if parts:
                exp_names_set.add(parts[0])
        exp_names = sorted(exp_names_set)

    if not exp_names:
        print("하네스 평가 기록 없음.")
        return

    # 지정 실험 필터 시 실제 파일 존재 여부 확인
    if experiment:
        matching = list(HARNESS_EVAL_DIR.glob(f"{experiment}_eval_*.json"))
        if not matching:
            print(f"'{experiment}' 실험의 하네스 평가 기록 없음.")
            return

    print("=== 하네스 평가 추이 (Cross-Run Comparison) ===\n")

    for exp_name in exp_names:
        paths = sorted(HARNESS_EVAL_DIR.glob(f"{exp_name}_eval_*.json"))
        if not paths:
            continue

        print(f"[{exp_name}] — {len(paths)}개 실행 기록")

        # 직렬화 방식으로 로드
        verdicts: list[HarnessVerdict] = []
        for p in paths:
            data = json.loads(p.read_text())
            verdicts.append(HarnessVerdict(
                experiment=data["experiment"],
                passed=data["passed"],
                score=data["score"],
                success_rate=data["success_rate"],
                avg_duration_ms=data["avg_duration_ms"],
                total_steps=data["total_steps"],
                issues=data.get("issues", []),
                suggestions=data.get("suggestions", []),
                timestamp=data.get("timestamp", ""),
            ))

        for i, v in enumerate(verdicts):
            ts = v.timestamp[:16]
            status = "✓" if v.passed else "✗"
            line = f"  {i+1}. [{ts}] {status} score={v.score:.3f}  rate={v.success_rate:.1%}"
            if i > 0:
                comparison = compare_runs(v, verdicts[i - 1])
                trend_sym = {"improving": "↑", "regressing": "↓", "stable": "→"}[comparison["trend"]]
                line += f"  {trend_sym} Δscore={comparison['delta_score']:+.3f}"
            print(line)

        if len(verdicts) >= 2:
            first, last = verdicts[0], verdicts[-1]
            overall = compare_runs(last, first)
            print(f"  전체 추이: {overall['trend']} | Δscore={overall['delta_score']:+.3f} "
                  f"({len(verdicts)} runs)")
        print()


def run_hypothesis_pipeline() -> None:
    """Run the full deterministic hypothesis validation pipeline.

    Executes: validate_experiment_config → run_experiment → save_results
    → analyze_results + format_report (full research report)
    → evaluate_harness + save_verdict (quality gate).
    """
    from experiments.hypothesis_validation.runner import (
        validate_experiment_config,
        run_experiment,
        save_results,
    )
    from harness_evaluator import evaluate_harness, save_verdict

    print("=== Hypothesis Validation — 전체 파이프라인 실행 ===\n")

    print("[1/4] Pre-mortem 검증...")
    issues = validate_experiment_config()
    if issues:
        for issue in issues:
            print(f"  ❌ {issue.task_id}: {issue.issue}")
        print("검증 실패 — 실험을 중단합니다.")
        sys.exit(1)
    print("  ✓ 모든 태스크 검증 통과\n")

    print("[2/4] 실험 실행 중...")
    result = run_experiment(max_attempts=5)
    path, data = save_results(result)
    print(f"  ✓ {len(result.task_results)}개 태스크 완료 → {path.name}\n")

    print("[3/4] 결과 분석...")
    from experiments.hypothesis_validation.analyzer import analyze_results, format_report
    report = analyze_results(result)
    print(format_report(report))

    print("\n[4/4] 하네스 평가...")
    verdict = evaluate_harness(data)
    save_verdict(verdict)
    status = "✓ PASS" if verdict.passed else "✗ FAIL"
    print(f"  {status}  score={verdict.score:.3f}  issues={len(verdict.issues)}")
    for issue in verdict.issues:
        print(f"  ⚠ {issue}")
    for suggestion in verdict.suggestions:
        print(f"  → {suggestion}")


def main(args_list: list[str] | None = None) -> None:
    parser = argparse.ArgumentParser(description="실험 결과 분석")
    parser.add_argument(
        "--harness-trend",
        nargs="?",
        const="",
        metavar="EXPERIMENT",
        help="하네스 평가 추이 출력 (선택적으로 실험 이름 지정)",
    )
    parser.add_argument(
        "--run",
        action="store_true",
        help="결정론적 가설 검증 실험을 실행하고 분석 출력",
    )
    args = parser.parse_args(args_list)

    if args.harness_trend is not None:
        exp_filter = args.harness_trend or None
        show_harness_trend(exp_filter)
        return

    if args.run:
        run_hypothesis_pipeline()
        return

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
