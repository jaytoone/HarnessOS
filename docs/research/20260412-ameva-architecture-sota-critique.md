# Ameva Architecture — SOTA Critique & Evolution Targets

**Date**: 2026-04-12  
**Purpose**: Ameva SKILL.md 각 구성 요소를 SOTA 기준으로 평론 → /live 진화 입력으로 사용  
**Current version**: Entity v2.0 + Corpus Router (Iter 11)

---

## 구성 요소 맵

```
[1] Corpus Registry         — 도메인 지식 등록 포맷
[2] Corpus Router           — 쿼리 → active_corpus 선택
[3] Corpus Pre-step         — doc 로드 + scope gate + core theory 주입
[4] Step 0 Outward Reception — 화자 epistemic profile 감지
[5] Mode Branch (A/B/C/D)   — 실행 경로 선택
[6] L1 /conceptual          — paradigm reframing + Stage 1/2/3
[7] L2 Dynamic Dispatch     — 스킬/에이전트 선택 + corpus pass-through
[8] Claim Grounding         — SELF-RAG + FLARE-lite + T3 + Grounding Wall
[9] Stage 2 Adversarial     — corpus sycophancy_checks
[10] Pre-output Quality Gate — 7-check binary gate
[11] Feedback Loop          — paradigm.json + nodes.jsonl 업데이트
```

---

## [1] Corpus Registry

### 현재 구현
YAML-in-SKILL.md 플랫 구조. 각 corpus는 `trigger`, `docs`, `taxonomy_groups`, `core_theory`, `scope_gate`, `sycophancy_checks`, `rwr_hints`를 포함한다. Corpus Router가 keyword overlap으로 매칭.

### SOTA 기준 평론

**강점**:
- Named tool per document 패턴 (SOTA for <50 doc corpora) — 각 doc을 독립적인 callable tool로 등록. MedPaLM2, LegalBERT 등 domain-specific vertical AI 프로덕션 시스템과 동일 접근법.
- Schema 표준화 — trigger/taxonomy/scope_gate/sycophancy_checks를 corpus 정의 안에 캡슐화. 단일 등록으로 Corpus Router + Pre-step + Stage 2가 자동 연결.

**갭 (SOTA 대비)**:
1. **Corpus quality metric 없음**: SkillsBench (curated +16.2pp vs self-gen -1.3pp)를 인용하지만 각 corpus의 품질을 측정하는 메트릭이 없다. 프로덕션 Vertical AI (예: Bloomberg GPT, LegalBERT)는 corpus별 recall@K, precision, coverage metric을 관리한다.
2. **Version control 없음**: corpus 업데이트 시 이전 버전과의 하위호환성, diff 추적 없음. 이론 v1→v2 전환처럼 corpus 내부 충돌이 발생할 때 T3 메타리뷰 문서 하나로만 해결 — corpus-level change log가 없다.
3. **Trigger keyword → embedding similarity**: 현재 keyword exact/partial match. MTEB 벤치마크에서 embedding similarity가 keyword match 대비 BM25 기준 +12-18% F1 향상. 동음이의어 ("갭" = 의류 브랜드 vs Gap_Intensity)나 도메인 신호 없는 질문에서 keyword Router가 실패할 수 있다.

**진화 타겟**: corpus마다 `quality_metrics` 필드 추가 (precision@5, recall@5, coverage_score). Trigger에 embedding_hint 활용한 semantic fallback 추가.

---

## [2] Corpus Router

### 현재 구현
```python
signals = extract_signals(query)
overlap = set(signals) ∩ set(corpus.trigger)
active_corpus = argmax(overlap_count)  # 또는 기본값 wtp
```
Keyword overlap count → argmax → active_corpus 선택.

### SOTA 기준 평론

**강점**:
- Tool-to-Agent Retrieval (arXiv:2511.01854) 패턴 적용 — corpus docs를 T 노드, skills를 A 노드로 하는 bipartite graph G=(A,T,E). 동일 벡터 공간에서 corpus와 skill을 함께 routing하는 구조.
- 충돌 처리 (동점 → LLM 분류 → 사용자 확인)가 명시적으로 정의되어 있음.

