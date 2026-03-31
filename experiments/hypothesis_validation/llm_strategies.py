"""LLM-based strategy implementations for hypothesis-vs-engineering experiment.

Uses OpenAI-compatible API (MiniMax by default) to compare two debugging strategies:
  - LLMEngineeringStrategy: prompt without hypothesis constraint
  - LLMHypothesisStrategy: prompt forcing explicit root-cause hypothesis first

This is the "real experiment" counterpart to strategies.py (researcher-coded).
Results are stochastic -- run multiple trials for statistical validity.
"""
import os
import re
from dataclasses import dataclass, field
from typing import Any

from openai import OpenAI

from experiments.hypothesis_validation.strategies import (
    AttemptResult,
    StrategyResult,
    _execute_attempt,
)
from experiments.hypothesis_validation.tasks import DebugTask


def _default_client() -> OpenAI:
    """MiniMax 환경변수가 있으면 MiniMax를, 없으면 OpenAI 기본값을 사용."""
    api_key = os.environ.get("MINIMAX_API_KEY")
    base_url = os.environ.get("MINIMAX_BASE_URL")
    if api_key and base_url:
        return OpenAI(api_key=api_key, base_url=base_url)
    return OpenAI()


# ---------------------------------------------------------------------------
# Extended result types with token tracking
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class LLMAttemptResult(AttemptResult):
    """AttemptResult extended with LLM token usage and raw response."""

    input_tokens: int = 0
    output_tokens: int = 0
    raw_response: str = ""
    extracted_code: str | None = None


@dataclass(frozen=True)
class LLMStrategyResult(StrategyResult):
    """StrategyResult extended with aggregated LLM token usage."""

    total_input_tokens: int = 0
    total_output_tokens: int = 0
    attempts: list[AttemptResult] = field(default_factory=list)


# ---------------------------------------------------------------------------
# System prompts
# ---------------------------------------------------------------------------


ENGINEERING_SYSTEM = (
    "You are a Python debugging expert. When given a buggy function and failing test cases, "
    "fix the bug. Return ONLY the corrected Python code inside a ```python code block. "
    "No explanation."
)

HYPOTHESIS_SYSTEM = (
    "You are a Python debugging expert who reasons about root causes before fixing.\n"
    "When given a buggy function:\n"
    "1. Write exactly one line: 'Hypothesis: <your root-cause hypothesis>'\n"
    "2. Then write the corrected code in a ```python code block.\n"
    "Be concise but explicit about the cause."
)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _build_user_prompt(task: DebugTask) -> str:
    test_lines = "\n".join(f"  {tc}" for tc in task.test_cases)
    return (
        f"Buggy function:\n```python\n{task.buggy_code}```\n\n"
        f"Test cases (must all pass):\n{test_lines}\n\nFix the bug."
    )


def _extract_code(text: str) -> str | None:
    """Extract first Python code block from LLM response."""
    # Prefer ```python ... ``` blocks (allow optional spaces after opening fence)
    match = re.search(r"```(?:python)?\s*\n(.*?)```", text, re.DOTALL)
    if match:
        return match.group(1).strip()
    # Fallback: bare code lines starting with def/import
    lines = [ln for ln in text.splitlines() if ln.startswith(("def ", "import ", "from "))]
    if lines:
        return "\n".join(lines)
    return None


def _extract_hypothesis(text: str) -> str | None:
    """Extract hypothesis line from hypothesis-strategy response."""
    match = re.search(r"[Hh]ypothesis:\s*(.+?)(?:\n|$)", text)
    return match.group(1).strip() if match else None


def _chat(
    client: OpenAI,
    model: str,
    system: str,
    messages: list[dict[str, Any]],
    max_tokens: int = 1024,
    _retries: int = 3,
) -> tuple[str, int, int]:
    """OpenAI chat completions 호출. (응답 텍스트, 입력 토큰, 출력 토큰) 반환."""
    import time
    full_messages = [{"role": "system", "content": system}] + messages
    for attempt in range(_retries):
        response = client.chat.completions.create(
            model=model,
            messages=full_messages,
            max_tokens=max_tokens,
        )
        if response.choices:
            raw = response.choices[0].message.content or ""
            in_tok = response.usage.prompt_tokens if response.usage else 0
            out_tok = response.usage.completion_tokens if response.usage else 0
            return raw, in_tok, out_tok
        # Empty/null response — transient API error, retry with backoff
        wait = 2 ** attempt
        if attempt < _retries - 1:
            time.sleep(wait)
    return "", 0, 0


# ---------------------------------------------------------------------------
# Strategies
# ---------------------------------------------------------------------------


