# Evolving Orchestration Prompts — Experiment Design

## Source
- **Paper**: Experience as a Compass: Multi-agent RAG with Evolving Orchestration and Agent Prompts
- **arXiv**: [2604.00901](https://arxiv.org/abs/2604.00901)
- **Absorbed via**: /inhale agent_research — arXiv cs.AI (2026-04-03)
- **Relevance**: 10.0/10 (hypothesis_validation)
- **Evolution Score**: 15.6 (top 1)

## Core Idea from Paper
기존 멀티에이전트 RAG는 정적 오케스트레이션 프롬프트를 사용하지만,
이 논문은 **에이전트 프롬프트 자체가 경험(과거 질의 결과)에 기반하여 진화**하는 메커니즘을 제시.
각 에이전트의 역할 프롬프트가 성공/실패 이력을 반영해 동적으로 재작성됨.
핵심: orchestration prompt = living document, not static template.

## HarnessOS Application

### Hypothesis
> live-inf의 goal evolution만으로는 자율 진화의 한 축만 커버.
> **orchestration prompt(=스킬 정의) 자체가 경험 기반으로 진화하면**
> 같은 goal에 대해 더 나은 실행 전략을 자동 발견할 수 있다.

### Current System (Baseline)
- live-inf는 `root_goal`만 진화 (Step 6b EVOLVE)
- 스킬 정의(SKILL.md)는 정적 — 사람이 수동 편집
- episode_memory는 과거 실행 기록 저장하지만, 스킬 프롬프트에 직접 반영되지 않음

### Proposed System (Treatment)
```
After each live-inf iteration:
  1. Load episode_memory for current skill (e.g., exhale, inhale)
  2. Extract: success_patterns, failure_patterns from last 5 episodes
  3. Generate SKILL_PATCH: 1-3 line modifications to the skill's <Steps> section
     - e.g., "Step 2에서 novelty_bonus 1.2→1.5로 상향 (과거 3회 novelty가 높은 항목이 더 유용했음)"
  4. Save SKILL_PATCH to .omc/skill-patches/{skill_name}.jsonl
  5. 다음 실행 시 SKILL_PATCH를 context primer에 주입 (스킬 파일 직접 수정 안 함)
```

### Experiment Protocol
- **Design**: A/B paired comparison (5 iterations each)
- **A (control)**: live-inf with static skill prompts
- **B (treatment)**: live-inf with experience-based skill patch injection
- **Metric**: best_score at convergence, iterations to converge
- **Statistical test**: paired t-test or Wilcoxon signed-rank (n=5)

### Implementation Plan
1. `.omc/skill-patches/` 디렉토리 생성
2. `scripts/skill_patcher.py` — episode memory → skill patch 생성기
3. live 스킬의 Step 3d (Context Priming)에 skill_patch 주입 로직 추가
4. A/B 테스트 스크립트

### Expected Outcome
- Treatment이 동일 iteration 수에서 +0.05~0.10 higher best_score
- 또는 동일 best_score에 도달하는 데 1-2 iteration 적게 소요

### Dependencies
- omc-episode-memory (existing)
- live/live-inf 스킬 (existing)
- evolution_safety.py (existing — safety monitoring)

## Status: proposed
## Verification Method: paired_comparison (A/B test via /live)
