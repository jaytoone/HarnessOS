"""Stuck-Agent Escape Rate runner.

Three runners:
  DeterministicStuckRunner      — fast, no API calls; uses misleading_fix_code for phase 1
  LLMStuckRunner                — real LLM calls; observes natural failure patterns
  ControlledLLMStuckRunner      — CONTROLLED: always injects misleading_fix_code as the
                                  "failed attempt", guaranteeing 100% stuck observations.
                                  This eliminates trivial trials and maximizes statistical power.

Experiment flow for each task × trial:
  Phase 1: Run engineering attempt  → if passes, task is "trivial" (skip)
                                     → if fails, agent is "stuck"
  Phase 2a (control):   Engineering rescue prompt → record escaped?
  Phase 2b (treatment): Hypothesis rescue prompt  → record escaped?

Key metric: escape_rate(treatment) - escape_rate(control)
"""
from __future__ import annotations

import json
import os
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Any

from openai import OpenAI

from constants import RESULTS_DIR, StuckTaskCategory
from experiments.hypothesis_validation.strategies import _execute_attempt
from experiments.hypothesis_validation.llm_strategies import (
    _chat,
    _default_client,
    _extract_code,
    _extract_hypothesis,
)
from experiments.stuck_agent.tasks import StuckTask, get_stuck_tasks


# ---------------------------------------------------------------------------
# Result dataclasses
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class RescueResult:
    """Outcome of a single rescue attempt (one phase-2 trial)."""

    escaped: bool
    attempts_used: int
    tokens_used: int
    strategy: str  # "engineering" | "hypothesis"
    extracted_code: str | None = None
    hypothesis: str | None = None


@dataclass(frozen=True)
class StuckTaskResult:
    """Full result for one (task, trial) pair."""

    task_id: str
    category: StuckTaskCategory
    trial: int
    phase1_passed: bool          # True = task was trivial for engineering (excluded)
    eng_rescue: RescueResult | None = None
    hyp_rescue: RescueResult | None = None
    del_rescue: RescueResult | None = None


@dataclass
class StuckExperimentResult:
    """Aggregated result for the full stuck-agent experiment."""

    model: str
    trials_per_task: int
    task_results: list[StuckTaskResult] = field(default_factory=list)
    run_timestamp: str = field(default_factory=lambda: datetime.now().isoformat())

    @property
    def stuck_results(self) -> list[StuckTaskResult]:
        """Only results where phase 1 FAILED (the agent was actually stuck)."""
        return [r for r in self.task_results if not r.phase1_passed]

    @property
    def eng_escaped(self) -> list[bool]:
        return [r.eng_rescue.escaped for r in self.stuck_results if r.eng_rescue]

    @property
    def hyp_escaped(self) -> list[bool]:
        return [r.hyp_rescue.escaped for r in self.stuck_results if r.hyp_rescue]

    @property
    def del_escaped(self) -> list[bool]:
        return [r.del_rescue.escaped for r in self.stuck_results if r.del_rescue]


# ---------------------------------------------------------------------------
# Deterministic runner (for CI / fast iteration)
# ---------------------------------------------------------------------------


class DeterministicStuckRunner:
    """Runs stuck-agent experiment without LLM calls.

    Phase 1: apply buggy_code  → always fails (by task design)
    Phase 2a (engineering): apply misleading_fix_code  → check if it passes
    Phase 2b (hypothesis):  apply correct_code         → always passes
    """

    def run(
        self,
        tasks: list[StuckTask] | None = None,
    ) -> StuckExperimentResult:
        if tasks is None:
            tasks = get_stuck_tasks()

        results: list[StuckTaskResult] = []
        for task in tasks:
            # Phase 1: buggy_code must fail (validates task design)
            _, _, phase1_pass = _execute_attempt(
                task.buggy_code, task.function_name, task.test_cases
            )
            if phase1_pass:
                # Task design error: buggy code somehow passes — record but skip
                results.append(
                    StuckTaskResult(
                        task_id=task.id,
                        category=task.category,
                        trial=1,
                        phase1_passed=True,
                    )
                )
                continue

            # Phase 2a: engineering rescue = apply misleading_fix
            eng_passed, _, eng_solved = _execute_attempt(
                task.misleading_fix_code, task.function_name, task.test_cases
            )
            eng_rescue = RescueResult(
                escaped=eng_solved,
                attempts_used=1,
                tokens_used=0,
                strategy="engineering",
                extracted_code=task.misleading_fix_code,
            )

            # Phase 2b: hypothesis rescue = apply correct_code
            hyp_passed, _, hyp_solved = _execute_attempt(
                task.correct_code, task.function_name, task.test_cases
            )
            hyp_rescue = RescueResult(
                escaped=hyp_solved,
                attempts_used=1,
                tokens_used=0,
                strategy="hypothesis",
                extracted_code=task.correct_code,
            )

            results.append(
                StuckTaskResult(
                    task_id=task.id,
                    category=task.category,
                    trial=1,
                    phase1_passed=False,
                    eng_rescue=eng_rescue,
                    hyp_rescue=hyp_rescue,
                )
            )

        return StuckExperimentResult(
            model="deterministic",
            trials_per_task=1,
            task_results=results,
        )


