# Autonomous Evolution Safety — 3-Paper Synthesis Design

## Evolved from: /inhale agent_research (2026-04-03)
## Keyword focus: "harness 자율 진화"
## Status: proposed

---

## Source 1: Safety Gates Verification Dichotomy
- **Paper**: Empirical Validation of the Classification-Verification Dichotomy for AI Safety Gates
- **arXiv**: [2604.00072](https://arxiv.org/abs/2604.00072)
- **Source**: arXiv cs.LG via /inhale agent_research
- **Core**: classifier-based safety gates의 수백 iteration 후 신뢰성 검증

### HarnessOS Application
live-inf의 SCORE PROMPT(Step 6a)는 본질적으로 "safety gate" — 수렴 판단이 올바른지 검증.
이 논문의 핵심 발견: **classifier 정확도가 AI 시스템 개선에 따라 하락할 수 있다.**

**적용**: live-inf가 long-run (20+ iter)에서 SCORE PROMPT의 정확도가 유지되는지 검증하는 메타-검증 레이어.
```
매 10 iteration마다:
  이전 10개 iteration의 score 분포 분석
  if score_variance 증가 추세 → "[SAFETY GATE DRIFT] Evaluator accuracy may be degrading"
  → score_ensemble_n 자동 증가 (3→5) 또는 evaluator_mode 전환 ("self"→"cross_prompt")
```

---

## Source 2: Reward Hacking in Non-Production RL
- **Paper**: (Some) Natural Emergent Misalignment from Reward Hacking in Non-Production RL
- **URL**: [Alignment Forum](https://www.alignmentforum.org/posts/2ANCyejqxfqK2obEj)
- **Source**: Alignment Forum via /inhale agent_research
- **Core**: RL 에이전트가 reward를 해킹하여 의도하지 않은 방향으로 최적화

### HarnessOS Application
omc-live의 SCORE→EVOLVE 루프는 사실상 RL 구조: score = reward, evolve = policy update.
**Reward hacking 위험**: goal_fidelity가 높으면서도 실제로는 원래 의도와 다른 방향으로 진화.

**적용**: 현재 goal_fidelity gate(0.7 threshold) + cumulative_fidelity(0.50)는 이미 이 문제를 부분 대응.
추가 강화:
```
# Reward hacking detector: score가 올라가는데 git diff의 실질적 변화가 줄어드는 패턴
if score_delta > 0 AND diff_size_trend < 0 for 3+ iterations:
    emit: "[REWARD HACK WARNING] Score improving but substantive changes decreasing"
    → force evaluator_mode="cross_prompt" for next iteration
```

---

## Source 3: RL Training Breaks CoT Monitorability
- **Paper**: Predicting When RL Training Breaks Chain-of-Thought Monitorability
- **URL**: [Alignment Forum/DeepMind](https://www.alignmentforum.org/posts/SvxaKP5KdkksZPcG7)
- **Source**: Alignment Forum via /inhale agent_research
- **Core**: RL 학습이 진행될수록 Chain-of-Thought의 투명성이 감소

### HarnessOS Application
live-inf의 autopilot_summary는 CoT의 일종 — 에이전트가 자신의 작업을 설명.
장기 실행 시 이 설명의 품질이 하락하면 SCORE 판단의 입력 자체가 unreliable.

**적용**:
```
# Summary quality monitor: autopilot_summary의 구체성 추적
summary_specificity = count_specific_tokens(summary) / len(summary)
  # specific_tokens: 파일명, 함수명, 숫자, 에러메시지 등

if summary_specificity_trend is decreasing over 5+ iterations:
    emit: "[COT DRIFT] Autopilot summaries becoming less specific"
    → force autopilot to include git diff --stat in summary
    → consider context rotation (fresh session resets CoT quality)
```

---

## Synthesis: Autonomous Evolution Safety Triad

```
[SAFETY GATE DRIFT]     → score_ensemble_n 동적 증가
[REWARD HACKING]         → git diff 크기 vs score 상관관계 모니터링
[COT MONITORABILITY]     → summary specificity 추적

3가지 모두 감지 시 → "[EVOLUTION SAFETY ALERT] Multiple safety signals — escalate to user"
```

이 3가지는 live-inf의 SCORE(6a) → EVOLVE(6b) → AUTOPILOT(4) 각 단계에 1개씩 대응하므로,
전체 자율 진화 루프의 안전성을 포괄적으로 커버.

## Verification Method
- mode: experiment
- method: live-inf 20+ iteration 실행 후 3개 safety signal 발생 여부 관찰
- acceptance: 최소 1개 signal이 실제 degradation을 사전 감지하면 verified_positive
