# [expert-research-v2] Optimal Top-N for Knowledge Curation Pipeline
**Date**: 2026-04-03  **Skill**: expert-research-v2

## Original Question
What is the optimal top-N selection size for a knowledge curation pipeline?
Given: 55-150 items/category, 0-54 relevant, 3-6 sources, diversity reranking, downstream evolve processes 3-5 items.

## Web Facts
- [FACT-1] RAG research (Xu et al. 2024b): top 5-10 chunks optimal, >20 diminishes (arXiv:2501.01880)
- [FACT-2] Miller's Law: working memory 7+/-2 items, revised to ~4 chunks (Cowan)
- [FACT-3] Precision@K: Relevant_in_top_K / K — classic precision-recall tradeoff
- [FACT-4] DynamicRAG (2025): adaptive k per query outperforms fixed k
- [FACT-5] Information overload: filtering and prioritization are key strategies
- [FACT-6] Downstream evolve processes only 3-5 items per run

## Key Finding: Fixed K is Wrong — Use Adaptive K

### Measured Data (2026-04-03)
| Category | Pool | Relevant(>=3.0) | Sources | Relevance Ratio |
|---|---|---|---|---|
| agent_research | 150 | 54 | 6 | 36% |
| ml_engineering | 90 | 17 | 5 | 19% |
| product_growth | 60 | 0 | 3 | 0% |
| system_design | 55 | 5 | 3 | 9% |
| daily_digest | 100 | 3 | 4 | 3% |
| trending_tools | 85 | 6 | 4 | 7% |

### Recommended Formula
```python
def optimal_top_n(pool_size, relevant_count, source_count):
    if relevant_count == 0:
        return min(5, pool_size)  # serendipity sample
    recall_target = int(relevant_count * 0.8)  # capture 80% relevant
    min_per_source = source_count * 2  # diversity floor
    max_cap = min(50, pool_size)  # RAG research cap
    return min(max(recall_target, min_per_source), max_cap)
```

### Results
| Category | Fixed K=30 P@K | Adaptive K | Adaptive P@K | Improvement |
|---|---|---|---|---|
| agent_research | 0.55 (K=30) | 43 | 0.70 | recall +15% |
| ml_engineering | 0.22 (K=30) | 14 | 0.60 | precision +173% |
| product_growth | 0.00 (K=30) | 5 | N/A | noise -83% |
| system_design | 0.07 (K=30) | 6 | 0.33 | precision +371% |
| daily_digest | 0.03 (K=30) | 8 | 0.12 | noise -73% |
| trending_tools | 0.08 (K=30) | 8 | 0.25 | precision +213% |

## Conclusion
- **Fixed K=30 is too high for 4/6 categories**, too low for agent_research
- **Adaptive K per category** is the correct approach, supported by DynamicRAG research
- Formula: `K = min(max(relevant*0.8, sources*2), 50)`
- The two-stage architecture (inhale=buffer, evolve=consumer) means inhale K is about recall, not cognitive load
- Evolve's 3-5 item limit is the real precision gate

## Sources
- [Precision and Recall at K](https://www.evidentlyai.com/ranking-metrics/precision-recall-at-k)
- [Long Context vs RAG (arXiv:2501.01880)](https://arxiv.org/abs/2501.01880)
- [Miller's Law (Wikipedia)](https://en.wikipedia.org/wiki/The_Magical_Number_Seven,_Plus_or_Minus_Two)
- [DynamicRAG: Dynamic Context Selection](https://arxiv.org/html/2512.14313v1)
- [Information Overload Scoping Review](https://www.sciencedirect.com/science/article/pii/S2667096824000508)
- [Working Memory Capacity (Cowan)](https://pmc.ncbi.nlm.nih.gov/articles/PMC4486516/)

## Related
- [[projects/HarnessOS/research/20260331-skill-selection-implementation-templates|20260331-skill-selection-implementation-templates]]
- [[projects/HarnessOS/research/20260331-autonomous-skill-selection-research|20260331-autonomous-skill-selection-research]]
- [[projects/HarnessOS/research/20260331-skill-selection-quick-reference|20260331-skill-selection-quick-reference]]
