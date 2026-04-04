# Autonomy-Preserving Agent Gate — Experiment Design

## Source
- **Paper**: Care-Conditioned Neuromodulation for Autonomy-Preserving Supportive Dialogue Agents
- **arXiv**: [2604.01576](https://arxiv.org/abs/2604.01576)
- **Absorbed via**: /inhale agent_research — arXiv cs.LG (2026-04-03)
- **Relevance**: 10.0/10 (hypothesis_validation)
- **Evolution Score**: 15.6 (top 1 tied)

## Core Idea from Paper
LLM 에이전트가 도움을 주되 유저의 자율성을 침해하지 않아야 한다는 tension.
표준 alignment은 "helpful"에 과도하게 최적화되어 유저 자율성을 침해할 수 있음.
논문은 "care-conditioned neuromodulation" — 에이전트가 개입 강도를 유저 상태에 따라 동적 조절.

## HarnessOS Application

### Hypothesis
> exhale의 "유저 확인 후 실행" 패턴은 binary (실행/미실행)이지만,
> **개입 강도를 3단계로 분류하면** 유저 경험과 자율 진화 효율이 동시에 개선된다.

### Current System (Baseline)
- exhale: 설계 생성 후 → 유저에게 "실행할까요?" (binary Y/N)
- live/live-inf: autonomous 실행 (유저 개입 없음, budget 내 자유)
- 중간이 없음 — either full autonomy or full manual

### Proposed System (Treatment)
```
Autonomy Level Classification (3-tier):
  L1 (INFORM): 확신도 높고 리스크 낮은 변경
     → 실행 + 사후 보고 ("이렇게 했습니다")
     예: 키워드 가중치 미세 조정, 문서 업데이트

  L2 (CONFIRM): 확신도 중간이거나 리스크 중간
     → 요약 제시 + 확인 요청 ("이렇게 하려는데 괜찮을까요?")
     예: 새 실험 설계 적용, 새 채널 추가

  L3 (DELEGATE): 확신도 낮거나 리스크 높은 변경
     → 설계만 제시 + 유저가 직접 실행
     예: 기존 코드 구조 변경, 외부 서비스 연결

Classification criteria:
  confidence = evolution_score / max_possible_score  (0.0-1.0)
  risk = file_change_scope * reversibility_factor     (0.0-1.0)

  if confidence > 0.8 AND risk < 0.3 → L1
  elif confidence > 0.5 OR risk < 0.6 → L2
  else → L3
```

### Experiment Protocol
- **Design**: Before/After comparison (10 exhale runs each)
- **Before (baseline)**: binary Y/N confirmation
- **After (treatment)**: 3-tier autonomy level
- **Metric 1**: user confirmation time (seconds from presentation to decision)
- **Metric 2**: acceptance rate per tier
- **Metric 3**: user override rate (유저가 L1→L3으로 올린 횟수)

### Implementation Plan
1. `scripts/autonomy_classifier.py` — evolution_score + file scope → autonomy level
2. exhale Step 6에 autonomy level 표시 추가
3. live 스킬에 L1 auto-execute 로직 추가

### Expected Outcome
- L1 items: 90%+ 자동 실행 (유저 시간 절약)
- L2 items: 70%+ 승인율
- L3 items: 50% 미만 직접 실행 (나머지는 수정 후 재제출)
- 전체 유저 확인 시간 40%+ 단축

### Dependencies
- exhale 스킬 (existing)
- evolution-registry.jsonl (existing)
- evolution_safety.py (L1 auto-execute 시 safety check 필수)

## Status: proposed
## Verification Method: before_after_comparison (10 exhale runs)
