# Vertical AI에서 에이전트/스킬을 자율 도구로 활용하는 방법론

**Date**: 2026-04-12  **Skill**: expert-research (lean v2)

## Original Question
Vertical AI 시스템에서 에이전트/스킬을 자율적으로 도구(tool)처럼 활용하게 하는 방법론 — Tool-Use Agent, Agentic Scaffold, Skill-as-Tool 패턴 연구/논문/방법론

---

## Key Answer

**스킬(Skill)은 도구(Tool)의 상위 추상화다** — 단순 API 호출이 아니라 세션 간 영속하는 절차적 메모리. Vertical AI에서 스킬을 자율 도구로 활용하려면 세 가지가 필요하다: (1) 스킬을 4-tuple로 형식화, (2) 임베딩+LLM 하이브리드 라우터, (3) 메타-스킬(스킬이 스킬을 생성) + 인간 검토 게이트.

---

## Detailed Analysis

### 1. 도구 vs 스킬 — 핵심 구분 (SoK arXiv:2602.20867)

스킬의 정식 정의: **S = (C, π, T, R)**

| 요소 | 의미 | 도구(Tool)와의 차이 |
|------|------|-------------------|
| **C** (applicability condition) | 언제 이 스킬이 활성화되는가 | 도구는 C 없음 (명시적 호출만) |
| **π** (executable policy) | 실행 중 내부 의사결정 | 도구는 결정론적 I/O |
| **T** (termination condition) | 스킬이 스스로 완료 판단 | 도구는 호출자가 판단 |
| **R** (callable interface) | 이름, 파라미터, 반환 타입 | 도구와 동일 |

**4가지 차원의 근본적 차이:**

| 차원 | 도구 | 스킬 |
|------|------|------|
| 구성 | 순차(sequential) | 계층적 DAG + 재귀 |
| 영속성 | 무상태(stateless) | 세션 간 재사용 |
| 검증 | I/O 스키마 | 결과 정확성 + 안전성 |
| 거버넌스 | 개별 도구 단위 | 신뢰 계층 + 샌드박싱 |

**실용적 기준**: 내부적으로 LLM 추론이 포함되면 스킬, 결정론적 I/O면 도구.

---

### 2. 라우팅 전략 — 임베딩 + LLM 하이브리드

**3단계 파이프라인** (SoK + Tool-to-Agent Retrieval arXiv:2511.01854):

```
태스크 입력
    ↓
[Stage 1] 임베딩 검색
  task_vec vs skill_description_vec → top-K 후보
    ↓
[Stage 2] LLM 선택
  후보 스킬의 메타데이터(C, π, R) 보고 최종 선택
    ↓
[Stage 3] 실행 + T(종료조건) 모니터링
```

**Tool-to-Agent Retrieval의 핵심 기여**: 도구와 에이전트를 같은 벡터 공간에 임베딩, 이분 그래프 G=(A,T,E)로 소유 관계 표현 → top-N 유사도로 검색 후 부모 에이전트 추출 → top-K 최종 선택.

성능: 70개 MCP 서버, 527개 도구 대상 — Recall@5 **+19.4%**, nDCG@5 **+17.7%** 향상. 8개 임베딩 모델에서 일관된 결과 (아키텍처 비의존적).

**현실적 적용 기준**: 스킬 수 < 20개 → LLM 직접 선택(컨텍스트에 전체 카탈로그 포함)이 더 효율적. 스킬 수 ≥ 20개 → 임베딩 계층 추가.

---

### 3. 스킬 구성 패턴 7가지 (SoK)

| 패턴 | 메커니즘 | 대표 시스템 |
|------|----------|------------|
| **메타데이터 기반** | SKILL.md = instructions+workflow+scripts 번들 | Claude Code |
| **코드-as-스킬** | 실행 가능한 프로그램 | Voyager |
| **워크플로우 강제** | 하드 게이트 프로세스 | LATS, TDD agents |
| **자가 진화 라이브러리** | 자동 증류+검증 | Voyager, CRADLE |
| **하이브리드 NL+코드** | 자연어+실행 가능 요소 혼합 | Claude skills |
| **메타-스킬** | 스킬이 스킬 생성 | Eureka, Self-Instruct |
| **마켓플레이스 배포** | 버전 관리, 배포 가능 패키지 | OpenClaw, MCP |