**갭 (SOTA 대비)**:
1. **라우팅 신뢰도 없음**: 현재 Router는 매칭 여부만 반환, 신뢰도(confidence score) 없음. RouteLLM (arXiv:2406.18665)은 라우팅 결정에 confidence threshold를 도입 — 낮은 신뢰도 → 더 강력한 모델 또는 사용자 확인으로 fallback. 현재 구조에서 confidence=0.51 vs confidence=0.99를 구분하지 못한다.
2. **Cold-start 취약**: 쿼리에 도메인 신호가 없으면 무조건 wtp 기본값. 범용 질문("AI 트렌드가 뭐야?")에서 무의미한 WTP corpus가 로드됨. 적절한 fallback: "no corpus match → generic entity mode (corpus pre-step skip)".
3. **단방향 routing**: 한 번 선택된 active_corpus는 세션 내내 고정. Multi-turn 대화에서 주제가 이동하면 Router가 재실행되지 않는다.

**진화 타겟**:
- Routing 신뢰도 점수 추가 (confidence < 0.5 → corpus_mode = "generic", pre-step skip)
- "no match → entity fallback" 명시적 처리 (corpus 없이도 Entity pipeline 실행 가능)
- Multi-turn 라우팅: 이전 active_corpus + 현재 쿼리 신호의 가중 평균으로 재선택 여부 판단

---

## [3] Corpus Pre-step

### 현재 구현
EAGER (기본) 또는 LAZY (budget-tight) 모드로 top 3-5 docs 선택 → Read → T4 scope gate → core_theory 주입. RRR (arXiv:2305.14283) 쿼리 리라이팅 적용.

### SOTA 기준 평론

**강점**:
- RRR (Rewrite-Retrieve-Read): 표면 질문을 도메인 taxonomy 언어로 변환 후 retrieval. EMNLP 2023에서 vanilla retrieval 대비 +8.9% F1.
- FLARE-lite: retrieval은 필요할 때만 (confidence trigger) — 불필요한 doc 로드 방지.
- Named tool per document: <50 doc corpus에서는 벡터 DB 없이 직접 Read가 더 효율적 (Tool-to-Agent paper 확인).

**갭 (SOTA 대비)**:
1. **Retrieval quality evaluation 없음**: CRAG (Corrective RAG, arXiv:2401.15884)는 retrieval 후 "이 문서가 쿼리에 실제로 관련있는가?"를 평가 (Correct/Ambiguous/Incorrect). 현재 구조는 taxonomy group으로 doc_ids를 선택하지만, 선택된 doc이 실제로 질문에 답할 수 있는지 검증하지 않는다. 예: "L4 진단"에 D1을 로드했지만 D1이 L4에 대해 불충분하면 → P2를 추가 로드해야 한다.
2. **Excerpt 추출 전략 없음**: "핵심 섹션만 발췌"가 명시되어 있지만 어떻게 추출하는지 정의 없음. Contextual Retrieval (Anthropic 2024) — 각 chunk 앞에 문서 전체 맥락을 200-400자 prefix로 추가 → 검색 정확도 +49%. 현재 raw excerpt 방식 대비 개선 여지 있음.
3. **FLARE forward-looking 미구현**: 현재 FLARE-lite는 "UNCERTAIN 발견 시 retrieval 트리거" (backward-looking). FLARE 원본은 생성 중 다음 토큰이 불확실하면 그 시점에 retrieval (forward-looking). 더 정확하지만 구현 복잡도 높음 — 현재 in-context LLM 환경에서는 approximation으로 충분할 수 있다.

**진화 타겟**:
- CRAG retrieval quality check 추가: 로드된 docs에 대해 "이 doc이 쿼리의 {aspect}를 실제로 다루는가?" 체크 → Incorrect 판정 시 fallback doc 추가
- Excerpt 추출에 맥락 prefix 전략 명시 (Contextual Retrieval 적용)

---

## [4] Step 0 — Outward Reception

### 현재 구현
Meisner 원칙 + 3차원 화자 프로파일링: epistemic_basis (data-driven/intuition-first/authority-referencing) + causal_model (linear/systemic/emergent) + locus_of_control (internal/external/distributed). Gap detection (no_data_anchor, no_agency, no_feedback_loop).

### SOTA 기준 평론

**강점**:
- Meisner 원칙은 LLM sycophancy 방지의 행동적 기반 — 화자에서 오는 것만 반영, 내부 준비된 답 금지. Sycophancy (Anthropic 2023, Perez et al. 2022) 연구와 일치.
- 3차원 프로파일은 Kahneman의 System 1/System 2 구분 + Dweck의 Growth Mindset 연구에서 지지되는 인지 분류.
- Gap 감지 (no_data_anchor 등)는 화자가 말하지 않은 것을 추론 — ToM (Theory of Mind) 기본 적용.

