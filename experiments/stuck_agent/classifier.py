"""Rule-based Stuck Type Classifier for stuck-agent experiment.

Given a buggy function's source code and test cases, classifies the bug
into one of four stuck-agent categories:

  red_herring   — symptom appears at a plausible but wrong location;
                  naive first fix addresses the red herring but fails
  semantic_inv  — logic is semantically inverted (boolean, comparison,
                  or return value inversion)
  hidden_assume — function has an implicit contract the code silently violates
  multi_bug     — two or more independent bugs that interact

These categories were empirically found to have DIFFERENT optimal debug strategies:
  red_herring  → hypothesis-driven strategy (+7.5% escape rate)
  semantic_inv → engineering-driven strategy (+40.0% escape rate)

See: Stuck-Agent Escape Rate experiment results (2026-03-31).
"""
from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Any


# ---------------------------------------------------------------------------
# Result type
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class ClassificationResult:
    """Output of StuckTypeClassifier.classify()."""

    category: str                   # predicted category
    confidence: float               # 0.0–1.0 (rule match strength)
    matched_rules: list[str]        # which rules fired
    recommended_strategy: str       # "hypothesis" | "engineering" | "either"
    rationale: str                  # human-readable explanation


# ---------------------------------------------------------------------------
# Rule definitions
# ---------------------------------------------------------------------------

# Patterns suggesting semantic inversion (return/logic flipped)
_SEMANTIC_INV_PATTERNS = [
    # return True/False inversion inside a loop
    (r"return\s+True\b.*\n.*return\s+False\b", "true/false return inversion"),
    (r"return\s+False\b.*\n.*return\s+True\b", "false/true return inversion"),
    # negated comparison used in filter/keep condition
    (r"\bnot\s+\w+\s+in\b", "inverted membership check (not in)"),
    (r"\bif\s+\w+\s+in\s+\w+\s*:", "membership check may be inverted"),
    # wrong operator direction in sort/comparison
    (r"return\s+\w+\s*>\s*\w+.*\n.*return\s+\w+\s*<\s*\w+", "comparison direction mismatch"),
]

# Patterns suggesting a red herring (fix targets symptom, not cause)
_RED_HERRING_PATTERNS = [
    # misleading hint about sorting, breaks, edge cases
    (r"\.sort\(reverse=", "sort direction change (common red herring)"),
    (r"break\b", "early break — may be misleading fix target"),
    (r"if\s+not\s+\w+\s*:", "empty-check guard — typical misleading fix"),
    (r"\.lower\(\)", "case normalization — may address symptom not cause"),
    (r"\.strip\(\)", "strip call — common red-herring patch"),
    # addition instead of multiplication (sign + result vs sign * result)
    (r"\bsign\s*\+\s*result\b", "sign + result arithmetic (should be *)"),
    # zero initialization for max
    (r"max_sum\s*=\s*0\b", "zero initialization for max (red herring for all-neg)"),
]

# Patterns suggesting hidden assumptions
_HIDDEN_ASSUME_PATTERNS = [
    # single return value where multiple expected
    (r"return\s+\w+\b(?!\s*\[)", "single scalar return — may miss multiple-value contract"),
    # function silently assumes input has certain property
    (r"return\s+None\b", "None return — may hide assumption about caller expectations"),
    # Exception swallowing
    (r"except\s+ValueError\s*:\s*\n\s*pass\b", "swallowing ValueError — hides contract violation"),
]

# Patterns suggesting multiple bugs
_MULTI_BUG_PATTERNS = [
    # Two distinct algorithmic operations (normalize: wrong formula + zero-division)
    (r"/\s*\w+\s*\n.*if\s+\w+\s*==\s*0", "division + zero-guard — suggests 2-bug pattern"),
    # Loop range + index access in same function (interleave bug pattern)
    (r"range\(len\(\w+\)\).*\n.*\w+\[i\]\s*\)", "range(len) + index — possible truncation+OOB"),
]


# ---------------------------------------------------------------------------
# Classifier
# ---------------------------------------------------------------------------