# ---------------------------------------------------------------------------
# LLM prompts
# ---------------------------------------------------------------------------


_PHASE1_SYSTEM = (
    "You are a Python debugging expert. Fix the buggy function. "
    "Return ONLY the corrected Python code in a ```python code block."
)

_ENG_RESCUE_SYSTEM = (
    "You are a Python debugging expert. Your previous fix attempt failed. "
    "Study the failure carefully and try a completely different approach. "
    "Return ONLY the corrected Python code in a ```python code block."
)

_HYP_RESCUE_SYSTEM = (
    "You are a Python debugging expert who uses structured hypothesis reasoning.\n"
    "Your previous fix attempt failed. Follow these steps:\n"
    "1. Write: 'Failure analysis: <why your previous fix was wrong>'\n"
    "2. Write: 'Root cause hypothesis: <the true root cause>'\n"
    "3. Write the corrected code in a ```python code block.\n"
    "Be concise and explicit."
)

_DEL_RESCUE_SYSTEM = (
    "You are an orchestrator agent. Your previous direct fix attempt failed.\n"
    "Use the ReAct delegation pattern to escape the stuck state:\n"
    "1. Write: 'Bug category: <red_herring | multi_bug | hidden_assume | semantic_inv>'\n"
    "2. Write: 'Delegating to: <specialist name> — strategy: <why this specialist>'\n"
    "   Specialists: TraceSpecialist (follows execution path), ContractSpecialist\n"
    "   (checks implicit contracts), InversionSpecialist (checks logic direction),\n"
    "   InteractionSpecialist (checks multi-bug interactions)\n"
    "3. Write: 'Specialist analysis: <what the specialist found>'\n"
    "4. Write the corrected code in a ```python code block.\n"
    "Be concise and explicit."
)


def _phase1_prompt(task: StuckTask) -> str:
    test_lines = "\n".join(f"  {tc}" for tc in task.test_cases)
    hint_section = f"\n\n{task.misleading_hint}" if task.misleading_hint else ""
    return (
        f"Buggy function:\n```python\n{task.buggy_code}```\n\n"
        f"Test cases (must all pass):\n{test_lines}{hint_section}\n\nFix the bug."
    )


def _rescue_prompt(
    task: StuckTask, failed_code: str, tests_passed: int, tests_total: int
) -> str:
    test_lines = "\n".join(f"  {tc}" for tc in task.test_cases)
    return (
        f"Original buggy function:\n```python\n{task.buggy_code}```\n\n"
        f"Your previous fix (which FAILED):\n```python\n{failed_code}```\n\n"
        f"It passed {tests_passed}/{tests_total} tests. "
        f"Test cases:\n{test_lines}\n\nFix the bug correctly."
    )


# ---------------------------------------------------------------------------
# LLM runner
# ---------------------------------------------------------------------------


