# [expert-research-v2] Playwright Test Agents v1.56 — Claude Code 활성화
**Date**: 2026-04-07  **Skill**: expert-research-v2

## Original Question
Playwright Test Agents NEW (Planner·Generator·Healer 3-Agent chain, v1.56 공식 릴리스)를 Claude Code에서 활성화하는 방법 리서치

## Web Facts

[FACT-1] Playwright v1.56에서 Test Agents 공식 릴리스. 3개 에이전트: Planner(앱 탐색→Markdown 테스트 계획), Generator(계획→Playwright 테스트 파일), Healer(실행→실패 자동 수정) (source: playwright.dev/docs/test-agents)

[FACT-2] Claude Code 활성화 명령: `npx playwright init-agents --loop=claude` — agent definitions(Markdown 파일)을 프로젝트에 생성 (source: playwright.dev/docs/test-agents)

[FACT-3] Loop 옵션: VS Code = `--loop=vscode`, OpenCode = `--loop=opencode`, Claude Code = `--loop=claude` (source: playwright.dev/docs/test-agents)

[FACT-4] 생성 파일 구조: `.github/` (agent definitions), `specs/` (Markdown 테스트 계획), `tests/` (생성된 테스트 파일), `playwright.config.ts` (source: playwright.dev/docs/test-agents)

[FACT-5] Agent definitions는 Markdown 파일이므로 커스터마이징 가능: Planner 탐색 전략, Generator 코드 스타일(네이밍 컨벤션 등) (source: shipyard.build)

[FACT-6] Playwright 업데이트 시 `init-agents` 재실행 필요 — 커스터마이징 덮어쓰임 위험 (source: shipyard.build)

[FACT-7] MCP를 통해 LLM이 실제 브라우저 DOM 관찰 — 추측 없이 실제 앱 동작 기반 결정 (source: supatest.ai)

[FACT-8] Claude Code MCP 설정: `claude mcp add playwright npx @playwright/mcp@latest` (global) / `--scope project` (팀 공유) (source: testomat.io, builder.io)

[FACT-9] 2026년 초 `@playwright/cli` 출시 — MCP 대비 토큰 약 4배 절감 (114k→27k). 단일 소스(testdino.com), 기능 동등성 미검증 (source: testdino.com)

[FACT-10] VS Code agentic 경험은 VS Code v1.105+ 필요 — Claude Code에는 무관 (source: testdino.com)

## Multi-Lens Analysis

### Domain Expert (Lens 1)
- 활성화 경로는 두 명령 (`init-agents` + MCP 설정)으로 명확함 [GROUNDED]
- 3-agent chain은 순차적 파이프라인 — Planner 오류가 하위 agent에 전파될 수 있음 [REASONED]
- `.github/` 내 Markdown agent definitions는 커스터마이징 핵심이자 업데이트 시 덮어쓰기 위험 [GROUNDED]
- `@playwright/cli`는 토큰 절감 대안이나 기능 동등성 미검증 [UNCERTAIN]
- `--scope project`로 팀 공유 및 git 관리 가능 [GROUNDED]

### Self-Critique (Lens 2)
- [OVERCONFIDENT] MCP 없이 `init-agents`만으로의 동작 범위 미확인
- [MISSING] Healer 무한루프 방지 메커니즘 미분석
- [MISSING] 인증 필요 앱에서의 Planner 처리 방법
- [CONFLICT] `@playwright/cli` 토큰 수치는 단일 소스 — 과신 주의

### Synthesis (Lens 3)
두 명령 모두 실행 권장 (MCP는 Healer 단계에서 critical). Planner 결과를 중간 검토하는 hybrid workflow 권장.

## Final Conclusion

### 활성화 절차

```bash
# 1. Prerequisites
npx playwright --version  # 1.56 이상 확인

# 2. Agent definitions 초기화
npx playwright init-agents --loop=claude

# 3. MCP 연결
claude mcp add playwright npx @playwright/mcp@latest          # 개인용
# 또는
claude mcp add playwright npx @playwright/mcp@latest --scope project  # 팀 공유
```

### 실행
Claude Code 대화창에서:
```
Run the Playwright Test Agents to generate tests for [URL or 기능 설명]
```

단계별 실행 권장: Planner → specs/ 검토 → Generator → tests/ 확인 → Healer(실패 시)

### 커스터마이징
`.github/` 내 Markdown 편집 (Planner: 탐색 전략/인증, Generator: 코드 스타일, Healer: 수정 범위)
업데이트 후 `git diff .github/`로 병합 확인 필수

### 주의사항
- 인증 필요 앱: Planner definition에 로그인 처리 명시
- 토큰 비용: `@playwright/cli` 대안 검토 가능 (기능 동등성 미검증)
- `.github/` 위치: GitHub Actions 워크플로 충돌 점검

## Sources
- [Playwright Test Agents 공식 문서](https://playwright.dev/docs/test-agents)
- [Playwright Agents: Planner, Generator, Healer in Action](https://dev.to/playwright/playwright-agents-planner-generator-and-healer-in-action-5ajh)
- [Write automated tests with Claude Code using Playwright Agents](https://shipyard.build/blog/playwright-agents-claude-code/)
- [Playwright MCP & Claude Code: AI-Powered Test Automation Guide](https://testomat.io/blog/playwright-mcp-claude-code/)
- [How to Use Playwright MCP Server with Claude Code](https://www.builder.io/blog/playwright-mcp-server-claude-code)
- [Playwright MCP Explained (2026)](https://testdino.com/blog/playwright-mcp/)
