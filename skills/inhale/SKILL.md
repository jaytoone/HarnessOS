---
name: entity-inhale
description: Collect knowledge from research channels (papers, tools, trending repos) and extract insights relevant to your agentic project
version: 1.0.0
author: jaytoone
tags: [entity, agent, knowledge, research, evolution, self-evolving]
category: research
---

# Entity Inhale — Knowledge Absorption Layer

Part of the **Entity** self-evolving agent framework. Automates the full knowledge absorption cycle: scans research channels, scores relevance, and injects actionable insights into your session context.

```
/inhale
```

## What It Does

1. Reads `docs/knowledge-channels.yaml` — your curated list of knowledge sources (arXiv, HuggingFace, GitHub trending, YouTube channels)
2. Runs the collection pipeline — fetches and scores items by relevance to your project
3. Extracts high-signal insights — filters noise, surfaces only actionable findings
4. Injects into session context — ready to drive `/exhale` experiment design

## When to Use

- Before starting a new experiment — check if relevant external research already exists
- Daily knowledge refresh — scan for papers/tools that move your project forward
- When you want external research to inform your next iteration goal

## Do Not Use When

- You want to manually add/edit channel sources — edit `docs/knowledge-channels.yaml` directly
- You want deep YouTube analysis — use the youtube analyzer script directly

## Configuration

```yaml
# docs/knowledge-channels.yaml (your project)
categories:
  - name: agent_research
    sources:
      - type: arxiv
        query: "autonomous agent self-evolution"
      - type: github_trending
        language: python
        topic: ai-agents
```

Override defaults:
```
/inhale category:ml_engineering   # specific category
/inhale top:10                    # top N items only
```

## Pipeline Architecture

```
knowledge-channels.yaml
    → knowledge_collector.py   (fetch + relevance score)
    → harness_updater.py       (inject into session context)
    → /exhale                  (convert insights to experiments)
```

## Example Output

```
[inhale] Scanned 3 channels (agent_research)
[inhale] Top insights (score ≥ 0.7):
  1. arXiv:2504.08066 — AI Scientist-v2: ensemble reviewer achieves 69% balanced accuracy
  2. GitHub trending: oh-my-codex — parallel agent execution framework (23k stars)
  3. HF paper: POET open-ended agent evolution — novelty search prevents local optima

Injected 3 insights → ready for /exhale
```

## Part of Entity Framework

```
/inhale  → absorb external knowledge
/exhale  → design experiments from insights
/live    → execute until convergence
```

See [Entity on GitHub](https://github.com/jaytoone/HarnessOS) for full framework.
