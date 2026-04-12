# Viral Growth / K-factor Core Theory (T1)
**corpus**: marketing_growth | **doc_id**: T1 | **layer**: L2  
**Date**: 2026-04-12 | **Status**: stable

---

## 1. K-factor Formula

**K = invitations_per_user × invitation_conversion_rate**

| K range | Growth effect | Practical implication |
|---------|--------------|----------------------|
| K < 0.3 | Viral supplementation only | Each 100 users generates <30 organic — minimal compounding |
| 0.3 ≤ K < 0.7 | Meaningful CAC reduction | Each 100 users generates 30–70 organic — viable supplementary channel |
| 0.7 ≤ K < 1.0 | Strong supplementary compounding | Sub-viral but substantial organic contribution |
| K ≥ 1.0 | Self-sustaining viral growth | Theoretically unbounded — scaling infrastructure required |

**Planning baseline**: Most successful viral products operate at K = 0.4–0.8 and supplement with other channels. K > 1.0 is a hyper-growth outlier, not a planning target.

---

## 2. Loop Velocity (Cycle Time)

**Viral cycle time** = time between a user completing the trigger action and their invitees completing the same action.

**Compounding effect**: At K = 0.7, a 2-day cycle → ~15 viral generations/month; a 14-day cycle → ~2. Halving cycle time at K > 1.0 roughly doubles growth rate.

**Lever priority**: When K > 0.5, optimizing cycle time often outweighs further increasing K.

**Benchmark range**: 2–14 days (B2C consumer apps: 2–5 days; B2B SaaS: 7–21 days).

---

## 3. Five Loop Archetypes

| Archetype | Mechanism | Canonical examples | Sharing source |
|-----------|-----------|-------------------|----------------|
| **Viral / referral** | Users directly invite contacts | Dropbox, PayPal | Incentive + workflow |
| **Product-led (embedded virality)** | Product usage distributes itself | Calendly, Figma, Zoom | Functional necessity |
| **Content SEO** | User behavior generates indexed content | Ahrefs free tools, Lemlist | Search discovery |
| **UGC / community** | User-created content compounds organic reach | TikTok, Substack | Platform amplification |
| **Paid reinvestment** | LTV > CAC funds next cohort | Twitch (CAC -70% via loop) | Economic flywheel |

**Archetype selection rule**: If sharing is not inherent to core product usage, choose incentivized referral loop — NOT product-led loop. Forcing PLG mechanics onto a non-collaborative product produces <2% share CTR.

---

## 4. Activation Rate (Primary Lever)

**Activation rate** = share of new users who complete the loop trigger action (the specific action that initiates viral sharing).

- Most commonly untracked metric in viral growth
- Optimizing K-factor on a low-activation product wastes capital
- **Optimization priority**: Activation Rate → Cycle Time → K-factor (in this order)

Only 34% of PLG companies actively track activation as a distinct metric (OpenView 2024).

---

## 5. PLG (Product-Led Growth) Context

- 60% of SaaS companies adopted PLG by 2024, up from 35% in 2021 (OpenView benchmark)
- PLG companies are 2x more likely to grow 100%+ YoY vs sales-led
- Gartner: 75% of B2B buying cycles will start with try-in-product by 2029

**PLG ≠ embedded virality by default**: PLG is a go-to-market motion; embedded virality is a specific loop archetype. A product can be PLG without being viral (e.g., no collaborative sharing).

---

## 6. Viral Quality Metrics

| Metric | Role | Measurement |
|--------|------|-------------|
| Invitation acceptance rate | Leading indicator — trust erosion before K collapses | Invites accepted / invites sent |
| Virally-acquired 30-day retention | Viral quality — warm introductions retain better | Cohort retention by acquisition source |
| K-factor per cohort | Trend over time — degradation signals loop health | Per-cohort K |
| Sharing rate | 15–40% of active users should share | Sharers / MAU |
| Invitation conversion | 10–30% of invitees should convert | New activations / invites sent |

**Trust monitoring rule**: If invitation acceptance rate drops >20% within 4 cohort weeks, the loop is extracting trust rather than creating value.

---

## 7. Benchmark Reference (Verified Multi-Source)

| Product | K-factor | Source quality |
|---------|----------|----------------|
| Dropbox | ~0.7 | Multi-source (Arfadia, Prefinery) |
| Dropbox referral % of daily signups | 35% at peak | GrowthHackers / Brands at Play |
| Dropbox growth via referral loop | 3,900% in 15 months | Multi-source |
| LinkedIn / PayPal / Zoom (hyper-growth) | 1.3–1.5 | MetricHQ |
| Slack (peak, single-source) | ~8.5 | Arfadia only — directional |
| Facebook (peak, single-source) | ~7 | Arfadia only — directional |

**⚠️ Slack/Facebook K benchmarks**: single-source, not independently verifiable. Treat as directional upper bound, not planning targets.

---

## Sources
- shno.co — Growth Loop Statistics 2026 (July 2025 compilation, 90+ stats)
- stratrix.com — The Anatomy of a Viral Growth Strategy
- MetricHQ — Viral Coefficient benchmarks
- OpenView Partners — SaaS PLG Benchmark 2024
- Arfadia — K-Factor Glossary and Growth Analysis Guide
- CraftUp — Growth Loop Examples and Templates (November 2025)
