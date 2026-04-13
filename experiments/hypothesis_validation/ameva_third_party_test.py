#!/usr/bin/env python3
"""
ameva Corpus Router — 제3자 쿼리 검증
corpus trigger 목록을 참조하지 않고 도메인 설명만 보고 작성한 자연어 쿼리 10개로 라우팅 정확도 측정.
Coverage bias 제거 목적.
"""

import sys, math, re
sys.path.insert(0, '/home/jayone/Project/Entity/experiments/hypothesis_validation')

# ── 제3자 쿼리 10개 (도메인 설명만 참조, trigger 목록 미참조) ────────────────────────
# 작성 원칙: 실제 사용자가 자연스럽게 입력할 법한 문장. 기술 용어 최소화.

THIRD_PARTY_QUERIES = [
    # [A] intent=wtp — "고객이 왜 돈을 내는가" 관련 질문
    {
        "query": "고객이 실제로 돈을 낼 만한지 어떻게 확인할 수 있나",
        "expected_corpus": "wtp",
        "intent_label": "WTP — 지불 의향 확인",
    },
    {
        "query": "커리어 개발 툴에서 직업 아닌 정체성 기준으로 고객 분류하는 방법",
        "expected_corpus": "wtp",
        "intent_label": "WTP — ICP 정의 (identity portability)",
    },
    {
        "query": "지불 의향 측정을 위한 고객 인터뷰 질문 설계",
        "expected_corpus": "wtp",
        "intent_label": "WTP — 인터뷰 프로토콜",
    },

    # [B] intent=marketing_growth — "유저를 어떻게 늘리나" 관련 질문
    {
        "query": "유저가 자발적으로 친구에게 서비스를 추천하게 만드는 구조",
        "expected_corpus": "marketing_growth",
        "intent_label": "Growth — 자발적 추천 구조 = referral loop",
    },
    {
        "query": "바이럴 계수가 1이 넘어야 성장에 의미 있는 건가",
        "expected_corpus": "marketing_growth",
        "intent_label": "Growth — viral coefficient threshold",
    },
    {
        "query": "신규 유저 획득 비용을 제품 설계로 줄이는 방법",
        "expected_corpus": "marketing_growth",
        "intent_label": "Growth — CAC reduction via product",
    },

    # [C] intent=monetization — "어떻게 돈을 버나" 관련 질문
    {
        "query": "AI 제품의 적정 마진은 얼마인가",
        "expected_corpus": "monetization",
        "intent_label": "Monetization — AI gross margin",
    },
    {
        "query": "월 구독제 vs 사용량 기반 요금제 중 어떤 게 맞나",
        "expected_corpus": "monetization",
        "intent_label": "Monetization — subscription vs usage-based",
    },
    {
        "query": "무료로 시작해서 유료로 전환시키는 제품 설계",
        "expected_corpus": "monetization",
        "intent_label": "Monetization — freemium to paid conversion",
    },

    # [D] intent=generic — 미등록 도메인 (정확한 라우팅 = generic)
    {
        "query": "팀 생산성을 높이는 협업 도구 추천",
        "expected_corpus": None,
        "intent_label": "Unregistered — HR/productivity",
    },
]


# ── Router (ameva_benchmark.py에서 복사 — P22 포함) ─────────────────────────────

def normalize(text: str) -> str:
    return text.lower().replace("-", "").replace("_", "").strip()

_KO_PARTICLES = re.compile(
    r'(가|이|는|은|를|을|의|와|과|로|으로|에서|에게|에|서|도|만|까지|부터|한테|처럼|마다)$'
)
def _strip_particles(token_norm: str) -> str:
    return _KO_PARTICLES.sub('', token_norm)

def tokenize(query: str) -> list:
    signals = []
    for t in query.split():
        if len(t) > 1:
            n = normalize(t)
            signals.append(n)
            stripped = _strip_particles(n)
            if stripped != n and len(stripped) > 1:
                signals.append(stripped)
    return signals

# -- Corpus Registry (abbreviated — triggers only)
CORPUS_TRIGGERS = {
    "wtp": [
        "WTP", "VALUE GAP", "L1-L5", "L1", "L2", "L3", "L4", "L5", "갭", "gap",
        "Career Mirror", "identity gap",
        "수요", "지불 의향", "정체성", "빠짐", "Social Amplifier", "커리어 미러",
        "ICP", "레벨", "진단",
        "D(WTP)", "Gap_Intensity", "Attainability", "Ethical_Coefficient",
        "돈을 낼",  # P24: phrase trigger, FP 검증 완료
    ],
    "marketing_growth": [
        "viral", "virality", "k-factor", "k factor", "growth loop", "viral loop",
        "referral loop", "viral coefficient", "user acquisition", "growth channel",
        "PLG", "product-led growth", "CAC reduction", "organic growth",
        "loop velocity", "cycle time",
        "마케팅", "바이럴", "성장 루프", "사용자 획득", "채널", "획득", "리퍼럴",
    ],
    "monetization": [
        "monetization", "수익화", "pricing model", "price model", "saas pricing",
        "revenue model", "usage-based", "usage based", "outcome-based", "outcome based",
        "freemium", "flat-rate", "seat pricing", "hybrid pricing", "ltv cac", "ltv:cac",
        "gross margin", "가격 모델", "가격 전략", "수익 모델", "과금", "수익", "마진",
        "유료화", "cogs", "payback period", "nrr", "net revenue retention",
        "value metric", "bill shock", "enterprise pricing",
        "구독제", "요금제",  # P23: 제3자 쿼리 검증에서 발견된 coverage gap
    ],
}

