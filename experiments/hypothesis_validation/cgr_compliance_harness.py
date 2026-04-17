#!/usr/bin/env python3
"""
CGR compliance harness — measures Entity QG29 adherence.

Invokes `claude -p` with /entity skill activation on a set of prompts that
should trigger QG29 (codebase/environment claims), then parses the response
for [CGR:compute_id], [GROUNDED:doc_id], and [UNCERTAIN: method=...] tags.

Limitations (important):
  * We can COUNT tags that ARE present; we CANNOT detect missing tags that
    SHOULD have been present. True QG29 compliance requires an LLM judge
    reading the response and classifying untagged assertions — out of scope
    for v1. This harness measures tag DENSITY, not full compliance.
  * `claude -p` invokes a one-shot non-interactive Claude session. Skill
    activation depends on `claude` CLI config and may not always load /entity.
    Output includes a `skill_active` probe (checks for QG-related vocabulary).

Usage:
  python3 cgr_compliance_harness.py --condition treatment --out report.json
  python3 cgr_compliance_harness.py --condition control   --out baseline.json

Output (JSON):
  {
    "condition": "treatment",
    "timestamp": "...",
    "results": [
      {
        "prompt": "...",
        "response_chars": N,
        "cgr_tags": [...],
        "grounded_tags": [...],
        "uncertain_method_tags": [...],
        "qg29_trigger_claims_estimated": N,
        "cgr_rate_estimated": 0.XX,
        "skill_active_probe": true/false
      }
    ],
    "aggregate": {
      "mean_cgr_rate": 0.XX,
      "mean_tag_density": 0.XX,
      "skill_active_fraction": 0.XX
    }
  }
"""
from __future__ import annotations

import argparse
import json
import os
import re
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

# Prompts designed to trigger QG29: each asserts or asks about codebase/env state.
# A compliant Entity response should back each claim with [CGR:], [GROUNDED:], or
# [UNCERTAIN: method=...] — not bare assertion.
PROMPTS = [
    "Using /entity, answer: Does `scripts/corpus_router.py` exist in "
    "/home/jayone/Project/Entity? Give a direct answer with evidence.",
    "Using /entity, answer: What is the current best_score recorded in "
    "`.omc/live-state.json`? Give a direct answer with evidence.",
    "Using /entity, answer: How many proposed items are in "
    "`.omc/evolution-registry.jsonl`? Give a direct answer with evidence.",
    "Using /entity, answer: Does the function `dispatch_cgr` exist anywhere "
    "in the Entity Python codebase? Give a direct answer with evidence.",
    "Using /entity, answer: What is check #26 in the Entity Quality Gate "
    "table (from ~/.claude/skills/entity/SKILL.md)? Give a direct answer with "
    "evidence.",
]

# Tag patterns — matches the QG29 spec from ~/.claude/skills/entity/SKILL.md
RE_CGR = re.compile(r"\[CGR:([^\]]+)\]")
RE_GROUNDED = re.compile(r"\[GROUNDED:([^\]]+)\]")
RE_UNCERTAIN_METHOD = re.compile(r"\[UNCERTAIN:\s*method[=:]([^\]]+)\]", re.IGNORECASE)

# Heuristic: how many factual codebase/env assertions the response makes.
# A sentence mentioning a file path, line number, score, count, or version
# counts as one QG29 trigger.
RE_TRIGGER = re.compile(
    r"(?i)(?:"
    r"[A-Za-z0-9_/]+\.(?:py|md|json|jsonl|sh|txt|yaml|yml)"   # file path
    r"|line\s+\d+"                                             # line reference
    r"|score\s*[=:]\s*[\d.]+"                                  # score
    r"|best_score\s*[=:]\s*[\d.]+"                             # metric
    r"|\d+\s+(?:proposed|accepted|items|tasks|tests?)"         # counts
    r"|version\s+[\d.]+"                                       # version
    r")"
)

# Skill-active probe: these tokens appear in Entity QG responses
SKILL_ACTIVE_TOKENS = [
    "Quality Gate", "QG26", "QG28", "QG29", "[GROUNDED:", "[CGR:",
    "[CONCLUSION]", "corpus", "routing",
]