**갭 (SOTA 대비)**:
1. **도메인 지식 수준 모델링 없음**: 현재 Step 0은 인식론적 스타일을 감지하지만, 화자의 WTP/VALUE GAP 지식 수준 (novice vs. expert)을 모델링하지 않는다. 전문가에게 L1-L5 설명하는 것은 낭비; 초보자에게 D(WTP) 공식부터 전제하면 맥락이 없다. Knowledge State Modeling (arXiv:2403.14624) — 화자의 사전 지식을 추론하고 그에 맞게 설명 깊이를 조절.
2. **Static profile — no update**: 프로파일은 메시지 수신 시 한 번만 형성, 대화 중 업데이트 없음. 화자가 "아, 그렇구나"라고 반응하면 epistemic_basis가 data-driven으로 이동할 수 있음. Active Learning 기반 user model update가 없다.
3. **Corpus-agnostic gap detection**: 현재 gap detection (no_feedback_loop 등)이 WTP 도메인에 특화되어 있다 (iter 10에서 추가됨). 다른 corpus에서는 이 gaps가 도메인과 맞지 않을 수 있음 → corpus-aware gap patterns이 corpus 정의에 포함되어야 한다.

**진화 타겟**:
- `user_domain_knowledge` 레벨 감지 추가 (novice/intermediate/expert — WTP corpus 관련 용어 사용 빈도로 추론)
- Corpus-aware gap detection: `active_corpus.gap_patterns`를 corpus 정의에 추가

---

## [5] Mode Branch (A/B/C/D)

### 현재 구현
사용자 플래그 (-r/-d/-rd)로 명시적 모드 선택. A=직접 실행, B=외부 RAG+직접, C=풀 파이프라인, D=도메인 dispatch. 핸드오프 플래그 (-l/-i).

### SOTA 기준 평론

**강점**:
- 명시적 모드 선택은 사용자 제어권을 보장 — 불필요한 L2 dispatch 없이 빠른 응답 가능.
- Opt-in 아키텍처: 기본(A)이 가장 간단, 플래그로 복잡도 추가. 인지 부하 최소화.

**갭 (SOTA 대비)**:
1. **자동 모드 추천 없음**: 사용자가 어떤 플래그를 써야 하는지 매번 결정해야 함. RouteLLM (2024)의 핵심 기여: 쿼리 복잡도를 LLM이 자동으로 평가 → 적절한 처리 경로 선택. "이 질문이 L2 dispatch를 필요로 하는가?"를 사용자 대신 시스템이 판단하면 마찰이 줄어든다.
2. **Mode C (풀 파이프라인)의 항상-느린 문제**: 단순 이론 질문에도 -rd를 쓰면 L2 dispatch + RAG가 실행됨. 쿼리 복잡도 기반 adaptive pipeline (FLARE의 confidence-based retrieval처럼) — "L2 dispatch가 실제로 필요한가?" 체크 후 skip 가능해야.
3. **Mode 전환 불가**: 실행 중 mode 변경 없음. 답변 생성 도중 "이건 외부 데이터가 필요하다"고 판단해도 Mode A → B로 전환할 수 없다 (이미 B로 시작했어야 함). FLARE는 생성 중 필요 시 retrieval 추가 — adaptive mid-execution mode는 현재 불가.

**진화 타겟**:
- Mode 자동 추천: `[Mode Recommendation] 이 질문 유형은 Mode D가 적합합니다 — -d 플래그로 실행하세요` 출력 (Mode A로 진행하되, 추천 emit)
- Mode A 실행 중 "retrieval 필요" 감지 → Mode B로 graceful upgrade (corpus 컨텍스트 재활용)

---

## [6] L1 /conceptual (Stage 1 Draft + Stage 2 + Stage 3)

### 현재 구현
paradigm.json + nodes.jsonl 읽기 → Refined Query Slot 추출 (CRANE ICML 2025) → Stage 1 Draft → Stage 1.5 SELF-RAG → Stage 2 Adversarial → Pre-output Gate → Stage 3 Deliver.

### SOTA 기준 평론

**강점**:
- CRANE (ICML 2025): 자유 추론 후 Refined Query Slot 추출 — 추론 흔적 폐기로 Attentional Residue 방지.
- Paradigm state (paradigm.json) 활용: 반복 질문 감지 + 새 각도 강제 → sycophancy 구조적 방어.

