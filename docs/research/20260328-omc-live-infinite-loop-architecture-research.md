# [expert-research-v2] 무한 자율 에이전트 실행 — 순환구조와 방법론 SOTA
**Date**: 2026-03-28  **Skill**: expert-research-v2 (3-agent pipeline)

## Original Question
무한 자율 에이전트 실행을 위한 적합한 순환구조와 방법론을 SOTA 연구하여, omc-live/omc-autopilot 스킬 오케스트레이터에 적용 가능한 패턴 발굴.

## Collected Facts (Fact Finder, web-verified)

- [FACT-1] Infinite Agentic Loop (github.com/disler, 2026, MIT): Wave 단위 병렬 서브에이전트 오케스트레이션. Context 소진 시 새 컨텍스트 + 외부 메모리 참조로 재시작. 진정한 무한 루프의 실용적 구현체. (source: https://github.com/disler/infinite-agentic-loop)
- [FACT-2] Oracle 개발자 블로그: 표준 AI agent loop = Reason→Act→Observe→Decide. 에이전트는 표준 챗 대비 4x, 멀티에이전트 시스템에서 최대 15x 더 많은 토큰 소비. (source: https://blogs.oracle.com/developers/what-is-the-ai-agent-loop-the-core-architecture-behind-autonomous-ai-systems)
- [FACT-3] Lifelong Learning of LLM-based Agents Roadmap (arXiv:2501.07278, TPAMI 2026 accepted): 3 모듈 — Perception / Memory / Action. Catastrophic forgetting 완화 + 장기 성능 향상 방법론 체계화. (source: https://arxiv.org/abs/2501.07278)
- [FACT-5] ASL (ICLR 2026 submission): 완전 closed-loop — Prompt Generator + Policy Model + Generative Reward Model이 하나의 LLM에서 공동 진화. GRM을 frozen하면 reward hacking → GRM continual training 필수. (source: https://openreview.net/forum?id=ySSq8Yavs4)
- [FACT-6] SSP (arXiv:2510.18821, Qwen, Oct 2025): LLM이 동시에 task proposer + problem solver로 기능. Competition + cooperation으로 공동 진화. Human supervision 불필요. (source: https://arxiv.org/abs/2510.18821)
- [FACT-7] Voyager (arXiv:2305.16291, 2023): Automatic curriculum + ever-growing skill library + self-verification. 3.3x unique items, 15.3x faster tech-tree. (source: https://voyager.minedojo.org/)
- [FACT-8] Memory in the Age of AI Agents (arXiv:2512.13564, Dec 2025, 47인 공저): 기존 long/short-term 분류 불충분. 3-form taxonomy: Forms/Functions/Dynamics. (source: https://arxiv.org/abs/2512.13564)
- [FACT-9] Episodic Memory Missing Piece (arXiv:2502.06975, Feb 2025): Episodic memory 5가지 핵심 속성이 단기→장기 전환에서 결정적. 통합 프레임워크 필요. (source: https://arxiv.org/abs/2502.06975)
- [FACT-10] A-MEM (arXiv:2502.12110, NeurIPS 2025): Zettelkasten 방식 동적 메모리. 새 메모리 추가 시 자동 링크 생성. Memory evolution 메커니즘으로 6개 foundation model에서 SOTA. (source: https://arxiv.org/abs/2502.12110)
- [FACT-11] MIRIX (arXiv:2507.07957, Jul 2025): 6종 전문화 메모리(Core/Episodic/Semantic/Procedural/Resource/KnowledgeVault) + 8 에이전트 협력. ScreenshotVQA +35% vs RAG 베이스라인, 스토리지 99.9% 절감. LOCOMO SOTA 85.4%. (source: https://arxiv.org/abs/2507.07957)
- [FACT-12] JitRL (arXiv:2601.18510, Jan 2026): Gradient update 없이 test-time policy optimization. Non-parametric memory + logit modulation. Fine-tuning 대비 30x 비용 절감. WebArena + Jericho SOTA. (source: https://arxiv.org/abs/2601.18510)
- [FACT-13] AGrail (arXiv:2502.11448, Feb 2025): Lifelong agent guardrail. Adaptive safety check generation. Task-specific 리스크 + systemic 리스크(CIA) 모두 대응. Cross-task transferability 입증. (source: https://arxiv.org/abs/2502.11448)
- [FACT-14] LlamaFirewall (arXiv:2505.03574, May 2025): PromptGuard 2 + AlignmentCheck(CoT 전체 실행 추적) + CodeShield. AlignmentCheck는 사용자 원래 목적에 대한 지속 모니터링. (source: https://arxiv.org/abs/2505.03574)
- [FACT-15] ProgAgent (arXiv:2603.07784, Mar 2026): PPO + coreset replay + synaptic intelligence. JAX-native JIT 루프. "Perfect memory" oracle보다 높은 성능. Catastrophic forgetting 완화. (source: https://arxiv.org/abs/2603.07784)
- [FACT-17] Goal Drift (arXiv:2505.02709, May 2025): 모든 LLM이 장기 실행에서 goal drift 발생. Claude 3.5 Sonnet 최우수: >100K 토큰에서 near-perfect adherence. Drift는 context 길이와 양의 상관관계. (source: https://arxiv.org/abs/2505.02709)
- [FACT-18] Letta/MemGPT (Aug 2025): 파일시스템 툴만 사용한 에이전트가 LoCoMo 74.0% → Mem0 graph variant 68.5% 초과. "스토리지 메커니즘보다 에이전트 검색 능력이 더 중요". (source: https://www.letta.com/blog/benchmarking-ai-agent-memory)
- [FACT-19] Agent0 (arXiv:2511.16043, Nov 2025): Curriculum Agent + Executor Agent 공생 co-evolution. Zero human-curated data. +18% 수학적 추론, +24% 일반 추론 (Qwen3-8B-Base). (source: https://arxiv.org/abs/2511.16043)

## Cross-Validation Matrix

| 주제 | 합의 수준 | 핵심 근거 |
|---|---|---|
| Outer/Inner loop 분리 아키텍처 | CONFIRMED-STRONG | FACT-1/2/3 + 기존 omc-live 설계 |
| 메모리 개선 필요 (flat JSONL 한계) | CONFIRMED-STRONG | FACT-8/10/11 + DA CRITICAL: 3-tier 오귀인 |
| Exploration 부재 = MAJOR gap | CONFIRMED | FACT-5/6/19 + DA MAJOR |
| score_variance → false plateau 위험 | CONFIRMED | DA CRITICAL + real deployment 검증 |
| cost_history = spec fiction | CONFIRMED-STRONG | real live-state.json 부재 + FACT-2 |
| Continuous alignment 필요 | CONFIRMED | FACT-14 LlamaFirewall AlignmentCheck |
| 동일모델 goal drift 위험 | CONTESTED | FACT-17 (drift 사실) vs. goal_fidelity gate (현재 구현) |
| Context exhaustion 처리 | UNRESOLVED | FACT-1/2 언급, 구현 방안 미정 |
| Catastrophic forgetting | UNRESOLVED | FACT-3/15, omc-live 미처리 |

## Devil's Advocate 핵심 비평 요약

**CRITICAL:**
1. 메모리 아키텍처 오귀인 — 실제 구현은 flat JSONL + bucket 휴리스틱 (3-tier 아님). FACT-8/10/11이 더 풍부한 대안 제시.
2. score_variance > 0.15 → 경고만, convergence 로직에 영향 없음 → false plateau 위험 실재하고 미처리.

**MAJOR:**
1. cost_history 필드: SKILL.md에 정의되어 있으나 실제 MarketGap/Doctor/CTX live-state.json에 부재 → "spec fiction"
2. Three Laws 체크는 이산 시점 게이트, 반복 실행 중 연속 alignment 모니터링 없음 (FACT-14 AlignmentCheck 미적용)
3. Step 6b는 순수 exploitation (weakest dimension 타겟팅) — exploration 메커니즘 없음 (FACT-5/6/19)

**MINOR:**
- Step 5a의 `git add -A` → .env 등 민감 파일 커밋 위험

## Final Conclusion — omc-live 적용 제안

### P1 (즉시 적용)

**[P1-1] score_variance 적응형 ensemble (Critical fix)**
- 근거: DA CRITICAL + 실제 배포 검증
- 구현: `score_variance > 0.15` 시 ensemble을 `2 * score_ensemble_n`회 재실행 후 재측정. 재측정 후에도 variance > 0.15이면 `[SCORE UNCERTAIN]` 로그 + plateau 판정 보류 (해당 iteration에서 plateau_count 증가 안 함)
- 위치: SKILL.md Score Parser 섹션

**[P1-2] Iteration Alignment Check (MAJOR fix)**
- 근거: FACT-17 (goal drift), FACT-14 (AlignmentCheck), DA MAJOR
- 구현: PRE-LOOP Step 1 또는 매 iteration 시작 시 1-prompt 체크:
  - "현재 {current_goal}이 original_goal '{original_goal}'의 범위 내에 있는가?"
  - similarity < 0.7 → `[ALIGNMENT WARNING]` 로그 + 사용자에게 확인 요청
- 이미 goal_fidelity 개념이 있으나 반복 실행 중 비활성화 상태 → 활성화

**[P1-3] cost_history compliance validation**
- 근거: DA MAJOR (spec fiction), FACT-2 (4-15x 토큰 노출)
- 구현: Step 4 (live-state.json write) 후 required fields 검증:
  - `["current_iteration", "best_score", "cost_history", "goal_fidelity"]` 중 누락 시 경고 + 기본값 삽입
- 위치: Step 4 (live-state.json 저장) 뒤에 validation 절 추가

### P2 (다음 세션 고려)

**[P2-1] Exploration rate in goal evolution**
- 근거: FACT-5/6/19 (co-evolution +18-24%), DA MAJOR
- 구현: Step 6b에 `exploration_rate: 0.2` config 추가. 20% 확률로 weakest dimension 외 방향 탐색 candidate 생성.

**[P2-2] Zettelkasten-style episode linking**
- 근거: FACT-10 (A-MEM, NeurIPS 2025), DA CRITICAL (메모리 오귀인)
- 구현: SAVE 시 현재 에피소드와 유사 과거 에피소드를 LLM으로 연결 메타데이터 추가. Vector DB 불필요 — LLM이 링크 결정.

**[P2-3] Context budget tracker**
- 근거: FACT-2 (15x 토큰), FACT-1 (context exhaustion 문제), DA MISSING
- 구현: `context_tokens_used` 카운터를 live-state.json에 추가. 모델 컨텍스트 한계의 70%에서 early handoff 트리거.

### P3 (선택적)

- Wave-based parallel mode: FACT-1 패턴으로 직렬 outer loop 대신 병렬 wave 실행 (진정한 infinite mode를 위한 대안 아키텍처)
- Catastrophic forgetting 체크: CONVERGED 시 이전 성공 에피소드 task type으로 빠른 regression 검증
- git add -A → git add -u 로 변경 (추적된 파일만 스테이징)

## Reference Sources
- https://github.com/disler/infinite-agentic-loop — Wave-based infinite loop 구현체
- https://arxiv.org/abs/2501.07278 — Lifelong LLM Agents Roadmap (TPAMI 2026)
- https://arxiv.org/abs/2510.18821 — SSP (Qwen, self-play task generation)
- https://openreview.net/forum?id=ySSq8Yavs4 — ASL (ICLR 2026, closed-loop co-evolution)
- https://arxiv.org/abs/2512.13564 — Memory in the Age of AI Agents (Dec 2025 survey)
- https://arxiv.org/abs/2502.12110 — A-MEM (NeurIPS 2025, Zettelkasten memory)
- https://arxiv.org/abs/2507.07957 — MIRIX (6-type multi-agent memory)
- https://arxiv.org/abs/2601.18510 — JitRL (Jan 2026, training-free continual)
- https://arxiv.org/abs/2505.03574 — LlamaFirewall (Meta, AlignmentCheck)
- https://arxiv.org/abs/2502.11448 — AGrail (lifelong guardrail)
- https://arxiv.org/abs/2603.07784 — ProgAgent (Mar 2026, continual RL)
- https://arxiv.org/abs/2505.02709 — Goal Drift benchmark (May 2025)
- https://arxiv.org/abs/2511.16043 — Agent0 (co-evolution, Nov 2025)
- https://www.letta.com/blog/benchmarking-ai-agent-memory — Letta LoCoMo benchmark