class LLMStuckRunner:
    """Runs stuck-agent experiment with real LLM calls.

    Each (task, trial):
      Phase 1: engineering attempt → if passes, skip (trivial)
                                   → if fails, extract context for phase 2
      Phase 2a: engineering rescue → fresh call with failure context
      Phase 2b: hypothesis rescue  → fresh call with hypothesis prompt
    """

    def __init__(
        self,
        client: OpenAI | None = None,
        model: str = "MiniMax-M2.5",
        max_rescue_attempts: int = 3,
    ) -> None:
        self.client = client or _default_client()
        self.model = model
        self.max_rescue_attempts = max_rescue_attempts

    def run(
        self,
        tasks: list[StuckTask] | None = None,
        trials_per_task: int = 3,
    ) -> StuckExperimentResult:
        if tasks is None:
            tasks = get_stuck_tasks()

        results: list[StuckTaskResult] = []
        total = len(tasks) * trials_per_task

        print(f"\n=== Stuck-Agent Escape Rate — {total} runs (LLM: {self.model}) ===\n")

        for task in tasks:
            for trial in range(1, trials_per_task + 1):
                print(f"  [{task.id} trial {trial}/{trials_per_task}]", end=" ", flush=True)
                tr = self._run_single(task, trial)
                results.append(tr)
                status = "trivial" if tr.phase1_passed else (
                    f"eng={'✓' if tr.eng_rescue and tr.eng_rescue.escaped else '✗'} "
                    f"hyp={'✓' if tr.hyp_rescue and tr.hyp_rescue.escaped else '✗'} "
                    f"del={'✓' if tr.del_rescue and tr.del_rescue.escaped else '✗'}"
                )
                print(status)

        return StuckExperimentResult(
            model=self.model,
            trials_per_task=trials_per_task,
            task_results=results,
        )

    def _run_single(self, task: StuckTask, trial: int) -> StuckTaskResult:
        """Run one (task, trial): phase 1 then phase 2a+2b in parallel."""

        # ── Phase 1: engineering attempt ────────────────────────────────
        p1_prompt = _phase1_prompt(task)
        p1_raw, p1_in, p1_out = _chat(
            self.client, self.model, _PHASE1_SYSTEM,
            [{"role": "user", "content": p1_prompt}],
        )
        p1_code = _extract_code(p1_raw)

        if p1_code:
            p1_passed_n, p1_total, p1_solved = _execute_attempt(
                p1_code, task.function_name, task.test_cases
            )
        else:
            p1_passed_n, p1_total, p1_solved = 0, len(task.test_cases), False

        if p1_solved:
            # Task too easy — skip rescue experiment for this trial
            return StuckTaskResult(
                task_id=task.id, category=task.category, trial=trial, phase1_passed=True
            )

        # ── Phase 2a: engineering rescue ─────────────────────────────────
        eng_rescue = self._rescue(
            task,
            failed_code=p1_code or task.buggy_code,
            tests_passed=p1_passed_n,
            tests_total=p1_total,
            rescue_system=_ENG_RESCUE_SYSTEM,
            strategy="engineering",
        )

        # ── Phase 2b: hypothesis rescue ───────────────────────────────────
        hyp_rescue = self._rescue(
            task,
            failed_code=p1_code or task.buggy_code,
            tests_passed=p1_passed_n,
            tests_total=p1_total,
            rescue_system=_HYP_RESCUE_SYSTEM,
            strategy="hypothesis",
        )

        # ── Phase 2c: delegation rescue ───────────────────────────────────
        del_rescue = self._rescue(
            task,
            failed_code=p1_code or task.buggy_code,
            tests_passed=p1_passed_n,
            tests_total=p1_total,
            rescue_system=_DEL_RESCUE_SYSTEM,
            strategy="delegation",
        )

        return StuckTaskResult(
            task_id=task.id,
            category=task.category,
            trial=trial,
            phase1_passed=False,
            eng_rescue=eng_rescue,
            hyp_rescue=hyp_rescue,
            del_rescue=del_rescue,
        )

    def _rescue(
        self,
        task: StuckTask,
        failed_code: str,
        tests_passed: int,
        tests_total: int,
        rescue_system: str,
        strategy: str,
    ) -> RescueResult:
        """Run rescue strategy from stuck state; returns on first success."""
        total_tokens = 0
        last_code: str | None = None
        last_hyp: str | None = None

        messages: list[dict[str, Any]] = [
            {"role": "user", "content": _rescue_prompt(task, failed_code, tests_passed, tests_total)}
        ]

        for attempt in range(1, self.max_rescue_attempts + 1):
            raw, in_tok, out_tok = _chat(self.client, self.model, rescue_system, messages)
            total_tokens += in_tok + out_tok
            code = _extract_code(raw)
            hyp = _extract_hypothesis(raw)
            if hyp:
                last_hyp = hyp
            last_code = code

            if code:
                _, _, solved = _execute_attempt(code, task.function_name, task.test_cases)
                if solved:
                    return RescueResult(
                        escaped=True,
                        attempts_used=attempt,
                        tokens_used=total_tokens,
                        strategy=strategy,
                        extracted_code=code,
                        hypothesis=last_hyp,
                    )

            # Prepare next attempt prompt with updated failure context
            messages.append({"role": "assistant", "content": raw})
            messages.append({
                "role": "user",
                "content": "Still failing. Try again with a different approach.",
            })

        return RescueResult(
            escaped=False,
            attempts_used=self.max_rescue_attempts,
            tokens_used=total_tokens,
            strategy=strategy,
            extracted_code=last_code,
            hypothesis=last_hyp,
        )