**갭 (SOTA 대비)**:
1. **Stage 1 Draft가 비검증 상태로 Stage 2 진입**: Stage 1.5 SELF-RAG가 있지만, Stage 1 Draft 자체의 구조적 완성도 (논리적 일관성, coverage)를 평가하는 단계가 없다. Process Reward Model (PRM, Lightman et al. 2023) — 답변 각 단계에 중간 점수를 부여, 낮은 점수 단계를 재생성. 현재는 Stage 1 전체를 한 번에 생성.
2. **Stage 2 Adversarial이 checklist 형식**: Du et al. (ICML 2024) Multi-perspective debate — 여러 에이전트가 병렬로 비판할 때 단일 순차 checklist보다 오류 발견율 높음 (+23% factual errors detected). 현재 7-check sequential보다 parallel critique가 더 효과적.
3. **Stage 3 Deliver에 Outward Profile만 적용**: 사용자 도메인 지식 수준 (novice/expert)이 Stage 3 언어 조정에 반영되지 않음 — 위 [4]의 gap과 연결.

**진화 타겟**:
- Stage 1.5 후 brief "draft coverage check" 추가: "이 질문의 핵심 aspects가 모두 커버됐는가?" (not per-claim, but per-question)
- Stage 2: 최소 1개의 "counterargument을 strong-man으로 제시하는" 체크 추가 (단순 오류 감지 넘어 대안 프레이밍 제시)

---

## [7] L2 Dynamic Domain Dispatch

### 현재 구현
system-reminder 전체 스킬 풀에서 동적 선택. Pre-check (REUSE/HYBRID/DISPATCH/RAG_FORCED). Corpus Pass-through: selected_skills에 corpus_context_block 주입. 3-5개 병렬 dispatch (MoA 2024).

### SOTA 기준 평론

