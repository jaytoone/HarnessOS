"""Debug tasks for hypothesis-vs-engineering experiment.

9 buggy Python functions across 3 difficulty categories:
  A (simple): obvious bugs
  B (causal): requires causal reasoning
  C (assumption): wrong implicit assumptions
"""
from dataclasses import dataclass, field


@dataclass
class DebugTask:
    id: str
    category: str  # "simple" | "causal" | "assumption"
    function_name: str
    buggy_code: str
    correct_code: str
    bug_description: str
    test_cases: list[dict] = field(default_factory=list)


def get_debug_tasks() -> list[DebugTask]:
    """Return all 9 debug tasks."""
    return [
        # --- Category A: Simple (obvious bugs) ---
        DebugTask(
            id="A1",
            category="simple",
            function_name="find_max_subarray",
            buggy_code=(
                "def find_max_subarray(arr, k):\n"
                "    if len(arr) < k:\n"
                "        return []\n"
                "    max_sum = sum(arr[:k])\n"
                "    max_start = 0\n"
                "    current_sum = max_sum\n"
                "    for i in range(1, len(arr) - k):\n"
                "        current_sum = current_sum - arr[i - 1] + arr[i + k - 1]\n"
                "        if current_sum > max_sum:\n"
                "            max_sum = current_sum\n"
                "            max_start = i\n"
                "    return arr[max_start:max_start + k]\n"
            ),
            correct_code=(
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
            bug_description="Off-by-one: range(len(arr) - k) misses the last window; should be range(len(arr) - k + 1).",
            test_cases=[
                {"input": {"arr": [1, 3, 2, 5, 1], "k": 2}, "expected": [2, 5]},
                {"input": {"arr": [5, 1, 1, 1, 9], "k": 2}, "expected": [1, 9]},
                {"input": {"arr": [1], "k": 2}, "expected": []},
            ],
        ),
        DebugTask(
            id="A2",
            category="simple",
            function_name="is_palindrome",
            buggy_code=(
                "def is_palindrome(s):\n"
                "    cleaned = ''.join(c.lower() for c in s if c.isalnum())\n"
                "    return cleaned != cleaned[::-1]\n"
            ),
            correct_code=(
                "def is_palindrome(s):\n"
                "    cleaned = ''.join(c.lower() for c in s if c.isalnum())\n"
                "    return cleaned == cleaned[::-1]\n"
            ),
            bug_description="Wrong operator: != should be ==.",
            test_cases=[
                {"input": {"s": "racecar"}, "expected": True},
                {"input": {"s": "hello"}, "expected": False},
                {"input": {"s": "A man a plan a canal Panama"}, "expected": True},
            ],
        ),
        DebugTask(
            id="A3",
            category="simple",
            function_name="safe_divide",
            buggy_code=(
                "def safe_divide(a, b):\n"
                "    return a / b\n"
            ),
            correct_code=(
                "def safe_divide(a, b):\n"
                "    if b == 0:\n"
                "        return None\n"
                "    return a / b\n"
            ),
            bug_description="Missing edge case: no check for division by zero.",
            test_cases=[
                {"input": {"a": 10, "b": 2}, "expected": 5.0},
                {"input": {"a": 1, "b": 0}, "expected": None},
                {"input": {"a": -6, "b": 3}, "expected": -2.0},
            ],
        ),
        # --- Category B: Causal Reasoning ---
        DebugTask(
            id="B1",
            category="causal",
            function_name="remove_duplicates",
            buggy_code=(
                "def remove_duplicates(lst):\n"
                "    seen = set()\n"
                "    for item in lst:\n"
                "        if item in seen:\n"
                "            lst.remove(item)\n"
                "        else:\n"
                "            seen.add(item)\n"
                "    return lst\n"
            ),
            correct_code=(
                "def remove_duplicates(lst):\n"
                "    seen = set()\n"
                "    result = []\n"
                "    for item in lst:\n"
                "        if item not in seen:\n"
                "            seen.add(item)\n"
                "            result.append(item)\n"
                "    return result\n"
            ),
            bug_description="Mutating list during iteration causes skipped elements.",
            test_cases=[
                {"input": {"lst": [1, 2, 3, 2, 1]}, "expected": [1, 2, 3]},
                {"input": {"lst": [1, 1, 1, 1]}, "expected": [1]},
                {"input": {"lst": [5, 3, 5, 3, 5]}, "expected": [5, 3]},
            ],
        ),
        DebugTask(
            id="B2",
            category="causal",
            function_name="make_multipliers",
            buggy_code=(
                "def make_multipliers(n):\n"
                "    return [lambda x: x * i for i in range(n)]\n"
            ),
            correct_code=(
                "def make_multipliers(n):\n"
                "    return [lambda x, i=i: x * i for i in range(n)]\n"
            ),
            bug_description="Closure captures loop variable by reference; all lambdas use final value of i.",
            test_cases=[
                {"input": {"n": 4}, "expected_check": "multipliers"},
                {"input": {"n": 3}, "expected_check": "multipliers"},
            ],
        ),
        DebugTask(
            id="B3",
            category="causal",
            function_name="are_equal_proportions",
            buggy_code=(
                "def are_equal_proportions(a, b, c, d):\n"
                "    return (a / b) == (c / d)\n"
            ),
            correct_code=(
                "def are_equal_proportions(a, b, c, d):\n"
                "    return abs((a / b) - (c / d)) < 1e-9\n"
            ),
            bug_description="Direct floating-point equality comparison fails due to precision errors.",
            test_cases=[
                {"input": {"a": 1, "b": 3, "c": 2, "d": 6}, "expected": True},
                {"input": {"a": 0.1, "b": 0.3, "c": 1, "d": 3}, "expected": True},
                {"input": {"a": 1, "b": 2, "c": 1, "d": 3}, "expected": False},
            ],
        ),
        # --- Category C: Wrong Assumption ---
        DebugTask(
            id="C1",
            category="assumption",
            function_name="count_unique_chars",
            buggy_code=(
                "def count_unique_chars(s):\n"
                "    return len(set(s))\n"
            ),
            correct_code=(
                "import unicodedata\n"
                "def count_unique_chars(s):\n"
                "    normalized = unicodedata.normalize('NFC', s)\n"
                "    return len(set(normalized))\n"
            ),
            bug_description="Assumes NFC normalization; combining characters (e.g. e + accent) counted separately.",
            test_cases=[
                {"input": {"s": "hello"}, "expected": 4},
                {"input": {"s": "e\u0301"}, "expected": 1},  # e + combining accent = one char after NFC
                {"input": {"s": "nae\u0308ve"}, "expected": 5},  # n,a,uml-e,v,e = 5 unique after NFC
            ],
        ),
        DebugTask(
            id="C2",
            category="assumption",
            function_name="get_most_frequent",
            buggy_code=(
                "def get_most_frequent(data):\n"
                "    freq = {}\n"
                "    for item in data:\n"
                "        freq[item] = freq.get(item, 0) + 1\n"
                "    return max(freq, key=freq.get)\n"
            ),
            correct_code=(
                "def get_most_frequent(data):\n"
                "    from collections import Counter\n"
                "    if not data:\n"
                "        return None\n"
                "    counter = Counter(data)\n"
                "    return counter.most_common(1)[0][0]\n"
            ),
            bug_description="Fails on empty input (max() on empty dict). Also, dict ordering assumption is misleading.",
            test_cases=[
                {"input": {"data": [1, 2, 2, 3, 3, 3]}, "expected": 3},
                {"input": {"data": []}, "expected": None},
                {"input": {"data": ["a", "b", "a"]}, "expected": "a"},
            ],
        ),
        DebugTask(
            id="C3",
            category="assumption",
            function_name="cached_fibonacci",
            buggy_code=(
                "def cached_fibonacci(n, cache={}):\n"
                "    if n in cache:\n"
                "        return cache[n]\n"
                "    if n <= 1:\n"
                "        return n\n"
                "    result = cached_fibonacci(n - 1) + cached_fibonacci(n - 2)\n"
                "    cache[n] = result\n"
                "    return result\n"
            ),
            correct_code=(
                "def cached_fibonacci(n, cache=None):\n"
                "    if cache is None:\n"
                "        cache = {}\n"
                "    if n in cache:\n"
                "        return cache[n]\n"
                "    if n <= 1:\n"
                "        return n\n"
                "    result = cached_fibonacci(n - 1, cache) + cached_fibonacci(n - 2, cache)\n"
                "    cache[n] = result\n"
                "    return result\n"
            ),
            bug_description="Mutable default argument shares state across calls; intended as per-call cache but persists.",
            test_cases=[
                {"input": {"n": 0}, "expected": 0},
                {"input": {"n": 1}, "expected": 1},
                {"input": {"n": 10}, "expected": 55},
            ],
        ),
    ]
