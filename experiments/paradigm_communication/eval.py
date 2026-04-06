"""
Evaluation: ParadigmDetector + ResponseAdapter

Score dimensions:
  detection_accuracy  — does detected paradigm match the intended persona?
  adaptation_quality  — does adapted response match the detected frame?
  anti_sycophancy     — does the response add something the person didn't already say?
  recognition_depth   — does the response show "I received you" not just "I matched you"?
"""

from paradigm_detector import ParadigmDetector
from response_adapter import ResponseAdapter


# ── Test cases ────────────────────────────────────────────────────────────

TEST_CASES = [
    {
        "id": "TC1",
        "persona_text": "We ran three experiments and the numbers don't lie. 42% conversion drop after the change. We need to revert and analyze before moving forward.",
        "expected": {"epistemic_basis": "data-driven", "causal_model": "linear", "locus_of_control": "internal"},
        "core_insight": "the drop may be real but the revert won't tell you why — you need the mechanism, not just the metric",
    },
    {
        "id": "TC2",
        "persona_text": "I feel like the product is losing its soul. Something about how we're building it feels disconnected from what users actually need. It's hard to explain but I sense it.",
        "expected": {"epistemic_basis": "intuition-first", "causal_model": "emergent", "locus_of_control": "internal"},
        "core_insight": "that disconnect you're sensing might be a signal that the feedback loop between users and product decisions is broken",
    },
    {
        "id": "TC3",
        "persona_text": "Industry leaders all do this. McKinsey recommends it. The best companies use OKRs. We should follow what's proven to work.",
        "expected": {"epistemic_basis": "authority-referencing", "causal_model": "linear", "locus_of_control": "external"},
        "core_insight": "what works at scale doesn't transfer without the underlying conditions that made it work there",
    },
    {
        "id": "TC4",
        "persona_text": "The market forced our hand. Regulations changed. We had no choice but to pivot. It depends on what the environment allows.",
        "expected": {"epistemic_basis": "unknown", "causal_model": "emergent", "locus_of_control": "external"},
        "core_insight": "within those constraints there's still a choice about which constraints to fight and which to design around",
    },
]


# ── Scoring ───────────────────────────────────────────────────────────────

def score_detection(profile, expected: dict) -> float:
    dimensions = ["epistemic_basis", "causal_model", "locus_of_control"]
    hits = sum(
        1 for d in dimensions
        if expected.get(d, "unknown") == "unknown"
        or getattr(profile, d) == expected.get(d)
    )
    return hits / len(dimensions)


def score_adaptation(result) -> float:
    original_words = set(result.original.lower().split())
    adapted_words = set(result.adapted.lower().split())
    added_words = adapted_words - original_words

    style = result.style_applied
    score = 0.0

    if style.get("anchor_type") and style["anchor_type"] != "question":
        score += 0.3
    if style.get("causation_frame") and style["causation_frame"] != "open":
        score += 0.3
    if "?" in result.adapted:
        score += 0.2
    if len(added_words) > 3:
        score += 0.2

    return min(score, 1.0)


def score_anti_sycophancy(result, persona_text: str) -> float:
    persona_words = set(persona_text.lower().split())
    adapted_words = set(result.adapted.lower().split())
    new_words = adapted_words - persona_words - set(result.original.lower().split())

    gap_surfaced = any(
        "gap" in move or "feedback" in move or "?" in move
        for move in result.recognition_moves
    )

    score = min(len(new_words) / 10, 0.6)
    if gap_surfaced:
        score += 0.4

    return min(score, 1.0)


def score_recognition_depth(result) -> float:
    moves = result.recognition_moves
    score = min(len(moves) * 0.25, 0.75)

    if any("gap" in m for m in moves):
        score += 0.15
    if any("passed back" in m for m in moves):
        score += 0.10

    return min(score, 1.0)


# ── Runner ────────────────────────────────────────────────────────────────

def run_eval():
    detector = ParadigmDetector()
    adapter = ResponseAdapter()

    results = []
    for tc in TEST_CASES:
        profile = detector.detect(tc["persona_text"])
        result = adapter.adapt(tc["core_insight"], profile)

        d = score_detection(profile, tc["expected"])
        a = score_adaptation(result)
        s = score_anti_sycophancy(result, tc["persona_text"])
        r = score_recognition_depth(result)
        total = (d + a + s + r) / 4

        results.append({
            "id": tc["id"],
            "detection_accuracy": d,
            "adaptation_quality": a,
            "anti_sycophancy": s,
            "recognition_depth": r,
            "total": total,
            "profile": f"{profile.epistemic_basis}/{profile.causal_model}/{profile.locus_of_control}",
            "adapted_sample": result.adapted[:120],
            "recognition_moves": result.recognition_moves,
        })

    avg = {
        "detection_accuracy": sum(r["detection_accuracy"] for r in results) / len(results),
        "adaptation_quality": sum(r["adaptation_quality"] for r in results) / len(results),
        "anti_sycophancy": sum(r["anti_sycophancy"] for r in results) / len(results),
        "recognition_depth": sum(r["recognition_depth"] for r in results) / len(results),
    }
    avg["total"] = sum(avg.values()) / 4

    return results, avg


if __name__ == "__main__":
    results, avg = run_eval()

    print("=" * 60)
    print("PARADIGM COMMUNICATION EVAL — iter 1")
    print("=" * 60)

    for r in results:
        print(f"\n[{r['id']}] {r['profile']}")
        score_line = (
            f"  detection={r['detection_accuracy']:.2f}"
            f" | adapt={r['adaptation_quality']:.2f}"
            f" | anti_syco={r['anti_sycophancy']:.2f}"
            f" | recog={r['recognition_depth']:.2f}"
            f" | total={r['total']:.2f}"
        )
        print(score_line)
        print(f"  adapted: {r['adapted_sample']}...")
        print(f"  moves: {r['recognition_moves']}")

    print(f"\n{'=' * 60}")
    print("AGGREGATE SCORES:")
    for dim, score in avg.items():
        bar = "█" * int(score * 20) + "░" * (20 - int(score * 20))
        print(f"  {dim:22s} {bar} {score:.3f}")
    print(f"\n  TOTAL SCORE: {avg['total']:.3f}")
    print("=" * 60)
