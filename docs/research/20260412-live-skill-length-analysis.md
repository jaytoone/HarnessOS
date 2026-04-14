# [expert-research] live / live-inf 스킬 길이 적절성 분석
**Date**: 2026-04-12  **Skill**: expert-research (lean v2, code-internal)

## Original Question
live, live-inf 스킬의 길이가 적절한가?

## Measurement

| Skill | Lines | Tokens (approx) | Rank (codebase) |
|-------|-------|-----------------|-----------------|
| `live` | 1526 | ~22k | 1st (공동) |
| `live-inf` | 930 | ~12.7k | 6th |

Comparison baseline (other complex skills): ttps-pipeline 1523, omc-configure-notifications 1213, omc-setup 1188, omc-team 967, expert-research-v2 434.

## Multi-Lens Analysis

### LENS 1: Domain Expert

1. **[REASONED] 복잡도 클래스 기준으로 live는 정당화 가능** — live는 단순 파이프라인 스킬이 아닌 멀티-이터레이션 오케스트레이터. iteration budget, scoring ensemble, context priming, routing, git checkpoint 등 복잡도가 실제로 높다. 같은 줄 수라도 linear pipeline vs. branching orchestrator는 다른 복잡도.

2. **[GROUNDED] changelog + arXiv 주석은 런타임 가치 제로** — 프론트매터 changelog 16줄(live), 13줄(live-inf) + 파라미터별 연구 근거 주석은 문서용이지 실행 지시문이 아님. LLM이 런타임에 읽어도 실행 품질에 기여하지 않음.

3. **[GROUNDED] live-inf의 토큰 추정 공식 중복은 설계 트레이드오프** — live-inf가 standalone으로 호출되는 것이 정상이므로 공식 복사는 신뢰성을 위한 의도적 선택. 다만 65줄 → ~20줄로 압축 가능.

4. **[REASONED] ASCII flowchart + 비교 표(live-inf)는 실행 지시문이 아님** — 55줄 flowchart와 20줄 비교표는 온보딩/디버깅 도구. README.md로 이동하면 실행 컨텍스트를 낭비하지 않음.

5. **[REASONED] 160줄 Skill Router 키워드 테이블은 과잉일 수 있으나 신중해야 함** — 명시적 테이블은 암묵적 routing이 실패했기 때문에 존재할 가능성이 높음. 근거 없이 삭제하면 routing regression 위험.

### LENS 2: Devil's Advocate

- **[OVERCONFIDENT]**: "changelog 16줄이 런타임 성능을 저해한다" — 전체 파일의 ~1%로 attention 영향은 무시할 수준.
- **[MISSING]**: 실제 런타임 실패 모드 분석 없음. 길이 자체가 문제인지, 아니면 critical step이 파일 깊숙이 위치한 position bias 문제인지 미확인.
- **[CONFLICT]**: live-inf 중복을 "poor implementation"으로 부르는 것은 standalone 신뢰성 요건과 충돌. 중복은 결함이 아니라 의도적 트레이드오프.
- **실질적 반론**: baseline 자체가 이 코드베이스는 1200-1500줄 스킬을 정상 운영함을 보여줌. live는 이상치가 아님. "너무 길다"는 주장에는 구체적 오작동 사례가 필요.

### LENS 3: Synthesis

**확정 삭감 대상 (Devil's Advocate 생존)**:

| 항목 | 파일 | 예상 절감 |
|------|------|-----------|
| changelog + arXiv patch history 이동 (CHANGELOG.md) | 양쪽 | live -16, live-inf -13 |
| 파라미터 rationale 압축 (다문장→1문장) | live | ~30-50줄 |
| ASCII flowchart + 비교표 이동 (README.md) | live-inf | ~75줄 |
| World Model JSON schema 예제 압축 | live-inf | ~35줄 |
| 토큰 추정 공식 압축 (65줄→20줄) | live-inf | ~45줄 |

**삭감 불가 항목**:
- Step 3e 라우팅 키워드 테이블 (생산 신뢰성)
- Step 6/6a/6b 스코어링 + EVOLVE 로직 (핵심 가치)
- 모든 prohibition + stop condition (가드레일)

**예상 결과**:
- `live`: 1526 → ~1400-1420줄 (약 8% 감소)
- `live-inf`: 930 → ~760-800줄 (약 15% 감소)

## Final Conclusion

**길이 적절성: live는 적절, live-inf는 약간 과잉**

- `live` 1526줄은 코드베이스 기준으로 정상 범위이며 복잡도가 정당화함.
- `live-inf` 930줄은 ~130-170줄 절감 가능 (flowchart, 비교표, JSON schema 이동/압축).
- 줄 감소보다 더 중요한 것: **critical step(Step 3 loop, Step 6 judgment)이 파일 내 적절한 위치에 있는가**. Position bias로 인해 파일 후반부 step이 무시되는 현상이 길이 자체보다 더 큰 실행 품질 리스크일 수 있음.

## Confidence: MEDIUM

**불확실성**:
- live-inf가 실제로 standalone 호출되는지 (중복 필요성 결정)
- 관찰된 런타임 실패가 길이에 기인한 사례 있는지 (preemptive vs. reactive 최적화)

## Related
- [[projects/Ameva/research/20260326-omc-live-skill-critique|20260326-omc-live-skill-critique]]
- [[projects/Ameva/research/20260414-ameva-loop-skill-spec|20260414-ameva-loop-skill-spec]]
- [[projects/Ameva/research/20260325-omc-live-patch-critique|20260325-omc-live-patch-critique]]
- [[projects/Ameva/research/20260328-omc-live-infinite-loop-architecture-research|20260328-omc-live-infinite-loop-architecture-research]]
- [[projects/Ameva/research/20260412-skill-structural-content-position-analysis|20260412-skill-structural-content-position-analysis]]
- [[projects/Ameva/research/20260327-omc-live-git-checkpoint-self-evolving-research|20260327-omc-live-git-checkpoint-self-evolving-research]]
- [[projects/Ameva/research/20260328-omc-live-science-research-domain-expansion|20260328-omc-live-science-research-domain-expansion]]
- [[projects/Ameva/research/20260326-omc-live-self-evolving-outer-loop|20260326-omc-live-self-evolving-outer-loop]]
