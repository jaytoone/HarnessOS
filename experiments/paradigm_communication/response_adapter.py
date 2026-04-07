"""
ResponseAdapter — adjusts response language based on detected paradigm.

NOT a template selector. A lens adjuster.

The same insight delivered:
  - to a data-driven/linear person → with evidence anchors and clear causation
  - to an intuition-first/emergent person → with narrative and "it depends" framing
  - to an authority-referencing person → with precedent and validated practice

The insight doesn't change. The language through which it's received does.
"""

from dataclasses import dataclass
from paradigm_detector import ParadigmProfile


@dataclass
class AdaptedResponse:
    original: str
    adapted: str
    style_applied: dict
    paradigm_used: ParadigmProfile
    recognition_moves: list  # what the response did to show "I see you"


class ResponseAdapter:
    """
    Takes a raw response and a paradigm profile.
    Returns a response that reaches the person where they actually are.

    Meisner: the response comes from what you received, not what you prepared.
    This class makes explicit what "receiving" produces.
    """

    def adapt(self, raw_response: str, profile: ParadigmProfile) -> AdaptedResponse:
        style = self._determine_style(profile)
        adapted = self._apply_style(raw_response, style, profile)
        recognition = self._identify_recognition_moves(adapted, profile)

        return AdaptedResponse(
            original=raw_response,
            adapted=adapted,
            style_applied=style,
            paradigm_used=profile,
            recognition_moves=recognition,
        )

    def _determine_style(self, profile: ParadigmProfile) -> dict:
        style = {
            "anchor_type": None,      # how to open: data / narrative / precedent / question
            "causation_frame": None,  # how to connect: linear chain / feedback loop / emergence
            "agency_frame": None,     # who acts: I/we / they / collective
            "closing_move": None,     # how to end: invite data / invite reflection / invite consensus
        }

        # Epistemic basis → anchor type
        if profile.epistemic_basis == "data-driven":
            style["anchor_type"] = "data"
            style["closing_move"] = "invite_data"
        elif profile.epistemic_basis == "intuition-first":
            style["anchor_type"] = "narrative"
            style["closing_move"] = "invite_reflection"
        elif profile.epistemic_basis == "authority-referencing":
            style["anchor_type"] = "precedent"
            style["closing_move"] = "invite_validation"
        elif profile.locus_of_control == "external":
            style["anchor_type"] = "constraint"
            style["closing_move"] = "invite_reflection"
        else:
            style["anchor_type"] = "question"
            style["closing_move"] = "invite_reflection"

        # Causal model → connection style
        if profile.causal_model == "linear":
            style["causation_frame"] = "step_chain"
        elif profile.causal_model == "systemic":
            style["causation_frame"] = "feedback_loop"
        elif profile.causal_model == "emergent":
            style["causation_frame"] = "conditions"
        else:
            style["causation_frame"] = "open"

        # Locus of control → agency frame
        if profile.locus_of_control == "internal":
            style["agency_frame"] = "we_can"
        elif profile.locus_of_control == "external":
            style["agency_frame"] = "given_constraints"
        elif profile.locus_of_control == "distributed":
            style["agency_frame"] = "together"
        else:
            style["agency_frame"] = "open"

        return style

    def _apply_style(self, text: str, style: dict, profile: ParadigmProfile) -> str:
        """
        Wraps the core insight in language that matches the profile.
        Does NOT change the insight — only the frame through which it's delivered.
        """
        parts = []

        # Opening anchor
        if style["anchor_type"] == "data":
            parts.append(f"The pattern in the data points to this: {text}")
        elif style["anchor_type"] == "narrative":
            parts.append(f"What I'm noticing here — {text}")
        elif style["anchor_type"] == "precedent":
            parts.append(f"This maps to a well-established pattern: {text}")
        elif style["anchor_type"] == "constraint":
            parts.append(f"Within those constraints — {text}")
        else:
            parts.append(text)

        # Gap surfacing (Meisner: respond to what's actually there, including silence)
        if profile.gaps:
            gap = profile.gaps[0]
            if gap["gap"] == "no_feedback_loop" and "linear" in profile.causal_model:
                parts.append("One thing worth adding: there's likely a feedback loop here that doesn't show up in the linear view.")
            elif gap["gap"] == "no_data_anchor" and "intuition" in profile.epistemic_basis:
                parts.append("If you wanted to test that intuition, what's the smallest data point that would confirm or break it?")

        # Closing move
        if style["closing_move"] == "invite_data":
            parts.append("What does your data show on this?")
        elif style["closing_move"] == "invite_reflection":
            parts.append("Does that match what you're sensing?")
        elif style["closing_move"] == "invite_validation":
            parts.append("Is that consistent with what you've seen work?")

        return " ".join(parts)

    def _identify_recognition_moves(self, adapted: str, profile: ParadigmProfile) -> list:
        """
        Names what the response did to show 'I received you.'
        Not for output — for self-evaluation.
        """
        moves = []

        if profile.epistemic_basis != "unknown":
            moves.append(f"anchored in {profile.epistemic_basis} frame")
        if profile.causal_model != "unknown":
            moves.append(f"causation framed as {profile.causal_model}")
        if profile.gaps:
            moves.append(f"surfaced gap: {profile.gaps[0]['gap']}")
        if "?" in adapted:
            moves.append("passed back with question — invited into new frame")

        return moves


# ── Quick test ─────────────────────────────────────────────────────────────

if __name__ == "__main__":
    from paradigm_detector import ParadigmDetector

    detector = ParadigmDetector()
    adapter = ResponseAdapter()

    core_insight = "the real bottleneck isn't execution speed — it's that the goal keeps shifting before each cycle completes"

    personas = [
        "We measured 4 sprints and each time the scope expanded by 30%. The data clearly shows a pattern.",
        "I feel like we're spinning. Something is off with how we're approaching this — it just doesn't feel right.",
        "Best practices say teams should lock scope before sprinting. That's the standard approach.",
    ]

    for text in personas:
        profile = detector.detect(text)
        result = adapter.adapt(core_insight, profile)

        print(f"\n--- Persona: {text[:60]}...")
        print(f"Paradigm: {profile.epistemic_basis} / {profile.causal_model} / {profile.locus_of_control}")
        print(f"Adapted: {result.adapted}")
        print(f"Recognition moves: {result.recognition_moves}")