**강점**:
- Zero-Waste RAG (Semantic Cache): Pre-check로 기존 docs/research/*.md 재활용. 중복 에이전트 실행 방지.
- Corpus Pass-through: L2 스킬 간 corpus context 공유 → cross-skill consistency 보장. 현재 생산 시스템 (LangGraph, CrewAI 멀티에이전트)에서 공유 컨텍스트 전달의 표준 패턴.
- 3-5 agents sweet spot (MoA): 실험적으로 검증된 병렬 dispatch 수.

**갭 (SOTA 대비)**:
1. **Routing history가 corpus-aware하지 않음**: world model의 `skill_routing_history`는 skill + score_delta를 추적하지만, 어떤 corpus 컨텍스트에서 해당 skill이 좋은 결과를 냈는지 기록하지 않는다. "wtp corpus에서 value-gap-theory를 3번 dispatched → avg score_delta +0.15"처럼 corpus-skill 조합의 history가 있으면 routing이 더 정확해진다.
2. **L2 synthesis 전략 없음**: 여러 스킬의 결과를 "종합"하지만, synthesis 전략이 명시되지 않았다. MoA (2024)는 proposer → aggregator 구조로 명시적 synthesis 단계를 정의. 현재는 LLM이 암묵적으로 종합.
3. **Corpus Pass-through의 일관성 보장 미검증**: 모든 L2 스킬이 corpus_context_block을 동일하게 해석한다는 보장이 없다. 각 스킬이 corpus context를 다르게 사용하면 synthesis 단계에서 충돌 발생 가능.

**진화 타겟**:
- `skill_routing_history`를 corpus-aware하게: `{skill, corpus_name, score_delta, iteration}`
- L2 synthesis: 명시적 aggregator step 추가 ("proposer 스킬들의 결과를 조정하는 최종 synthesis 단계")

---

## [8] Claim Grounding Protocol

### 현재 구현
SELF-RAG Stage 1.5 (per-claim [IsSup] loop) + FLARE-lite (confidence 기반 on-demand retrieval) + T3 Conflict Resolution (T2>T1, T4>T2, T3 globally) + Grounding Wall (corpus 없이 도메인 팩트 emit 금지).

### SOTA 기준 평론

**강점**:
- SELF-RAG (arXiv:2310.11511) 충실한 in-context 구현: [Retrieve]/[IsSup]/[IsRel] 토큰을 프롬프트 기반으로 에뮬레이션.
- T3 Conflict Resolution: 내부 corpus 간 충돌을 우선순위 규칙으로 해결 — [CONFLICT] 태그로 사용자에게 투명하게 공개.
- Grounding Wall: "corpus 없이 도메인 팩트 emit 금지" — RAG faithfulness의 가장 강력한 보장.

**갭 (SOTA 대비)**:
1. **[IsUse] 토큰 없음**: SELF-RAG 원본에는 [Retrieve], [IsRel], [IsSup], [IsUse] 4개 special token. 현재 [IsSup] (claim이 corpus로 지지되는가)만 구현; [IsUse] (이 claim이 답변에 실제로 유용한가)가 없다. 결과: 모든 grounded claim이 포함되지만, 일부는 답변의 유용성에 기여하지 않을 수 있다 (faithful but not useful).
2. **Fine-tuned vs in-context SELF-RAG**: SELF-RAG 논문의 fine-tuned 모델은 in-context prompting 대비 factual accuracy +14%. 현재 in-context 에뮬레이션은 approximation — LLM이 [IsSup] 판단을 틀릴 수 있음. 완화책: [IsSup] 판단 시 해당 corpus 섹션을 quote로 제시하게 강제.
3. **Cross-document grounding 없음**: 현재 per-claim retrieval은 단일 doc에서 지지를 찾음. 실제로는 여러 doc에 걸친 복합 claim (T2 공식 + D1 진단 기준 조합)이 많다 — multi-doc grounding이 없어서 "T2와 D1이 함께 지지해야 성립하는 주장"을 단일 doc [GROUNDED]로 처리할 위험.

**진화 타겟**:
- [IsSup] 체크 시 corpus 섹션 직접 인용 강제 (hallucination 방지 강화)
- Multi-doc grounding 태그: `[GROUNDED: T2+D1, 복합 근거]`

---

## [9] Stage 2 Adversarial (Sycophancy Checks)

### 현재 구현
`active_corpus.sycophancy_checks` 실행 (corpus별 7개 항목). WTP의 경우: enthusiasm≠WTP, ICP=identity portability, Social_Amplifier≠순수곱셈, 빠짐, 스코프게이트, 실험미실행, v1→v2.

### SOTA 기준 평론

**강점**:
- Corpus-aware sycophancy: 도메인별 오류 패턴을 corpus 정의에 캡슐화 → 범용 adversarial보다 정밀.
- 7개 구체 항목: 각 항목이 이전 반증/오류 경험에서 도출됨 (T4 HC-2 기준 등).

**갭 (SOTA 대비)**:
1. **Sequential checklist vs Parallel debate**: Du et al. (ICML 2024) — 동일 주제에 여러 LLM이 독립적으로 critique할 때 sequential보다 +23% 더 많은 factual error 발견. 현재 7개 항목이 순차 실행되므로 앞 항목의 bias가 뒤 항목에 영향.
2. **Meta-sycophancy 없음**: 질문 자체의 프레이밍이 특정 결론을 유도하는 경우 ("L5 WTP가 높다고 했는데...")에 대한 체크가 없다. Constitutional AI (Bai et al. 2022) — "이 질문 자체가 특정 답을 전제하고 있는가?" 체크.
3. **Adversarial quality 미측정**: 체크를 실행했는지 여부만 기록, 얼마나 강하게 비판했는지 없음. 형식적 통과 위험.

**진화 타겟**:
- Meta-sycophancy check Q0 추가: "이 질문 자체가 특정 WTP 수준을 전제하고 있는가? 전제가 있다면 명시."
- Adversarial intensity marker: 각 체크 후 `[PASS: 이유]` / `[FLAGGED: 이유 + 수정]`으로 실행 증거 남기기

---

## [10] Pre-output Quality Gate

### 현재 구현
7개 binary check (T4 gate, grounding tags, UNCERTAIN+검증방법, v1폐기, Stage 2 실행, 실험미실행, corpus references). 실패 → 해당 섹션 수정 후 재출력.

### SOTA 기준 평론

**강점**:
- 명시적 pre-output gate 패턴: 의료/법률 Vertical AI에서 표준 (예: IBM Watson Oncology의 confidence threshold).
- 7개 항목이 서로 독립적으로 체크 — 병렬 실행 가능 구조.

**갭 (SOTA 대비)**:
1. **Binary pass/fail, no scoring**: Process Reward Model (PRM) 접근법 — 각 check를 0-1 스코어로 평가, 임계값 이하만 수정. Binary gate는 "살짝 미흡한 것"과 "완전히 틀린 것"을 동일하게 처리.
2. **수정 지침 없음**: "실패 → 해당 섹션 수정"이지만 HOW가 없다. 각 실패 check에 specific repair action이 있어야 한다. 예: "corpus references 없음 → draft에서 사용된 doc_id 목록을 추출해 Corpus References 섹션 추가."
3. **Gate 실패율 미추적**: 어떤 check가 가장 자주 실패하는지 데이터 없음. Feedback Loop에서 gate failure를 기록하면 어떤 체크가 반복적으로 필요한지 알 수 있다 → 해당 check를 더 일찍 Stage 1에 통합 가능.

**진화 타겟**:
- 각 gate check에 `repair_action` 추가: 실패 시 구체적 수정 방법 명시
- Gate failure 로그를 Feedback Loop에 추가: `gate_failures: [{check_name, frequency}]`

---

## [11] Feedback Loop

### 현재 구현
매 세션 후: paradigm.json (session_count++, corpus-grounding gap), paradigm_history.jsonl (스냅샷), nodes/{PROJECT}.jsonl (corpus_refs, grounding_gaps, l2_bundle, paradigm_tags).

### SOTA 기준 평론

**강점**:
- Corpus_refs 확장 필드: 노드에 어떤 corpus docs가 사용됐는지 기록 → cross-session corpus 사용 패턴 파악 가능.
- Grounding_gaps 필드: UNCERTAIN claim이 어떤 검증 방법을 필요로 하는지 기록 → 반복 UNCERTAIN이 corpus 확장 신호가 됨.

**갭 (SOTA 대비)**:
1. **Corpus Router 실패 기록 없음**: Corpus Router가 wrong corpus를 선택했을 때 (사용자가 수정하거나 결과가 off-target인 경우) 이 실패를 기록하지 않는다. Routing failure data = trigger keyword 개선을 위한 가장 valuable한 signal.
2. **Memory decay 없음**: nodes.jsonl에 계속 추가만 됨. Kosmos (arXiv:2511.02824)의 episodic consolidation — 반복된 패턴은 general rule로 승격, 오래된 specific nodes는 decay. 현재는 모든 노드가 동일 가중치.
3. **Gate failure → corpus improvement 연결 없음**: Pre-output gate 실패가 corpus의 어떤 gap에서 비롯됐는지 연결되지 않는다. "D(WTP) 관련 [UNCERTAIN] 반복" → T2 문서 보강 신호로 처리해야 하는데, 현재는 그냥 grounding_gaps에만 기록됨.

**진화 타겟**:
- Routing outcome 기록 추가: `{corpus_selected, routing_confidence, outcome: correct/incorrect}`
- Gate failure → corpus action 제안: "이 gate check가 3회 이상 실패 → corpus.{doc_id} 보강 또는 새 doc 추가 검토"

---

## 종합 진화 우선순위

| 우선순위 | 컴포넌트 | 개선 | Impact |
|---------|---------|------|--------|
| P1 | Corpus Router | "no match → entity fallback" + routing confidence | High — cold-start failure 방지 |
| P1 | Step 0 | user_domain_knowledge 감지 + corpus-aware gap patterns | High — 응답 적합성 |
| P2 | Corpus Pre-step | CRAG quality check 추가 | Medium — retrieval precision |
| P2 | Stage 2 Adversarial | Q0 meta-sycophancy check + intensity marker | Medium — 오류 감지율 |
| P2 | Quality Gate | repair_action 명시 + gate failure 로그 | Medium — 실패 복구 속도 |
| P3 | Feedback Loop | routing outcome 기록 + corpus action 제안 | Medium — 장기 품질 |
| P3 | L2 Dispatch | corpus-aware routing history + explicit synthesis | Low-Medium |
| P4 | Claim Grounding | [IsSup] + corpus quote 강제 + multi-doc grounding | Low — 이미 Grounding Wall 존재 |

---

## Sources

- SELF-RAG: arXiv:2310.11511 (Asai et al. 2023)
- FLARE: EMNLP 2023 (Jiang et al.)
- CRAG: arXiv:2401.15884 (Yan et al. 2024)
- RRR: arXiv:2305.14283 (Ma et al. 2023)
- Tool-to-Agent Retrieval: arXiv:2511.01854
- MoA: arXiv:2406.04692 (Wang et al. 2024)
- RouteLLM: arXiv:2406.18665 (Ong et al. 2024)
- CRANE: ICML 2025 (Adapala et al.)
- Constitutional AI: Bai et al. 2022 (Anthropic)
- Process Reward Model: Lightman et al. 2023 (OpenAI)
- Du et al. ICML 2024: Multi-perspective debate
- Contextual Retrieval: Anthropic 2024
- Kosmos episodic memory: arXiv:2511.02824
- SkillsBench: curated vs self-generated skill quality