**중요한 품질 수치** (SkillsBench): 자가 생성 스킬 = 평균 **-1.3pp** 성능, 큐레이션 스킬 = **+16.2pp** 성능. → 메타-스킬로 초안 생성 후 인간 검토 게이트 필수.

---

### 4. 자율 도구 선택의 전제 조건

**AutoTool (arXiv:2512.13278)**: 명시적인 도구 선택 훈련(explicit tool-selection training)이 없으면 zero-shot 자율 선택은 ground-truth 대비 유의미하게 낮은 성능. 파인튜닝이 불가능한 환경(Claude Code 등)에서의 대안: few-shot 예시를 오케스트레이터 프롬프트에 삽입.

**MCPAgentBench (arXiv:2512.24565)** 측정 3요소:
1. 도구 호출이 필요한가 (vs 직접 응답)
2. 후보군에서 적절한 도구 선택 → Invocation Accuracy
3. 올바른 파라미터 식별 → Parameter F1

---

### 5. Vertical AI의 Cognitive Skills Module

**arXiv:2501.00881**: Vertical AI = LLM 인지 백본 + 실시간 적응 + 업계별 워크플로우. Cognitive Skills Module = 도메인 특화 목적 추론 능력을 캡슐화한 단위.

일반 AI 스킬 vs Vertical AI 스킬의 핵심 차이:
- 일반 AI: "무엇을 할 수 있는가(capability)" 중심
- Vertical AI: "이 도메인에서 어떤 추론 패턴을 사용하는가(reasoning pattern)" 중심

---

## Entity 프로젝트 즉시 적용 로드맵

### Phase 1 — 지금 당장: SKILL.md 4-tuple 표준화

현재 SKILL.md는 R(인터페이스)만 형식화. C, T를 프론트매터에 추가:

```yaml
---
name: value-gap-theory
description: "VALUE GAP demand theory diagnostic — L1-L5 identity gap classification"
condition: "사용자가 지식/정체성 제품의 수요 발생 원인 또는 WTP를 분석할 때"
termination: "L1-L5 레벨 확정 + 빠짐 감사 완료 OR 스코프 외로 판명"
interface:
  input: "제품 아이디어 또는 ICP 설명"
  output: "갭 레벨 진단 + D(WTP) 예측 + 빠짐 리스크 점수"
status: stable
---
```

### Phase 2 — 단기: LLM 직접 선택 라우터 (live-inf 루프 수정)

오케스트레이터 시스템 프롬프트에 스킬 카탈로그 + few-shot 예시 추가:

```
Available Skills:
- value-gap-theory: condition="지식/정체성 제품 수요 분석"
- career-mirror-builder: condition="Career Mirror 빌드 실행"
- wtp-validator: condition="B2B SaaS 기능적 WTP 검증"
- expert-research: condition="외부 정보 조사 필요"

Few-shot routing examples:
Task: "이 아이디어 WTP 분석해줘" (커리어 관련)
→ value-gap-theory (identity product, not B2B SaaS)

Task: "Career Mirror 시드 코호트 모집 어떻게 시작?"
→ career-mirror-builder (execution scaffold 필요)

Task: "최신 agent tool-use 논문 조사"
→ expert-research (외부 정보 필요)
```

### Phase 3 — 중기 (스킬 수 20+ 시): 임베딩 라우팅

각 SKILL.md에 `embedding_hint` 필드 추가 (20-50 토큰 압축 문장). 로컬 numpy 코사인 유사도로 top-3 후보 선정 → LLM 최종 선택. 외부 벡터 DB 불필요.

