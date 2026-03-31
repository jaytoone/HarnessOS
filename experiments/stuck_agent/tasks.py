"""Deceptive bug tasks for Stuck-Agent Escape Rate experiment.

8 tasks across 4 categories, each designed so that a naive first-pass
engineering fix fails (misleading_fix_code), while hypothesis-driven
reasoning finds the true root cause (correct_code).

Categories:
  red_herring    — symptom appears at wrong location
  multi_bug      — two interacting bugs; fixing one exposes/hides the other
  hidden_assume  — implicit contract the function silently violates
  semantic_inv   — logic is semantically inverted in a non-obvious way
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from constants import StuckTaskCategory


@dataclass(frozen=True)
class StuckTask:
    """A debug task designed to expose stuck-agent behavior.

    Fields:
        id               — unique identifier (D1–D8)
        category         — deception type
        function_name    — the Python function to fix
        buggy_code       — the original broken code
        misleading_fix_code — what engineering typically tries first (still wrong)
        correct_code     — the real fix
        bug_description  — human-readable root cause
        misleading_description — why the misleading fix seems reasonable
        test_cases       — executable tests that distinguish all three versions
    """

    id: str
    category: StuckTaskCategory
    function_name: str
    buggy_code: str
    misleading_fix_code: str
    correct_code: str
    bug_description: str
    misleading_description: str
    test_cases: list[dict[str, Any]] = field(default_factory=list)
    # Injected into phase-1 prompt to steer LLM toward the wrong fix (red herring).
    # This makes stuck state controlled and reproducible.
    misleading_hint: str = ""


def get_stuck_tasks() -> list[StuckTask]:
    """Return all 8 stuck-agent tasks."""
    return [
        # ── Category: red_herring ──────────────────────────────────────────
        StuckTask(
            id="D1",
            category="red_herring",
            function_name="max_product_pair",
            misleading_hint="Hint from senior engineer: the issue is that .sort() sorts in ascending order by default — try sorting in descending order to get the two largest values.",
            buggy_code=(
                "def max_product_pair(nums):\n"
                "    nums.sort()\n"
                "    return nums[-1] * nums[-2]\n"
            ),
            misleading_fix_code=(
                # Engineering sees "sort" and thinks maybe the sort direction is wrong
                "def max_product_pair(nums):\n"
                "    nums.sort(reverse=True)\n"
                "    return nums[-1] * nums[-2]\n"
            ),
            correct_code=(
                "def max_product_pair(nums):\n"
                "    nums.sort()\n"
                "    return max(nums[-1] * nums[-2], nums[0] * nums[1])\n"
            ),
            bug_description=(
                "Only checks the two largest positives; misses two large negatives "
                "whose product can exceed the top-two positive product."
            ),
            misleading_description=(
                "Engineering sees .sort() and suspects direction — tries reverse=True "
                "but that still only checks bottom-two, which is also wrong."
            ),
            test_cases=[
                {"input": {"nums": [1, 2, 3, 4]}, "expected": 12},
                {"input": {"nums": [-10, -9, 1, 2]}, "expected": 90},
                {"input": {"nums": [-5, -4, 3, 2]}, "expected": 20},
                {"input": {"nums": [0, 1, 2, 3]}, "expected": 6},
            ],
        ),
        StuckTask(
            id="D2",
            category="red_herring",
            function_name="count_subarrays_equal_sum",
            misleading_hint="Hint from bug report: the function terminates the inner loop too early for certain inputs — removing the break statement should fix the counting issue.",
            buggy_code=(
                "def count_subarrays_equal_sum(arr, target):\n"
                "    count = 0\n"
                "    for i in range(len(arr)):\n"
                "        current = 0\n"
                "        for j in range(i, len(arr)):\n"
                "            current += arr[j]\n"
                "            if current == target:\n"
                "                count += 1\n"
                "                break\n"  # red herring: break stops early
                "    return count\n"
            ),
            misleading_fix_code=(
                # Engineering sees break → might try removing it but keep other issues
                "def count_subarrays_equal_sum(arr, target):\n"
                "    count = 0\n"
                "    for i in range(len(arr)):\n"
                "        current = 0\n"
                "        for j in range(i, len(arr)):\n"
                "            current += arr[j]\n"
                "            if current == target:\n"
                "                count += 1\n"
                # no break — but for positive arrays only this still misses negative sums
                "    return count\n"
            ),
            correct_code=(
                "def count_subarrays_equal_sum(arr, target):\n"
                "    count = 0\n"
                "    prefix_counts: dict[int, int] = {0: 1}\n"
                "    current = 0\n"
                "    for x in arr:\n"
                "        current += x\n"
                "        count += prefix_counts.get(current - target, 0)\n"
                "        prefix_counts[current] = prefix_counts.get(current, 0) + 1\n"
                "    return count\n"
            ),
            bug_description=(
                "The break stops counting after the first subarray ending at position j "
                "that equals target, missing overlapping subarrays starting at i."
            ),
            misleading_description=(
                "Removing break fixes the overlapping case for positive arrays but "
                "is still O(n²) and wrong for arrays with negative numbers."
            ),
            test_cases=[
                {"input": {"arr": [1, 1, 1], "target": 2}, "expected": 2},
                # break fails here: arr[0..1]=[1,2] and arr[0..3]=[1,2,-1,1] both sum to 3
                {"input": {"arr": [1, 2, -1, 1], "target": 3}, "expected": 2},
                {"input": {"arr": [-1, 1, 1], "target": 1}, "expected": 3},
                {"input": {"arr": [1], "target": 1}, "expected": 1},
            ],
        ),
        # ── Category: multi_bug ───────────────────────────────────────────
        StuckTask(
            id="D3",
            category="multi_bug",
            function_name="normalize_scores",
            misleading_hint="Hint from code review: the function crashes when all scores are zero — add a guard for division by zero and it should work correctly.",
            buggy_code=(
                "def normalize_scores(scores):\n"
                "    max_score = max(scores)\n"
                "    return [s / max_score for s in scores]\n"
            ),
            misleading_fix_code=(
                # Engineering adds zero-division guard (fixes crash but wrong formula)
                "def normalize_scores(scores):\n"
                "    max_score = max(scores)\n"
                "    if max_score == 0:\n"
                "        return [0.0] * len(scores)\n"
                "    return [s / max_score for s in scores]\n"
            ),
            correct_code=(
                "def normalize_scores(scores):\n"
                "    mn, mx = min(scores), max(scores)\n"
                "    if mx == mn:\n"
                "        return [0.0] * len(scores)\n"
                "    return [(s - mn) / (mx - mn) for s in scores]\n"
            ),
            bug_description=(
                "Bug 1: divides by max instead of range (mx-mn), so scores with a "
                "non-zero minimum are not normalized to [0,1]. "
                "Bug 2: all-equal case causes division by zero."
            ),
            misleading_description=(
                "Adding a zero guard prevents the crash from Bug 2 but Bug 1 (wrong "
                "formula) remains — e.g. scores=[3,4,5] normalize to [0.6,0.8,1.0] "
                "instead of [0.0,0.5,1.0]."
            ),
            test_cases=[
                {"input": {"scores": [0, 50, 100]}, "expected": [0.0, 0.5, 1.0]},
                {"input": {"scores": [3, 4, 5]}, "expected": [0.0, 0.5, 1.0]},
                {"input": {"scores": [7, 7, 7]}, "expected": [0.0, 0.0, 0.0]},
                {"input": {"scores": [1, 2]}, "expected": [0.0, 1.0]},
            ],
        ),
        StuckTask(
            id="D4",
            category="multi_bug",
            function_name="interleave_lists",
            misleading_hint="Hint from bug report: the function raises an IndexError when list b is shorter than a — use min(len(a), len(b)) in the range() to fix the crash.",
            buggy_code=(
                "def interleave_lists(a, b):\n"
                "    result = []\n"
                "    for i in range(len(a)):\n"  # Bug 1: stops at len(a)
                "        result.append(a[i])\n"
                "        result.append(b[i])\n"  # Bug 2: index error if b shorter
                "    return result\n"
            ),
            misleading_fix_code=(
                # Engineering adds min() guard — fixes crash but still truncates
                "def interleave_lists(a, b):\n"
                "    result = []\n"
                "    for i in range(min(len(a), len(b))):\n"
                "        result.append(a[i])\n"
                "        result.append(b[i])\n"
                "    return result\n"
            ),
            correct_code=(
                "def interleave_lists(a, b):\n"
                "    result = []\n"
                "    i = 0\n"
                "    while i < len(a) or i < len(b):\n"
                "        if i < len(a):\n"
                "            result.append(a[i])\n"
                "        if i < len(b):\n"
                "            result.append(b[i])\n"
                "        i += 1\n"
                "    return result\n"
            ),
            bug_description=(
                "Bug 1: range(len(a)) skips remaining b elements when b is longer. "
                "Bug 2: b[i] raises IndexError when b is shorter than a."
            ),
            misleading_description=(
                "min() guard fixes the crash but silently drops the tail of whichever "
                "list is longer — both lists must be fully included."
            ),
            test_cases=[
                {"input": {"a": [1, 2], "b": [3, 4]}, "expected": [1, 3, 2, 4]},
                {"input": {"a": [1, 2, 3], "b": [4]}, "expected": [1, 4, 2, 3]},
                {"input": {"a": [1], "b": [2, 3, 4]}, "expected": [1, 2, 3, 4]},
                {"input": {"a": [], "b": [1]}, "expected": [1]},
            ],
        ),
        # ── Category: hidden_assume ───────────────────────────────────────
        StuckTask(
            id="D5",
            category="hidden_assume",
            function_name="find_duplicate",
            misleading_hint="Hint: the function doesn't handle the empty list edge case — add an early return for empty input and the tests should pass.",
            buggy_code=(
                "def find_duplicate(nums):\n"
                "    seen = set()\n"
                "    for n in nums:\n"
                "        if n in seen:\n"
                "            return n\n"
                "        seen.add(n)\n"
                "    return None\n"
            ),
            misleading_fix_code=(
                # Engineering adds early return optimization — doesn't address
                # the assumption that only ONE duplicate exists
                "def find_duplicate(nums):\n"
                "    if not nums:\n"
                "        return None\n"
                "    seen = set()\n"
                "    for n in nums:\n"
                "        if n in seen:\n"
                "            return n\n"
                "        seen.add(n)\n"
                "    return None\n"
            ),
            correct_code=(
                "def find_duplicate(nums):\n"
                "    seen = set()\n"
                "    duplicates = []\n"
                "    for n in nums:\n"
                "        if n in seen and n not in duplicates:\n"
                "            duplicates.append(n)\n"
                "        seen.add(n)\n"
                "    return duplicates if duplicates else None\n"
            ),
            bug_description=(
                "Assumes only one duplicate exists — returns immediately on first "
                "duplicate, silently missing all subsequent duplicates."
            ),
            misleading_description=(
                "Adding empty-list guard is a reasonable defensive check but doesn't "
                "fix the hidden assumption: callers expect ALL duplicates returned."
            ),
            test_cases=[
                {"input": {"nums": [1, 2, 3, 2]}, "expected": [2]},
                {"input": {"nums": [1, 1, 2, 2]}, "expected": [1, 2]},
                {"input": {"nums": [1, 2, 3]}, "expected": None},
                {"input": {"nums": [3, 3, 3]}, "expected": [3]},
            ],
        ),
        StuckTask(
            id="D6",
            category="hidden_assume",
            function_name="parse_key_value",
            misleading_hint="Hint from error log: the function throws ValueError on malformed input — wrap the split in a try/except to handle bad pairs gracefully.",
            buggy_code=(
                "def parse_key_value(s):\n"
                "    result = {}\n"
                "    for pair in s.split(','):\n"
                "        k, v = pair.split('=')\n"
                "        result[k.strip()] = v.strip()\n"
                "    return result\n"
            ),
            misleading_fix_code=(
                # Engineering adds try/except for malformed pairs
                "def parse_key_value(s):\n"
                "    result = {}\n"
                "    for pair in s.split(','):\n"
                "        try:\n"
                "            k, v = pair.split('=')\n"
                "            result[k.strip()] = v.strip()\n"
                "        except ValueError:\n"
                "            pass\n"
                "    return result\n"
            ),
            correct_code=(
                "def parse_key_value(s):\n"
                "    result = {}\n"
                "    for pair in s.split(','):\n"
                "        if '=' not in pair:\n"
                "            continue\n"
                "        k, _, v = pair.partition('=')\n"
                "        result[k.strip()] = v.strip()\n"
                "    return result\n"
            ),
            bug_description=(
                "pair.split('=') raises ValueError when pair contains no '=' and "
                "raises ValueError with too many values when value itself contains '='."
            ),
            misleading_description=(
                "Silently swallowing ValueError hides parse errors but still returns "
                "partial results — values containing '=' are still silently dropped."
            ),
            test_cases=[
                {"input": {"s": "a=1,b=2"}, "expected": {"a": "1", "b": "2"}},
                {"input": {"s": "url=http://x=y,c=3"}, "expected": {"url": "http://x=y", "c": "3"}},
                {"input": {"s": "k=v,noequals,m=n"}, "expected": {"k": "v", "m": "n"}},
                {"input": {"s": "x=1"}, "expected": {"x": "1"}},
            ],
        ),
        # ── Category: semantic_inv ────────────────────────────────────────
        StuckTask(
            id="D7",
            category="semantic_inv",
            function_name="filter_valid_emails",
            misleading_hint="Hint: the boundary condition uses strict less-than (<) which may be off-by-one — try changing < to <= in the condition check.",
            buggy_code=(
                "def filter_valid_emails(emails):\n"
                "    valid = []\n"
                "    for e in emails:\n"
                "        at = e.find('@')\n"
                "        dot = e.rfind('.')\n"
                "        if at < 0 or dot < at:\n"  # inverted: should be dot > at
                "            valid.append(e)\n"
                "    return valid\n"
            ),
            misleading_fix_code=(
                # Engineering changes < to <= (boundary fix, not root cause)
                "def filter_valid_emails(emails):\n"
                "    valid = []\n"
                "    for e in emails:\n"
                "        at = e.find('@')\n"
                "        dot = e.rfind('.')\n"
                "        if at <= 0 or dot <= at:\n"
                "            valid.append(e)\n"
                "    return valid\n"
            ),
            correct_code=(
                "def filter_valid_emails(emails):\n"
                "    valid = []\n"
                "    for e in emails:\n"
                "        at = e.find('@')\n"
                "        dot = e.rfind('.')\n"
                "        if at > 0 and dot > at:\n"
                "            valid.append(e)\n"
                "    return valid\n"
            ),
            bug_description=(
                "Condition is semantically inverted: `at < 0 or dot < at` keeps "
                "INVALID emails (no @ or dot before @) and filters out valid ones. "
                "Should be `at > 0 and dot > at`."
            ),
            misleading_description=(
                "Changing < to <= still keeps the inverted OR/AND logic — swapping "
                "to <= just shifts the boundary without fixing the inversion."
            ),
            test_cases=[
                {"input": {"emails": ["a@b.com", "bad", "x@y.z"]},
                 "expected": ["a@b.com", "x@y.z"]},
                {"input": {"emails": ["no-at.com", "a@b.com"]}, "expected": ["a@b.com"]},
                {"input": {"emails": ["@nodomain", "ok@test.io"]}, "expected": ["ok@test.io"]},
                {"input": {"emails": []}, "expected": []},
            ],
        ),
        StuckTask(
            id="D8",
            category="semantic_inv",
            function_name="is_strictly_increasing",
            misleading_hint="Hint from code review: the comparison operator >= should be > for strictly increasing (not non-decreasing) — change >= to > in the condition.",
            buggy_code=(
                "def is_strictly_increasing(nums):\n"
                "    for i in range(len(nums) - 1):\n"
                "        if nums[i] >= nums[i + 1]:\n"  # correct condition
                "            return True\n"              # inverted: should return False
                "    return False\n"                     # inverted: should return True
            ),
            misleading_fix_code=(
                # Engineering changes >= to > (tweaks operator, misses the inversion)
                "def is_strictly_increasing(nums):\n"
                "    for i in range(len(nums) - 1):\n"
                "        if nums[i] > nums[i + 1]:\n"
                "            return True\n"
                "    return False\n"
            ),
            correct_code=(
                "def is_strictly_increasing(nums):\n"
                "    for i in range(len(nums) - 1):\n"
                "        if nums[i] >= nums[i + 1]:\n"
                "            return False\n"
                "    return True\n"
            ),
            bug_description=(
                "Return values are semantically inverted: returns True on failure "
                "condition and False after passing all checks."
            ),
            misleading_description=(
                "Changing >= to > addresses strict vs non-strict but not the "
                "inversion — the function still returns True for non-increasing sequences."
            ),
            test_cases=[
                {"input": {"nums": [1, 2, 3]}, "expected": True},
                {"input": {"nums": [1, 1, 2]}, "expected": False},
                {"input": {"nums": [3, 2, 1]}, "expected": False},
                {"input": {"nums": [5]}, "expected": True},
            ],
        ),
    ]
