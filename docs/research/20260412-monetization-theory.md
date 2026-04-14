# SaaS / AI Monetization Core Theory (T1)
**corpus**: monetization | **doc_id**: T1 | **layer**: L2  
**Date**: 2026-04-12 | **Status**: stable

---

## 1. Pricing Model Taxonomy

| Model | Mechanism | Best-fit signal | Risk |
|-------|-----------|----------------|------|
| **Flat-rate / Seat** | Fixed price per user or tier | Predictable usage, B2B procurement | Value leakage at high-usage end |
| **Usage-based (UBP)** | Price per unit consumed (API call, token, seat-hour) | Variable demand, AI inference cost pass-through | Revenue volatility, customer fear of runaway costs |
| **Outcome-based** | Price tied to measurable business result delivered | High-trust relationships, verifiable ROI | Attribution complexity, long sales cycle |
| **Hybrid** | Seat/tier floor + usage or outcome overage | Balances predictability (buyer) + upside (vendor) | Billing complexity, segmentation discipline required |
| **Freemium** | Core value free → paid upgrade for advanced features | PLG motion, viral/referral loop support | High support cost per free user, conversion rate usually 2–5% |

**2026 benchmark** (OpenView + ChartMogul combined):
- 67%+ of SaaS companies >$10M ARR use hybrid or usage-based components
- Pure seat-based declining: < 30% of new B2B SaaS launches (2025 cohort)
- Outcome-based: < 10% deployed at scale, growing in AI-native products

---

## 2. AI-Specific Margin Constraints

AI products face structurally different COGS than traditional SaaS:

```
AI COGS = Inference cost + Training amortization + Data pipeline cost
Traditional SaaS COGS = Hosting + Support + Auth infra
```

| Metric | Traditional SaaS | AI SaaS (LLM-native) |
|--------|-----------------|---------------------|
| Gross margin (target) | 75–85% | 50–65% (inference-heavy) |
| COGS sensitivity | Low (mostly fixed infra) | High (scales with usage) |
| Unit economics lever | CAC/LTV ratio | Inference cost per output + caching |

**Critical implication**: Usage-based pricing with AI products must account for inference cost floors. Pricing below ~3× inference COGS creates margin inversion at scale.

---

## 3. Value Metric Selection

**Value metric** = the unit that most closely correlates with value delivered to customer.

Selection rule:
1. What does the customer measure their own success in? → align pricing unit there
2. Is your COGS correlated with that unit? → if yes, UBP is natural
3. Can the customer predict and budget for it? → if no, add seat/floor hedge

Examples:
- "Meetings transcribed" → transcription minutes (usage)
- "Deals closed faster" → outcome-based (% of deal size)
- "Teams collaborate" → seats (flat/hybrid)
- "API calls processed" → API calls (pure usage)

---

## 4. Freemium Conversion Economics

```
Freemium net value = (conversion_rate × LTV_paid) − (support_cost_per_free + infra_cost_per_free)
```

Viable only when:
- Conversion rate ≥ 2% (consumer) / 5% (B2B PLG)
- Free-to-paid upgrade path has clear friction-removal moment (Aha → Paywall)
- Viral/referral loop K-factor is meaningful (each free user generates ≥ 0.3 referrals)

**Anti-pattern**: Freemium with no viral loop and no clear paywall = permanent charity tier.

---

## 5. LTV:CAC Framework

```
LTV   = ARPU × Gross_Margin × (1 / Churn_Rate)
CAC   = Total_Sales_Marketing_Spend / New_Customers_Acquired
Payback_Period = CAC / (ARPU × Gross_Margin)
```

| Ratio | Status | Action |
|-------|--------|--------|
| LTV:CAC < 1 | Burning → stop scaling | Raise price or cut CAC |
| LTV:CAC 1–3 | Marginal | Optimize before scaling |
| LTV:CAC 3–5 | Healthy | Scale paid acquisition |
| LTV:CAC > 5 | Underpriced or exceptional retention | Consider price increase |

**Payback period target**: 12–18 months (B2B SaaS); < 24 months for enterprise.

---

## 6. Pricing Motion Alignment (Pricing × GTM)

| GTM motion | Preferred pricing model | Rationale |
|------------|------------------------|-----------|
| PLG (product-led) | Freemium + usage-based | Low friction entry, expands naturally |
| SLG (sales-led) | Flat-rate per seat (negotiated) | Predictable, fits procurement |
| CLG (community-led) | Hybrid (free community + paid tools) | Network effect monetization |
| DLG (data-led) | Outcome or usage-based | Aligns incentives with data value delivered |

---

## Sources
- OpenView Partners — SaaS Pricing Benchmark 2025
- ChartMogul — SaaS Metrics Report Q4 2025
- a16z — "The New Math of AI SaaS Unit Economics" (2025)
- Pricing I/O — Value Metric Selection Framework (2025)
- Paddle — SaaS Monetization Trends 2026 State of the Industry

## Related
- [[projects/Ameva/research/20260325-omc-autopilot-loop-vs-agent-research-trends|20260325-omc-autopilot-loop-vs-agent-research-trends]]
- [[projects/Ameva/research/20260411-wtp-demand-genesis-theory|20260411-wtp-demand-genesis-theory]]
