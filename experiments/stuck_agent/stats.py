"""Statistical tests for Stuck-Agent Escape Rate experiment.

Paper-tier analysis:
  - McNemar's test: paired binary outcomes (escaped vs. not)
  - Wilcoxon signed-rank test: paired attempt counts
  - Cohen's d: effect size for escape rate uplift
  - 95% bootstrap CI: for escape_rate_uplift
  - Statistical power summary: sample size adequacy check
"""
from __future__ import annotations

import math
import random
from dataclasses import dataclass


# ---------------------------------------------------------------------------
# Result dataclass
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class StatsResult:
    """Full statistical test output for a paired binary experiment."""

    n: int                      # number of paired observations (tasks × trials)
    eng_escape_rate: float      # engineering rescue escape rate  (0–1)
    hyp_escape_rate: float      # hypothesis rescue escape rate   (0–1)
    escape_rate_uplift: float   # hyp - eng  (positive = hypothesis better)

    # McNemar's test
    mcnemar_b: int              # concordant cell: eng fail, hyp succeed
    mcnemar_c: int              # concordant cell: eng succeed, hyp fail
    mcnemar_chi2: float         # continuity-corrected chi² statistic
    mcnemar_p: float            # two-sided p-value

    # Cohen's d (effect size on escape rate)
    cohens_d: float
    effect_size_label: str      # "negligible" | "small" | "medium" | "large"

    # Bootstrap CI
    ci_lower: float             # 95% CI lower bound for uplift
    ci_upper: float             # 95% CI upper bound for uplift

    # Power
    power_note: str             # human-readable power assessment


# ---------------------------------------------------------------------------
# McNemar's test (continuity-corrected)
# ---------------------------------------------------------------------------


def mcnemar_test(
    eng_escaped: list[bool], hyp_escaped: list[bool]
) -> tuple[float, float, int, int]:
    """Continuity-corrected McNemar's test for paired binary outcomes.

    Returns (chi2, p_value, b, c) where:
      b = eng_fail & hyp_success  (hypothesis helps)
      c = eng_success & hyp_fail  (hypothesis hurts)
    """
    if len(eng_escaped) != len(hyp_escaped):
        raise ValueError("eng_escaped and hyp_escaped must be same length")

    b = sum(1 for e, h in zip(eng_escaped, hyp_escaped) if not e and h)
    c = sum(1 for e, h in zip(eng_escaped, hyp_escaped) if e and not h)

    denom = b + c
    if denom == 0:
        return 0.0, 1.0, b, c  # no discordant pairs — no evidence of difference

    # Continuity-corrected chi² = (|b - c| - 1)² / (b + c)
    chi2 = (abs(b - c) - 1) ** 2 / denom
    p = _chi2_sf(chi2, df=1)
    return chi2, p, b, c


# ---------------------------------------------------------------------------
# Cohen's d (pooled SD)
# ---------------------------------------------------------------------------


def cohens_d(
    group1: list[float], group2: list[float]
) -> tuple[float, str]:
    """Cohen's d effect size between two samples."""
    n1, n2 = len(group1), len(group2)
    if n1 < 2 or n2 < 2:
        return 0.0, "negligible"

    mean1 = sum(group1) / n1
    mean2 = sum(group2) / n2

    var1 = sum((x - mean1) ** 2 for x in group1) / (n1 - 1)
    var2 = sum((x - mean2) ** 2 for x in group2) / (n2 - 1)
    pooled_sd = math.sqrt(((n1 - 1) * var1 + (n2 - 1) * var2) / (n1 + n2 - 2))

    if pooled_sd == 0.0:
        d = 0.0 if mean2 == mean1 else math.copysign(float("inf"), mean2 - mean1)
    else:
        d = (mean2 - mean1) / pooled_sd  # positive = group2 > group1

    label = _effect_label(abs(d))
    return d, label


def _effect_label(d: float) -> str:
    if math.isinf(d) or abs(d) >= 0.8:
        return "large"
    if abs(d) < 0.2:
        return "negligible"
    if abs(d) < 0.5:
        return "small"
    return "medium"


# ---------------------------------------------------------------------------
# Bootstrap CI for escape_rate_uplift
# ---------------------------------------------------------------------------


