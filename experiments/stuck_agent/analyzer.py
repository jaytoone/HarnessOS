"""Analysis and paper-ready reporting for Stuck-Agent Escape Rate experiment.

Produces:
  - Per-category escape rate breakdown
  - Statistical test summary (McNemar, Cohen's d, 95% CI)
  - Paper-ready result table (text format)
"""
from __future__ import annotations

import json
from pathlib import Path

from experiments.stuck_agent.stats import (
    KruskalWallisResult,
    StatsResult,
    analyze,
    kruskal_wallis_3way,
)


def analyze_results_file(
    path: Path,
) -> tuple[dict, StatsResult, KruskalWallisResult | None]:
    """Load a stuck_agent JSON result file and run full statistical analysis.

    Returns (raw_data, StatsResult, KruskalWallisResult).
    KruskalWallisResult is None if no delegation data present.
    """
    data = json.loads(path.read_text())
    tasks = data.get("tasks", [])

    stuck_tasks = [t for t in tasks if not t.get("phase1_passed", False)]
    eng_escaped = [t.get("eng_escaped", False) for t in stuck_tasks]
    hyp_escaped = [t.get("hyp_escaped", False) for t in stuck_tasks]
    del_escaped = [t.get("del_escaped", False) for t in stuck_tasks]

    stats = analyze(eng_escaped, hyp_escaped)
    kw = None
    if any(t.get("del_escaped") is not None for t in stuck_tasks):
        kw = kruskal_wallis_3way(eng_escaped, hyp_escaped, del_escaped)
    return data, stats, kw


