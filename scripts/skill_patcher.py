"""Evolving Orchestration — Skill Patch Generator.

Extracts success/failure patterns from episode memory and generates
context patches for skills, enabling skill prompts to evolve based
on experience without modifying the SKILL.md files directly.

Source: /inhale → /exhale (2026-04-04)
  Paper: Experience as a Compass: Multi-agent RAG with
         Evolving Orchestration and Agent Prompts (arXiv:2604.00901)

Usage:
  from scripts.skill_patcher import SkillPatcher
  patcher = SkillPatcher.from_episodes(".omc/episodes.jsonl")
  patch = patcher.generate_patch("exhale")
  # → inject patch into context primer before skill execution
"""
from __future__ import annotations

import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any


@dataclass
class SkillPatch:
    """A context patch for a specific skill."""
    skill_name: str
    success_patterns: list[str]
    failure_patterns: list[str]
    parameter_adjustments: list[str]
    iteration_source: int   # which iteration generated this patch
    confidence: float       # 0.0-1.0 based on episode count

    def to_context_block(self) -> str:
        """Format as injectable context block."""
        if not self.success_patterns and not self.failure_patterns:
            return ""

        lines = [f"[SKILL PATCH — {self.skill_name} | confidence={self.confidence:.2f}]"]

        if self.success_patterns:
            lines.append("Proven approaches (DO MORE of these):")
            for p in self.success_patterns[:3]:
                lines.append(f"  + {p}")

        if self.failure_patterns:
            lines.append("Failed approaches (AVOID these):")
            for p in self.failure_patterns[:3]:
                lines.append(f"  - {p}")

        if self.parameter_adjustments:
            lines.append("Suggested parameter adjustments:")
            for a in self.parameter_adjustments[:3]:
                lines.append(f"  ~ {a}")

        return "\n".join(lines)


class SkillPatcher:
    """Generates experience-based patches for skill prompts.

    Reads episode history and extracts patterns that should
    influence future skill executions — without modifying SKILL.md.
    """

    def __init__(self, episodes: list[dict], world_model: dict | None = None):
        self.episodes = episodes
        self.world_model = world_model or {}

    @classmethod
    def from_episodes(
        cls,
        episodes_path: str | Path = ".omc/episodes.jsonl",
        world_model_path: str | Path = ".omc/world-model.json",
    ) -> "SkillPatcher":
        """Load from episode and world model files."""
        episodes = []
        ep_path = Path(episodes_path)
        if ep_path.exists():
            for line in ep_path.read_text().strip().split("\n"):
                if line.strip():
                    episodes.append(json.loads(line))

        world_model = {}
        wm_path = Path(world_model_path)
        if wm_path.exists():
            world_model = json.loads(wm_path.read_text())

        return cls(episodes, world_model)

    def generate_patch(self, skill_name: str) -> SkillPatch:
        """Generate a context patch for the given skill.

        Analyzes episodes where this skill was used (or similar tasks)
        and extracts actionable patterns.
        """
        relevant = self._filter_episodes(skill_name)

        success_patterns = []
        failure_patterns = []
        param_adjustments = []

        for ep in relevant:
            outcome = ep.get("outcome", "unknown")
            # Support both episode schema variants:
            # v1 (new): key_decision, summary, failure_pattern
            # v2 (actual): approach, task_desc, key_errors, project_hints
            key_decision = ep.get("key_decision") or ep.get("approach", "")
            summary = ep.get("summary") or ep.get("task_desc", "")
            hints = ep.get("project_hints", [])

            if outcome in ("success", "evolved"):
                if key_decision:
                    success_patterns.append(key_decision[:120])
                elif summary:
                    success_patterns.append(summary[:100])
                for hint in hints[:2]:
                    success_patterns.append(str(hint)[:80])
            elif outcome in ("failure", "partial"):
                key_errors = ep.get("key_errors", [])
                failure_reason = ep.get("failure_pattern", "")
                if not failure_reason and key_errors:
                    failure_reason = "; ".join(str(e) for e in key_errors[:2])
                if not failure_reason and summary:
                    failure_reason = summary[:100]
                if failure_reason:
                    failure_patterns.append(failure_reason)

        # Extract from world model
        wm_tried = self.world_model.get("tried_strategies", [])
        for strategy in wm_tried:
            if strategy.get("outcome") == "success" and strategy.get("score", 0) > 0.8:
                success_patterns.append(
                    f"Goal '{strategy['goal'][:60]}' scored {strategy['score']:.2f}"
                )
            weak_dim = strategy.get("weak_dim")
            if weak_dim:
                param_adjustments.append(
                    f"Dimension '{weak_dim}' has been weakest — prioritize it"
                )

        # Extract from dead ends
        for dead_end in self.world_model.get("dead_ends", []):
            failure_patterns.append(
                f"Dead end: '{dead_end['goal'][:60]}' (score={dead_end.get('score', '?')})"
            )

        # Deduplicate
        success_patterns = list(dict.fromkeys(success_patterns))
        failure_patterns = list(dict.fromkeys(failure_patterns))
        param_adjustments = list(dict.fromkeys(param_adjustments))

        confidence = min(len(relevant) / 5.0, 1.0)  # 5+ episodes = full confidence

        return SkillPatch(
            skill_name=skill_name,
            success_patterns=success_patterns,
            failure_patterns=failure_patterns,
            parameter_adjustments=param_adjustments,
            iteration_source=max((ep.get("iteration", 0) for ep in relevant), default=0),
            confidence=confidence,
        )

    def _filter_episodes(self, skill_name: str) -> list[dict]:
        """Filter episodes relevant to the given skill."""
        relevant = []
        skill_keywords = {
            "exhale": ["evolve", "exhale", "knowledge", "experiment design"],
            "inhale": ["inhale", "collect", "knowledge", "digest"],
            "live": ["live", "autonomous", "outer loop", "evolution"],
            "live-inf": ["infinite", "live-inf", "convergence", "world model"],
        }
        keywords = skill_keywords.get(skill_name, [skill_name])

        for ep in self.episodes:
            ep_text = json.dumps(ep).lower()
            if any(kw in ep_text for kw in keywords):
                relevant.append(ep)

        return relevant

    def save_patch(self, patch: SkillPatch, output_dir: str | Path = ".omc/skill-patches") -> Path:
        """Save patch to disk for persistence across sessions."""
        out = Path(output_dir)
        out.mkdir(parents=True, exist_ok=True)
        path = out / f"{patch.skill_name}.json"
        path.write_text(json.dumps({
            "skill_name": patch.skill_name,
            "success_patterns": patch.success_patterns,
            "failure_patterns": patch.failure_patterns,
            "parameter_adjustments": patch.parameter_adjustments,
            "iteration_source": patch.iteration_source,
            "confidence": patch.confidence,
        }, ensure_ascii=False, indent=2))
        return path

    @staticmethod
    def load_patch(skill_name: str, patch_dir: str | Path = ".omc/skill-patches") -> SkillPatch | None:
        """Load a previously saved patch."""
        path = Path(patch_dir) / f"{skill_name}.json"
        if not path.exists():
            return None
        data = json.loads(path.read_text())
        return SkillPatch(**data)
