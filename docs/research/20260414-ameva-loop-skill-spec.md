# [expert-research-v2] Ameva Loop Skill — 설계 Spec
**Date**: 2026-04-14  **Skill**: expert-research (lean v2)

## Original Question

omc-live/live-inf를 base로, 개발 편향 제거 + Ameva Swarm Intelligence 개념에 맞는
도메인-native 자율 수렴 루프 스킬 설계 spec.

---

## Web Facts

[FACT-1] SwarmSys (arXiv:2510.10047): Explorer→Worker→Validator 3역할 분산 검증.
         중앙 oracle 없이 "debate-driven consensus"로 수렴. Validators가 convergence 선언.
[FACT-2] SwarmSys Pheromone trace: corpus docs가 digital stigmergy 역할.
         성공 매칭 → compatibility score 강화 (cosine similarity 임베딩).
[FACT-3] SwarmSys ε-greedy: ε≈0.15 초기. High-performer 탐색 감소, Underperformer 증가.
[FACT-4] MAE Proposer-Solver-Judge (arXiv:2510.23595): 단일 LLM에서 3역할.
         외부 ground truth 없이 closed self-improving loop.
[FACT-5] MAE Oracle-free: Judge = domain-agnostic rubric. 진입 임계 score ≥ 0.7.
         필터 제거 시 -3.72% 성능 하락 확인.
[FACT-6] MAE Co-evolution 압력: Proposer reward += (1 - Solver success rate).
         "challenging but solvable" 문제 생성 압력 → trivial evolution 방지.
[FACT-7] Self-play without code oracle: 오픈 도메인 → LLM-as-Judge 필수.
[FACT-8] RAG oracle-free metrics: context_precision, faithfulness, answer_relevance.
[FACT-9] EvolveR: RAG는 knowledge gap 해결, but 자신의 interaction에서 학습 불가. lifecycle 필요.
[FACT-10] Agentic RAG 2026: plan→retrieve→reason→critique→rewrite→reflect 루프 until convergence.

---

## Multi-Lens Analysis

### Lens 1: Domain Expert

**Insight 1 — Corpus = Pheromone Trail (Stigmergy)** [GROUNDED: FACT-2]
Ameva의 corpus docs는 SwarmSys의 pheromone trace와 구조적으로 동일하다.
- corpus doc이 [GROUNDED:doc_id] 태그를 많이 받을수록 → "이 경로가 유효하다"는 stigmergy 신호
- doc이 [UNCERTAIN]이나 [CONFLICT] 태그를 받을수록 → 개선 대상 마킹 (감쇠 신호)
- 루프의 각 iteration은 corpus doc 품질을 개선하거나 새 doc을 추가하여 pheromone trail을 강화

**Insight 2 — Oracle-free Convergence: 4차원 Corpus Quality Metrics** [GROUNDED: FACT-5, FACT-8]
코드 oracle(lint/test/typecheck) 없이 수렴을 판단하려면 corpus-native 지표 필요:

| 지표 | 정의 | Target | 코드 oracle 대응 |
|------|------|--------|-----------------|
| `grounding_rate` | [GROUNDED] tags / total domain claims | ≥ 0.85 | test pass rate |
| `routing_precision` | corpus_mode="corpus" / total queries | ≥ 0.80 | coverage % |
| `claim_quality` | 1 - ([UNCERTAIN] / total claims) | ≥ 0.75 | type-check |
| `sycophancy_pass` | Stage 2 [PASS] / total checks | ≥ 0.90 | lint pass |

MAE quality threshold 0.7 참조: 4차원 중 어느 하나가 0.7 미만 → 수렴 미달.

**Insight 3 — 3-Role Swarm Evaluation: Explorer-Reasoner-Auditor** [GROUNDED: FACT-1, FACT-4]
MAE의 Proposer-Solver-Judge를 corpus evolution 맥락으로 재매핑:

```
Explorer  (← MAE Proposer): corpus gap 탐지 + 개선 질문 생성
           reward = gap_novelty + (1 - Reasoner success rate)  [FACT-6]
Reasoner  (← MAE Solver):   /ameva -rd로 질문 실행, corpus 참조하여 답변
           reward = grounding_rate + claim_quality
Auditor   (← MAE Judge):    응답의 [GROUNDED/UNCERTAIN/FLAGGED] 비율 평가
           reward = sycophancy_pass (format/rubric compliance)
```

