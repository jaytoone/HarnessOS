#!/usr/bin/env python3
"""
mirage_classifier.py — classify live-inf failure episodes against the Mirage
taxonomy (arXiv:2604.11978).

Taxonomy (5 categories):
  perception — failure to understand input/state (parsing errors, misread)
  planning   — wrong strategy/plan (drift, bad sub-goals, scope creep)
  memory     — context dilution, forgetting, stale references
  execution  — tool errors, code errors, timeouts, runtime crashes
  recovery   — unable to recover from a transient failure (retry loops, oscillation)

Approach: hybrid
  1. Keyword-heuristic pass — fast, deterministic, covers common cases.
  2. LLM fallback (optional via --llm-fallback) — classifies episodes where
     heuristic confidence is low.

Input: .omc/episodes.jsonl
Output: JSON report with per-episode category + aggregate distribution.

Usage:
  python3 scripts/mirage_classifier.py                          # heuristic only
  python3 scripts/mirage_classifier.py --llm-fallback           # hybrid
  python3 scripts/mirage_classifier.py --out mirage_report.json # custom output
"""
from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path


CATEGORIES = ["perception", "planning", "memory", "execution", "recovery"]

# Keyword rules (case-insensitive). Tuned against episode schema seen in
# .omc/episodes.jsonl: fields `key_errors`, `approach`, `project_hints`.
KEYWORD_RULES = {
    "perception": [
        r"\bparse\s*(?:error|failure|bug)\b",
        r"\boutput\s*parser\b",
        r"\bmisread\b|\bmisinterpret",
        r"\bambiguous?\s*(?:input|spec|intent)",
        r"\bintent\s*clarification\b",
    ],
    "planning": [
        r"\bplan\s*drift\b",
        r"\bwrong\s*(?:strategy|plan|approach)\b",
        r"\bscope\s*creep\b",
        r"\bgoal\s*(?:drift|mismatch|misalignment)\b",
        r"\bsub[- ]?goals?\b.*\b(?:wrong|bad|broken)\b",
        r"\bstrategy\s*(?:mismatch|failure)\b",
    ],
    "memory": [
        r"\bcontext\s*(?:dilution|overflow|exceed|pollut)",
        r"\bforget\b|\bforgot\b|\bforgetting\b",
        r"\bstale\s*(?:memory|reference|state|score)\b",
        r"\bpatch(?:es)?\s*accumulat",
        r"\bauto[- ]?compact\b",
        r"\btoken\s*(?:limit|exhaust)",
    ],
    "execution": [
        r"\btool\s*(?:error|failure|crash)\b",
        r"\b(?:timeout|timed\s*out)\b",
        r"\b(?:code|runtime|type)\s*error\b",
        r"\bexception\b",
        r"\bimport\s*error\b",
        r"\bbuild\s*(?:error|failure)\b",
        r"\btransient\s*(?:failure|error)\b",
    ],
    "recovery": [
        r"\bretry\s*loop\b",
        r"\boscillat",
        r"\binfinite\s*loop\b",
        r"\brecover(?:y)?\s*(?:fail|broken)\b",
        r"\bfallback\s*(?:broken|missing)\b",
        r"\brollback\b.*\b(?:failed|broken)\b",
    ],
}

COMPILED_RULES = {
    cat: [re.compile(p, re.IGNORECASE) for p in pats]
    for cat, pats in KEYWORD_RULES.items()
}


def episode_text(ep: dict) -> str:
    """Concatenate the signal-bearing fields of an episode into one string."""
    parts = []
    for key in ("task_desc", "approach", "key_errors", "project_hints", "fatal_type"):
        val = ep.get(key)
        if isinstance(val, list):
            parts.extend(str(v) for v in val)
        elif val:
            parts.append(str(val))
    return " | ".join(parts)


def heuristic_classify(text: str) -> tuple[str | None, dict, float]:
    """
    Heuristic classification.
    Returns (top_category | None, hit_counts_per_category, confidence).
    confidence = (top_hits - second_hits) / max(1, total_hits)  — margin-based.
    None when no rule matches at all.
    """
    hits = {cat: 0 for cat in CATEGORIES}
    for cat, patterns in COMPILED_RULES.items():
        for p in patterns:
            if p.search(text):
                hits[cat] += 1

    total = sum(hits.values())
    if total == 0:
        return None, hits, 0.0

    ranked = sorted(hits.items(), key=lambda kv: -kv[1])
    top_cat, top_n = ranked[0]
    second_n = ranked[1][1] if len(ranked) > 1 else 0
    confidence = (top_n - second_n) / total
    return top_cat, hits, round(confidence, 3)


LLM_PROMPT_TEMPLATE = """Classify this agent failure episode into ONE Mirage failure category.

Mirage taxonomy (pick exactly one):
- perception: failure to understand input/state (parsing errors, misread, ambiguous intent)
- planning:   wrong strategy/plan (drift, bad sub-goals, scope creep, misalignment)
- memory:     context dilution, forgetting, stale references, patch accumulation
- execution:  tool errors, code crashes, timeouts, runtime exceptions
- recovery:   unable to recover from a transient failure (retry loops, oscillation)

Episode:
{episode_text}

Output EXACTLY one line in this format:
category: <perception|planning|memory|execution|recovery>
"""


