# Skill / Agent Audit — 분류 오류 및 수정 항목

**기준**: Agent = 프레임워크/전문가 (독립 실행 전문 능력), Skill = 에이전트 사용 스케폴드 (워크플로우 정의)  
**제외**: omc- 계열 전체  
**날짜**: 2026-04-09 | **수정**: 2026-04-10 (expert-research 항목 정정)

---

## Category A — 네이밍 오류 (이름이 역할과 불일치)

| 항목 | 현재 위치 | 문제 | 권고 |
|------|----------|------|------|
| `ontolo-agent` | skill | 이름에 "agent" 포함 → 사용자가 Agent tool로 호출 시도할 가능성. 실제로는 라우팅 스케폴드 (어떤 agent를 쓸지 결정) | 이름 → `skill-router` 또는 `agent-router` 로 변경. 혹은 실제 Agent subtype으로 전환 |

---

## Category B — 스킬이지만 에이전트 역할 수행 (직접 전문 작업 실행, 에이전트 미위임)

에이전트 사용 스케폴드가 아니라 Claude 자신이 전문가로서 동작하는 케이스.  
이 경우 skill로 두는 것이 **잘못은 아니지만**, "스킬 = 스케폴드" 기준과 어긋남.

| 항목 | 문제 설명 | 권고 |
|------|----------|------|
| `human-edge` | "Expert bias-to-direction engine" — 편향 분석부터 방향 결론까지 Claude 단독 수행. 에이전트 위임 없음. 전문가 그 자체. | Agent subtype으로 전환하거나, skill 내부에서 `human-edge` 전용 agent dispatch 추가 |
| `marl-5stage` | "A single LLM performs 5 roles sequentially" — Claude가 S1~S5를 직접 수행. 에이전트 없음. 품질 게이트 프로토콜. | 명칭을 `quality-gate` 등으로 변경, 또는 5단계 각각을 개별 agent로 분리하는 스케폴드로 재설계 |
| ~~`expert-research`~~ | ~~Claude 단독 리서치~~ | **수정됨**: expert-research ≠ expert-research-v2. 별개 도구 (lean 단일 에이전트 vs 3-agent pipeline). 독립 유지 정상. |

---

## Category C — 에이전트와 스킬 간 중복 (기능 겹침)

| Skill | 중복 Agent | 겹치는 기능 | 권고 |
|-------|-----------|------------|------|
| `wtp-validator` (skill) | `biz-wtp-validator` (agent) | WTP 검증 로직 동일 도메인 | skill은 `biz-wtp-validator` agent를 호출하는 스케폴드로 재구성. 현재 skill이 직접 처리하면 중복 |
| ~~`expert-research`~~ | — | — | **수정됨**: 독립 유지 (lean vs deep 트레이드오프 공존 설계) |
| `ontolo-agent` (skill) | 전체 agent pool | 라우팅 | Skill로 유지 시 네이밍 수정 필수 |

---

## Category D — 유틸리티 커맨드 (Agent도 Skill도 아닌 명령 레이어)

현재 skill로 분류되어 있으나 실제로는 특정 작업 자동화 커맨드.

| 항목 | 설명 | 권고 |
|------|------|------|
| `g1` | "Record a decision to G1 session memory" — 메모리 쓰기 단일 작업 | skill보다는 CLI 커맨드 또는 hook으로 관리 |
| `dash-post` | "Auto-post today's work log" — 특정 외부 서비스 자동화 | Agent task로 전환 (dev-executor 수준) |
| `youtuber` | "YouTube Shorts upload workflow" — 특정 플랫폼 자동화 | Agent task로 전환 또는 skill 유지 시 내부 agent 위임 명시 |

---

## Category E — 기타 (정상이지만 설명 개선 필요)

| 항목 | 현황 | 개선 포인트 |
|------|------|-------------|
| `intent-clarifier` | meta-cognitive layer, 에이전트 미위임 | 스케폴드 목적(다른 workflow 진입 전 전처리)이 명확하므로 skill 유지 OK. 설명에 "pre-hook layer" 명시 권장 |
| `asker` | 유저의 Reading List 기반 상담 | 특정 컨텍스트(Reading List)에 귀속된 domain advisor. Session-bound이므로 skill 유지 OK. 단, 역할이 "스케폴드"가 아닌 "advisor"임을 설명에 명시 |
| `inhale` / `exhale` | knowledge pipeline 일부 | `evolve` 스케폴드의 서브 스텝. 단독 호출 가능하나 `evolve`의 구성 요소로 관계 명시 필요 |

---

## 요약 — 우선순위별 수정 항목

### P1 (즉시 수정)
1. **`ontolo-agent`** — 이름 변경 (agent → router)

### P2 (구조 재설계)
2. **`expert-research`** — ~~deprecated~~ (롤백: expert-research-v2와 별개 내용, 독립 유지)
3. **`wtp-validator`** — `biz-wtp-validator` agent 호출 스케폴드로 재구성

### P3 (선택적 개선)
4. **`human-edge`** — agent subtype 전환 검토
5. **`marl-5stage`** — 명칭 변경 또는 agent 분리 구조 검토
6. **`g1` / `dash-post` / `youtuber`** — agent task 또는 hook 레이어로 이동 검토

---

## 올바른 스케폴드 사례 (수정 불필요)

- `expert-research-v2` — 3-agent pipeline 명시적 위임 ✓
- `biz-synthesis` — biz-sales/strategy/gap-theory 병렬 dispatch ✓
- `bs-framework-synthesis` — framework agent 자동 선택 dispatch ✓
- `entity` / `live` / `live-inf` / `conceptual` — 워크플로우 오케스트레이션 ✓
- `evolve` — inhale→exhale→live 파이프라인 ✓
- `ttps` — /entity, /live 통합 하네스 ✓