class StuckTypeClassifier:
    """Rule-based classifier for stuck-agent bug categories.

    Uses lightweight regex heuristics on the buggy function's source code.
    No ML model required — designed for fast, interpretable classification.

    Recommended strategy by category (from empirical results):
      red_herring  → hypothesis (root-cause reasoning avoids the red herring)
      semantic_inv → engineering (direct code inspection spots the inversion)
      hidden_assume, multi_bug → either (results showed 100% escape for both)
    """

    STRATEGY_MAP: dict[str, str] = {
        "semantic_inv": "engineering",
        "red_herring": "hypothesis",
        "hidden_assume": "either",
        "multi_bug": "either",
    }

    def classify(
        self,
        buggy_code: str,
        test_cases: list[dict[str, Any]] | None = None,
    ) -> ClassificationResult:
        """Classify a buggy function into a stuck-agent category.

        Args:
            buggy_code: source code of the buggy Python function
            test_cases: optional list of test dicts (may inform classification)

        Returns:
            ClassificationResult with predicted category and confidence
        """
        scores: dict[str, float] = {
            "semantic_inv": 0.0,
            "red_herring": 0.0,
            "hidden_assume": 0.0,
            "multi_bug": 0.0,
        }
        matched: dict[str, list[str]] = {k: [] for k in scores}

        # Evaluate each category's patterns
        for pattern, desc in _SEMANTIC_INV_PATTERNS:
            if re.search(pattern, buggy_code, re.DOTALL | re.MULTILINE):
                scores["semantic_inv"] += 1.0
                matched["semantic_inv"].append(desc)

        for pattern, desc in _RED_HERRING_PATTERNS:
            if re.search(pattern, buggy_code, re.DOTALL | re.MULTILINE):
                scores["red_herring"] += 0.7
                matched["red_herring"].append(desc)

        for pattern, desc in _HIDDEN_ASSUME_PATTERNS:
            if re.search(pattern, buggy_code, re.DOTALL | re.MULTILINE):
                scores["hidden_assume"] += 0.8
                matched["hidden_assume"].append(desc)

        for pattern, desc in _MULTI_BUG_PATTERNS:
            if re.search(pattern, buggy_code, re.DOTALL | re.MULTILINE):
                scores["multi_bug"] += 1.0
                matched["multi_bug"].append(desc)

        # Apply test-case-based hints
        if test_cases:
            scores = self._adjust_from_tests(scores, test_cases)

        # Select best category
        best_cat = max(scores, key=lambda k: scores[k])
        best_score = scores[best_cat]

        # Confidence: normalized score vs. total
        total = sum(scores.values())
        confidence = best_score / total if total > 0 else 0.25

        # Fallback: if no patterns matched, default to red_herring (most common)
        if total == 0:
            best_cat = "red_herring"
            confidence = 0.25

        strategy = self.STRATEGY_MAP[best_cat]
        rationale = self._rationale(best_cat, matched[best_cat], confidence)

        return ClassificationResult(
            category=best_cat,
            confidence=round(confidence, 3),
            matched_rules=matched[best_cat],
            recommended_strategy=strategy,
            rationale=rationale,
        )

    def _adjust_from_tests(
        self,
        scores: dict[str, float],
        test_cases: list[dict[str, Any]],
    ) -> dict[str, float]:
        """Use test case patterns to adjust category scores."""
        # boolean expected values → semantic_inv boost
        bool_expected = sum(
            1 for tc in test_cases
            if isinstance(tc.get("expected"), bool)
        )
        if bool_expected >= 2:
            scores["semantic_inv"] += 0.5

        # list expected values → hidden_assume or multi_bug
        list_expected = sum(
            1 for tc in test_cases
            if isinstance(tc.get("expected"), list)
        )
        if list_expected >= 2:
            scores["hidden_assume"] += 0.3
            scores["multi_bug"] += 0.3

        # negative number inputs → red_herring common pattern
        neg_inputs = sum(
            1 for tc in test_cases
            for v in (tc.get("input") or {}).values()
            if isinstance(v, (int, float)) and v < 0
        )
        if neg_inputs >= 1:
            scores["red_herring"] += 0.3

        return scores

    def _rationale(self, category: str, rules: list[str], confidence: float) -> str:
        """Generate human-readable rationale for the classification."""
        desc = {
            "semantic_inv": "logic is semantically inverted (boolean/return value)",
            "red_herring": "symptom points to plausible but incorrect fix location",
            "hidden_assume": "function silently violates an implicit caller contract",
            "multi_bug": "two or more interacting bugs present",
        }
        rule_str = "; ".join(rules[:3]) if rules else "no specific patterns matched"
        return (
            f"Classified as '{category}' ({desc[category]}). "
            f"Confidence: {confidence:.0%}. "
            f"Matched rules: [{rule_str}]."
        )
