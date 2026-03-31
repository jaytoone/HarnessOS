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
# Exact McNemar p-value (binomial-based)
# ---------------------------------------------------------------------------


def mcnemar_exact_p(b: int, c: int) -> float:
    """Exact two-sided p-value for McNemar's test via binomial distribution.

    Under H0: P(discordant pair favors hyp) = 0.5.
    p = 2 * P(X <= min(b,c)) where X ~ Binomial(b+c, 0.5).
    """
    n = b + c
    if n == 0:
        return 1.0
    lo = min(b, c)
    p = 2.0 * sum(_binom_pmf(n, k, 0.5) for k in range(lo + 1))
    return min(p, 1.0)


def _binom_pmf(n: int, k: int, p: float) -> float:
    """Binomial PMF: C(n,k) * p^k * (1-p)^(n-k)."""
    log_pmf = _log_comb(n, k) + k * math.log(p) + (n - k) * math.log(1 - p)
    return math.exp(log_pmf)


def _log_comb(n: int, k: int) -> float:
    """log C(n, k) via log-gamma for numerical stability."""
    return math.lgamma(n + 1) - math.lgamma(k + 1) - math.lgamma(n - k + 1)


# ---------------------------------------------------------------------------
# Power analysis for McNemar's test
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class PowerAnalysisResult:
    """Required sample size for McNemar's test at target power."""

    category: str
    current_n: int
    current_b: int
    current_c: int
    current_p: float
    estimated_discordant_rate: float  # (b+c)/n — proportion of discordant pairs
    estimated_effect: float           # |b-c|/(b+c) — directional imbalance
    required_n_for_significance: int  # n needed to reach p < alpha
    trials_per_task: int              # assuming fixed task count, trials needed
    task_count: int


def power_analysis_by_category(
    category: str,
    eng_escaped: list[bool],
    hyp_escaped: list[bool],
    task_count: int,
    alpha: float = 0.05,
) -> PowerAnalysisResult:
    """Estimate required n to achieve p < alpha for a given category.

    Uses simulation: iterates n from current to 500, scaling discordant pair
    counts proportionally, until exact p < alpha.
    """
    n = len(eng_escaped)
    b = sum(1 for e, h in zip(eng_escaped, hyp_escaped) if not e and h)
    c = sum(1 for e, h in zip(eng_escaped, hyp_escaped) if e and not h)
    current_p = mcnemar_exact_p(b, c)

    if n == 0:
        return PowerAnalysisResult(
            category=category, current_n=0, current_b=0, current_c=0,
            current_p=1.0, estimated_discordant_rate=0.0, estimated_effect=0.0,
            required_n_for_significance=-1, trials_per_task=-1, task_count=task_count,
        )

    disc_rate = (b + c) / n
    effect = abs(b - c) / (b + c) if (b + c) > 0 else 0.0

    # Scale b and c proportionally as n grows
    required_n = -1
    for test_n in range(n, 2001):
        scaled_b = round(b * test_n / n)
        scaled_c = round(c * test_n / n)
        if mcnemar_exact_p(scaled_b, scaled_c) < alpha:
            required_n = test_n
            break

    trials_needed = math.ceil(required_n / task_count) if required_n > 0 else -1

    return PowerAnalysisResult(
        category=category,
        current_n=n,
        current_b=b,
        current_c=c,
        current_p=current_p,
        estimated_discordant_rate=disc_rate,
        estimated_effect=effect,
        required_n_for_significance=required_n,
        trials_per_task=trials_needed,
        task_count=task_count,
    )


# ---------------------------------------------------------------------------
# Category-level analysis
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class CategoryStatsResult:
    """Statistical summary for a single stuck-agent category."""

    category: str
    n: int
    eng_escape_rate: float
    hyp_escape_rate: float
    uplift: float
    mcnemar_b: int
    mcnemar_c: int
    mcnemar_exact_p: float
    significant: bool   # p < 0.05
    power_analysis: PowerAnalysisResult


