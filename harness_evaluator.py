"""
Harness Self-Evaluator: 실험 하네스 자체의 품질을 평가하고 개선 피드백을 생성.

Anthropic의 Generator/Evaluator 분리 패턴과 MetaClaw의 교차 실행 학습에서 영감:
- 실험 결과를 품질 기준(threshold)과 대조하여 하네스 수준의 진단 수행
- 반복 실행 간 개선/퇴보 추이를 추적
- 구체적인 하네스 개선 제안(actionable feedback) 생성

References:
  - Anthropic "Harness Design for Long-Running Apps" (2026-03)
  - Karpathy AutoResearch: meta-optimization of program MD
  - MetaClaw: cross-run learning with time-decay lessons
"""
import json
from dataclasses import asdict, dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Any

from constants import RESULTS_DIR, ExperimentName


# ── 품질 기준 ──────────────────────────────────────────────────────────────────

@dataclass(frozen=True)
class QualityThreshold:
    """실험 유형별 합격 기준."""
    min_success_rate: float  # 0.0 ~ 1.0
    max_avg_duration_ms: int  # 허용 평균 응답 시간
    min_steps: int  # 최소 실행 스텝 수


THRESHOLDS: dict[ExperimentName, QualityThreshold] = {
    "context_memory": QualityThreshold(
        min_success_rate=0.7,
        max_avg_duration_ms=30_000,
        min_steps=5,
    ),
    "coding_failure": QualityThreshold(
        min_success_rate=0.5,
        max_avg_duration_ms=60_000,
        min_steps=5,
    ),
    "hypothesis_validation": QualityThreshold(
        min_success_rate=0.8,   # both strategies should solve most tasks
        max_avg_duration_ms=0,  # no duration constraint (deterministic)
        min_steps=9,            # minimum 9 steps (12 tasks × 2 strategies = 24 steps, threshold is lenient)
    ),
}


# ── 평가 결과 ──────────────────────────────────────────────────────────────────

@dataclass(frozen=True)
class HarnessVerdict:
    """하네스 평가 판정 결과."""
    experiment: str
    passed: bool
    score: float  # 0.0 ~ 1.0 종합 점수
    success_rate: float
    avg_duration_ms: float
    total_steps: int
    issues: list[str] = field(default_factory=list)
    suggestions: list[str] = field(default_factory=list)
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())


# ── 핵심 평가 로직 ─────────────────────────────────────────────────────────────

def evaluate_harness(data: dict[str, Any]) -> HarnessVerdict:
    """
    실험 결과 JSON dict를 받아 하네스 품질을 평가.

    Returns:
        HarnessVerdict with pass/fail, score, issues, and suggestions.
    """
    experiment = data.get("experiment", "unknown")
    steps: list[dict[str, Any]] = data.get("steps", [])
    total = len(steps)
    threshold = THRESHOLDS.get(experiment)

    # 빈 결과 처리
    if total == 0:
        return HarnessVerdict(
            experiment=experiment,
            passed=False,
            score=0.0,
            success_rate=0.0,
            avg_duration_ms=0.0,
            total_steps=0,
            issues=["실험 스텝이 0개입니다."],
            suggestions=["실험 구성(tasks/prompts)을 확인하세요."],
        )

    success_count = sum(1 for s in steps if s.get("status") == "success")
    success_rate = success_count / total

    durations = [s.get("duration_ms", 0) for s in steps]
    avg_duration = sum(durations) / len(durations) if durations else 0.0

    issues: list[str] = []
    suggestions: list[str] = []

    # ── 기준 대비 검사 ──
    if threshold is not None:
        if success_rate < threshold.min_success_rate:
            issues.append(
                f"성공률 {success_rate:.1%}가 기준 {threshold.min_success_rate:.1%} 미달"
            )
            suggestions.append(
                "프롬프트 설계를 개선하거나 컨텍스트 길이 범위를 조정하세요."
            )

        if avg_duration > threshold.max_avg_duration_ms:
            issues.append(
                f"평균 응답 시간 {avg_duration:.0f}ms가 기준 {threshold.max_avg_duration_ms}ms 초과"
            )
            suggestions.append(
                "타임아웃 설정을 늘리거나 더 빠른 모델/엔드포인트를 사용하세요."
            )

        if total < threshold.min_steps:
            issues.append(
                f"실행 스텝 {total}개가 최소 기준 {threshold.min_steps}개 미달"
            )
            suggestions.append(
                "실험 반복 횟수(REPEATS)나 태스크 수를 늘리세요."
            )

    # ── 실험 유형별 심층 진단 ──
    if experiment == "context_memory":
        _diagnose_context_memory(steps, issues, suggestions)
    elif experiment == "coding_failure":
        _diagnose_coding_failure(steps, data.get("summary", {}), issues, suggestions)
    elif experiment == "hypothesis_validation":
        _diagnose_hypothesis_validation(steps, data.get("summary", {}), issues, suggestions)

    # ── 종합 점수 계산 ──
    score = _compute_score(success_rate, avg_duration, total, threshold)
    passed = len(issues) == 0

    return HarnessVerdict(
        experiment=experiment,
        passed=passed,
        score=score,
        success_rate=success_rate,
        avg_duration_ms=avg_duration,
        total_steps=total,
        issues=issues,
        suggestions=suggestions,
    )


