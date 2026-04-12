# Marketing / Growth Corpus Draft
**Protocol**: expert-research-v2  
**Domain**: Viral Growth / K-factor / Growth Loops / User Acquisition Channels  
**Date**: 2026-04-12  
**Status**: DRAFT — human review required before promotion to stable

---

## Phase 1 — Web Grounding

### Sources Retrieved

1. **shno.co — Growth Loop Statistics for 2026** (July 2025 compilation, 90+ stats, 30+ primary sources)  
   URL: https://www.shno.co/marketing-statistics/growth-loop-statistics

2. **Stratrix — The Anatomy of a Viral Growth Strategy** (8-component framework, case studies: Calendly, Loom, LinkedIn, Facebook)  
   URL: https://www.stratrix.com/strategy-studio/viral-growth-strategy

3. **MetricHQ — Viral Coefficient benchmarks**  
   URL: https://www.metrichq.org/marketing/viral-coefficient/

4. **CraftUp — Growth Loop Examples and Templates** (November 2025)  
   Referenced via shno.co compilation

5. **OpenView Partners — SaaS PLG benchmark 2024** (60% PLG adoption)  
   Referenced via shno.co compilation

6. **Arfadia — K-Factor Glossary and Growth Analysis Guide**  
   Referenced via shno.co compilation

7. **Insightful CFO Blog — Viral Coefficient Engineering Guide** (July 2025)  
   Referenced via shno.co compilation

---

## Phase 2 — Multi-Lens Analysis

### LENS 1 (Domain Expert): Key Insights with Evidence Tags

**Insight 1 — K-factor is a compound variable, not a single dial**  
K = invitations_per_user × conversion_rate. Practitioners often try to increase K by pushing more invitations but the conversion rate lever is typically higher-leverage. Slack's peak K ≈ 8.5 and Facebook's ≈ 7 were achieved by combining collaborative workflow virality (high conversion) with high branching (team-based product). Most "successful viral products" actually operate at K = 0.4–0.8 and supplement with other channels — K > 1.0 is the exception, not the baseline expectation.  
[src: shno.co/MetricHQ/Arfadia; stratrix.com component-2]

**Insight 2 — Cycle time is the hidden multiplier; reducing it outweighs increasing K when K > 1.0**  
At K = 0.7 with a 2-day cycle, a product completes ~15 viral generations per month; at a 14-day cycle the same K yields ~2. Dropbox's sub-1.0 K (≈ 0.7) drove 3,900% growth in 15 months precisely because its utility-embedded reward (storage) compressed activation time. Loop velocity is underoptimized by most growth teams.  
[src: shno.co CraftUp Nov-2025; stratrix.com component-4]

**Insight 3 — Five loop archetypes cover most documented high-growth mechanics**  
(a) Viral/referral — users invite directly (Dropbox, PayPal)  
(b) Product-led — usage itself distributes (Calendly, Figma, Zoom)  
(c) Content SEO — user behavior generates indexed content (Ahrefs free tool, Lemlist)  
(d) UGC/community — user-created content compounds organic reach (TikTok, Substack)  
(e) Paid reinvestment — LTV > CAC funds next cohort (Twitch reduced CAC 70% via loop)  
The most durable loops embed virality into core product usage ("embedded virality") so sharing is inseparable from utility.  
[src: shno.co; stratrix.com component-1]

**Insight 4 — PLG is now dominant; 60% of SaaS adopted PLG by 2024, up from 35% in 2021**  
Gartner projects 75% of B2B buying cycles will start with a try-in-product experience by 2029. PLG companies are 2x more likely to grow 100%+ YoY vs sales-led. Only 34% of PLG companies actively track activation as a distinct metric — the most common missed measurement gap.  
[src: OpenView 2024 benchmark; ProductLed.org; shno.co]

**Insight 5 — Viral loop quality matters more than viral loop volume**  
Virally-acquired users consistently show higher 30-day retention than paid-acquired users because they arrive via warm introductions. LinkedIn's $13M lawsuit (2015) is the canonical case of aggressive viral optimization destroying trust capital. Invitation acceptance rate decay signals loop health degradation before K-factor collapse.  
[src: stratrix.com components 7–8; shno.co MetricHQ]

---

### LENS 2 (Devil's Advocate): Overconfidence and Missing Elements

**Challenge 1 — K-factor benchmarks from shno.co are single-source aggregates**  
Slack K ≈ 8.5 and Facebook K ≈ 7 are cited from "Arfadia K-Factor glossary" without primary sourcing to Slack/Facebook internal data. These figures are plausible but not independently verifiable. The corpus should treat hyper-growth K benchmarks as directional, not authoritative.

**Challenge 2 — The "growth loop beats funnel" framing conflates correlation with causation**  
The 40% higher CLV and 40% lower CAC statistics are from Trumpet Marketing (July 2025), a vendor with commercial incentive to promote loop-based tools. Loop-based companies may have better LTV not because of loop mechanics but because PLG self-selects for stronger product-market fit.

