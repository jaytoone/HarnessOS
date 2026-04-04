# Execution-Verified Evolution — Experiment Design

## Source
- **Paper**: Execution-Verified Reinforcement Learning for Optimization Modeling
- **arXiv**: [2604.00442](https://arxiv.org/abs/2604.00442)
- **Absorbed via**: /inhale agent_research — arXiv cs.AI (2026-04-03)
- **Relevance**: 10.0/10 (stuck_agent)
- **Evolution Score**: 15.0 (top 3)

## Core Idea from Paper
기존 에이전트 파이프라인이 LLM 자기 평가에 의존하는 반면,
이 논문은 **실행 결과를 직접 검증하여 RL reward로 사용** — "실행이 곧 검증".
아무리 LLM이 "잘했다"고 말해도, 실행 결과가 다르면 부정 보상.

## HarnessOS Application

### Hypothesis
> live-inf의 SCORE 단계(6a)는 LLM self-scoring에 과도하게 의존.
> **auto_oracle 결과(pytest, lint, type-check)를 RL-style reward로
> EVOLVE 방향에 직접 반영하면** Goodhart drift가 감소하고
> goal evolution의 quality가 향상된다.

### Current System (Baseline)
- SCORE: LLM ensemble (3회) + auto_oracle (pytest/lint/type-check)
- auto_oracle 결과는 score 차원에 매핑되지만, EVOLVE 방향 결정에는 간접 영향
- goal evolution은 weakest_dimension 기반 — oracle 결과와 느슨하게 연결

### Proposed System (Treatment)
```
Execution-Verified EVOLVE:

1. SCORE 단계에서 auto_oracle raw results 보존:
   oracle_raw = {
     "test_pass_rate": 0.95,
     "lint_errors": 2,
     "type_errors": 0,
     "build_success": true,
     "diff_size": 142  # lines changed
   }

2. EVOLVE 프롬프트에 oracle_raw 직접 주입:
   "Auto-oracle results: {oracle_raw}
    These are GROUND TRUTH — they override LLM self-assessment.
    Evolve the goal to address ORACLE-detected weaknesses first,
    LLM-detected weaknesses second."

3. EVOLVE 후보 평가에 oracle 예측 추가:
   "For each CANDIDATE, predict what the auto_oracle would return.
    Prefer candidates where predicted oracle results improve."

4. Reward signal 정의:
   execution_reward = (
     0.4 * test_pass_rate_delta +
     0.3 * (1 - lint_errors / 10) +
     0.2 * build_success +
     0.1 * min(diff_size / 200, 1.0)  # 적절한 변화량
   )

   if execution_reward < 0 → block EVOLVE (regression)
```

### Experiment Protocol
- **Design**: A/B paired comparison (3 live-inf runs each)
- **A (control)**: standard EVOLVE (LLM self-score driven)
- **B (treatment)**: execution-verified EVOLVE (oracle reward driven)
- **Metric 1**: best_score at convergence
- **Metric 2**: reward_hacking alert count (Safety Triad)
- **Metric 3**: test_pass_rate trajectory (oracle ground truth)
- **Statistical test**: paired comparison, effect_size threshold > 0.05

### Implementation Plan
1. live 스킬 Step 6a에 oracle_raw 보존 로직 추가
2. Step 6b EVOLVE 프롬프트에 oracle_raw injection
3. execution_reward 계산 함수 (scripts/evolution_safety.py에 추가)
4. execution_reward < 0 시 EVOLVE 차단 로직

### Expected Outcome
- reward_hacking 감지 빈도 50%+ 감소 (oracle 기반 보정으로 사전 방지)
- test_pass_rate regression 0회 (oracle reward < 0 → EVOLVE 차단)
- best_score 차이는 미미할 수 있음 (0~0.05) — 핵심은 reliability 개선

### Dependencies
- evolution_safety.py (Safety Triad — reward_hacking detector)
- live/live-inf 스킬 auto_oracle 코드 (existing in Step 6a)
- pytest/lint/type-check 인프라 (project-dependent)

## Status: proposed
## Verification Method: paired_comparison (A/B via /live)
