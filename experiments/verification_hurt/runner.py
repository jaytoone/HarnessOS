"""Verification Hurt Experiment

Research basis: "When Verification Hurts: Asymmetric Effects of Multi-Agent Feedback"
arXiv:2603.27076

핵심 가설:
  검증(verification) 피드백이 항상 탈출을 돕지는 않는다.
  특정 조건에서는 오히려 stuck 상태를 고착시킨다.

실험 설계:
  stuck_agent 태스크에 4가지 verification_mode를 적용하고
  escape_rate를 비교한다.

verification_mode:
  none      — 검증 없음 (기존 engineering rescue)
  strict    — 매 attempt마다 검증 피드백 제공
  lenient   — 3 attempt에 1번 검증
  adaptive  — 성공 신뢰도 기반 적응형 검증

Usage:
  python experiments/verification_hurt/runner.py --trials 10 --mode all
  python experiments/verification_hurt/runner.py --mode strict --trials 5
"""

from __future__ import annotations

import json
import random
import re
from dataclasses import dataclass, asdict
from datetime import datetime
from pathlib import Path
from typing import Literal

import os

from openai import OpenAI

from constants import RESULTS_DIR
from experiments.hypothesis_validation.llm_strategies import _chat, _default_client

_MODEL = os.environ.get("MINIMAX_MODEL", "MiniMax-M2.5")
_SYSTEM = "You are a Python coding assistant. Be concise and precise."
from experiments.stuck_agent.tasks import get_stuck_tasks

VerificationMode = Literal["none", "strict", "lenient", "adaptive"]

VERIFICATION_FEEDBACK_PROMPT = """Previous attempt result: FAILED
Code submitted:
```python
{code}
```
Verification feedback hint: {hint}

Generate a corrected Python solution. Output ONLY the code."""

RESCUE_PROMPT = """You are debugging a Python coding problem.
Task: {task_description}

Failed attempt:
```python
{failed_code}
```

Generate a working Python solution. Output ONLY the code."""


def _generate_hint(task_desc: str, failed_code: str, client: OpenAI) -> str:
    resp, _, _ = _chat(
        client=client,
        model=_MODEL,
        system=_SYSTEM,
        messages=[{
            "role": "user",
            "content": (
                f"Task: {task_desc}\n\nFailed code:\n```python\n{failed_code}\n```\n\n"
                "In one sentence, what is the most likely bug? Be specific, no full solution."
            )
        }],
        max_tokens=100,
    )
    return resp.strip()


def _extract_code(text: str) -> str:
    m = re.search(r"```(?:python)?\n(.*?)```", text, re.DOTALL)
    if m:
        return m.group(1).strip()
    lines = [l for l in text.strip().split("\n") if not l.startswith("#")]
    return "\n".join(lines).strip()


def _execute_code(code: str, test_fn=None) -> tuple[bool, str]:
    try:
        namespace: dict = {}
        exec(compile(code, "<string>", "exec"), namespace)  # noqa: S102
        if test_fn:
            return bool(test_fn(namespace)), ""
        return True, ""
    except Exception as e:
        return False, str(e)


@dataclass
class VerificationTrialResult:
    task_id: str
    mode: VerificationMode
    escaped: bool
    attempts_used: int
    tokens_used: int
    verification_calls: int


@dataclass
class VerificationExperimentResult:
    mode: VerificationMode
    n_trials: int
    n_escaped: int
    escape_rate: float
    avg_attempts: float
    avg_verifications: float
    trials: list