**Insight 4 — omc 의존성 완전 제거 경로** [REASONED: live SKILL.md 구조 분석]
omc-autopilot이 제공하는 기능 중 Ameva loop에 실제 필요한 것은:
- Phase-aware retry → 인라인 failure classification으로 대체
- Episode memory → `.ameva/episode-state.json` 자체 관리
- Goal tree → in-skill goal_tree dict로 대체
omc-failure-router, omc-goal-tree는 omc-autopilot에 묶여 있어 함께 제거 가능.

**Insight 5 — Context Rotation 유지 (live-inf 상속)** [REASONED: FACT-9]
EvolveR의 핵심 발견: "RAG는 knowledge gap 해결하나 자신의 interaction에서 systematic learning 불가."
→ Context Rotation + `.ameva/infinite-state.json`은 유지해야 한다.
세션 간 world model 연속성이 corpus evolution loop에서도 필수.

### Lens 2: Devil's Advocate

**[MISSING] Swarm의 "분산" 개념 — Ameva loop에서 실제 분산인가?**
Explorer-Reasoner-Auditor가 동일 Claude instance에서 실행되면 진정한 swarm이 아니다.
진짜 swarm은 병렬 독립 에이전트가 필요. 단일 인스턴스 순차 실행은 "swarm aesthetic"에 불과.
→ 수정: Explorer-Auditor를 별도 Agent() 호출로 병렬화하면 실질적 swarm 달성.

**[OVERCONFIDENT] Grounding rate만으로 수렴 판단 충분하다?**
grounding_rate가 높아도 corpus 자체가 틀렸으면 의미없다 (garbage-in-garbage-out).
→ 수정: T4 falsification criteria 통과 여부를 별도 oracle로 추가. corpus doc이 반증 기준을 충족하는지 per-doc 검사.

**[MISSING] "trivial evolution" 방지 메커니즘**
MAE의 Proposer가 Solver failure에서 reward를 받는 이유 [FACT-6]: 너무 쉬운 개선만 반복하는 것을 막기 위해.
→ corpus iteration이 "이미 잘 되는 doc 계속 테스트"로 수렴할 위험. 탐색 압력 설계 필요.

**[CONFLICT] ε-greedy [FACT-3] vs Pareto convergence (live-inf 상속)**
live-inf는 per-dimension Pareto vector 기반 수렴. ε-greedy는 단일 스칼라 기반.
두 메커니즘이 충돌할 수 있다.
→ 수정: Pareto vector 유지 (4차원 중 모든 차원이 plateau여야 수렴), ε는 exploration_rate로 통합.

### Lens 3: Practical Synthesizer

1. **Swarm 실질화**: Explorer + Auditor를 parallel Agent() calls. Reasoner만 sequential (corpus context 필요).
2. **Convergence oracle**: 4차원 metrics + T4 falsification gate. T4 gate가 primary (corpus 정합성), 4차원이 secondary (품질 수준).
3. **Trivial evolution 방지**: Explorer reward에 `gap_novelty` 포함. 이미 [GROUNDED] 비율 높은 doc은 낮은 탐색 우선순위.
4. **omc 의존성**: autopilot/episode-memory/goal-tree/failure-router 전부 인라인 대체.

---

## Final Conclusion: Ameva Loop Skill Spec (v0.1)

### 스킬 정보

```yaml
name: ameva-inf
description: >
  Infinite corpus-evolution loop for Ameva domain knowledge.
  Swarm-inspired (Explorer+Reasoner+Auditor), oracle-free convergence
  via corpus quality metrics. omc-independent. Terminates on plateau
  across all 4 quality dimensions or explicit stop.
```

---

### 아키텍처

```
ameva-inf (Infinite Corpus Evolution Loop)
  ├── [STIGMERGY]  Corpus State Layer  — docs as pheromone trails
  ├── [SWARM]      Explorer (parallel) + Reasoner + Auditor (parallel)
  ├── [EVOLVE]     Goal elevation engine  (corpus quality → next gap)
  ├── [CONVERGE]   4D Quality Oracle  (grounding_rate + routing_precision
  │                                    + claim_quality + sycophancy_pass)
  └── [ROTATE]     Context Rotation  — .ameva/infinite-state.json
```

---