# ---------------------------------------------------------------------------
# Controlled LLM runner (100% stuck observations)
# ---------------------------------------------------------------------------


class ControlledLLMStuckRunner:
    """Controlled stuck-agent experiment.

    Phase 1 is SHORT-CIRCUITED: always uses misleading_fix_code as the
    canonical "failed engineering attempt". This guarantees every (task, trial)
    produces a stuck observation (phase1_passed=False always).

    Benefit: eliminates trivial-trial variance → 100% statistical power for
    the same API budget. Used for paper-tier analysis.
    """

    def __init__(
        self,
        client: OpenAI | None = None,
        model: str = "MiniMax-M2.5",
        max_rescue_attempts: int = 3,
    ) -> None:
        self.client = client or _default_client()
        self.model = model
        self.max_rescue_attempts = max_rescue_attempts

    def run(
        self,
        tasks: list[StuckTask] | None = None,
        trials_per_task: int = 3,
    ) -> StuckExperimentResult:
        if tasks is None:
            tasks = get_stuck_tasks()

        results: list[StuckTaskResult] = []
        total = len(tasks) * trials_per_task

        print(
            f"\n=== Controlled Stuck-Agent — {total} runs (LLM: {self.model}) ===\n"
            f"    [Phase 1 injected: misleading_fix_code as failed attempt]\n"
        )

        for task in tasks:
            # Pre-compute misleading fix failure context (same for all trials)
            mf_passed, mf_total, mf_solved = _execute_attempt(
                task.misleading_fix_code, task.function_name, task.test_cases
            )

            for trial in range(1, trials_per_task + 1):
                print(f"  [{task.id} trial {trial}/{trials_per_task}]", end=" ", flush=True)

                eng_rescue = self._rescue(
                    task,
                    failed_code=task.misleading_fix_code,
                    tests_passed=mf_passed,
                    tests_total=mf_total,
                    rescue_system=_ENG_RESCUE_SYSTEM,
                    strategy="engineering",
                )
                hyp_rescue = self._rescue(
                    task,
                    failed_code=task.misleading_fix_code,
                    tests_passed=mf_passed,
                    tests_total=mf_total,
                    rescue_system=_HYP_RESCUE_SYSTEM,
                    strategy="hypothesis",
                )
                del_rescue = self._rescue(
                    task,
                    failed_code=task.misleading_fix_code,
                    tests_passed=mf_passed,
                    tests_total=mf_total,
                    rescue_system=_DEL_RESCUE_SYSTEM,
                    strategy="delegation",
                )

                tr = StuckTaskResult(
                    task_id=task.id,
                    category=task.category,
                    trial=trial,
                    phase1_passed=False,  # always stuck by design
                    eng_rescue=eng_rescue,
                    hyp_rescue=hyp_rescue,
                    del_rescue=del_rescue,
                )
                results.append(tr)

                status = (
                    f"eng={'✓' if eng_rescue.escaped else '✗'} "
                    f"hyp={'✓' if hyp_rescue.escaped else '✗'} "
                    f"del={'✓' if del_rescue.escaped else '✗'}"
                )
                print(status)

        return StuckExperimentResult(
            model=f"{self.model}[controlled]",
            trials_per_task=trials_per_task,
            task_results=results,
        )

    def _rescue(
        self,
        task: StuckTask,
        failed_code: str,
        tests_passed: int,
        tests_total: int,
        rescue_system: str,
        strategy: str,
    ) -> RescueResult:
        """Rescue from controlled stuck state."""
        total_tokens = 0
        last_code: str | None = None
        last_hyp: str | None = None

        messages: list[dict[str, Any]] = [
            {
                "role": "user",
                "content": _rescue_prompt(task, failed_code, tests_passed, tests_total),
            }
        ]

        for attempt in range(1, self.max_rescue_attempts + 1):
            raw, in_tok, out_tok = _chat(self.client, self.model, rescue_system, messages)
            total_tokens += in_tok + out_tok
            code = _extract_code(raw)
            hyp = _extract_hypothesis(raw)
            if hyp:
                last_hyp = hyp
            last_code = code

            if code:
                _, _, solved = _execute_attempt(code, task.function_name, task.test_cases)
                if solved:
                    return RescueResult(
                        escaped=True,
                        attempts_used=attempt,
                        tokens_used=total_tokens,
                        strategy=strategy,
                        extracted_code=code,
                        hypothesis=last_hyp,
                    )

            messages.append({"role": "assistant", "content": raw})
            messages.append({
                "role": "user",
                "content": "Still failing. Try again with a different approach.",
            })

        return RescueResult(
            escaped=False,
            attempts_used=self.max_rescue_attempts,
            tokens_used=total_tokens,
            strategy=strategy,
            extracted_code=last_code,
            hypothesis=last_hyp,
        )