def _diagnose_context_memory(
    steps: list[dict[str, Any]],
    issues: list[str],
    suggestions: list[str],
) -> None:
    """context_memory 실험 전용 진단."""
    # 위치별 성공률 편차 검사
    by_position: dict[str, list[bool]] = {}
    for s in steps:
        pos = s.get("position", "unknown")
        by_position.setdefault(pos, []).append(s.get("status") == "success")

    if len(by_position) >= 2:
        rates = {pos: sum(v) / len(v) for pos, v in by_position.items()}
        max_rate = max(rates.values())
        min_rate = min(rates.values())
        if max_rate - min_rate > 0.3:
            worst_pos = min(rates, key=lambda k: rates[k])
            issues.append(
                f"위치별 성공률 편차가 {max_rate - min_rate:.1%}로 큼 "
                f"(최저: {worst_pos} {min_rate:.1%})"
            )
            suggestions.append(
                f"'{worst_pos}' 위치의 프롬프트 설계를 강화하세요 "
                "(예: 비밀 코드 앞뒤에 구분자 추가)."
            )

    # 긴 컨텍스트에서의 성능 저하 검사
    by_ctx: dict[int, list[bool]] = {}
    for s in steps:
        ctx = s.get("context_tokens", 0)
        by_ctx.setdefault(ctx, []).append(s.get("status") == "success")

    sorted_ctx = sorted(by_ctx.keys())
    if len(sorted_ctx) >= 2:
        shortest_rate = sum(by_ctx[sorted_ctx[0]]) / len(by_ctx[sorted_ctx[0]])
        longest_rate = sum(by_ctx[sorted_ctx[-1]]) / len(by_ctx[sorted_ctx[-1]])
        if shortest_rate > 0 and longest_rate / shortest_rate < 0.5:
            suggestions.append(
                "긴 컨텍스트에서 성능이 크게 저하됩니다. "
                "중간 컨텍스트 길이를 추가하여 정확한 저하 곡선을 측정하세요."
            )


def _diagnose_coding_failure(
    steps: list[dict[str, Any]],
    summary: dict[str, Any],
    issues: list[str],
    suggestions: list[str],
) -> None:
    """coding_failure 실험 전용 진단."""
    # 카테고리별 분석
    by_category: dict[str, list[bool]] = {}
    for s in steps:
        cat = s.get("category", "unknown")
        by_category.setdefault(cat, []).append(s.get("status") == "success")

    for cat, results in by_category.items():
        rate = sum(results) / len(results) if results else 0.0
        if rate < 0.3:
            issues.append(f"카테고리 '{cat}'의 성공률이 {rate:.1%}로 매우 낮음")
            suggestions.append(
                f"'{cat}' 카테고리의 태스크 난이도를 조정하거나 "
                "단계적 힌트를 제공하세요."
            )

    # 실패 급증 시점 조기 발생 검사
    inflection = summary.get("failure_inflection_step")
    total = len(steps)
    if inflection is not None and total > 0 and inflection <= total * 0.3:
        issues.append(
            f"실패 급증이 전체의 30% 지점(스텝 {inflection}/{total}) 이전에 발생"
        )
        suggestions.append(
            "초반 태스크 난이도를 낮추거나 에이전트 워밍업 단계를 추가하세요."
        )


