# Solver-Sampler Mismatch — Applied to biz-synthesis / MAD

## Source
- **Origin**: When Reasoning Models Hurt Behavioral Simulation: A Solver-Sampler Mismatch
  in Multi-Agent LLM Negotiation
- **arXiv**: 2604.11840
- **Absorbed via**: /inhale agent_research (2026-04-16)
- **Relevance**: 10.0 × type_weight(hypothesis_validation=1.3) × novelty=1.2 → 15.6
- **Registry status**: proposed

## Core Insight
A common assumption is that *stronger reasoning models produce better multi-agent simulations*.
The paper shows the opposite can hold: for behavioral simulation, a strong **solver** (optimal
reasoner) systematically diverges from the distribution of actual human/agent behavior that a
**sampler** (diverse behavior emulator) must reproduce. Stronger models collapse behavioral
diversity and converge too quickly to optimal play, reducing simulation fidelity.

Entity's `biz-synthesis` and MAD (`biz-sales-mda`, `biz-sales-moa`) workflows assume stronger
sub-agents → better debate quality. If solver-sampler mismatch applies, Opus-driven MAD rounds
may *reduce* argument diversity vs Sonnet/Haiku — yielding premature convergence on a single
viewpoint instead of genuine multi-perspective synthesis.

## Formal Statement

- **H0**: MAD round diversity (inter-agent argument divergence) is non-decreasing in
  reasoning-model strength (Haiku → Sonnet → Opus).
- **H1**: MAD round diversity is **non-monotonic** or **decreasing** in model strength —
  i.e., Opus rounds show lower divergence than Sonnet rounds (solver-sampler mismatch).

## Variables
- **Independent**: MAD sub-agent model tier (Haiku / Sonnet / Opus).
- **Dependent**:
  - **Diversity**: pairwise semantic distance between the 3 sub-agent outputs (embedding cosine dist).
  - **Convergence round**: which round does position overlap exceed threshold (e.g., cosine > 0.85).
  - **Final verdict quality**: human/oracle rating of synthesis (0–1).
- **Controlled**: same 10 business problems, same MAD structure (3 agents × 3 rounds),
  same synthesis prompt.

## Measurement Method
1. Fix a 10-problem business test set — draw from `biz-sales-moa` past invocations or synthesize
   new "hard" prompts where multiple viewpoints are defensible.
2. Run each problem × 3 model tiers × 3 trials (seed variation) = 90 runs.
3. Per run: capture round-1 outputs, compute pairwise cosine distance among 3 sub-agents; repeat
   per round.
4. Compare diversity curves across tiers. If Opus curve lies *below* Sonnet curve (lower diversity),
   H1 supported.
5. Statistical test: Kruskal-Wallis H-test on round-1 diversity scores across tiers; pairwise
   Mann-Whitney U for Opus vs Sonnet with Bonferroni correction.

## Success Criteria
- H1 supported: Kruskal-Wallis p < 0.05 with Opus mean diversity < Sonnet mean diversity.
- Effect size: median Opus diversity < 0.85 × median Sonnet diversity.

## Integration Points
- Reuse `biz-sales-mda` skill as the MAD harness — inject model-tier override flag.
- Embedding model: reuse existing `mcp__claude-flow__embeddings_generate` if available; otherwise
  `sentence-transformers` via `code-search` MCP.
- Output: `experiments/hypothesis_validation/solver_sampler_mismatch_report.md` with per-tier
  diversity trajectories.

## Expected Outcome
Two plausible outcomes and what each implies:
1. **H1 supported** — default to Sonnet for MAD rounds, reserve Opus only for the final synthesis
   step. This would update `biz-sales-mda` and `biz-synthesis` skill defaults.
2. **H0 supported** — the assumption holds; no change. Documents the evidence.

Either way the MAD configuration becomes grounded rather than assumed.

## Open Risks
- Diversity-as-cosine-distance is a proxy; high distance can mean "off-topic", not "diverse
  valid viewpoints". Mitigation: secondary relevance filter before computing distance.
- Trial count (3 per cell) is low for robust inference. If initial signal is ambiguous,
  escalate to 10 trials per cell.
- Cost: 90 runs with Opus can be expensive. Mitigation: pilot with 3 problems first, escalate
  only if pilot shows a directional signal.