**Challenge 3 — Loop velocity data lacks industry segmentation**  
The 2–14 day cycle time range (CraftUp, Nov 2025) collapses B2C messaging (hours), B2C consumer apps (days), and B2B SaaS (weeks) into a single band. Marketing vertical applications differ substantially; a corpus claiming universal K-factor benchmarks without segmentation will produce bad routing decisions.

**Challenge 4 — Anti-patterns are underspecified in the source material**  
Sources describe anti-patterns anecdotally (LinkedIn spam, bolted-on referral buttons) but do not provide failure rate statistics. The "adding multiple loops simultaneously" anti-pattern identified by CraftUp lacks quantitative backing.

**Challenge 5 — AI-native viral coefficient claims are very new data**  
The "AI-native companies are 3.3x more likely to be viral growth outliers" stat (Arfadia, 2024) is a single-study claim about a fast-moving category. ChatGPT's loop dynamics (shared GPTs) may not generalize to narrower vertical AI tools.

---

### LENS 3 (Synthesizer): Reconciled, Actionable Insights

**S1 — Use K-factor as a relative benchmark, not an absolute target**  
K > 1.0 is academically interesting but practically rare. The actionable threshold is: K > 0.3 provides meaningful CAC reduction (every 100 paid users generates 30+ organic), K > 0.7 creates compounding supplementary growth, K > 1.0 requires scaling preparation. Do not set K > 1.0 as a gate for strategy activation.

**S2 — Optimize the loop in this priority order: Activation Rate → Cycle Time → K-factor**  
Activation rate (do new users complete the trigger action?) is the most predictive metric and the most commonly untracked. Fix the leaky activation floor before trying to increase invitation volume.

**S3 — Match loop archetype to product mechanics, not aspiration**  
If sharing is not inherent to core usage, an incentivized referral loop is the correct intervention — not a product-led loop. Forcing PLG mechanics onto a non-collaborative tool produces "bolted-on virality" (< 2% share CTR). The archetype selection is a product architecture decision, not a marketing decision.

**S4 — Treat trust as a non-negotiable constraint in all loop design**  
Invitation acceptance rate is the leading indicator of trust erosion, K-factor collapse is the lagging indicator. Monitor acceptance rate weekly; if it drops > 20% within 4 cohort weeks, the loop is extracting trust rather than creating value.

**S5 — PLG + content SEO loops have the strongest evidence base for sustainable compounding**  
UGC loops show impressive ROI numbers (400% return) but depend on platform-level content moderation investment. For early-stage products, PLG embedded virality + content SEO is the highest confidence combination.

---

## Phase 3 — Research Synthesis Summary

### Core Quantitative Benchmarks (verified multi-source)

| Metric | Value | Source Quality |
|---|---|---|
| Slack peak K-factor | ~8.5 | Single source (Arfadia) — directional |
| Dropbox K-factor | ~0.7 | Multi-source (Arfadia, Prefinery) |
| Dropbox referral % of daily signups | 35% at peak | GrowthHackers via Brands at Play |
| Dropbox growth via referral loop | 3,900% in 15 months | Multi-source |
| LinkedIn/PayPal/Zoom K range | 1.3–1.5 hyper-growth | MetricHQ |
| PLG adoption (SaaS, 2024) | 60% | OpenView 2024 benchmark |
| Loop-driven LTV premium | +40% vs funnel | Trumpet Marketing (vendor — use cautiously) |
| PLG companies tracking activation | 34% | ProductLed benchmark |
| Two-sided incentive conversion lift | +25–50% | Stratrix (aggregated) |
| Viral cycle time (B2C–B2B range) | 2–14 days | CraftUp Nov-2025 |
| Sharing rate target | 15–40% active users | Stratrix dashboard |
| Invitation conversion target | 10–30% | Stratrix dashboard |

---

## Draft Corpus YAML

