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
        else:
            print(f"  스텝 수: {len(data.get('steps', []))}")
        print()


if __name__ == "__main__":  # pragma: no cover
    main()
