"""Strategy simulators for hypothesis-vs-engineering experiment.

Two debugging strategies are compared using researcher-coded attempt sequences.
Each attempt is actual Python code that is exec()'d against real test cases.
No probability models -- results come from actual code execution.

Validity note: attempt code was written by the researcher to represent
"typical fix patterns" for each strategy. This measures the theoretical
upper bound of each strategy, not actual LLM behavior.
"""
from dataclasses import dataclass, field
from typing import Any

from constants import StrategyName
from experiments.hypothesis_validation.tasks import DebugTask


@dataclass(frozen=True)
class AttemptResult:
    """Result of a single debugging attempt for one task."""

    attempt_num: int
    success: bool
    tests_passed: int = 0
    tests_total: int = 0
    hypothesis: str | None = None
    hypothesis_correct: bool | None = None


@dataclass(frozen=True)
class StrategyResult:
    """Aggregated result for one strategy run on a single task."""

    task_id: str
    strategy: StrategyName
    solved: bool
    attempts: list[AttemptResult] = field(default_factory=list)
    total_attempts: int = 0


def _execute_attempt(
    attempt_code: str,
    func_name: str,
    test_cases: list[dict[str, Any]],
) -> tuple[int, int, bool]:
    """Execute attempt code and run test cases against it.

    Returns (passed, total, all_passed).
    Uses compile+exec on trusted researcher-written fixture code only.
    """
    namespace: dict[str, object] = {}
    try:
        compiled = compile(attempt_code, "<attempt>", "exec")
        exec(compiled, namespace)  # noqa: S102 -- trusted researcher fixture code
    except Exception:
        return 0, len(test_cases), False

    fn = namespace.get(func_name)
    if fn is None or not callable(fn):
        return 0, len(test_cases), False

    passed = 0
    total = len(test_cases)
    for tc in test_cases:
        try:
            inp = tc["input"]
            # Special handling for B2 (make_multipliers) which uses expected_check
            if tc.get("expected_check") == "multipliers":
                multipliers = fn(**inp)
                # Correct: multiplier[i](x) == x * i
                n = inp["n"]
                correct = all(m(3) == 3 * i for i, m in enumerate(multipliers))
                if correct:
                    passed += 1
            else:
                result = fn(**inp)
                if result == tc["expected"]:
                    passed += 1
        except Exception:
            pass

    return passed, total, passed == total


# =============================================================================
# Researcher-coded attempt sequences per task
# =============================================================================
# Each dict maps task_id -> list of attempt code strings
# Engineering: no hypothesis, represents "symptom-driven" fix attempts
# Hypothesis: each attempt is (code, hypothesis_text)

