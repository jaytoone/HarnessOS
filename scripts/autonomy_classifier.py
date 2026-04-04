"""Autonomy-Preserving 3-Tier Classification for exhale artifacts.

Classifies evolution artifacts into 3 autonomy levels based on
confidence (evolution_score) and risk (file change scope).

Source: /inhale → /exhale (2026-04-04)
  Paper: Care-Conditioned Neuromodulation for Autonomy-Preserving
         Supportive Dialogue Agents (arXiv:2604.01576)

Tiers:
  L1 (INFORM):   High confidence + low risk → auto-execute + report
  L2 (CONFIRM):  Medium confidence or risk → present + ask confirmation
  L3 (DELEGATE): Low confidence or high risk → present design only

Usage:
  from scripts.autonomy_classifier import classify_autonomy, AutonomyLevel
  level = classify_autonomy(evolution_score=15.6, mode="code", files_changed=["scripts/foo.py"])
"""
from __future__ import annotations

import re
from dataclasses import dataclass
from enum import Enum
from pathlib import Path


class AutonomyLevel(Enum):
    L1_INFORM = "L1"    # auto-execute + report after
    L2_CONFIRM = "L2"   # present summary + ask Y/N
    L3_DELEGATE = "L3"  # present design only, user executes


@dataclass
class AutonomyResult:
    level: AutonomyLevel
    confidence: float      # 0.0-1.0
    risk: float            # 0.0-1.0
    reason: str
    action: str            # what to tell the user


# Risk factors by file pattern
HIGH_RISK_PATTERNS = [
    r"\.omc/",             # live/live-inf state files
    r"SKILL\.md$",         # skill definitions
    r"CLAUDE\.md$",        # system instructions
    r"\.env",              # environment/secrets
    r"goal-tree\.json$",   # goal tree
    r"live-state\.json$",  # live state
]

MEDIUM_RISK_PATTERNS = [
    r"scripts/",           # core scripts
    r"experiments/",       # experiment code
    r"__init__\.py$",      # module init
]

LOW_RISK_PATTERNS = [
    r"docs/",              # documentation
    r"\.md$",              # markdown files
    r"\.jsonl$",           # append-only logs
]


def _compute_risk(mode: str, files_changed: list[str] | None = None) -> float:
    """Compute risk score (0.0-1.0) based on mode and files affected."""
    # Base risk by mode
    mode_risk = {
        "experiment": 0.2,   # just a design doc
        "hypothesis": 0.2,   # just a hypothesis doc
        "design": 0.3,       # design doc, may influence decisions
        "code": 0.6,         # actual code changes
    }.get(mode, 0.5)

    if not files_changed:
        return mode_risk

    # Adjust by file patterns
    max_file_risk = 0.0
    for f in files_changed:
        for pattern in HIGH_RISK_PATTERNS:
            if re.search(pattern, f):
                max_file_risk = max(max_file_risk, 0.9)
                break
        else:
            for pattern in MEDIUM_RISK_PATTERNS:
                if re.search(pattern, f):
                    max_file_risk = max(max_file_risk, 0.5)
                    break
            else:
                for pattern in LOW_RISK_PATTERNS:
                    if re.search(pattern, f):
                        max_file_risk = max(max_file_risk, 0.2)
                        break
                else:
                    max_file_risk = max(max_file_risk, 0.4)

    # Weighted: mode risk 40%, file risk 60%
    return mode_risk * 0.4 + max_file_risk * 0.6


def _compute_confidence(evolution_score: float, max_score: float = 18.0) -> float:
    """Normalize evolution_score to 0.0-1.0 confidence."""
    return min(evolution_score / max_score, 1.0)


def classify_autonomy(
    evolution_score: float,
    mode: str = "experiment",
    files_changed: list[str] | None = None,
    max_score: float = 18.0,
) -> AutonomyResult:
    """Classify an exhale artifact into L1/L2/L3 autonomy tier.

    Args:
        evolution_score: From exhale Step 2 (relevance * type_weight * novelty)
        mode: experiment | hypothesis | design | code
        files_changed: List of file paths that would be modified
        max_score: Maximum possible evolution_score (for normalization)

    Returns:
        AutonomyResult with level, confidence, risk, reason, and action
    """
    confidence = _compute_confidence(evolution_score, max_score)
    risk = _compute_risk(mode, files_changed)

    if confidence > 0.7 and risk < 0.4:
        return AutonomyResult(
            level=AutonomyLevel.L1_INFORM,
            confidence=confidence,
            risk=risk,
            reason=f"High confidence ({confidence:.2f}) + low risk ({risk:.2f})",
            action="Auto-executing. Will report results after completion.",
        )
    elif confidence < 0.4 and risk > 0.6:
        # L3 first: low confidence AND high risk → delegate
        return AutonomyResult(
            level=AutonomyLevel.L3_DELEGATE,
            confidence=confidence,
            risk=risk,
            reason=f"Low confidence ({confidence:.2f}) + high risk ({risk:.2f})",
            action="Presenting design only. Please review and execute manually.",
        )
    else:
        return AutonomyResult(
            level=AutonomyLevel.L2_CONFIRM,
            confidence=confidence,
            risk=risk,
            reason=f"Moderate confidence ({confidence:.2f}) or risk ({risk:.2f})",
            action="Presenting summary for your confirmation before proceeding.",
        )


def format_autonomy_header(result: AutonomyResult, artifact_name: str) -> str:
    """Format autonomy classification as a display header."""
    icons = {
        AutonomyLevel.L1_INFORM: "[L1 INFORM]",
        AutonomyLevel.L2_CONFIRM: "[L2 CONFIRM]",
        AutonomyLevel.L3_DELEGATE: "[L3 DELEGATE]",
    }
    return (
        f"{icons[result.level]} {artifact_name}\n"
        f"  Confidence: {result.confidence:.2f} | Risk: {result.risk:.2f}\n"
        f"  {result.reason}\n"
        f"  -> {result.action}"
    )