### omc-live 대비 변경 매트릭스

| live-inf 구성 요소 | ameva-inf 처리 |
|--------------------|---------------|
| `omc-autopilot` (inner loop) | ❌ 제거 → 인라인 Reasoner 실행 |
| `omc-episode-memory` | ❌ 제거 → `.ameva/episode-state.json` 자체 관리 |
| `omc-goal-tree` | ❌ 제거 → in-skill `goal_tree` dict |
| `omc-failure-router` | ❌ 제거 → 인라인 failure classification |
| Repo Context Injection | ❌ 제거 (code-specific) |
| TDD Gate | ❌ 제거 (code-specific) |
| Auto Oracle (lint/test/typecheck) | ❌ 제거 → 4D Corpus Quality Oracle |
| Wave 1 code specialists | ❌ 제거 → Explorer가 대체 |
| Context Rotation | ✅ 유지 (live-inf 상속) |
| World Model / Epistemic State Layer | ✅ 유지 |
| Score ensemble (N=3) | ✅ 유지 |
| Pareto convergence | ✅ 유지 (4차원 모두 plateau) |
| Novelty Escape | ✅ 유지 |
| goal_fidelity cumulative check | ✅ 유지 |

---

### Swarm 3-Role Protocol

#### Explorer (parallel Agent — "gap probe")
```
역할: 현재 corpus의 취약 지점 탐지 + 다음 iteration 목표 질문 생성
입력: 현재 corpus grounding stats + world model (dead ends 포함)
출력: [GAP-PROBE] — 가장 낮은 품질 차원의 개선 질문 1개

reward = gap_novelty_score + (1 - Reasoner_success_rate_last_iter)
         [MAE Proposer co-evolution pressure 적용 — FACT-6]

탐색 규칙:
  - 이미 grounding_rate > 0.9인 doc → 탐색 우선순위 낮음
  - [UNCERTAIN] 비율 높은 doc → 탐색 우선순위 높음
  - world_model dead_ends에 있는 접근법 → 스킵
```

#### Reasoner (sequential — corpus context 필요)
```
역할: Explorer의 GAP-PROBE로 /ameva -rd 실행
입력: GAP-PROBE + corpus context
출력: grounded 응답 + per-claim tags [GROUNDED/REASONED/UNCERTAIN]

reward = grounding_rate(response) + claim_quality(response)
```

#### Auditor (parallel Agent — "debate validator")
```
역할: Reasoner 응답 평가 + corpus 개선 사항 추출
입력: Reasoner 응답 + active corpus docs
출력: [AUDIT-RESULT] — sycophancy_pass score + corpus delta 제안

reward = rubric_compliance (format + [PASS/FLAGGED] coverage)
         [MAE Judge: format compliance only — FACT-4]

평가 기준:
  - Stage 2 sycophancy_checks 통과율
  - [GROUNDED] 없는 domain claims 탐지
  - corpus doc에 역으로 반영할 개선사항 추출
```

---

### 4D Corpus Quality Oracle (코드 oracle 대체)

```python
def compute_quality_vector(session_results: list) -> dict:
    """
    Returns 4D quality vector from last N ameva runs.
    No code execution required — purely from response analysis.
    """
    return {
        "grounding_rate":    count([GROUNDED]) / count(domain_claims),
        "routing_precision": count(corpus_mode="corpus") / count(total_queries),
        "claim_quality":     1.0 - (count([UNCERTAIN]) / count(total_claims)),
        "sycophancy_pass":   count(Stage2_PASS) / count(Stage2_checks),
    }

# Convergence oracle
def is_converged(history: list[dict], plateau_k=5, epsilon=0.03) -> bool:
    """
    Pareto convergence: ALL 4 dimensions stagnant for plateau_k iterations.
    MAE quality gate: any dimension < 0.70 → not converged (improve that dim first).
    """
    if any(history[-1][d] < 0.70 for d in QUALITY_DIMS):
        return False  # MAE 0.7 threshold [FACT-5]
    if len(history) < plateau_k:
        return False
    recent = history[-plateau_k:]
    return all(
        max(r[d] for r in recent) - min(r[d] for r in recent) < epsilon
        for d in QUALITY_DIMS
    )
```