ENGINEERING_ATTEMPTS: dict[str, list[str]] = {
    # --- A1: off-by-one in sliding window ---
    "A1": [
        # Attempt 1: Common first try -- just add +1 to range (obvious fix)
        (
            "def find_max_subarray(arr, k):\n"
            "    if len(arr) < k:\n"
            "        return []\n"
            "    max_sum = sum(arr[:k])\n"
            "    max_start = 0\n"
            "    current_sum = max_sum\n"
            "    for i in range(1, len(arr) - k + 1):\n"
            "        current_sum = current_sum - arr[i - 1] + arr[i + k - 1]\n"
            "        if current_sum > max_sum:\n"
            "            max_sum = current_sum\n"
            "            max_start = i\n"
            "    return arr[max_start:max_start + k]\n"
        ),
    ],
    # --- A2: wrong comparison operator ---
    "A2": [
        # Attempt 1: Spot the != vs == immediately
        (
            "def is_palindrome(s):\n"
            "    cleaned = ''.join(c.lower() for c in s if c.isalnum())\n"
            "    return cleaned == cleaned[::-1]\n"
        ),
    ],
    # --- A3: missing zero division check ---
    "A3": [
        # Attempt 1: Add try/except (common but imprecise)
        (
            "def safe_divide(a, b):\n"
            "    try:\n"
            "        return a / b\n"
            "    except ZeroDivisionError:\n"
            "        return None\n"
        ),
    ],
    # --- B1: mutating list during iteration ---
    "B1": [
        # Attempt 1: Use list(set()) -- loses order, fails order-sensitive tests
        (
            "def remove_duplicates(lst):\n"
            "    return list(set(lst))\n"
        ),
        # Attempt 2: Try list comprehension with 'not in' (O(n^2) but correct)
        (
            "def remove_duplicates(lst):\n"
            "    seen = set()\n"
            "    result = []\n"
            "    for item in lst:\n"
            "        if item not in seen:\n"
            "            seen.add(item)\n"
            "            result.append(item)\n"
            "    return result\n"
        ),
    ],
    # --- B2: closure captures loop variable ---
    "B2": [
        # Attempt 1: Try adding a copy of i (wrong approach -- same closure bug)
        (
            "def make_multipliers(n):\n"
            "    result = []\n"
            "    for i in range(n):\n"
            "        def mul(x):\n"
            "            return x * i\n"
            "        result.append(mul)\n"
            "    return result\n"
        ),
        # Attempt 2: Try using a wrapper function (correct -- creates new scope)
        (
            "def make_multipliers(n):\n"
            "    def make_mul(i):\n"
            "        return lambda x: x * i\n"
            "    return [make_mul(i) for i in range(n)]\n"
        ),
    ],
    # --- B3: floating-point equality ---
    "B3": [
        # Attempt 1: Round both sides (fragile, may work for these cases)
        (
            "def are_equal_proportions(a, b, c, d):\n"
            "    return round(a / b, 10) == round(c / d, 10)\n"
        ),
        # Attempt 2: Use epsilon comparison (correct)
        (
            "def are_equal_proportions(a, b, c, d):\n"
            "    return abs((a / b) - (c / d)) < 1e-9\n"
        ),
    ],
    # --- C1: unicode normalization ---
    "C1": [
        # Attempt 1: Try stripping non-ASCII (wrong direction)
        (
            "def count_unique_chars(s):\n"
            "    cleaned = ''.join(c for c in s if ord(c) < 128)\n"
            "    return len(set(cleaned))\n"
        ),
        # Attempt 2: Try using list instead of set (still wrong)
        (
            "def count_unique_chars(s):\n"
            "    chars = []\n"
            "    for c in s:\n"
            "        if c not in chars:\n"
            "            chars.append(c)\n"
            "    return len(chars)\n"
        ),
        # Attempt 3: Try encode/decode (still wrong for combining chars)
        (
            "def count_unique_chars(s):\n"
            "    return len(set(s.encode('utf-8').decode('utf-8')))\n"
        ),
        # Attempt 4: Find unicodedata.normalize (correct)
        (
            "import unicodedata\n"
            "def count_unique_chars(s):\n"
            "    normalized = unicodedata.normalize('NFC', s)\n"
            "    return len(set(normalized))\n"
        ),
    ],
    # --- C2: empty input handling ---
    "C2": [
        # Attempt 1: Add a check but still use max() (correct for these cases)
        (
            "def get_most_frequent(data):\n"
            "    if not data:\n"
            "        return None\n"
            "    freq = {}\n"
            "    for item in data:\n"
            "        freq[item] = freq.get(item, 0) + 1\n"
            "    return max(freq, key=freq.get)\n"
        ),
    ],
    # --- C3: mutable default argument ---
    "C3": [
        # Attempt 1: Use None sentinel pattern (correct)
        (
            "def collect_unique(items, result=None):\n"
            "    if result is None:\n"
            "        result = []\n"
            "    for item in items:\n"
            "        if item not in result:\n"
            "            result.append(item)\n"
            "    return result\n"
        ),
    ],
    # --- A4: binary search off-by-one in loop termination ---
    "A4": [
        # Attempt 1: Fix `< high` to `<= high` (obvious spot, correct immediately)
        (
            "def binary_search(arr, target):\n"
            "    low, high = 0, len(arr) - 1\n"
            "    while low <= high:\n"
            "        mid = (low + high) // 2\n"
            "        if arr[mid] == target:\n"
            "            return mid\n"
            "        elif arr[mid] < target:\n"
            "            low = mid + 1\n"
            "        else:\n"
            "            high = mid - 1\n"
            "    return -1\n"
        ),
    ],
    # --- B4: balanced parens — counter doesn't catch early close ---
    "B4": [
        # Attempt 1: Check counts separately (same logical error — order still ignored)
        (
            "def is_balanced_parens(s):\n"
            "    return s.count('(') == s.count(')')\n"
        ),
        # Attempt 2: Track running count; return False when negative (correct)
        (
            "def is_balanced_parens(s):\n"
            "    count = 0\n"
            "    for c in s:\n"
            "        if c == '(':\n"
            "            count += 1\n"
            "        elif c == ')':\n"
            "            count -= 1\n"
            "        if count < 0:\n"
            "            return False\n"
            "    return count == 0\n"
        ),
    ],
    # --- C4: float currency formatting ---
    "C4": [
        # Attempt 1: Use round() first — same binary float precision issue
        (
            "def format_currency(amount):\n"
            "    return f'${round(amount, 2):.2f}'\n"
        ),
        # Attempt 2: Use Decimal with str() to avoid float imprecision (correct)
        (
            "from decimal import Decimal, ROUND_HALF_UP\n"
            "def format_currency(amount):\n"
            "    d = Decimal(str(amount)).quantize("
            "Decimal('0.01'), rounding=ROUND_HALF_UP)\n"
            "    return f'${d}'\n"
        ),
    ],
}


