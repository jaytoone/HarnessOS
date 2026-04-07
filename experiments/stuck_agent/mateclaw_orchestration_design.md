# MateClaw Multi-Agent Orchestration Pattern — Experiment Design

## Source
- **Post**: MateClaw Brings Multi-Agent Orchestration to the Java Ecosystem Finally
- **URL**: https://dev.to/teum/mateclaw-brings-multi-agent-orchestration-to-the-java-ecosystem-finally-7o5
- **Absorbed via**: /inhale trending_tools — dev.to (2026-04-06)
- **Relevance**: 10.0/10 (stuck_agent)

## Core Idea
MateClaw는 Spring Boot + ReAct 에이전트 + MCP 프로토콜 + 7개 채팅 플랫폼을 하나의 스택으로
통합한 Java 생태계용 멀티에이전트 오케스트레이션 프레임워크.
핵심 패턴: (1) ReAct 루프로 각 에이전트가 독립 추론, (2) MCP로 에이전트 간 통신,
(3) 플랫폼 어댑터로 외부 인터페이스 통일. stuck_agent 탈출에 유효한 패턴은
"에이전트가 막혔을 때 다른 에이전트에 위임(delegation)"하는 ReAct 기반 handoff.

## HarnessOS Application

### Hypothesis
> H0: HarnessOS의 현재 stuck_agent 탈출 전략 (단일 에이전트 재시도)은 delegation 기반
>     멀티에이전트 handoff보다 탈출률이 낮다.
> H1: MateClaw의 ReAct delegation 패턴을 적용하면 stuck_agent 탈출률이 현재 대비
>     20% 이상 향상된다.

### Current System (Baseline)
`experiments/stuck_agent/runner.py`:
- 단일 에이전트가 막히면 재시도 (Engineering) 또는 가설 재구성 (Hypothesis) 전략 적용
- 탈출 실패 시 timeout → 해당 태스크 실패 처리
- 다른 에이전트에 위임하는 메커니즘 없음

### Proposed System (Treatment)
ReAct Delegation Gate 추가:

```python
class ReActDelegationEscaper:
    """
    When primary agent is stuck (N consecutive failures),
    delegate to a specialized sub-agent with different tool set.

    Based on MateClaw's delegation pattern:
    - Agent A stuck → handoff to Agent B with context transfer
    - Agent B uses different strategy (tool subset, different prompt)
    - Result merged back into primary agent's context
    """

    STUCK_THRESHOLD = 3  # consecutive failures before delegation

    def should_delegate(self, attempt_history: list) -> bool:
        if len(attempt_history) < self.STUCK_THRESHOLD:
            return False
        recent = attempt_history[-self.STUCK_THRESHOLD:]
        return all(not a.succeeded for a in recent)

    def delegate(self, task, stuck_context) -> DelegationResult:
        # Select specialist agent based on task category
        specialist = self._select_specialist(task.category)
        # Transfer compressed context (not full history)
        compressed = self._compress_context(stuck_context)
        return specialist.attempt(task, seed_context=compressed)

    def _select_specialist(self, category):
        specialists = {
            "red_herring": HypothesisAgent(tool_subset=["search", "verify"]),
            "semantic_inv": EngineeringAgent(tool_subset=["debug", "trace"]),
            "misleading_hint": CriticalAgent(tool_subset=["challenge", "test"]),
        }
        return specialists.get(category, FallbackAgent())
```

### Experiment Protocol
- **Design**: 3-way comparison (Engineering vs Hypothesis vs ReAct-Delegation)
- **Task set**: 14 controlled tasks (기존 red_herring + semantic_inv + misleading_hint)
- **Trials**: 5 per condition = 210 obs
- **Metric**: escape_rate (stuck → solved), attempt_count_until_escape
- **Statistical test**: Kruskal-Wallis H-test (3 조건 비교)
- **Success**: p < 0.05 AND delegation_escape_rate > baseline + 0.20

### Implementation Plan
1. `experiments/stuck_agent/runner.py` — `ReActDelegationEscaper` 클래스 추가
2. `experiments/stuck_agent/tasks.py` — 3번째 strategy 조건 추가
3. `experiments/stuck_agent/analyzer.py` — 3-way 통계 비교 로직 추가
4. `experiments/stuck_agent/stats.py` — Kruskal-Wallis H-test 추가

### Expected Outcome
- red_herring 카테고리에서 delegation이 가장 효과적 (전문화된 에이전트 활용)
- 전체 escape_rate: delegation > hypothesis > engineering 순서로 가설

### Dependencies
- 기존 `runner.py`의 `StuckRunner` 클래스
- `tasks.py`의 task category 분류 (red_herring, semantic_inv, misleading_hint)
- MiniMax API (MINIMAX_API_KEY) — 전문가 에이전트 LLM 백엔드