**T4 Falsification Gate** (primary oracle):
```
각 active corpus doc에 대해:
  T4 Hard Claims (HC-1..N) 중 현재 doc이 위반하는 HC 있는가?
  → HC 위반 발견 → 해당 doc 개선 priority = CRITICAL (수렴 불가)
  → 모든 HC 통과 → secondary oracle (4D) 기준으로 수렴 판단
```

---

### State Files (.ameva/ — omc/ 독립)

```
.ameva/
  infinite-state.json    # Context rotation state (live-inf 상속)
  world-model.json       # Epistemic state — tried/known/uncertain
  episode-state.json     # Per-iteration history (episode-memory 대체)
  quality-history.jsonl  # 4D quality vector per iteration
  goal-tree.json         # Goal evolution tree (goal-tree 대체)
  corpus-delta.json      # Proposed corpus improvements per iteration
```

---

### Config (omc-live 대비 변경/추가)

```yaml
# ameva-inf default config
max_outer_iterations: null         # infinite (live-inf 상속)
plateau_k: 5                       # 5회 연속 all-dim plateau → 수렴
epsilon: 0.03                      # 4D quality change threshold
quality_threshold: 0.70            # MAE 0.7 gate [FACT-5]
exploration_rate: 0.15             # SwarmSys ε≈0.15 [FACT-3]
pareto_convergence: true           # 4차원 모두 plateau여야 수렴

# oracle 설정 (코드 oracle 전부 비활성)
oracle_cmd: null                   # 코드 실행 oracle 없음
oracle_type: "corpus_quality"      # 4D corpus metrics + T4 falsification

# swarm 설정
swarm_roles: ["explorer", "reasoner", "auditor"]
explorer_parallel: true            # Explorer = parallel Agent() call
auditor_parallel: true             # Auditor = parallel Agent() call
reasoner_sequential: true          # Reasoner needs corpus context

# state 경로 (.omc/ 아님)
state_dir: ".ameva"

# 비활성화 (omc 편향 제거)
tdd_gate: false
repo_context_injection: false
wave1_specialists: null            # Explorer가 Wave 1 역할 대체
domain_profile: null               # Ameva corpus가 domain context
```

---

### PRE-LOOP: Session Resume (live-inf 상속 + 경로만 변경)

```python
if .ameva/infinite-state.json exists:
    state = read(".ameva/infinite-state.json")
    if state.status == "ROTATING":
        restore_all_state_from(state)
        → Skip init, go to World Model load
else:
    initialize_state(root_goal=args)
    → Corpus Stigmergy Init (new — Ameva specific)
```

**Corpus Stigmergy Init** (신규):
```python
# 세션 시작 시 corpus docs의 현재 품질 상태를 pheromone trail로 로드
pheromone_state = {}
for corpus_name, corpus in CORPUS_REGISTRY.items():
    for doc_id, filename in corpus.docs.items():
        doc_path = corpus.corpus_root + filename
        if exists(doc_path):
            # 파일 크기 + 마지막 수정일을 proxy로 사용
            # (향후: grounding_rate history에서 실제 강도 계산)
            pheromone_state[f"{corpus_name}.{doc_id}"] = {
                "strength": 0.5,  # 초기값 — quality history에서 업데이트
                "last_improved": file_mtime(doc_path),
                "flagged": False
            }
# .ameva/world-model.json에 pheromone_state 저장
```

---

### MAIN LOOP: Per-Iteration Protocol

