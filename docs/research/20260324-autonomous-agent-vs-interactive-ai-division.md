# [expert-research-v2] 자율 에이전트 vs 인터랙티브 AI 분업 경계
**Date**: 2026-03-24  **Skill**: expert-research-v2

## Original Question
Claude가 직접 Broadcaster 코드를 수동으로 수정하는 이유 - 자율 에이전트(OpenHands 등)가 이런 작업을 알아서 해야 하는 것 아닌가? 자율 에이전트 vs 인간-AI 협업(Claude Code)의 적절한 분업 경계는 무엇인가?

## Web Facts

[FACT-1] 2025 RCT: 경험 있는 개발자가 AI 에이전트 사용 시 작업 19% 느려짐 — "리뷰/디버깅/re-prompting 오버헤드" 때문. (source: https://www.faros.ai/blog/best-ai-coding-agents-2026)

[FACT-2] OpenHands ICLR 2025: "대부분의 AI 에이전트는 아직 research artifact — 복잡하고 long-horizon한 실제 작업을 신뢰성 있게 수행하지 못한다." (source: https://openreview.net/pdf/95990590797cff8b93c33af989ecf4ac58bde9bb.pdf)

[FACT-3] HITL/HOTL 프레임워크: "고도로 변동적인 작업(예외 多) → HITL; 저위험 반복 작업 → 자율." 쓰기/사이드이펙트 작업은 "안전성 검증 전까지 기본적으로 감독 필요." (source: https://www.permit.io/blog/human-in-the-loop-for-ai-agents-best-practices-frameworks-use-cases-and-demo)

[FACT-4] "초기 파일럿은 위험 수준 무관하게 HITL로 시작 → 신뢰도 데이터 축적 후 HOTL → 완전 자율로 점진적 전환." (source: https://www.stackai.com/insights/human-in-the-loop-ai-agents-how-to-design-approval-workflows-for-safe-and-scalable-automation)

[FACT-5] Agent 실패 패턴: "잘못된 task 분해, 역할 불복종, 과도한 경계 침범." (source: https://openreview.net/pdf/4ad6b1217a99a5f8e7a76d23157ebf94d0e328d6.pdf)

## Multi-Lens Analysis

### Domain Expert (Lens 1)
1. **실시간 발견 작업 = HITL 적합**: MiniMax TTS 플랜 오류(2061)는 실행 전 예측 불가. 6가지 모델명 탐색은 사전 명세 작성 불가 → 자율 에이전트 취약 영역.
2. **이미 실패한 sandbox 컨텍스트**: 직전 세션 OpenHands 3중 장애(Docker isolation, workspace path, .env 접근) → Claude Code 재사용이 효율적.
3. **분업 원칙**: GitHub Issue로 기술 가능 → 자율; 발견이 선행되어야 → 인터랙티브.

### Self-Critique (Lens 2)
- [OVERCONFIDENT]: "OpenHands가 탐색적 디버깅에 취약하다" — SWE-bench 60.6%는 탐색적 디버깅 포함. 더 정확히는 "현재 설정되지 않은 상태에서의 자율 에이전트"가 취약함.
- [MISSING]: 사용자 질문의 본질은 "왜 OpenHands를 트리거하는 시스템이 없는가?" — 설계 문제.
- [MISSING]: 현재 Broadcaster는 GitHub Issue tracker, 실패 알림, OpenHands 트리거 파이프라인이 전혀 없음. "자율 에이전트가 해야 했다"는 전제 자체가 성립하지 않는 인프라 상태.

### Synthesis (Lens 3)
이번 수정을 Claude Code가 한 것은 **적절**했으나, 장기 목표(자율 에이전트 생산성)를 위해 **트리거 인프라 설계**가 필요하다.
실용 분업 설계:
- 명확한 task → GitHub Issue → OpenHands 자율 실행
- 탐색적 디버깅 → Claude Code 인터랙티브
- 야간 자동화 → Cron + OpenHands + 실패 시 Issue 자동 생성

## Final Conclusion

**이번 수정을 Claude Code가 직접 한 것은 옳았다.** 이유:
1. MiniMax API 플랜 제한은 실행해봐야 드러나는 런타임 정보 (사전 명세 불가)
2. 이미 OpenHands sandbox 실패로 Claude Code 세션이 활성화되어 있었음
3. 6가지 모델명 탐색 루프는 HITL이 효율적인 "변동성 높은 예외 처리" 유형

**그러나 사용자의 지적이 가리키는 방향도 옳다**: 자율 에이전트 비전을 실현하려면 "OpenHands에게 이 오류를 전달하는 파이프라인"이 먼저 설계되어야 한다. 현재 Broadcaster에는 그 인프라가 없다.

**핵심 원칙**: *GitHub Issue로 쓸 수 있으면 → 자율 에이전트. 쓰기 전에 발견이 필요하면 → Claude Code.*

## Sources
- https://www.faros.ai/blog/best-ai-coding-agents-2026
- https://openreview.net/pdf/95990590797cff8b93c33af989ecf4ac58bde9bb.pdf
- https://www.permit.io/blog/human-in-the-loop-for-ai-agents-best-practices-frameworks-use-cases-and-demo
- https://www.stackai.com/insights/human-in-the-loop-ai-agents-how-to-design-approval-workflows-for-safe-and-scalable-automation
- https://www.auxiliobits.com/blog/how-to-choose-between-autonomous-and-human-in-the-loop-agents/