def run_verification_trial(
    task,
    mode: VerificationMode,
    client: OpenAI,
    max_attempts: int = 3,
) -> VerificationTrialResult:
    failed_code = getattr(task, "misleading_fix_code", "# no previous attempt")
    task_desc = getattr(task, "misleading_description", getattr(task, "description", str(task)))

    verification_calls = 0
    tokens_used = 0

    for attempt in range(1, max_attempts + 1):
        provide_feedback = False
        if mode == "strict":
            provide_feedback = True
        elif mode == "lenient":
            provide_feedback = (attempt % 3 == 0)
        elif mode == "adaptive":
            provide_feedback = random.random() < (attempt / max_attempts)

        if provide_feedback and attempt > 1:
            hint = _generate_hint(task_desc, failed_code, client)
            verification_calls += 1
            prompt = VERIFICATION_FEEDBACK_PROMPT.format(
                code=failed_code, hint=hint,
            )
        else:
            prompt = RESCUE_PROMPT.format(
                task_description=task_desc,
                failed_code=failed_code,
            )

        response, _, _ = _chat(
            client=client,
            model=_MODEL,
            system=_SYSTEM,
            messages=[{"role": "user", "content": prompt}],
            max_tokens=512,
        )
        tokens_used += int(len(response.split()) * 1.3)
        code = _extract_code(response)

        test_cases = getattr(task, "test_cases", None)
        fn_name = getattr(task, "function_name", None)

        def test_fn(ns, tc=test_cases, fn=fn_name):
            if not tc or not fn or fn not in ns:
                return False
            f = ns[fn]
            try:
                return all(f(**c["input"]) == c["expected"] for c in tc)
            except Exception:
                return False

        passed, _ = _execute_code(code, test_fn)

        if passed:
            return VerificationTrialResult(
                task_id=task.id,
                mode=mode,
                escaped=True,
                attempts_used=attempt,
                tokens_used=tokens_used,
                verification_calls=verification_calls,
            )
        failed_code = code

    return VerificationTrialResult(
        task_id=task.id,
        mode=mode,
        escaped=False,
        attempts_used=max_attempts,
        tokens_used=tokens_used,
        verification_calls=verification_calls,
    )


def run_experiment(
    modes: list,
    n_trials: int = 10,
    max_attempts: int = 3,
    client: OpenAI | None = None,
) -> dict:
    if client is None:
        client = _default_client()

    tasks = get_stuck_tasks()
    sampled = random.sample(tasks, min(n_trials, len(tasks)))
    results: dict = {}

    for mode in modes:
        print(f"  Running mode={mode} ({len(sampled)} trials)...")
        trials = []
        for task in sampled:
            trial = run_verification_trial(task, mode, client, max_attempts)
            trials.append(trial)
            status = "ESCAPED" if trial.escaped else "stuck  "
            print(f"    [{status}] {task.id} (verif={trial.verification_calls})")

        n_escaped = sum(1 for t in trials if t.escaped)
        escape_rate = n_escaped / len(trials) if trials else 0.0
        avg_attempts = sum(t.attempts_used for t in trials) / len(trials) if trials else 0.0
        avg_verif = sum(t.verification_calls for t in trials) / len(trials) if trials else 0.0

        results[mode] = VerificationExperimentResult(
            mode=mode, n_trials=len(trials), n_escaped=n_escaped,
            escape_rate=escape_rate, avg_attempts=avg_attempts,
            avg_verifications=avg_verif, trials=trials,
        )
        print(f"    -> escape_rate={escape_rate:.1%} | avg_verif={avg_verif:.1f}")

    return results


def print_summary(results: dict) -> None:
    print("\n" + "=" * 55)
    print("VERIFICATION HURT EXPERIMENT SUMMARY")
    print("=" * 55)
    print(f"{'Mode':<12} {'Escape%':>8} {'AvgAttempts':>12} {'AvgVerif':>9}")
    print("-" * 55)
    for mode, r in sorted(results.items(), key=lambda x: -x[1].escape_rate):
        print(f"{mode:<12} {r.escape_rate:>7.1%} {r.avg_attempts:>12.1f} {r.avg_verifications:>9.1f}")
    print("=" * 55)
    if "none" in results and "strict" in results:
        delta = results["strict"].escape_rate - results["none"].escape_rate
        if delta < -0.05:
            print(f"\n[FINDING] Verification HURTS (delta={delta:+.1%})")
        elif delta > 0.05:
            print(f"\n[FINDING] Verification HELPS (delta={delta:+.1%})")
        else:
            print(f"\n[FINDING] No significant difference (delta={delta:+.1%})")


def save_results(results: dict, output_dir: Path = RESULTS_DIR) -> Path:
    output_dir.mkdir(exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    out_path = output_dir / f"verification_hurt_{timestamp}.json"
    serializable = {mode: asdict(r) for mode, r in results.items()}
    out_path.write_text(json.dumps(serializable, indent=2, ensure_ascii=False))
    print(f"[SAVED] {out_path}")
    return out_path


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--mode", default="all")
    parser.add_argument("--trials", type=int, default=10)
    parser.add_argument("--max-attempts", type=int, default=3)
    args = parser.parse_args()

    all_modes = ["none", "strict", "lenient", "adaptive"]
    modes = all_modes if args.mode == "all" else [args.mode]

    print(f"Verification Hurt Experiment | modes={modes} trials={args.trials}")
    client = _default_client()
    results = run_experiment(modes, args.trials, args.max_attempts, client)
    print_summary(results)
    save_results(results)