def print_report(
    data: dict,
    stats: StatsResult,
    kw: KruskalWallisResult | None = None,
) -> None:
    """Print a paper-ready result report to stdout."""
    model = data.get("model", "?")
    trials = data.get("trials_per_task", "?")
    n_stuck = data.get("n_stuck", stats.n)
    n_trivial = data.get("n_trivial", 0)

    print("\n" + "=" * 60)
    print("  Stuck-Agent Escape Rate — Statistical Report")
    print("=" * 60)
    print(f"  Model     : {model}  |  trials/task: {trials}")
    print(f"  Stuck obs : {n_stuck}  |  trivial (excluded): {n_trivial}")
    print()

    # Main result table
    if kw is not None:
        print("  ┌────────────────────────────────────────────────────┐")
        print("  │  Strategy      Escape Rate   Δ vs Eng               │")
        print("  ├────────────────────────────────────────────────────┤")
        eng_pct = kw.eng_escape_rate * 100
        hyp_pct = kw.hyp_escape_rate * 100
        del_pct = kw.del_escape_rate * 100
        hyp_sign = "+" if hyp_pct - eng_pct >= 0 else ""
        del_sign = "+" if del_pct - eng_pct >= 0 else ""
        print(f"  │  Engineering   {eng_pct:>6.1f}%   (baseline)                │")
        print(f"  │  Hypothesis    {hyp_pct:>6.1f}%   {hyp_sign}{hyp_pct-eng_pct:.1f}%               │")
        print(f"  │  Delegation    {del_pct:>6.1f}%   {del_sign}{del_pct-eng_pct:.1f}%               │")
        print("  └────────────────────────────────────────────────────┘")
    else:
        print("  ┌─────────────────────────────────────────────┐")
        print("  │  Strategy      Escape Rate   Δ (uplift)      │")
        print("  ├─────────────────────────────────────────────┤")
        eng_pct = stats.eng_escape_rate * 100
        hyp_pct = stats.hyp_escape_rate * 100
        uplift_pct = stats.escape_rate_uplift * 100
        sign = "+" if uplift_pct >= 0 else ""
        print(f"  │  Engineering   {eng_pct:>6.1f}%                        │")
        print(f"  │  Hypothesis    {hyp_pct:>6.1f}%      {sign}{uplift_pct:.1f}%          │")
        print("  └─────────────────────────────────────────────┘")
    print()

    # Statistical tests
    print("  Statistical Tests")
    print("  -----------------")
    sig = "✓ SIGNIFICANT" if stats.mcnemar_p < 0.05 else "✗ not significant"
    print(f"  McNemar Eng vs Hyp (b={stats.mcnemar_b}, c={stats.mcnemar_c}): "
          f"χ²={stats.mcnemar_chi2:.3f}, p={stats.mcnemar_p:.4f}  {sig}")
    print(f"  Cohen's d : {stats.cohens_d:+.3f}  ({stats.effect_size_label} effect)")
    print(f"  95% CI    : [{stats.ci_lower*100:+.1f}%, {stats.ci_upper*100:+.1f}%]")

    if kw is not None:
        kw_sig = "✓ SIGNIFICANT" if kw.significant else "✗ not significant"
        print()
        print(f"  Kruskal-Wallis 3-way (Eng vs Hyp vs Del):")
        print(f"    H={kw.H_statistic:.4f}, p={kw.p_value:.6f}  {kw_sig}")
        print(f"    Dominant strategy: {kw.dominant_strategy}")
    print()

    # Power note
    print(f"  Power     : {stats.power_note}")

    # Category breakdown
    tasks = data.get("tasks", [])
    stuck_tasks = [t for t in tasks if not t.get("phase1_passed", False)]
    has_del = any(t.get("del_escaped") is not None for t in stuck_tasks)
    by_cat: dict[str, dict[str, list[bool]]] = {}
    for t in stuck_tasks:
        cat = t.get("category", "unknown")
        if cat not in by_cat:
            by_cat[cat] = {"eng": [], "hyp": [], "del": []}
        by_cat[cat]["eng"].append(t.get("eng_escaped", False))
        by_cat[cat]["hyp"].append(t.get("hyp_escaped", False))
        by_cat[cat]["del"].append(bool(t.get("del_escaped", False)))

    if by_cat:
        print()
        print("  By Category")
        print("  -----------")
        if has_del:
            print(f"  {'Category':<16} {'n':>4}  {'Eng':>7}  {'Hyp':>7}  {'Del':>7}  {'Δhyp':>7}  {'Δdel':>7}")
        else:
            print(f"  {'Category':<16} {'n':>4}  {'Eng':>7}  {'Hyp':>7}  {'Δ':>7}")
        for cat, vals in sorted(by_cat.items()):
            n = len(vals["eng"])
            er = sum(vals["eng"]) / n * 100 if n else 0
            hr = sum(vals["hyp"]) / n * 100 if n else 0
            dr = sum(vals["del"]) / n * 100 if n else 0
            hyp_s = "+" if hr - er >= 0 else ""
            del_s = "+" if dr - er >= 0 else ""
            if has_del:
                print(f"  {cat:<16} {n:>4}  {er:>6.1f}%  {hr:>6.1f}%  {dr:>6.1f}%  "
                      f"{hyp_s}{hr-er:.1f}%  {del_s}{dr-er:.1f}%")
            else:
                sign = "+" if hr - er >= 0 else ""
                print(f"  {cat:<16} {n:>4}  {er:>6.1f}%  {hr:>6.1f}%  {sign}{hr-er:.1f}%")

    print()
    print("  Token overhead (hypothesis / delegation vs engineering):")
    eng_tok = data.get("eng_total_tokens", 0)
    hyp_tok = data.get("hyp_total_tokens", 0)
    del_tok = data.get("del_total_tokens", 0)
    if eng_tok > 0:
        hyp_oh = (hyp_tok / eng_tok - 1) * 100
        hyp_s = "+" if hyp_oh >= 0 else ""
        print(f"    Engineering: {eng_tok:,}  |  Hypothesis: {hyp_tok:,} ({hyp_s}{hyp_oh:.1f}%)")
        if del_tok > 0:
            del_oh = (del_tok / eng_tok - 1) * 100
            del_s = "+" if del_oh >= 0 else ""
            print(f"    Delegation : {del_tok:,} ({del_s}{del_oh:.1f}%)")

    print("=" * 60)