# ---------------------------------------------------------------------------
# Serialization
# ---------------------------------------------------------------------------


def save_results(result: StuckExperimentResult, output_dir: Path | None = None) -> Path:
    """Persist StuckExperimentResult to JSON in results/."""
    if output_dir is None:
        output_dir = RESULTS_DIR
    output_dir.mkdir(parents=True, exist_ok=True)

    stuck = result.stuck_results
    n = len(stuck)
    eng_escaped = result.eng_escaped
    hyp_escaped = result.hyp_escaped
    del_escaped = result.del_escaped

    eng_rate = sum(eng_escaped) / n if n else 0.0
    hyp_rate = sum(hyp_escaped) / n if n else 0.0
    del_rate = sum(del_escaped) / n if n else 0.0

    data: dict[str, Any] = {
        "experiment": "stuck_agent",
        "model": result.model,
        "trials_per_task": result.trials_per_task,
        "run_timestamp": result.run_timestamp,
        "n_stuck": n,
        "n_trivial": sum(1 for r in result.task_results if r.phase1_passed),
        "eng_escape_rate": round(eng_rate, 4),
        "hyp_escape_rate": round(hyp_rate, 4),
        "del_escape_rate": round(del_rate, 4),
        "escape_rate_uplift_hyp": round(hyp_rate - eng_rate, 4),
        "escape_rate_uplift_del": round(del_rate - eng_rate, 4),
        "eng_total_tokens": sum(
            r.eng_rescue.tokens_used for r in stuck if r.eng_rescue
        ),
        "hyp_total_tokens": sum(
            r.hyp_rescue.tokens_used for r in stuck if r.hyp_rescue
        ),
        "del_total_tokens": sum(
            r.del_rescue.tokens_used for r in stuck if r.del_rescue
        ),
        "tasks": [_task_result_to_dict(r) for r in result.task_results],
    }

    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    path = output_dir / f"stuck_agent_{ts}.json"
    path.write_text(json.dumps(data, indent=2))
    return path


def _task_result_to_dict(r: StuckTaskResult) -> dict[str, Any]:
    d: dict[str, Any] = {
        "task_id": r.task_id,
        "category": r.category,
        "trial": r.trial,
        "phase1_passed": r.phase1_passed,
    }
    if r.eng_rescue:
        d["eng_escaped"] = r.eng_rescue.escaped
        d["eng_attempts"] = r.eng_rescue.attempts_used
        d["eng_tokens"] = r.eng_rescue.tokens_used
    if r.hyp_rescue:
        d["hyp_escaped"] = r.hyp_rescue.escaped
        d["hyp_attempts"] = r.hyp_rescue.attempts_used
        d["hyp_tokens"] = r.hyp_rescue.tokens_used
        d["hypothesis"] = r.hyp_rescue.hypothesis
    if r.del_rescue:
        d["del_escaped"] = r.del_rescue.escaped
        d["del_attempts"] = r.del_rescue.attempts_used
        d["del_tokens"] = r.del_rescue.tokens_used
    return d