def _diagnose_hypothesis_validation(
    steps: list[dict[str, Any]],
    summary: dict[str, Any],
    issues: list[str],
    suggestions: list[str],
) -> None:
    """hypothesis_validation 실험 전용 진단."""
    # 전략별 성공률 비교
    by_strategy: dict[str, list[bool]] = {}
    for s in steps:
        strategy = s.get("strategy", "unknown")
        by_strategy.setdefault(strategy, []).append(s.get("status") == "success")

    min_rate = THRESHOLDS["hypothesis_validation"].min_success_rate
    for strategy, results in by_strategy.items():
        rate = sum(results) / len(results) if results else 0.0
        if rate < min_rate:
            issues.append(f"전략 '{strategy}' 성공률 {rate:.1%}가 기준 {min_rate:.0%} 미달")
            suggestions.append(
                f"'{strategy}' 전략의 attempt 시퀀스 또는 프롬프트를 점검하세요."
            )

    # 카테고리별 attempt 평균 비교 (hypothesis 이점 확인)
    eng_avg = summary.get("engineering_avg_attempts", 0.0)
    hyp_avg = summary.get("hypothesis_avg_attempts", 0.0)
    if eng_avg > 0 and hyp_avg > 0 and (eng_avg - hyp_avg) < 0.3:
        suggestions.append(
            "두 전략 간 attempt 차이가 작습니다. "
            "가설 기반 접근의 이점이 뚜렷한 harder 태스크를 추가하세요."
        )

    # 카테고리 다양성 검사: 단일 카테고리만 있으면 외적 타당도 위험
    categories = {s.get("category", "unknown") for s in steps if s.get("category")}
    if len(categories) == 1:
        suggestions.append(
            f"태스크가 '{next(iter(categories))}' 카테고리에만 집중되어 있습니다. "
            "simple/causal/assumption 3개 카테고리를 포함하면 외적 타당도가 높아집니다."
        )

    # 태스크 수 적정성 검사: 전략당 5개 미만이면 통계적 유의성 경고
    task_count = summary.get("task_count", len(steps) // 2 if steps else 0)
    if 0 < task_count < 5:
        issues.append(
            f"태스크 수({task_count}개)가 통계적 유의성을 위한 최소 기준(5개) 미달"
        )
        suggestions.append(
            "최소 5개 이상의 태스크로 실험을 확장하세요."
        )


def _compute_score(
    success_rate: float,
    avg_duration: float,
    total_steps: int,
    threshold: QualityThreshold | None,
) -> float:
    """0.0~1.0 범위의 종합 점수 계산. 가중 평균 방식."""
    # 성공률 점수 (가중치 0.6)
    rate_score = min(success_rate, 1.0)

    # 응답 시간 점수 (가중치 0.2) - 기준 대비 비율
    if threshold and threshold.max_avg_duration_ms > 0:
        duration_ratio = avg_duration / threshold.max_avg_duration_ms
        duration_score = max(0.0, 1.0 - max(0.0, duration_ratio - 1.0))
    else:
        duration_score = 1.0 if avg_duration < 30_000 else 0.5

    # 충분성 점수 (가중치 0.2) - 최소 스텝 대비 비율
    if threshold and threshold.min_steps > 0:
        sufficiency_score = min(total_steps / threshold.min_steps, 1.0)
    else:
        sufficiency_score = 1.0 if total_steps >= 5 else total_steps / 5.0

    score = rate_score * 0.6 + duration_score * 0.2 + sufficiency_score * 0.2
    return round(min(score, 1.0), 3)


# ── 교차 실행 비교 (Cross-Run Comparison) ──────────────────────────────────────

def compare_runs(
    current: HarnessVerdict,
    previous: HarnessVerdict,
) -> dict[str, Any]:
    """두 실행 결과를 비교하여 개선/퇴보 추이 반환."""
    delta_score = current.score - previous.score
    delta_rate = current.success_rate - previous.success_rate
    delta_duration = current.avg_duration_ms - previous.avg_duration_ms

    trend: str
    if delta_score > 0.05:
        trend = "improving"
    elif delta_score < -0.05:
        trend = "regressing"
    else:
        trend = "stable"

    return {
        "trend": trend,
        "delta_score": round(delta_score, 3),
        "delta_success_rate": round(delta_rate, 3),
        "delta_avg_duration_ms": round(delta_duration, 1),
        "current_score": current.score,
        "previous_score": previous.score,
    }


# ── 결과 저장 ──────────────────────────────────────────────────────────────────

HARNESS_EVAL_DIR = RESULTS_DIR / "harness_evals"


def save_verdict(verdict: HarnessVerdict) -> Path:
    """하네스 평가 결과를 JSON으로 저장."""
    HARNESS_EVAL_DIR.mkdir(parents=True, exist_ok=True)
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    path = HARNESS_EVAL_DIR / f"{verdict.experiment}_eval_{ts}.json"

    path.write_text(json.dumps(asdict(verdict), ensure_ascii=False, indent=2))
    return path


def _verdict_from_dict(data: dict[str, Any]) -> HarnessVerdict:
    """JSON 딕셔너리에서 HarnessVerdict 객체를 복원."""
    return HarnessVerdict(
        experiment=data["experiment"],
        passed=data["passed"],
        score=data["score"],
        success_rate=data["success_rate"],
        avg_duration_ms=data["avg_duration_ms"],
        total_steps=data["total_steps"],
        issues=data.get("issues", []),
        suggestions=data.get("suggestions", []),
        timestamp=data.get("timestamp", ""),
    )


def load_latest_verdict(experiment: ExperimentName) -> HarnessVerdict | None:
    """특정 실험의 가장 최근 하네스 평가 결과를 로드."""
    if not HARNESS_EVAL_DIR.exists():
        return None

    paths = sorted(HARNESS_EVAL_DIR.glob(f"{experiment}_eval_*.json"), reverse=True)
    if not paths:
        return None

    return _verdict_from_dict(json.loads(paths[0].read_text()))