class LLMEngineeringStrategy:
    """Engineering-only LLM strategy: no hypothesis, symptom-driven fixes."""

    def __init__(
        self,
        client: OpenAI | None = None,
        model: str = "MiniMax-M2.5",
    ) -> None:
        self.client = client or _default_client()
        self.model = model

    def run(self, task: DebugTask, max_attempts: int = 5) -> LLMStrategyResult:
        """태스크에 대해 엔지니어링 전략으로 LLM 수정 시도를 실행하고 LLMStrategyResult를 반환."""
        results: list[AttemptResult] = []
        total_input = 0
        total_output = 0

        messages: list[dict[str, Any]] = [{"role": "user", "content": _build_user_prompt(task)}]

        for attempt_num in range(1, max_attempts + 1):
            raw, in_tok, out_tok = _chat(self.client, self.model, ENGINEERING_SYSTEM, messages)
            total_input += in_tok
            total_output += out_tok

            code = _extract_code(raw)
            if code:
                passed, total, solved = _execute_attempt(
                    code, task.function_name, task.test_cases
                )
            else:
                passed, total, solved = 0, len(task.test_cases), False

            attempt = LLMAttemptResult(
                attempt_num=attempt_num,
                success=solved,
                tests_passed=passed,
                tests_total=total,
                input_tokens=in_tok,
                output_tokens=out_tok,
                raw_response=raw,
                extracted_code=code,
            )
            results.append(attempt)

            if solved:
                return LLMStrategyResult(
                    task_id=task.id,
                    strategy="llm_engineering",
                    solved=True,
                    attempts=results,
                    total_attempts=attempt_num,
                    total_input_tokens=total_input,
                    total_output_tokens=total_output,
                )

            # Append failure feedback for next attempt
            messages.append({"role": "assistant", "content": raw})
            messages.append({
                "role": "user",
                "content": (
                    f"That solution passed {passed}/{total} tests. "
                    "Try a different approach to fix the bug."
                ),
            })

        return LLMStrategyResult(
            task_id=task.id,
            strategy="llm_engineering",
            solved=False,
            attempts=results,
            total_attempts=len(results),
            total_input_tokens=total_input,
            total_output_tokens=total_output,
        )


class LLMHypothesisStrategy:
    """Hypothesis-first LLM strategy: explicit causal reasoning before fixing."""

    def __init__(
        self,
        client: OpenAI | None = None,
        model: str = "MiniMax-M2.5",
    ) -> None:
        self.client = client or _default_client()
        self.model = model

    def run(self, task: DebugTask, max_attempts: int = 5) -> LLMStrategyResult:
        """태스크에 대해 가설 전략으로 LLM 수정 시도를 실행하고 LLMStrategyResult를 반환."""
        results: list[AttemptResult] = []
        total_input = 0
        total_output = 0

        messages: list[dict[str, Any]] = [{"role": "user", "content": _build_user_prompt(task)}]

        for attempt_num in range(1, max_attempts + 1):
            raw, in_tok, out_tok = _chat(self.client, self.model, HYPOTHESIS_SYSTEM, messages)
            total_input += in_tok
            total_output += out_tok

            hypothesis = _extract_hypothesis(raw)
            code = _extract_code(raw)

            if code:
                passed, total, solved = _execute_attempt(
                    code, task.function_name, task.test_cases
                )
            else:
                passed, total, solved = 0, len(task.test_cases), False

            attempt = LLMAttemptResult(
                attempt_num=attempt_num,
                success=solved,
                tests_passed=passed,
                tests_total=total,
                hypothesis=hypothesis,
                hypothesis_correct=solved,
                input_tokens=in_tok,
                output_tokens=out_tok,
                raw_response=raw,
                extracted_code=code,
            )
            results.append(attempt)

            if solved:
                return LLMStrategyResult(
                    task_id=task.id,
                    strategy="llm_hypothesis",
                    solved=True,
                    attempts=results,
                    total_attempts=attempt_num,
                    total_input_tokens=total_input,
                    total_output_tokens=total_output,
                )

            # Feedback with hypothesis refinement prompt
            messages.append({"role": "assistant", "content": raw})
            messages.append({
                "role": "user",
                "content": (
                    f"Your solution passed {passed}/{total} tests. "
                    "Revise your hypothesis and fix accordingly."
                ),
            })

        return LLMStrategyResult(
            task_id=task.id,
            strategy="llm_hypothesis",
            solved=False,
            attempts=results,
            total_attempts=len(results),
            total_input_tokens=total_input,
            total_output_tokens=total_output,
        )
