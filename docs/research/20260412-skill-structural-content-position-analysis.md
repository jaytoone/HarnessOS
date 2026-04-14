# [expert-research] LLM 스킬 파일 구조적 콘텐츠(flowchart/table) 실행 품질 영향 분석
**Date**: 2026-04-12  **Skill**: expert-research (lean v2)

## Original Question
LLM 스킬 파일에서 ASCII flowchart / 비교 테이블 같은 구조적 콘텐츠가 직접 실행되지 않아도 "읽으면 이해에 도움이 된다"는 주장이 맞는가?

## Web Facts

[FACT-1] Context rot (Chroma 2025): Claude, GPT-4, Gemini 포함 18개 모델 전부 입력 길이 증가 시 성능 저하. 일부 모델 95%→60% 정확도 하락. (source: research.trychroma.com/context-rot)

[FACT-2] Position bias: LLM은 입력의 시작/끝에 가장 많은 attention. 관련 정보가 중간에 있으면 시작/끝 대비 정확도 30%+ 하락. (source: arxiv.org/abs/2510.05381)

[FACT-3] 3000 토큰 임계점: 추론 성능이 3000 토큰 이후부터 저하 시작 — 컨텍스트 윈도우 크기와 무관. (source: blog.promptlayer.com/disadvantage-of-long-prompt-for-llm/)

[FACT-4] Tab-CoT / 구조적 형식 효과: 표 형식 CoT가 표준 CoT 대비 산술 과제 2.2% 성능 향상. 그래프/트리 구조는 추론·계획 과제에서 유의미한 향상. (source: learnprompting.org/blog/guide-to-chain-of-thought-part-one)

[FACT-5] Redundancy 규칙: 핵심 제약조건 경계 반복("Return only valid JSON")은 유효. 동일 작업을 3가지 방식으로 반복하는 것은 효과 없음. (source: medium.com/@2nick2patel2/prompt-hygiene-for-engineers)

## Final Conclusion

### 사용자 직관의 정확도
**부분적으로 맞음**. Transformer는 "구조적 요약 = 앞 내용의 합성 의미"라는 학습 연관성을 이용하므로 구조적 콘텐츠가 comprehension에 도움이 되는 것은 사실. 단, 이 효과는 **위치에 결정적으로 의존**한다.

### 원소별 판정

| 콘텐츠 | 현재 위치 | 판정 | 근거 |
|--------|-----------|------|------|
| 55줄 ASCII flowchart | 930줄 파일 끝 | **삭제** | 절차적 내용 중복, ASCII art는 Tab-CoT 효과 없음, context rot 구간 |
| 20줄 비교 테이블 (live vs live-inf) | 930줄 파일 끝 | **상단으로 이동** | 제약 명확화 기능 → 고 attention 위치에서 최대 효과 |

### 핵심 원리
- "읽으면 이해에 도움" = 맞음, BUT → **파일 앞부분에서만 priming 효과 발생**
- 파일 끝에서 읽는 구조적 콘텐츠 = context rot 구간 + position bias 저하 → priming 불가
- 비교 테이블을 PURPOSE 직후로 이동하면 "어떤 점이 live와 다른가"를 먼저 인지하고 세부 단계를 읽을 수 있음

### 실행 권고
1. flowchart → 삭제 완료 (2026-04-12 적용)
2. 비교 테이블 → `<Purpose>` 직후로 이동 (2026-04-12 적용)
3. 파일 전체 길이 → 추가 감소 권장 (현재 ~875줄, 목표 600-700줄)

## Confidence: HIGH (flowchart 삭제) / MEDIUM-HIGH (비교 테이블 재배치)

## Sources
- [Context Rot — Chroma Research](https://research.trychroma.com/context-rot)
- [Context Length Alone Hurts LLM Performance](https://arxiv.org/abs/2510.05381)
- [Disadvantage of Long Prompt](https://blog.promptlayer.com/disadvantage-of-long-prompt-for-llm/)
- [Guide to Chain-of-Thought](https://learnprompting.org/blog/guide-to-chain-of-thought-part-one)
- [Prompt Hygiene for Engineers](https://medium.com/@2nick2patel2/prompt-hygiene-for-engineers-edc4cabdbc28)

## Related
- [[projects/Ameva/research/20260412-live-skill-length-analysis|20260412-live-skill-length-analysis]]
- [[projects/Ameva/research/20260326-omc-live-skill-critique|20260326-omc-live-skill-critique]]
