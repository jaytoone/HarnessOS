"""Autonomous Evolution Safety Triad.

3개의 safety signal 감지기를 제공하여 live/live-inf의
장기 자율 진화 루프에서 발생하는 degradation을 사전 감지.

Source: /inhale → /evolve (2026-04-03)
  - Safety Gate Drift: arXiv:2604.00072
  - Reward Hacking: Alignment Forum (Golechha et al.)
  - CoT Monitorability: Alignment Forum/DeepMind (Kaufmann et al.)

Usage:
  from scripts.evolution_safety import EvolutionSafetyMonitor
  monitor = EvolutionSafetyMonitor.from_live_state(".omc/live-state.json")
  alerts = monitor.check_all()
"""
from __future__ import annotations

import json
import re
import statistics
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any


@dataclass
class SafetyAlert:
    """A single safety alert from the triad."""
    signal: str          # "safety_gate_drift" | "reward_hacking" | "cot_drift"
    severity: str        # "warning" | "critical"
    message: str
    recommendation: str
    iteration: int
    data: dict = field(default_factory=dict)


class EvolutionSafetyMonitor:
    """Monitors 3 safety signals during autonomous evolution loops.

    Designed to be called after each iteration's SCORE step (6a)
    in live/live-inf, before the EVOLVE decision.
    """

    def __init__(
        self,
        score_history: list[dict],
        cost_history: list[dict] | None = None,
        summaries: list[str] | None = None,
        window: int = 10,
    ):
        self.score_history = score_history
        self.cost_history = cost_history or []
        self.summaries = summaries or []
        self.window = window

    @classmethod
    def from_live_state(cls, path: str | Path) -> "EvolutionSafetyMonitor":
        """Load from .omc/live-state.json."""
        data = json.loads(Path(path).read_text())
        return cls(
            score_history=data.get("score_history", []),
            cost_history=data.get("cost_history", []),
        )

    # ─── Signal 1: Safety Gate Drift ───────────────────────────
    # Source: arXiv:2604.00072
    # Detect: score_variance가 시간이 지남에 따라 증가하는 추세

    def check_safety_gate_drift(self) -> SafetyAlert | None:
        """Score evaluator의 정확도가 장기 실행에서 하락하는지 감지.

        score_variance의 이동 평균이 증가 추세이면 경고.
        """
        if len(self.score_history) < 6:
            return None

        variances = [
            h.get("score_variance", 0.0)
            for h in self.score_history
            if "score_variance" in h
        ]
        if len(variances) < 6:
            return None

        # 전반부 vs 후반부 variance 비교
        mid = len(variances) // 2
        first_half_avg = statistics.mean(variances[:mid])
        second_half_avg = statistics.mean(variances[mid:])

        if second_half_avg > first_half_avg * 1.5 and second_half_avg > 0.08:
            current_iter = self.score_history[-1].get("iteration", len(self.score_history))
            return SafetyAlert(
                signal="safety_gate_drift",
                severity="critical" if second_half_avg > 0.15 else "warning",
                message=(
                    f"Score variance trending up: {first_half_avg:.3f} → {second_half_avg:.3f} "
                    f"(+{((second_half_avg/first_half_avg)-1)*100:.0f}%)"
                ),
                recommendation=(
                    "Increase score_ensemble_n (3→5) or switch evaluator_mode to 'cross_prompt'"
                ),
                iteration=current_iter,
                data={
                    "first_half_variance": round(first_half_avg, 4),
                    "second_half_variance": round(second_half_avg, 4),
                },
            )
        return None

    # ─── Signal 2: Reward Hacking ──────────────────────────────
    # Source: Alignment Forum (Golechha et al.)
    # Detect: score가 올라가는데 실질적 변화(diff size)가 줄어드는 패턴

    def check_reward_hacking(self) -> SafetyAlert | None:
        """Score는 증가하지만 실제 코드 변화량은 감소하는 패턴 감지.

        cost_history의 relative_cost를 변화량 proxy로 사용.
        """
        if len(self.score_history) < 4 or len(self.cost_history) < 4:
            return None

        recent_n = min(4, len(self.score_history))
        recent_scores = [h.get("score", 0) for h in self.score_history[-recent_n:]]
        recent_costs = [h.get("relative_cost", 1.0) for h in self.cost_history[-recent_n:]]

        # Score 증가 추세 확인
        score_increasing = all(
            recent_scores[i] >= recent_scores[i - 1] - 0.02
            for i in range(1, len(recent_scores))
        )

        # Cost(=변화량 proxy) 감소 추세 확인
        cost_decreasing = all(
            recent_costs[i] <= recent_costs[i - 1] + 0.1
            for i in range(1, len(recent_costs))
        ) and recent_costs[-1] < recent_costs[0] * 0.7

        if score_increasing and cost_decreasing:
            current_iter = self.score_history[-1].get("iteration", len(self.score_history))
            return SafetyAlert(
                signal="reward_hacking",
                severity="warning",
                message=(
                    f"Score stable/increasing ({recent_scores[0]:.2f}→{recent_scores[-1]:.2f}) "
                    f"but change volume decreasing ({recent_costs[0]:.1f}→{recent_costs[-1]:.1f})"
                ),
                recommendation=(
                    "Force evaluator_mode='cross_prompt' for next iteration. "
                    "Check if improvements are substantive or cosmetic."
                ),
                iteration=current_iter,
                data={
                    "score_trend": [round(s, 3) for s in recent_scores],
                    "cost_trend": [round(c, 3) for c in recent_costs],
                },
            )
        return None

    # ─── Signal 3: CoT Monitorability Drift ────────────────────
    # Source: Alignment Forum/DeepMind (Kaufmann et al.)
    # Detect: autopilot summary의 구체성이 하락

    def check_cot_drift(self) -> SafetyAlert | None:
        """Autopilot summary의 구체성이 하락하는지 감지.

        구체성 = (파일명, 함수명, 숫자 등 specific token 수) / 전체 단어 수
        """
        if len(self.summaries) < 4:
            return None

        specificities = [self._compute_specificity(s) for s in self.summaries]

        recent_n = min(4, len(specificities))
        first = specificities[:recent_n]
        last = specificities[-recent_n:]

        first_avg = statistics.mean(first) if first else 0
        last_avg = statistics.mean(last) if last else 0

        if first_avg > 0 and last_avg < first_avg * 0.6:
            current_iter = len(self.summaries)
            return SafetyAlert(
                signal="cot_drift",
                severity="warning",
                message=(
                    f"Summary specificity declining: {first_avg:.2f} → {last_avg:.2f} "
                    f"(-{((1 - last_avg/first_avg))*100:.0f}%)"
                ),
                recommendation=(
                    "Force autopilot to include 'git diff --stat' in summary. "
                    "Consider context rotation for fresh CoT quality."
                ),
                iteration=current_iter,
                data={
                    "first_specificity": round(first_avg, 3),
                    "last_specificity": round(last_avg, 3),
                },
            )
        return None

    @staticmethod
    def _compute_specificity(text: str) -> float:
        """텍스트의 구체성 점수 (0.0~1.0).

        Specific tokens: 파일 경로, 함수명(snake_case/CamelCase),
        숫자, 에러 메시지 등.
        """
        if not text:
            return 0.0
        words = text.split()
        if not words:
            return 0.0
        # 구두점 제거한 clean word로 판별
        specific = 0
        for w in words:
            clean = w.rstrip(".,;:!?)")
            if not clean or len(clean) < 2:
                continue
            if (
                "/" in clean                          # 파일 경로
                or re.search(r"\.\w{1,4}$", clean)    # 확장자 (foo.py, bar.md)
                or "_" in clean and len(clean) > 3    # snake_case (4자 이상)
                or re.match(r"^[A-Z][a-z]+[A-Z]", clean)  # CamelCase
                or re.match(r"^\d+\.?\d*$", clean)    # 숫자
                or clean.startswith("0x")              # hex
            ):
                specific += 1
        return min(specific / len(words), 1.0)

    # ─── Combined Check ────────────────────────────────────────

    def check_all(self) -> list[SafetyAlert]:
        """3개 safety signal 모두 확인. 발견된 alert 리스트 반환."""
        alerts = []
        for check in [
            self.check_safety_gate_drift,
            self.check_reward_hacking,
            self.check_cot_drift,
        ]:
            alert = check()
            if alert:
                alerts.append(alert)
        return alerts

    def format_alerts(self, alerts: list[SafetyAlert]) -> str:
        """Alert 리스트를 사람이 읽기 좋은 형태로 포맷."""
        if not alerts:
            return "[EVOLUTION SAFETY] All clear — no safety signals detected."

        lines = []
        for a in alerts:
            icon = "!!" if a.severity == "critical" else "!"
            lines.append(
                f"[{a.signal.upper()} {icon}] iter {a.iteration}: {a.message}\n"
                f"  → {a.recommendation}"
            )

        if len(alerts) >= 3:
            lines.append(
                "\n[EVOLUTION SAFETY ALERT] All 3 signals firing — escalate to user."
            )

        return "\n".join(lines)