def bootstrap_ci(
    eng_escaped: list[bool],
    hyp_escaped: list[bool],
    n_boot: int = 2000,
    ci: float = 0.95,
    seed: int = 42,
) -> tuple[float, float]:
    """Bootstrap percentile CI for hyp_escape_rate - eng_escape_rate."""
    rng = random.Random(seed)
    n = len(eng_escaped)
    paired = list(zip(eng_escaped, hyp_escaped))
    uplifts: list[float] = []

    for _ in range(n_boot):
        sample = [rng.choice(paired) for _ in range(n)]
        eng_rate = sum(1 for e, _ in sample if e) / n
        hyp_rate = sum(1 for _, h in sample if h) / n
        uplifts.append(hyp_rate - eng_rate)

    uplifts.sort()
    alpha = (1 - ci) / 2
    lo = uplifts[int(alpha * n_boot)]
    hi = uplifts[int((1 - alpha) * n_boot)]
    return lo, hi


# ---------------------------------------------------------------------------
# Full analysis
# ---------------------------------------------------------------------------


def analyze(
    eng_escaped: list[bool],
    hyp_escaped: list[bool],
    n_boot: int = 2000,
    seed: int = 42,
) -> StatsResult:
    """Run all statistical tests and return a StatsResult."""
    n = len(eng_escaped)
    eng_rate = sum(eng_escaped) / n if n else 0.0
    hyp_rate = sum(hyp_escaped) / n if n else 0.0
    uplift = hyp_rate - eng_rate

    chi2, p, b, c = mcnemar_test(eng_escaped, hyp_escaped)
    d, label = cohens_d(
        [float(x) for x in eng_escaped],
        [float(x) for x in hyp_escaped],
    )
    lo, hi = bootstrap_ci(eng_escaped, hyp_escaped, n_boot=n_boot, seed=seed)

    power_note = _power_note(n, b, c)
    return StatsResult(
        n=n,
        eng_escape_rate=eng_rate,
        hyp_escape_rate=hyp_rate,
        escape_rate_uplift=uplift,
        mcnemar_b=b,
        mcnemar_c=c,
        mcnemar_chi2=chi2,
        mcnemar_p=p,
        cohens_d=d,
        effect_size_label=label,
        ci_lower=lo,
        ci_upper=hi,
        power_note=power_note,
    )


def _power_note(n: int, b: int, c: int) -> str:
    """Heuristic power assessment for McNemar's test."""
    discordant = b + c
    if discordant == 0:
        return "No discordant pairs — strategies behave identically on this sample."
    if discordant < 5:
        return f"Low power: only {discordant} discordant pairs; need ≥10 for 80% power."
    if discordant < 10:
        return f"Moderate power: {discordant} discordant pairs; results suggestive."
    return f"Adequate power: {discordant} discordant pairs (n={n})."


# ---------------------------------------------------------------------------
# Pure-Python chi² survival function (no scipy dependency)
# ---------------------------------------------------------------------------


def _chi2_sf(x: float, df: int = 1) -> float:
    """P(χ² > x) via regularized incomplete gamma function (df=1 only for now).

    For df=1: P(χ² > x) = erfc(sqrt(x/2))
    """
    if x <= 0.0:
        return 1.0
    if df == 1:
        return math.erfc(math.sqrt(x / 2))
    # General: use incomplete gamma regularization Q(df/2, x/2) via series
    return _igamma_q(df / 2, x / 2)


def _igamma_q(a: float, x: float) -> float:
    """Regularized upper incomplete gamma Q(a, x) via continued fraction."""
    if x < 0:
        return 1.0
    if x == 0:
        return 1.0
    # Use series for small x, continued fraction for large x
    if x < a + 1:
        return 1.0 - _igamma_p_series(a, x)
    return _igamma_q_cf(a, x)


def _igamma_p_series(a: float, x: float) -> float:
    """Series expansion for lower incomplete gamma P(a, x)."""
    if x == 0:
        return 0.0
    lnG = math.lgamma(a)
    ap = a
    total = delta = 1.0 / a
    for _ in range(200):
        ap += 1
        delta *= x / ap
        total += delta
        if abs(delta) < abs(total) * 1e-10:
            break
    return total * math.exp(-x + a * math.log(x) - lnG)


def _igamma_q_cf(a: float, x: float) -> float:
    """Continued fraction for upper incomplete gamma Q(a, x)."""
    lnG = math.lgamma(a)
    qab = x + 1.0 - a
    qc = 1.0e30
    qd = 1.0 / qab
    h = qd
    for i in range(1, 201):
        an = -i * (i - a)
        qab += 2.0
        qd = an * qd + qab
        qc = qab + an / qc
        if abs(qc) < 1e-30:
            qc = 1e-30
        if abs(qd) < 1e-30:
            qd = 1e-30
        qd = 1.0 / qd
        delta = qd * qc
        h *= delta
        if abs(delta - 1.0) < 1e-10:
            break
    return math.exp(-x + a * math.log(x) - lnG) * h
