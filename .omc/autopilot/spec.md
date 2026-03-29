# Autopilot Spec: 자율 에이전트 통합 시스템 (Autonomous Agent Integration)
**Generated**: 2026-03-25
**Source**: 이 대화의 expert-research 결과 (docs/research/20260325-*)

## 목표
이전 연구(AREA-A: 목표 자율 업데이트, AREA-B: 하위 루프 구성)에서 도출된 설계 패턴을
Claude Code에서 즉시 사용 가능한 스킬 생태계로 구현한다.

## 구현 대상 (Phase 1 우선순위)

### 1. omc-episode-memory (신규 스킬)
**위치**: `/home/jayone/.claude/skills/omc-episode-memory/SKILL.md`
**역할**: 에피소딕 메모리 — ralph/autopilot 실행 후 요약 저장 + 다음 실행 시 검색 주입

**핵심 기능**:
- `save` 모드: 실행 요약을 `.omc/episodes.jsonl`에 append
  - 필드: timestamp, task_type, outcome(success/failure), key_errors[], approach_used, duration_estimate
- `load` 모드: 현재 태스크와 유사한 에피소드 검색 (키워드 매칭) → 컨텍스트 주입
- Three Laws Endure 조건: safety_metric 저하 시 에피소드 저장 스킵
- 기존 autopilot Phase 5: 삭제 전 save 모드 호출 후 cleanup

**파일**: `.omc/episodes.jsonl` (JSONL 포맷, 무한 append)

### 2. omc-goal-tree (신규 스킬)
**위치**: `/home/jayone/.claude/skills/omc-goal-tree/SKILL.md`
**역할**: GoalTree 관리 — 목표 Level 0-3 업데이트 프로토콜

**핵심 기능**:
- Level 0 (파라미터): 목표 세부 파라미터 변경 (임계값 조정 등)
- Level 1 (서브 목표 재구성): 최상위 목표 유지, 분해 방식 변경
- Level 2 (목표 확장): 기존 유지 + 새 목표 추가
- Level 3 (목표 교체): 완전히 다른 목표로 대체 (Three Laws 검증 필수)
- 목표 변경 시 보상 함수 재설계 동반 필수 (goal-reward misalignment 방지)
- Three Laws: Endure(안전) → Excel(성능 보존) → Evolve(변경 허가) 순차 검증

**파일**: `.omc/goal-tree.json`

### 3. omc-failure-router (신규 스킬)
**위치**: `/home/jayone/.claude/skills/omc-failure-router/SKILL.md`
**역할**: 실패 분류 라우터 — Transient/Persistent/Fatal 3유형 처리

**핵심 기능**:
- Transient: N회 미만 → 하위 재시도
- Persistent: 상위 루프 신호 → 서브 목표 재분해 OR 에이전트 교체
- Fatal: omc-goal-tree Level 2/3 트리거
- Oscillation 방지: `.omc/failure-history.json` + 지수 백오프 (base=2, max=32)
- 같은 에러 패턴 감지 시 escalation 강제

### 4. autopilot Phase 5 패치
**위치**: `/home/jayone/.claude/skills/omc-autopilot/SKILL.md` 수정
**변경**: Phase 5 Cleanup 단계 앞에 "omc-episode-memory save 호출" 삽입

## 파일 구조
```
~/.claude/skills/
├── omc-episode-memory/SKILL.md  (신규)
├── omc-goal-tree/SKILL.md        (신규)
├── omc-failure-router/SKILL.md   (신규)
└── omc-autopilot/SKILL.md        (패치)

.omc/  (프로젝트별 상태)
├── episodes.jsonl          (에피소딕 메모리)
├── goal-tree.json          (현재 GoalTree)
└── failure-history.json    (실패 이력 + 백오프 카운터)
```

## 비기능 요구사항
- 각 스킬은 독립적으로 동작 가능 (부분 채택 허용)
- 기존 omc-autopilot/ralph/ultrawork과 하위 호환
- 스킬 파일은 Markdown만 사용 (코드 실행 없음, LLM 지시문)
- 파일 경로는 프로젝트 루트 기준 `.omc/` 사용

## 검증 기준
- 각 SKILL.md가 Use_When / Do_Not_Use_When / Steps 섹션 포함
- 스킬 간 상호 참조 파일 경로 일치
- Three Laws 조건이 omc-goal-tree에서 완전히 기술됨
- omc-failure-router가 Fatal 시 omc-goal-tree를 명시적으로 호출
