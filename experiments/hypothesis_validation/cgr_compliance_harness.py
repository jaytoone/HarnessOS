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


class HarnessBlockedError(RuntimeError):
    """Raised when the harness cannot measure due to an environmental block
    (e.g. CLI not authenticated). Distinct from per-call failures."""


def invoke_entity(prompt: str, timeout: int = 90) -> str:
    """Run `claude -p <prompt> --bare` and return stdout.

    Detects common auth failures and raises HarnessBlockedError so the caller
    can abort the whole run rather than silently reporting zero metrics.
    """
    try:
        result = subprocess.run(
            ["claude", "-p", prompt, "--bare"],
            capture_output=True,
            text=True,
            timeout=timeout,
        )
        out = result.stdout
        if "Not logged in" in out or "Please run /login" in out:
            raise HarnessBlockedError(
                "claude CLI not authenticated — run `/login` interactively, "
                "then re-run the harness. Partial results are meaningless."
            )
        return out
    except subprocess.TimeoutExpired:
        return "[ERROR] claude -p timed out"
    except FileNotFoundError:
        raise HarnessBlockedError("claude CLI not found in PATH")
    except HarnessBlockedError:
        raise
    except Exception as exc:  # noqa: BLE001
        return f"[ERROR] {exc}"


def _normalize_trigger(raw: str) -> str:
    """Canonicalize a trigger string so repeated mentions collapse into one claim.

    - file paths: lowercase, strip leading `./`, collapse whitespace
    - numeric claims (score=0.65, best_score=0.75): keep metric name + value pair
    - line references (line 264): normalize to 'line:N'
    - version refs (version 1.2.3): normalize to 'version:N'
    """
    s = raw.strip().lower()
    if s.startswith("./"):
        s = s[2:]
    s = re.sub(r"\s+", " ", s)
    # Line reference
    m = re.match(r"line\s+(\d+)", s)
    if m:
        return f"line:{m.group(1)}"
    # Version reference
    m = re.match(r"version\s+([\d.]+)", s)
    if m:
        return f"version:{m.group(1)}"
    return s


def analyze_response(response: str) -> dict:
    """Extract tag counts + compliance estimates from a single response.

    Emits TWO metrics:
    - raw_cgr_rate: naive tagged/triggers ratio (honest, but inflates denominator
      when the same claim is mentioned multiple times)
    - normalized_cgr_rate: denominator uses distinct claim identities
      (one file path mentioned 3× counts as 1 claim); this is the interpretable
      compliance metric.
    """
    cgr = RE_CGR.findall(response)
    grounded = RE_GROUNDED.findall(response)
    uncertain = RE_UNCERTAIN_METHOD.findall(response)
    triggers_raw = RE_TRIGGER.findall(response)

    # Claim-identity dedup: group repeated mentions of the same file/metric/line
    unique_claims = {_normalize_trigger(t) for t in triggers_raw}

    total_triggers_raw = len(triggers_raw)
    total_claims_unique = len(unique_claims)
    tagged_count = len(cgr) + len(grounded) + len(uncertain)

    # Raw rate (legacy, documented as under-counting)
    if total_triggers_raw == 0:
        raw_rate = 1.0 if tagged_count > 0 else 0.0
    else:
        raw_rate = min(1.0, tagged_count / total_triggers_raw)

    # Normalized rate (claim-identity dedup applied to denominator)
    if total_claims_unique == 0:
        normalized_rate = 1.0 if tagged_count > 0 else 0.0
    else:
        normalized_rate = min(1.0, tagged_count / total_claims_unique)

    skill_active = any(tok in response for tok in SKILL_ACTIVE_TOKENS)

    return {
        "response_chars": len(response),
        "cgr_tags": cgr,
        "grounded_tags": grounded,
        "uncertain_method_tags": uncertain,
        "qg29_trigger_mentions_raw": total_triggers_raw,
        "qg29_trigger_claims_unique": total_claims_unique,
        "qg29_trigger_claims_estimated": total_claims_unique,  # back-compat key
        "cgr_rate_raw": round(raw_rate, 3),
        "cgr_rate_normalized": round(normalized_rate, 3),
        "cgr_rate_estimated": round(normalized_rate, 3),  # back-compat key (now uses normalized)
        "skill_active_probe": skill_active,
    }


def run(condition: str, out_path: Path, prompts: list[str], dry_run: bool = False) -> dict:
    results = []
    for i, prompt in enumerate(prompts, 1):
        print(f"[{i}/{len(prompts)}] {prompt[:70]}...", file=sys.stderr)
        if dry_run:
            response = "[DRY-RUN: no invocation]"
        else:
            try:
                response = invoke_entity(prompt)
            except HarnessBlockedError as err:
                print(f"\n[HARNESS BLOCKED] {err}", file=sys.stderr)
                blocked_report = {
                    "condition": condition,
                    "timestamp": datetime.now(timezone.utc).isoformat(),
                    "blocked": True,
                    "block_reason": str(err),
                    "prompts_attempted": i - 1,
                    "results": results,
                }
                out_path.write_text(json.dumps(blocked_report, ensure_ascii=False, indent=2))
                print(f"[HARNESS BLOCKED] Report → {out_path}", file=sys.stderr)
                return blocked_report
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