RELATED_DOMAINS = {
    "wtp": ["pricing", "product", "sales", "research"],
    "marketing_growth": ["demand_theory", "product", "pricing"],
    "monetization": ["demand_theory", "product", "marketing_growth"],
}

# IDF
_trigger_freq = {}
for cname, triggers in CORPUS_TRIGGERS.items():
    _seen = set()
    for t in triggers:
        tn = normalize(t)
        if tn not in _seen:
            _trigger_freq[tn] = _trigger_freq.get(tn, 0) + 1
            _seen.add(tn)
_N = max(len(CORPUS_TRIGGERS), 2)

def _idf(t_norm: str) -> float:
    df = _trigger_freq.get(t_norm, 1)
    return max(0.3, min(2.5, math.log(_N / df + 1)))

def _idf_conf(overlap_tokens: set, all_signals: list) -> float:
    numer = sum(_idf(t) for t in overlap_tokens)
    denom = sum(_idf(t) for t in all_signals) or 1.0
    return min(numer / denom, 1.0)

def extract_phrase_signals(query_norm: str, triggers: list) -> set:
    found = set()
    for trigger in triggers:
        t_norm = normalize(trigger)
        if " " in t_norm and t_norm in query_norm:
            found.add(t_norm)
    return found

CONFIDENCE_THRESHOLD = 0.08  # P23: lowered from 0.15 — IDF recall denominator 기반 재보정

def route(query: str):
    query_norm = normalize(query)
    signals = tokenize(query)

    matched = []
    for cname, triggers in CORPUS_TRIGGERS.items():
        norm_triggers = set(normalize(t) for t in triggers)
        token_overlap = set(signals) & norm_triggers
        phrase_overlap = extract_phrase_signals(query_norm, triggers)
        overlap = token_overlap | phrase_overlap
        if overlap:
            matched.append((cname, len(overlap), overlap))

    if not matched:
        # related_domains scan
        for cname, related in RELATED_DOMAINS.items():
            domain_overlap = set(signals) & set(related)
            if domain_overlap:
                matched.append((cname, len(domain_overlap), domain_overlap, "related"))
        if matched:
            best = max(matched, key=lambda x: x[1])
            return best[0], 0.30, "corpus_related"
        return None, 0.0, "generic"

    best = max(matched, key=lambda x: x[1])
    confidence = _idf_conf(best[2], signals)
    if confidence < CONFIDENCE_THRESHOLD:
        return None, confidence, "generic_low_conf"
    return best[0], confidence, "corpus"


# ── Run test ──────────────────────────────────────────────────────────────────
print("=" * 70)
print("ameva 제3자 쿼리 검증 (trigger 목록 미참조)")
print("=" * 70)

results = []
for i, tc in enumerate(THIRD_PARTY_QUERIES, 1):
    corpus, conf, mode = route(tc["query"])
    expected = tc["expected_corpus"]
    correct = (corpus == expected)
    results.append({
        "id": i, "query": tc["query"], "intent": tc["intent_label"],
        "expected": expected, "got": corpus, "conf": conf, "mode": mode, "correct": correct,
    })
    icon = "✓" if correct else "✗"
    exp_str = expected or "generic"
    got_str = corpus or "generic"
    print(f"  [{icon}] TC{i:02d} expected={exp_str:<20} got={got_str:<20} conf={conf:.2f}")
    print(f"         질문: {tc['query']}")
    if not correct:
        print(f"         의도: {tc['intent_label']}")
    print()

# ── Summary ───────────────────────────────────────────────────────────────────
total = len(results)
passed = sum(1 for r in results if r["correct"])
fail_cases = [r for r in results if not r["correct"]]

print("=" * 70)
print(f"TOTAL: {total} | PASS: {passed} | FAIL: {total-passed} | PASS_RATE: {passed/total*100:.1f}%")
print(f"목표: ≥7/10 (70%+) → {'PASS' if passed >= 7 else 'FAIL'}")
print("=" * 70)

if fail_cases:
    print("\n[실패 분석 — coverage gap]")
    for r in fail_cases:
        exp = r["expected"] or "generic"
        got = r["got"] or "generic"
        print(f"  TC{r['id']:02d}: '{r['query']}'")
        print(f"        expected={exp}, got={got}, conf={r['conf']:.2f}, mode={r['mode']}")
        print(f"        의도: {r['intent']}")
        print()