HYPOTHESIS_ATTEMPTS: dict[str, list[tuple[str, str]]] = {
    # Format: (attempt_code, hypothesis_text)
    # --- A1: off-by-one ---
    "A1": [
        (
            "def find_max_subarray(arr, k):\n"
            "    if len(arr) < k:\n"
            "        return []\n"
            "    max_sum = sum(arr[:k])\n"
            "    max_start = 0\n"
            "    current_sum = max_sum\n"
            "    for i in range(1, len(arr) - k + 1):\n"
            "        current_sum = current_sum - arr[i - 1] + arr[i + k - 1]\n"
            "        if current_sum > max_sum:\n"
            "            max_sum = current_sum\n"
            "            max_start = i\n"
            "    return arr[max_start:max_start + k]\n",
            "range upper bound is off by 1, missing last valid window position",
        ),
    ],
    # --- A2: wrong operator ---
    "A2": [
        (
            "def is_palindrome(s):\n"
            "    cleaned = ''.join(c.lower() for c in s if c.isalnum())\n"
            "    return cleaned == cleaned[::-1]\n",
            "comparison operator is inverted (!=  should be ==)",
        ),
    ],
    # --- A3: missing edge case ---
    "A3": [
        (
            "def safe_divide(a, b):\n"
            "    if b == 0:\n"
            "        return None\n"
            "    return a / b\n",
            "missing guard for b==0 causes ZeroDivisionError",
        ),
    ],
    # --- B1: mutation during iteration ---
    "B1": [
        (
            "def remove_duplicates(lst):\n"
            "    seen = set()\n"
            "    result = []\n"
            "    for item in lst:\n"
            "        if item not in seen:\n"
            "            seen.add(item)\n"
            "            result.append(item)\n"
            "    return result\n",
            "mutating list during iteration causes iterator to skip elements; "
            "build a new list instead",
        ),
    ],
    # --- B2: closure variable capture ---
    "B2": [
        (
            "def make_multipliers(n):\n"
            "    return [lambda x, i=i: x * i for i in range(n)]\n",
            "closure captures loop variable i by reference; all lambdas see "
            "final value. Fix: bind i as default arg",
        ),
    ],
    # --- B3: floating-point equality ---
    "B3": [
        (
            "def are_equal_proportions(a, b, c, d):\n"
            "    return abs((a / b) - (c / d)) < 1e-9\n",
            "direct == on floats fails due to representation error; "
            "use epsilon comparison",
        ),
    ],
    # --- C1: unicode normalization ---
    "C1": [
        (
            "import unicodedata\n"
            "def count_unique_chars(s):\n"
            "    normalized = unicodedata.normalize('NFC', s)\n"
            "    return len(set(normalized))\n",
            "set(s) treats base char + combining mark as separate; "
            "NFC normalization composes them first",
        ),
    ],
    # --- C2: empty input ---
    "C2": [
        (
            "def get_most_frequent(data):\n"
            "    if not data:\n"
            "        return None\n"
            "    from collections import Counter\n"
            "    counter = Counter(data)\n"
            "    return counter.most_common(1)[0][0]\n",
            "max() on empty sequence raises ValueError; "
            "guard empty input and use Counter for clarity",
        ),
    ],
    # --- C3: mutable default argument ---
    "C3": [
        (
            "def collect_unique(items, result=None):\n"
            "    if result is None:\n"
            "        result = []\n"
            "    for item in items:\n"
            "        if item not in result:\n"
            "            result.append(item)\n"
            "    return result\n",
            "mutable default list persists across calls; "
            "use None sentinel and create fresh list per call",
        ),
    ],
    # --- A4: binary search off-by-one ---
    "A4": [
        (
            "def binary_search(arr, target):\n"
            "    low, high = 0, len(arr) - 1\n"
            "    while low <= high:\n"
            "        mid = (low + high) // 2\n"
            "        if arr[mid] == target:\n"
            "            return mid\n"
            "        elif arr[mid] < target:\n"
            "            low = mid + 1\n"
            "        else:\n"
            "            high = mid - 1\n"
            "    return -1\n",
            "loop bound `< high` terminates before checking when low==high; "
            "the single remaining candidate is skipped; fix to `<= high`",
        ),
    ],
    # --- B4: balanced parens counter ---
    "B4": [
        (
            "def is_balanced_parens(s):\n"
            "    count = 0\n"
            "    for c in s:\n"
            "        if c == '(':\n"
            "            count += 1\n"
            "        elif c == ')':\n"
            "            count -= 1\n"
            "        if count < 0:\n"
            "            return False\n"
            "    return count == 0\n",
            "counter cancels out for ')(' ending at 0, hiding invalid ordering; "
            "a negative count means a closing paren appeared before its opener",
        ),
    ],
    # --- C4: float currency formatting ---
    "C4": [
        (
            "from decimal import Decimal, ROUND_HALF_UP\n"
            "def format_currency(amount):\n"
            "    d = Decimal(str(amount)).quantize("
            "Decimal('0.01'), rounding=ROUND_HALF_UP)\n"
            "    return f'${d}'\n",
            "binary float cannot represent 0.675 exactly (stored slightly below); "
            "str(amount) preserves the decimal string, Decimal gives exact arithmetic",
        ),
    ],
}