```yaml
name: marketing_growth
primary_domain: go_to_market
related_domains: [demand_theory, product, pricing]
layer: L2
domain: "Viral growth / K-factor / growth loops / user acquisition channels"
trigger:
  - viral
  - virality
  - k-factor
  - k factor
  - growth loop
  - viral loop
  - referral loop
  - viral coefficient
  - user acquisition
  - growth channel
  - PLG
  - product-led growth
  - CAC reduction
  - organic growth
  - loop velocity
  - cycle time
  - 마케팅
  - 바이럴
  - 성장 루프
  - 사용자 획득
  - 채널
  - 획득
  - 리퍼럴
corpus_root: /home/jayone/Project/Entity/docs/research/
docs: {}  # empty — docs to be filled after stable review
taxonomy_groups:
  이론:
    - K-factor formula (K = invitations_per_user × conversion_rate)
    - viral coefficient thresholds (< 0.3 / 0.3-0.7 / 0.7-1.0 / > 1.0)
    - loop archetype taxonomy (viral, PLG, content SEO, UGC, paid reinvestment)
    - network effects vs viral growth distinction
    - STEPPS framework (Social Currency, Triggers, Emotion, Public, Practical Value, Stories)
  실행:
    - activation rate optimization (most underprioritized lever)
    - cycle time compression tactics
    - two-sided incentive design
    - viral funnel tracking (sharers → invites → clicks → signups → activations → re-sharers)
    - cohort K-factor monitoring
    - invitation acceptance rate as trust signal
  검증:
    - cohort decay chart (K-factor over time per cohort)
    - retained viral users vs paid-acquired user comparison
    - loop attribution methodology (first-party, post-ATT)
    - benchmark contextualization by loop type and B2C/B2B segment
core_theory: |
  K-factor (viral coefficient) = invitations_per_user × invitation_conversion_rate.
  K > 1.0 creates theoretically self-sustaining growth; most successful viral products
  operate at K = 0.4–0.8 and supplement with other channels. Cycle time (time between
  viral generations) is the compounding multiplier: at K > 1.0, halving cycle time
  roughly doubles growth rate. Five loop archetypes cover high-growth mechanics:
  viral/referral, product-led (embedded virality), content SEO, UGC/community, and
  paid reinvestment. Activation rate — the share of new users who complete the loop
  trigger action — is the most predictive metric and the most commonly untracked.
  Viral loop sustainability requires treating trust (invitation acceptance rate) as a
  non-negotiable constraint.
scope_gate:
  - "Query involves growth rate mechanics, referral programs, or user acquisition cost optimization"
  - "Query involves loop design, loop archetype selection, or viral coefficient diagnosis"
  - "Query involves PLG, freemium conversion funnels, or embedded virality assessment"
  out_action: "PLG or AARRR framework for non-viral scenarios; demand_theory corpus for WTP/pricing questions; product corpus for feature design questions without acquisition context"
sycophancy_checks:
  Q1: "Is the user assuming K > 1.0 is achievable for their product? Most products achieve K = 0.3–0.7 and still grow well — correct this expectation before strategy design."
  Q2: "Is the user treating viral growth as a marketing tactic rather than a product architecture decision? Bolted-on referral buttons underperform embedded virality by an order of magnitude."
  Q3: "Is the user optimizing K-factor before fixing activation rate? Increasing K on a low-activation product wastes capital — activation is the higher-leverage prior step."
  Q4: "Is the user citing Slack/Facebook K-factor benchmarks (8.5 / 7) as realistic targets? These are outlier hyper-growth peak figures from single-source data, not planning baselines."
  Q5: "Is the user measuring loop success by invitation volume rather than retained virally-acquired users? High invitation volume with poor retention signals trust erosion, not growth."
gap_patterns:
  loop_archetype_mismatch: "User describes a non-collaborative product but asks for PLG/embedded virality — route to incentivized referral design instead"
  k_factor_overreach: "User sets K > 1.0 as baseline target — reframe around CAC reduction value at K = 0.3–0.7 range"
  activation_blind_spot: "User discusses loop mechanics without mentioning activation rate — flag as measurement gap"
  trust_erosion_risk: "User proposes high-frequency invite prompts or contact harvesting — apply anti-spam / trust preservation check"
  vanity_viral_metrics: "User reports high invitation counts without retention data — redirect to viral quality metrics (30-day retention of virally-acquired users)"
rwr_hints:
  "go viral": "engineer viral loop (K-factor, loop archetype, cycle time)"
  "word of mouth": "referral loop / UGC loop / viral coefficient"
  "growth hack": "loop mechanics / activation optimization"
  "paid vs organic": "CAC structure analysis / loop supplementation model"
  "referral program": "incentivized viral loop / two-sided incentive design"
  "user acquisition": "loop archetype selection / channel mix / K-factor baseline"
  "viral marketing": "viral coefficient engineering / loop architecture"
  "shares": "loop trigger design / sharing rate optimization"
  "채널 전략": "loop archetype selection / PLG vs incentivized vs content SEO"
  "사용자 획득": "K-factor diagnostic / activation rate / loop velocity"
status: draft
```

## Related
- [[projects/Entity/research/20260412-marketing-growth-diagnostic|20260412-marketing-growth-diagnostic]]
- [[projects/Entity/research/20260411-wtp-clg-community-strategy|20260411-wtp-clg-community-strategy]]
- [[projects/Entity/research/20260411-wtp-product-design-patterns|20260411-wtp-product-design-patterns]]
- [[projects/Entity/research/20260412-marketing-growth-loop-playbook|20260412-marketing-growth-loop-playbook]]
- [[projects/Entity/research/20260412-marketing-growth-falsification|20260412-marketing-growth-falsification]]
- [[projects/Entity/research/20260412-marketing-growth-theory|20260412-marketing-growth-theory]]
- [[projects/Entity/research/20260331-skill-selection-implementation-templates|20260331-skill-selection-implementation-templates]]
- [[projects/Entity/research/20260412-skill-as-tool-vertical-ai|20260412-skill-as-tool-vertical-ai]]