def llm_classify(text: str, timeout: int = 30) -> str | None:
    """Fall back to `claude -p --bare` when heuristic confidence is low."""
    try:
        result = subprocess.run(
            ["claude", "-p", LLM_PROMPT_TEMPLATE.format(episode_text=text), "--bare"],
            capture_output=True,
            text=True,
            timeout=timeout,
        )
        out = result.stdout.strip().lower()
        m = re.search(r"category:\s*(perception|planning|memory|execution|recovery)", out)
        return m.group(1) if m else None
    except (subprocess.TimeoutExpired, FileNotFoundError, Exception):
        return None


def classify_episode(ep: dict, use_llm: bool, low_conf_threshold: float = 0.20) -> dict:
    text = episode_text(ep)
    cat, hits, conf = heuristic_classify(text)
    method = "heuristic"
    llm_cat = None

    if use_llm and (cat is None or conf < low_conf_threshold):
        llm_cat = llm_classify(text)
        if llm_cat is not None:
            cat = llm_cat
            method = "llm_fallback"
            conf = None  # LLM does not report confidence

    return {
        "ts": ep.get("ts", "?"),
        "task_desc": ep.get("task_desc", "")[:80],
        "outcome": ep.get("outcome", "?"),
        "category": cat,
        "method": method,
        "heuristic_hits": hits,
        "heuristic_confidence": conf,
        "llm_category": llm_cat,
    }


def run(episodes_path: Path, use_llm: bool, out_path: Path) -> dict:
    if not episodes_path.exists():
        print(f"[ERROR] {episodes_path} not found", file=sys.stderr)
        sys.exit(1)

    episodes = [json.loads(l) for l in episodes_path.read_text().splitlines() if l.strip()]
    print(f"[MIRAGE] Loaded {len(episodes)} episodes from {episodes_path}", file=sys.stderr)

    results = [classify_episode(ep, use_llm) for ep in episodes]

    # Aggregate distribution (only on episodes we could classify)
    classified = [r["category"] for r in results if r["category"] is not None]
    dist = Counter(classified)
    total = len(classified)
    unclassified = sum(1 for r in results if r["category"] is None)

    # Build distribution with all 5 categories (even zero-count)
    full_dist = {cat: {"count": dist.get(cat, 0),
                       "fraction": round(dist.get(cat, 0) / max(1, total), 3)}
                 for cat in CATEGORIES}

    # H1 preliminary check: is the dominant category ≥ 40%?
    if total > 0:
        dominant = max(full_dist.items(), key=lambda kv: kv[1]["count"])
        dominant_cat, dominant_info = dominant
        h1_supported_preliminary = dominant_info["fraction"] >= 0.40
    else:
        dominant_cat = None
        dominant_info = None
        h1_supported_preliminary = False

    report = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "episodes_path": str(episodes_path),
        "episodes_total": len(episodes),
        "episodes_classified": total,
        "episodes_unclassified": unclassified,
        "mode": "hybrid" if use_llm else "heuristic_only",
        "distribution": full_dist,
        "dominant_category": dominant_cat,
        "h1_preliminary": {
            "dominant_category": dominant_cat,
            "dominant_fraction": dominant_info["fraction"] if dominant_info else None,
            "threshold": 0.40,
            "supported_preliminary": h1_supported_preliminary,
            "sample_size": total,
            "statistical_power": "insufficient" if total < 25 else "adequate",
            "note": "Full chi-square test requires total >= 25 (5 per category × 5 categories).",
        },
        "per_episode": results,
    }

    out_path.write_text(json.dumps(report, ensure_ascii=False, indent=2))
    print(f"\n[MIRAGE] Report → {out_path}", file=sys.stderr)
    print(f"  classified: {total}/{len(episodes)} | unclassified: {unclassified}", file=sys.stderr)
    print(f"  distribution: {dict(dist)}", file=sys.stderr)
    if dominant_cat:
        print(
            f"  dominant: {dominant_cat} ({dominant_info['fraction']:.2%})"
            f" | H1 preliminary: {'supported' if h1_supported_preliminary else 'not supported'}"
            f" (n={total}, power={'low' if total < 25 else 'ok'})",
            file=sys.stderr,
        )
    return report


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--episodes", type=Path, default=Path(".omc/episodes.jsonl"))
    parser.add_argument("--llm-fallback", action="store_true",
                        help="call `claude -p` for low-confidence heuristic cases")
    parser.add_argument("--out", type=Path, default=Path("mirage_classification_report.json"))
    args = parser.parse_args()
    run(args.episodes, args.llm_fallback, args.out)
    return 0


if __name__ == "__main__":
    sys.exit(main())
