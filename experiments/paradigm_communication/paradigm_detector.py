"""
ParadigmDetector — reads epistemic_basis / causal_model / locus_of_control from text.

Meisner principle: don't prepare the response.
Receive the other person first. The right words come from what you actually received.

This module is the "receiving" layer.
"""

import re
from dataclasses import dataclass, field
from typing import Optional


@dataclass
class ParadigmProfile:
    epistemic_basis: str = "unknown"      # data-driven / intuition-first / authority-referencing
    causal_model: str = "unknown"         # linear / systemic / emergent
    locus_of_control: str = "unknown"     # internal / external / distributed
    confidence: float = 0.0
    signals: list = field(default_factory=list)
    gaps: list = field(default_factory=list)   # what they're NOT saying


# ── Signal dictionaries ────────────────────────────────────────────────────

EPISTEMIC_SIGNALS = {
    "data-driven": [
        r"\b(data|evidence|metric|measure|stat|number|percent|result|study|research|prove|show)\b",
        r"\b(analysis|analyze|quantif|benchmark|test|experiment|validate)\b",
    ],
    "intuition-first": [
        r"\b(feel|sense|gut|instinct|intuit|believe|think|seem|probably|likely|hunch)\b",
        r"\b(experience tells|in my experience|i've seen|pattern|usually|typically)\b",
    ],
    "authority-referencing": [
        r"\b(expert|industry|standard|best practice|according to|research says|studies show)\b",
        r"\b(everyone|they say|people say|common knowledge|well-known|accepted)\b",
    ],
}

CAUSAL_SIGNALS = {
    "linear": [
        r"\b(if.{0,20}then|because|therefore|so|leads to|results in|causes|due to)\b",
        r"\b(step \d|first.{0,10}then|finally|in order to|to achieve)\b",
        r"\b(proven|follow|adopt|implement|apply|use|should do|we should)\b",
        r"\b(before moving|need to.{0,20}before|revert|sequential|analyze.{0,20}then|fix.{0,20}then)\b",
    ],
    "systemic": [
        r"\b(feedback|loop|cycle|system|structure|dynamic|interconnect|depend|influence)\b",
        r"\b(underlying|root cause|pattern|cascade|ripple|compound|leverage)\b",
    ],
    "emergent": [
        r"\b(emerge|evolve|adapt|complex|unpredictable|organic|self-organiz|develop over)\b",
        r"\b(context|situational|it depends|case by case|nuance|fluid)\b",
        r"\b(soul|disconnected|hard to explain|sense|feels wrong|something about|losing its)\b",
    ],
}

LOCUS_SIGNALS = {
    "internal": [
        r"\b(I |I've|I'm|my |we |our |I need|I want|I decided|I chose|I believe)\b",
        r"\b(we can|we should|we need to|our responsibility|our choice)\b",
    ],
    "external": [
        r"\b(they|market|environment|constraints|forced|no choice|have to|must|required)\b",
        r"\b(pressure|demands|stakeholders|regulations|competition|limited by)\b",
        r"\b(industry leaders|industry|McKinsey|best companies|leaders do|everyone does|all do this)\b",
    ],
    "distributed": [
        r"\b(together|collaborate|community|shared|ecosystem|network|peers|partners)\b",
        r"\b(collective|joint|mutual|co-|aligned|coordination)\b",
    ],
}

# Absence signals — what NOT being said reveals
GAP_PATTERNS = {
    "no_data_anchor": (EPISTEMIC_SIGNALS["data-driven"], "speaks without data — may be intuition-first or authority-reliant"),
    "no_agency": (EPISTEMIC_SIGNALS["intuition-first"] + [r"\bI \b", r"\bwe \b"], "avoids first-person — external locus likely"),
    "no_feedback_loop": (CAUSAL_SIGNALS["systemic"], "only linear causation — systemic effects invisible"),
}


# ── Detector ───────────────────────────────────────────────────────────────

class ParadigmDetector:
    """
    Reads a conversation turn and extracts the speaker's paradigm profile.

    Usage:
        detector = ParadigmDetector()
        profile = detector.detect("I think we need data before deciding anything.")
        # profile.epistemic_basis → "data-driven"
    """

    def detect(self, text: str) -> ParadigmProfile:
        text_lower = text.lower()
        profile = ParadigmProfile()
        signals = []

        profile.epistemic_basis, eb_score, eb_signals = self._score_dimension(
            text_lower, EPISTEMIC_SIGNALS
        )
        profile.causal_model, cm_score, cm_signals = self._score_dimension(
            text_lower, CAUSAL_SIGNALS
        )
        profile.locus_of_control, loc_score, loc_signals = self._score_dimension(
            text_lower, LOCUS_SIGNALS
        )

        signals.extend(eb_signals + cm_signals + loc_signals)
        profile.signals = signals
        profile.confidence = (eb_score + cm_score + loc_score) / 3.0
        profile.gaps = self._detect_gaps(text_lower)

        return profile

    def _score_dimension(self, text: str, signal_dict: dict) -> tuple:
        scores = {}
        matched_signals = []

        for label, patterns in signal_dict.items():
            count = 0
            for pattern in patterns:
                matches = re.findall(pattern, text, re.IGNORECASE)
                count += len(matches)
                if matches:
                    matched_signals.append(f"{label}:{matches[0]}")
            scores[label] = count

        if not any(scores.values()):
            return "unknown", 0.0, []

        winner = max(scores, key=scores.get)
        total = sum(scores.values()) or 1
        confidence = scores[winner] / total

        return winner, confidence, matched_signals[:3]

    def _detect_gaps(self, text: str) -> list:
        gaps = []
        for gap_name, (patterns, description) in GAP_PATTERNS.items():
            found = any(
                re.search(p, text, re.IGNORECASE) for p in patterns
            )
            if not found:
                gaps.append({"gap": gap_name, "description": description})
        return gaps


# ── Quick test ─────────────────────────────────────────────────────────────

if __name__ == "__main__":
    detector = ParadigmDetector()

    samples = [
        ("data-driven/linear", "We need to analyze the metrics first. The data shows a 23% drop. If we fix the funnel, revenue will increase."),
        ("intuition-first/emergent", "I feel like the market is shifting. These things tend to evolve on their own — it depends on how the community responds."),
        ("authority-referencing/systemic", "Best practices say we should have feedback loops. The industry standard is to look at the underlying structure, not just symptoms."),
        ("internal/emergent", "I've decided we need to adapt. I think the system will evolve if we create the right conditions."),
    ]

    for expected, text in samples:
        p = detector.detect(text)
        print(f"\n[{expected}]")
        print(f"  text: {text[:60]}...")
        print(f"  detected: {p.epistemic_basis} / {p.causal_model} / {p.locus_of_control}")
        print(f"  confidence: {p.confidence:.2f}")
        print(f"  gaps: {[g['gap'] for g in p.gaps]}")
