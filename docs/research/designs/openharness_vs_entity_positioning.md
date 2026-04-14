# OpenHarness vs Entity — Competitive Positioning Design

## Source
- **Post**: OpenHarness: Claude Code보다 44배 가벼운 Python 기반 오픈소스 AI 에이전트 하네스 프레임워크
- **URL**: https://discuss.pytorch.kr/t/openharness-claude-code-44-python-ai-feat-hkuds/9559
- **Absorbed via**: /inhale agent_research — Chrome Reading List [RL:C1] (2026-04-08)
- **Relevance**: 9.0/10 (general)
- **Status**: proposed
- **Goal alignment**: 마켓 배포 시퀀스 — 포지셔닝 명확화 필요

## Core Claim (OpenHarness)
- Python 기반 오픈소스 에이전트 하네스
- "Claude Code보다 44배 가벼움" — 메모리/시작속도 기준 추정
- HKUDS 연구 그룹 릴리즈

## Entity vs OpenHarness 차별점 분석

### OpenHarness가 다루는 것
- 경량 에이전트 실행 런타임 (inference harness)
- Python SDK 레이어
- 단일 에이전트 실행 최적화

### Entity가 다루는 것 (차별화 포인트)
1. **자기진화 루프**: inhale → exhale → live-inf — 지식이 코드를 바꾸는 메타-레이어
2. **스킬 생태계**: 100+ 스킬 + SkillsMP 마켓 — 런타임이 아니라 행동 조각의 조합
3. **A/B 실험 프레임워크**: 스킬 변경의 효과를 실험으로 검증
4. **Epistemic 추론**: /entity + /conceptual — 에이전트 실행이 아니라 지성적 추론

### 포지셔닝 공식
```
OpenHarness: "가볍게 실행하는 에이전트 런타임"
Entity: "스스로 진화하는 에이전트 오케스트레이션 + 지식 생태계"
```
→ 경쟁이 아닌 레이어 분리: OpenHarness를 Entity 위에서 실행 런타임으로 활용 가능

### 마켓 배포 시사점
- GeekNews/PyTorchKR 포스팅 시 OpenHarness와의 차이를 명시하면 신뢰도 +
- "44배 가벼운 런타임 + 자기진화 오케스트레이션" 조합 포지셔닝 가능
- Oh My Codex 댓글 세딩 시 OpenHarness 언급 예상 → 사전 대응 메시지 준비

### Action Items
1. `docs/marketing/entity_positioning_messages.md` 업데이트 — OpenHarness 비교 섹션 추가
2. GeekNews 포스트에 "OpenHarness와 다른 점" 단락 삽입
3. 장기: OpenHarness를 Entity의 execution backend 옵션으로 통합 검토

## Related
- [[projects/Ameva/marketing/geeknews_post|geeknews_post]]
- [[projects/Ameva/research/designs/oh_my_codex_vs_harnessos_positioning|oh_my_codex_vs_harnessos_positioning]]
- [[projects/Ameva/marketing/entity_positioning_messages|entity_positioning_messages]]