### Phase 4 — 거버넌스: 스킬 품질 보호

```
메타-스킬 생성 → status: draft
    ↓
인간 검토 게이트 (필수, 생략 불가)
    ↓
status: reviewed → stable
    ↓
~/.claude/skills/에 commit
```

자동 deploy 금지. 자가 생성 스킬의 -1.3pp 품질 저하 누적 방지.

---

## Caveats & Trade-offs

**임베딩 라우팅의 규모 역설**: 스킬이 10개 미만인 현 시점에서 임베딩 파이프라인 도입은 유지 비용이 정확도 향상을 초과할 수 있다. LLM 직접 선택으로 시작하고 스킬 20개 초과 시 전환.

**메타-스킬 품질 붕괴 위험**: 검토 없이 자율 생성-deploy 루프를 허용하면 라이브러리 품질이 점진적으로 저하된다. 인간 게이트는 선택이 아닌 필수.

**C(조건) 충돌 문제**: 여러 스킬이 동일 태스크에 C=True를 주장하면 현재 구조에 해결 메커니즘이 없다. 스킬 수 증가 시 priority 필드 또는 conflict resolution 로직 필요.

---

## Recommendations

1. **이번 주**: 모든 SKILL.md에 `condition`, `termination`, `status` 필드 추가
2. **다음 주**: live-inf 루프 오케스트레이터에 스킬 카탈로그 + few-shot 라우터 추가
3. **스킬 20개 도달 시**: numpy 코사인 유사도 기반 임베딩 라우팅 도입
4. **지금부터**: 신규 스킬은 반드시 `status: draft` → 검토 → `status: stable` 경로

---

## Sources

- [SoK: Agentic Skills — Beyond Tool Use in LLM Agents](https://arxiv.org/html/2602.20867)
- [Tool-to-Agent Retrieval: Bridging Tools and Agents](https://arxiv.org/abs/2511.01854)
- [AutoTool: Dynamic Tool Selection and Integration](https://arxiv.org/html/2512.13278v1)
- [Agentic Systems: Vertical AI Agents (arXiv:2501.00881)](https://arxiv.org/abs/2501.00881)
- [MCPAgentBench: Real-world Tool Use Benchmark](https://arxiv.org/abs/2512.24565)
- [Agent Skills: Anthropic's Claude Code Skills](https://thenewstack.io/agent-skills-anthropics-next-bid-to-define-ai-standards/)
- [LLM-Based Agents for Tool Learning: A Survey](https://link.springer.com/article/10.1007/s41019-025-00296-9)

---

## Further Investigation Needed

- Entity 현재 스킬 수 및 live-inf 라우팅 방식 실측 (`ls ~/.claude/skills/`)
- LLM 직접 선택 라우터 vs 임베딩 라우팅의 crossover point 실험
- C(조건) 충돌 해결 메커니즘 설계 (priority 필드 vs LLM 중재)
- Cognitive Skills Module 구체 구현 방식 (arXiv:2501.00881 세부 확인)

## Related
- [[projects/Ameva/research/designs/oss_agent_tools_2026_integration|oss_agent_tools_2026_integration]]
- [[projects/Ameva/research/20260411-wtp-career-mirror-mvp|20260411-wtp-career-mirror-mvp]]
- [[projects/Ameva/research/20260326-omc-live-skill-critique|20260326-omc-live-skill-critique]]
- [[projects/Ameva/research/20260412-live-skill-length-analysis|20260412-live-skill-length-analysis]]
- [[projects/Ameva/research/20260331-autonomous-skill-selection-research|20260331-autonomous-skill-selection-research]]
- [[projects/Ameva/research/20260331-skill-selection-implementation-templates|20260331-skill-selection-implementation-templates]]
- [[projects/Ameva/research/20260411-wtp-career-mirror-pricing|20260411-wtp-career-mirror-pricing]]
- [[projects/Ameva/research/20260411-wtp-demand-genesis-theory|20260411-wtp-demand-genesis-theory]]
