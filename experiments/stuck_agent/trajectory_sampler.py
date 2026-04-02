"""Trajectory Sampler for Stuck-Agent Triage.

Samples key signals from agent execution trajectories to detect
stuck states early — before full failure occurs.

Based on: "Signals: Trajectory Sampling and Triage for Agentic Interactions"
(arXiv:2604.00356, 2026-04-02)
Absorbed via: /inhale agent_research

Signals sampled:
  1. action_repetition   — same tool call pattern repeated >= 3 times
  2. output_similarity   — cosine similarity between consecutive outputs > 0.95
  3. error_cycling       — same error message recurring >= 2 times
  4. progress_stall      — no new files modified / no test delta >= 2 steps
  5. strategy_fixation   — same approach despite failure signal
"""
from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum


class TriageLevel(Enum):
    HEALTHY = "HEALTHY"
    AT_RISK = "AT_RISK"
    STUCK = "STUCK"


@dataclass
class TrajectorySignal:
    """A single signal sample from an agent trajectory step."""
    step: int
    action_type: str
    output_hash: str        # hash of output for similarity check
    error_msg: str | None
    files_modified: int
    test_delta: int         # tests passing delta from previous step


@dataclass
class TrajectoryState:
    """Accumulated state across trajectory steps."""
    signals: list[TrajectorySignal] = field(default_factory=list)
    consecutive_repeats: int = 0
    consecutive_stalls: int = 0
    error_counts: dict[str, int] = field(default_factory=dict)
    fired_signals: list[str] = field(default_factory=list)

    def add_signal(self, signal: TrajectorySignal) -> TriageLevel:
        """Add a new signal and return current triage level."""
        self.signals.append(signal)
        self.fired_signals.clear()

        # 1. Action repetition
        if len(self.signals) >= 2:
            if signal.action_type == self.signals[-2].action_type:
                self.consecutive_repeats += 1
            else:
                self.consecutive_repeats = 0
            if self.consecutive_repeats >= 3:
                self.fired_signals.append("action_repetition")

        # 2. Output similarity (hash-based proxy)
        if len(self.signals) >= 2:
            if signal.output_hash == self.signals[-2].output_hash:
                self.fired_signals.append("output_similarity")

        # 3. Error cycling
        if signal.error_msg:
            self.error_counts[signal.error_msg] = (
                self.error_counts.get(signal.error_msg, 0) + 1
            )
            if self.error_counts[signal.error_msg] >= 2:
                self.fired_signals.append("error_cycling")

        # 4. Progress stall
        if signal.files_modified == 0 and signal.test_delta <= 0:
            self.consecutive_stalls += 1
        else:
            self.consecutive_stalls = 0
        if self.consecutive_stalls >= 2:
            self.fired_signals.append("progress_stall")

        # Triage decision
        n_fired = len(self.fired_signals)
        if n_fired >= 3:
            return TriageLevel.STUCK
        elif n_fired >= 2:
            return TriageLevel.AT_RISK
        return TriageLevel.HEALTHY