```
Iteration N:

STEP 1 — EXPLORER (parallel): Gap Probe
  Agent(subagent_type="research-explore",
    prompt=f"Ameva corpus 현재 상태: {pheromone_state summary}
            World model dead_ends: {world_model.dead_ends}
            다음으로 개선해야 할 corpus gap을 1개 식별하라.
            grounding_rate < 0.80이거나 [UNCERTAIN] 비율 > 0.25인 doc_id 우선.
            출력: [GAP-PROBE] doc_id + 개선 질문")
  → GAP-PROBE: {doc_id, improvement_question}

STEP 2 — REASONER (sequential): /ameva -rd 실행
  Skill("ameva", args=f"-rd {GAP-PROBE.improvement_question}")
  → ameva_response (corpus-routed, grounded)
  → extract: grounding_rate, claim_quality, uncertainty_list

STEP 3 — AUDITOR (parallel): Consensus Validation
  Agent(subagent_type="feature-dev:code-reviewer",  # 분석 역할로 전용
    prompt=f"다음 ameva 응답을 corpus grounding 기준으로 평가하라:
            {ameva_response}
            평가 기준:
            1. [GROUNDED] 없는 domain claims 탐지
            2. Stage 2 sycophancy_checks 위반 여부 (Q1-Q7 기준)
            3. T4 Hard Claims 위반 여부
            4. corpus doc에 반영 가능한 개선사항 추출
            출력: [AUDIT-RESULT] {sycophancy_pass, hc_violations, corpus_delta}")
  → AUDIT-RESULT

STEP 4 — QUALITY COMPUTE:
  quality_vector = compute_quality_vector(
      ameva_response + AUDIT-RESULT + quality_history[-5:]
  )
  quality_history.append(quality_vector)

STEP 5 — CONVERGENCE CHECK:
  if is_converged(quality_history):
      → CONVERGED (corpus quality plateau)
  elif quality_vector.any() < 0.70:
      → IMPROVE priority dim (MAE threshold)
  else:
      → EVOLVE goal (next gap)

STEP 6 — CORPUS DELTA APPLY (수렴 미달 시):
  if AUDIT-RESULT.corpus_delta not empty:
      → 사용자에게 corpus improvement 제안 emit
      (실제 corpus doc 수정은 human-in-the-loop — auto-write 금지)

STEP 7 — STIGMERGY UPDATE:
  pheromone_state[GAP-PROBE.doc_id].strength =
      0.7 * prev_strength + 0.3 * quality_vector.grounding_rate
  if quality_vector.grounding_rate < 0.70:
      pheromone_state[GAP-PROBE.doc_id].flagged = True

STEP 8 — CONTEXT CHECK:
  if context_pct > 90%:
      serialize(.ameva/infinite-state.json)
      emit: "[ROTATE] Context limit reached — resume with /ameva-inf continue"
      → STOP (next session auto-resumes)
```

---

### Goal Evolution (EVOLVE step)

```python
def evolve_goal(current_goal, quality_vector, pheromone_state):
    # 가장 낮은 품질 차원 식별
    weakest_dim = min(quality_vector, key=quality_vector.get)
    weakest_doc = min(pheromone_state, key=lambda d: pheromone_state[d]["strength"])

    next_goal = f"{weakest_doc} corpus doc의 {weakest_dim} 개선: " \
                f"현재 {quality_vector[weakest_dim]:.2f} → target ≥ 0.80"

    # goal_fidelity check (live-inf 상속)
    fidelity = semantic_similarity(next_goal, root_goal)
    if fidelity < 0.70:
        emit: f"[FIDELITY WARN] goal_fidelity={fidelity:.2f} < 0.70 → skip EVOLVE"
        return current_goal  # goal 동결

    return next_goal
```

---

### 제외 목록 (명시적 non-goal)

- ❌ 코드 생성/수정 (Repo Context, TDD, lint)
- ❌ omc-* 스킬 의존 (omc-autopilot, omc-episode-memory 등)
- ❌ corpus doc 자동 수정 (human-in-the-loop 유지)
- ❌ 개발 task_type 라우팅 (code/debug/ui → ameva-inf 비적합)

---

### 적합 사용 사례

- Ameva corpus 품질을 반복적으로 개선하는 자율 루프
- 특정 corpus doc의 grounding_rate/claim_quality 목표 달성
- 새 corpus 등록 후 안정화 (draft → stable 자동 검증)
- ameva benchmark 점수 자율 최적화

---

## Sources

- [SwarmSys: Decentralized Swarm-Inspired Agents](https://arxiv.org/html/2510.10047v1)
- [Multi-Agent Evolve: LLM Self-Improve through Co-evolution](https://arxiv.org/html/2510.23595v1)
- [EvolveR: Self-Evolving LLM Agents](https://arxiv.org/html/2510.16079v1)
- [RAG Evaluation Technical Guide](https://toloka.ai/blog/rag-evaluation-a-technical-guide-to-measuring-retrieval-augmented-generation/)
- [SwarmSys Industry Report](https://powerdrill.ai/blog/swarm-intelligence-in-agentic-ai-an-industry-report)
- [Agentic RAG 2026 LangGraph](https://medium.com/@vinodkrane/next-generation-agentic-rag-with-langgraph-2026-edition-d1c4c068d2b8)
