# [expert-research-v2] AI 하네스(Harness) 개념 및 사용법
**Date**: 2026-03-30  **Skill**: expert-research-v2

## Original Question
하네스(Harness)란 무엇인가? AI 에이전트 맥락에서의 정의와 사용 방법, 별도 API 필요 여부

## Web Facts
[FACT-1] 하네스는 AI 에이전트를 제어·보호·조율하는 계층. 제약(constraints), 피드백 루프, 검증, 수정 메커니즘의 집합체 (source: openai.com/index/harness-engineering)
[FACT-2] 구성요소: 제약(아키텍처 경계) + 정보(컨텍스트 엔지니어링) + 검증(테스트/린팅) + 수정(피드백 루프) (source: daleseo.com/harness-engineering)
[FACT-3] Anthropic 3-에이전트 구조: Planner + Generator(스프린트 계약 협상) + Evaluator(Playwright QA) (source: anthropic.com/engineering/harness-design-long-running-apps)
[FACT-4] 별도 외부 API 불필요. CLAUDE.md/AGENTS.md + CI/CD + 기존 인프라 활용이 핵심 (source: inngest.com/blog/your-agent-needs-a-harness-not-a-framework)
[FACT-5] 2026년 패러다임: "에이전트가 아니라 하네스가 진짜 어려운 부분" — 엔지니어 3명이 하네스로 100만 줄 앱 구현 (source: medium.com)
[FACT-6] Stripe Minions: 주당 1,300개 AI PR. 성공 핵심 = 좁은 작업 설계 + 샌드박스 격리 + 반복 피드백 (source: mindstudio.ai)
[FACT-7] 하네스 vs 프레임워크: 하네스는 기존 인프라 재활용, 내구성·관찰성·상태 지속성 확보 (source: inngest.com)

## Final Conclusion
(see below)

## Sources
- https://openai.com/index/harness-engineering/
- https://www.anthropic.com/engineering/harness-design-long-running-apps
- https://www.inngest.com/blog/your-agent-needs-a-harness-not-a-framework
- https://www.mindstudio.ai/blog/what-is-ai-agent-harness-stripe-minions