@dataclass(frozen=True)
class ExperimentMetadata:
    """Explicit validity declaration for this experiment."""

    simulation_type: str = "researcher_coded_attempts"
    validity_claim: str = "within_study_validity"
    limitation: str = (
        "attempt sequences coded by researcher may favor hypothesis strategy"
    )
    what_this_proves: str = (
        "hypothesis_strategy_CAN_solve_in_fewer_attempts_IF_agent_follows_strategy"
    )
    what_this_does_not_prove: str = (
        "real_LLM_will_follow_hypothesis_strategy_correctly"
    )


class EngineeringStrategy:
    """Engineering approach simulation.

    Each task has a sequence of researcher-coded fix attempts representing
    'typical symptom-driven fixes an agent might try without explicit
    causal reasoning'. Attempts are actual Python code exec()'d against
    real test cases. No probability model.
    """

    def run(self, task: DebugTask, max_attempts: int = 5) -> StrategyResult:
        """태스크에 대해 엔지니어링 전략 시도를 순서대로 실행하고 StrategyResult를 반환."""
        attempts_code = ENGINEERING_ATTEMPTS.get(task.id, [])
        results: list[AttemptResult] = []

        for i, code in enumerate(attempts_code):
            if i >= max_attempts:
                break
            passed, total, solved = _execute_attempt(
                code, task.function_name, task.test_cases,
            )
            results.append(AttemptResult(
                attempt_num=i + 1,
                success=solved,
                tests_passed=passed,
                tests_total=total,
                hypothesis=None,
                hypothesis_correct=None,
            ))
            if solved:
                return StrategyResult(
                    task_id=task.id,
                    strategy="engineering",
                    solved=True,
                    attempts=results,
                    total_attempts=i + 1,
                )

        return StrategyResult(
            task_id=task.id,
            strategy="engineering",
            solved=False,  # early return covers the solved=True case
            attempts=results,
            total_attempts=len(results),
        )


class HypothesisStrategy:
    """Hypothesis-driven approach simulation.

    Each task has a sequence of (code, hypothesis) pairs representing
    'causal-reasoning-first fix attempts'. The hypothesis is declared
    before writing the fix. Attempts are actual Python code exec()'d
    against real test cases. No probability model.
    """

    def run(self, task: DebugTask, max_attempts: int = 5) -> StrategyResult:
        """태스크에 대해 가설 전략 시도를 순서대로 실행하고 StrategyResult를 반환."""
        attempts_data = HYPOTHESIS_ATTEMPTS.get(task.id, [])
        results: list[AttemptResult] = []

        for i, (code, hypothesis) in enumerate(attempts_data):
            if i >= max_attempts:
                break
            passed, total, solved = _execute_attempt(
                code, task.function_name, task.test_cases,
            )
            # hypothesis_correct = did this attempt actually solve all tests
            results.append(AttemptResult(
                attempt_num=i + 1,
                success=solved,
                tests_passed=passed,
                tests_total=total,
                hypothesis=hypothesis,
                hypothesis_correct=solved,
            ))
            if solved:
                return StrategyResult(
                    task_id=task.id,
                    strategy="hypothesis",
                    solved=True,
                    attempts=results,
                    total_attempts=i + 1,
                )

        return StrategyResult(
            task_id=task.id,
            strategy="hypothesis",
            solved=False,  # early return covers the solved=True case
            attempts=results,
            total_attempts=len(results),
        )