def analyze_by_category(
    tasks: list[dict],
    task_count_by_category: dict[str, int] | None = None,
) -> dict[str, CategoryStatsResult]:
    """Compute per-category McNemar exact p and power analysis.

    Args:
        tasks: list of task dicts from results JSON (each with eng_escaped, hyp_escaped, category)
        task_count_by_category: {category: unique_task_count} — for power analysis trials calc
    """
    from collections import defaultdict
    by_cat: dict[str, dict[str, list[bool]]] = defaultdict(lambda: {"eng": [], "hyp": []})

    for t in tasks:
        if t.get("phase1_passed", False):
            continue
        cat = t.get("category", "unknown")
        by_cat[cat]["eng"].append(bool(t.get("eng_escaped", False)))
        by_cat[cat]["hyp"].append(bool(t.get("hyp_escaped", False)))

    results: dict[str, CategoryStatsResult] = {}
    for cat, vals in sorted(by_cat.items()):
        eng = vals["eng"]
        hyp = vals["hyp"]
        n = len(eng)
        b = sum(1 for e, h in zip(eng, hyp) if not e and h)
        c = sum(1 for e, h in zip(eng, hyp) if e and not h)
        p = mcnemar_exact_p(b, c)
        task_count = (task_count_by_category or {}).get(cat, max(1, n // 5))
        pa = power_analysis_by_category(cat, eng, hyp, task_count=task_count)

        results[cat] = CategoryStatsResult(
            category=cat,
            n=n,
            eng_escape_rate=sum(eng) / n if n else 0.0,
            hyp_escape_rate=sum(hyp) / n if n else 0.0,
            uplift=(sum(hyp) - sum(eng)) / n if n else 0.0,
            mcnemar_b=b,
            mcnemar_c=c,
            mcnemar_exact_p=p,
            significant=p < 0.05,
            power_analysis=pa,
        )
    return results


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


# ---------------------------------------------------------------------------
# Bootstrap Variance Estimator — effect size collapse risk predictor
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class BootstrapEffectResult:
    """Bootstrap-based effect size variance estimate for a category."""

    category: str
    n: int
    observed_effect: float           # |b-c|/(b+c) from raw data
    bootstrap_mean: float            # mean effect across bootstrap resamples
    bootstrap_std: float             # std dev of bootstrapped effects
    ci_90_lower: float               # 5th percentile of bootstrapped effects
    ci_90_upper: float               # 95th percentile of bootstrapped effects
    collapse_risk: str               # "HIGH" | "MEDIUM" | "LOW"
    collapse_threshold: float        # effect size below which collapse is likely
    collapse_probability: float      # P(bootstrap effect < collapse_threshold)


def bootstrap_effect_variance(
    category: str,
    eng_escaped: list[bool],
    hyp_escaped: list[bool],
    n_bootstrap: int = 2000,
    collapse_threshold_ratio: float = 0.3,
    seed: int = 42,
) -> BootstrapEffectResult:
    """Estimate effect size variance and collapse risk via bootstrap.

    Resamples (eng, hyp) pairs with replacement n_bootstrap times,
    computing |b-c|/(b+c) for each resample. High variance indicates
    the observed effect may be a sampling artifact (collapse risk).

    Args:
        category: Category name (for labeling).
        eng_escaped: Boolean escape outcomes for engineering strategy.
        hyp_escaped: Boolean escape outcomes for hypothesis strategy.
        n_bootstrap: Number of bootstrap resamples (default 2000).
        collapse_threshold_ratio: Effect size threshold ratio — collapse_threshold =
            observed_effect * collapse_threshold_ratio. Collapse probability is
            P(bootstrap_effect < collapse_threshold). Default 0.3 means threshold
            is 30% of the observed effect.
        seed: Random seed for reproducibility.

    Returns:
        BootstrapEffectResult with variance metrics and collapse risk assessment.
    """
    rng = random.Random(seed)
    n = len(eng_escaped)
    pairs = list(zip(eng_escaped, hyp_escaped))

    if n == 0:
        return BootstrapEffectResult(
            category=category, n=0,
            observed_effect=0.0, bootstrap_mean=0.0, bootstrap_std=0.0,
            ci_90_lower=0.0, ci_90_upper=0.0,
            collapse_risk="HIGH", collapse_threshold=0.0, collapse_probability=1.0,
        )

    # Observed effect
    b_obs = sum(1 for e, h in pairs if not e and h)
    c_obs = sum(1 for e, h in pairs if e and not h)
    disc_obs = b_obs + c_obs
    observed_effect = abs(b_obs - c_obs) / disc_obs if disc_obs > 0 else 0.0

    # Bootstrap
    effects: list[float] = []
    for _ in range(n_bootstrap):
        sample = [rng.choice(pairs) for _ in range(n)]
        b = sum(1 for e, h in sample if not e and h)
        c = sum(1 for e, h in sample if e and not h)
        disc = b + c
        effects.append(abs(b - c) / disc if disc > 0 else 0.0)

    effects_sorted = sorted(effects)
    mean_eff = sum(effects) / len(effects)
    var_eff = sum((x - mean_eff) ** 2 for x in effects) / len(effects)
    std_eff = math.sqrt(var_eff)

    p5_idx = int(0.05 * n_bootstrap)
    p95_idx = int(0.95 * n_bootstrap)
    ci_lower = effects_sorted[p5_idx]
    ci_upper = effects_sorted[p95_idx]

    # Collapse risk: based on CI lower bound (absolute, not relative).
    # An effect can "collapse" to near-zero regardless of its observed magnitude.
    # If the 90% CI lower bound is < 0.15 (near-negligible), the effect is at risk.
    # This is more informative than P(effect < 30% of observed) for small observed values.
    collapse_threshold = observed_effect * collapse_threshold_ratio
    collapse_prob = sum(1 for e in effects if e < collapse_threshold) / n_bootstrap

    # Override collapse risk using CI lower bound
    if ci_lower < 0.10:
        risk = "HIGH"   # CI lower is near-zero — effect may not be real
    elif ci_lower < 0.20:
        risk = "MEDIUM"
    else:
        risk = "LOW"

    return BootstrapEffectResult(
        category=category,
        n=n,
        observed_effect=observed_effect,
        bootstrap_mean=mean_eff,
        bootstrap_std=std_eff,
        ci_90_lower=ci_lower,
        ci_90_upper=ci_upper,
        collapse_risk=risk,
        collapse_threshold=collapse_threshold,
        collapse_probability=collapse_prob,
    )
