"""A/B Test Framework for Skill Patch Injection.

Compares live-inf convergence behavior:
  A (control):   static skill prompts (no patches)
  B (treatment): experience-based skill patch injection (.omc/skill-patches/)

Source: experiments/stuck_agent/evolving_orchestration_design.md
Paper:  arxiv:2604.00901 — Experience as a Compass

Usage:
  # Record a result (call after each /live-inf run)
  python3 scripts/ab_test_skill_patch.py record --condition control --score 0.82 --iters 3 --goal "..."
  python3 scripts/ab_test_skill_patch.py record --condition treatment --score 0.91 --iters 2 --goal "..."

  # Analyze results
  python3 scripts/ab_test_skill_patch.py analyze

  # Toggle control mode (disables skill patches for next run)
  python3 scripts/ab_test_skill_patch.py disable-patches
  python3 scripts/ab_test_skill_patch.py enable-patches
"""
from __future__ import annotations

import argparse
import json
import shutil
from datetime import datetime
from pathlib import Path
from statistics import mean, stdev


RESULTS_FILE = Path(".omc/ab_test_results.jsonl")
PATCH_DIR = Path(".omc/skill-patches")
PATCH_DIR_DISABLED = Path(".omc/skill-patches.disabled")


def record(condition: str, score: float, iters: int, goal: str) -> None:
    """Record a single A/B trial result."""
    entry = {
        "condition": condition,
        "score": score,
        "iters_to_converge": iters,
        "goal": goal[:120],
        "timestamp": datetime.now().isoformat(),
    }
    RESULTS_FILE.parent.mkdir(parents=True, exist_ok=True)
    with open(RESULTS_FILE, "a") as f:
        f.write(json.dumps(entry, ensure_ascii=False) + "\n")
    print(f"[RECORDED] {condition}: score={score:.3f}, iters={iters}")


def analyze() -> None:
    """Analyze A/B test results with descriptive stats."""
    if not RESULTS_FILE.exists():
        print("No results yet. Run trials first.")
        return

    results = [json.loads(l) for l in RESULTS_FILE.read_text().strip().split("\n") if l.strip()]
    control = [r for r in results if r["condition"] == "control"]
    treatment = [r for r in results if r["condition"] == "treatment"]

    print(f"\n{'='*50}")
    print("A/B TEST RESULTS: Skill Patch Injection")
    print(f"{'='*50}")
    print(f"Total trials: {len(results)} (A={len(control)}, B={len(treatment)})")
    print()

    for name, group in [("A (control — static)", control), ("B (treatment — patched)", treatment)]:
        if not group:
            print(f"{name}: no data")
            continue
        scores = [r["score"] for r in group]
        iters = [r["iters_to_converge"] for r in group]
        print(f"{name}:")
        print(f"  best_score — mean={mean(scores):.3f}", end="")
        if len(scores) > 1:
            print(f"  stdev={stdev(scores):.3f}  n={len(scores)}", end="")
        print()
        print(f"  iters      — mean={mean(iters):.1f}", end="")
        if len(iters) > 1:
            print(f"  stdev={stdev(iters):.2f}", end="")
        print()

    if control and treatment:
        score_delta = mean(r["score"] for r in treatment) - mean(r["score"] for r in control)
        iter_delta = mean(r["iters_to_converge"] for r in control) - mean(r["iters_to_converge"] for r in treatment)
        print()
        print(f"Effect size:")
        print(f"  score improvement: {score_delta:+.3f} ({'positive' if score_delta > 0 else 'negative'})")
        print(f"  iter reduction:    {iter_delta:+.1f} fewer iterations in treatment")
        print()
        # Hypothesis check
        hypothesis_met = score_delta >= 0.05 or iter_delta >= 1.0
        print(f"Hypothesis: treatment > control + 0.05 score OR < control iters")
        print(f"Result: {'SUPPORTED' if hypothesis_met else 'NOT SUPPORTED'}")
    print(f"{'='*50}\n")


def disable_patches() -> None:
    """Disable skill patches for control condition."""
    if PATCH_DIR.exists() and not PATCH_DIR_DISABLED.exists():
        shutil.move(str(PATCH_DIR), str(PATCH_DIR_DISABLED))
        print(f"[CONTROL] Skill patches disabled → {PATCH_DIR_DISABLED}")
    elif PATCH_DIR_DISABLED.exists():
        print("[CONTROL] Already disabled.")
    else:
        print("[CONTROL] No patch dir to disable.")


def enable_patches() -> None:
    """Re-enable skill patches for treatment condition."""
    if PATCH_DIR_DISABLED.exists():
        shutil.move(str(PATCH_DIR_DISABLED), str(PATCH_DIR))
        print(f"[TREATMENT] Skill patches re-enabled → {PATCH_DIR}")
    elif PATCH_DIR.exists():
        print("[TREATMENT] Already enabled.")
    else:
        print("[TREATMENT] No disabled patches found.")


def status() -> None:
    """Show current condition and patch status."""
    has_patches = PATCH_DIR.exists() and any(PATCH_DIR.glob("*.json"))
    disabled = PATCH_DIR_DISABLED.exists()
    mode = "TREATMENT (patches active)" if has_patches else ("CONTROL (patches disabled)" if disabled else "CONTROL (no patches)")
    print(f"Current condition: {mode}")

    if RESULTS_FILE.exists():
        results = [json.loads(l) for l in RESULTS_FILE.read_text().strip().split("\n") if l.strip()]
        print(f"Recorded trials: {len(results)} total")
    else:
        print("No trials recorded yet.")


def main() -> None:
    parser = argparse.ArgumentParser(description="A/B test for skill patch injection")
    sub = parser.add_subparsers(dest="cmd")

    r = sub.add_parser("record", help="Record a trial result")
    r.add_argument("--condition", required=True, choices=["control", "treatment"])
    r.add_argument("--score", required=True, type=float)
    r.add_argument("--iters", required=True, type=int)
    r.add_argument("--goal", default="")

    sub.add_parser("analyze", help="Analyze results")
    sub.add_parser("disable-patches", help="Switch to control condition")
    sub.add_parser("enable-patches", help="Switch to treatment condition")
    sub.add_parser("status", help="Show current condition")

    args = parser.parse_args()

    if args.cmd == "record":
        record(args.condition, args.score, args.iters, args.goal)
    elif args.cmd == "analyze":
        analyze()
    elif args.cmd == "disable-patches":
        disable_patches()
    elif args.cmd == "enable-patches":
        enable_patches()
    elif args.cmd == "status":
        status()
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