def invoke_entity(prompt: str, timeout: int = 90) -> str:
    """Run `claude -p <prompt> --bare` and return stdout."""
    try:
        result = subprocess.run(
            ["claude", "-p", prompt, "--bare"],
            capture_output=True,
            text=True,
            timeout=timeout,
        )
        return result.stdout
    except subprocess.TimeoutExpired:
        return "[ERROR] claude -p timed out"
    except FileNotFoundError:
        return "[ERROR] claude CLI not found"
    except Exception as exc:  # noqa: BLE001
        return f"[ERROR] {exc}"


def analyze_response(response: str) -> dict:
    """Extract tag counts + compliance estimate from a single response."""
    cgr = RE_CGR.findall(response)
    grounded = RE_GROUNDED.findall(response)
    uncertain = RE_UNCERTAIN_METHOD.findall(response)
    triggers = RE_TRIGGER.findall(response)

    total_triggers = len(triggers)
    tagged_count = len(cgr) + len(grounded) + len(uncertain)

    # cgr_rate_estimated: proportion of trigger claims that appear to be tagged.
    # Over-count guard: responses may include more tags than raw triggers
    # (one tag can cover multiple mentions) — clamp to [0, 1].
    if total_triggers == 0:
        cgr_rate = 0.0 if tagged_count == 0 else 1.0  # no triggers, any tags → perfect
    else:
        cgr_rate = min(1.0, tagged_count / total_triggers)

    skill_active = any(tok in response for tok in SKILL_ACTIVE_TOKENS)

    return {
        "response_chars": len(response),
        "cgr_tags": cgr,
        "grounded_tags": grounded,
        "uncertain_method_tags": uncertain,
        "qg29_trigger_claims_estimated": total_triggers,
        "cgr_rate_estimated": round(cgr_rate, 3),
        "skill_active_probe": skill_active,
    }


def run(condition: str, out_path: Path, prompts: list[str], dry_run: bool = False) -> dict:
    results = []
    for i, prompt in enumerate(prompts, 1):
        print(f"[{i}/{len(prompts)}] {prompt[:70]}...", file=sys.stderr)
        response = "[DRY-RUN: no invocation]" if dry_run else invoke_entity(prompt)
        analysis = analyze_response(response)
        analysis["prompt"] = prompt
        results.append(analysis)

    # Aggregate
    active_count = sum(1 for r in results if r["skill_active_probe"])
    mean_cgr = sum(r["cgr_rate_estimated"] for r in results) / max(1, len(results))
    mean_density = sum(
        len(r["cgr_tags"]) + len(r["grounded_tags"]) + len(r["uncertain_method_tags"])
        for r in results
    ) / max(1, len(results))

    report = {
        "condition": condition,
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "prompts_total": len(prompts),
        "dry_run": dry_run,
        "results": results,
        "aggregate": {
            "mean_cgr_rate": round(mean_cgr, 3),
            "mean_tag_density": round(mean_density, 2),
            "skill_active_fraction": round(active_count / max(1, len(results)), 3),
        },
    }

    out_path.write_text(json.dumps(report, ensure_ascii=False, indent=2))
    print(f"\nReport → {out_path}", file=sys.stderr)
    print(
        f"  mean_cgr_rate        = {report['aggregate']['mean_cgr_rate']:.3f}",
        file=sys.stderr,
    )
    print(
        f"  mean_tag_density     = {report['aggregate']['mean_tag_density']:.2f}",
        file=sys.stderr,
    )
    print(
        f"  skill_active_fraction= {report['aggregate']['skill_active_fraction']:.3f}",
        file=sys.stderr,
    )
    return report


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument(
        "--condition",
        choices=["control", "treatment"],
        required=True,
        help="control = pre-QG29 baseline; treatment = post-QG29",
    )
    parser.add_argument(
        "--out",
        type=Path,
        default=Path("cgr_compliance_report.json"),
        help="output JSON report path",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="skip claude invocations; produce structure-only report",
    )
    args = parser.parse_args()

    run(args.condition, args.out, PROMPTS, dry_run=args.dry_run)
    return 0


if __name__ == "__main__":
    sys.exit(main())
