# [expert-research-v2] OpenHands 전역 자율 에이전트 설정 아키텍처

**Date**: 2026-03-24  **Skill**: expert-research-v2

## Original Question

OpenHands를 다중 프로젝트에 전역으로 설정하고, 수면 중에도 자율 동작하여 작업을 완성하는 최적 아키텍처는 무엇인가?

---

## Web Facts

[FACT-1] OpenHands **Headless Mode** 공식 지원: `openhands --headless -t "task"` — UI 없이 스크립트 자동화 가능. (source: https://docs.openhands.dev/openhands/usage/run-openhands/headless-mode)

[FACT-2] **OpenHands CLI** 경량 바이너리: github.com/OpenHands/OpenHands-CLI — 단일 바이너리, 여러 머신/프로젝트에 설치 가능. (source: https://github.com/OpenHands/OpenHands-CLI)

[FACT-3] **GitHub Action 공식 지원**: `fix-me` 라벨 또는 `@openhands-agent` 멘션으로 자동 트리거, PR 자동 생성. (source: https://docs.openhands.dev/openhands/usage/run-openhands/github-action)

[FACT-4] **GitHub Resolver**: `.github/workflows/openhands-resolver.yml` 복사로 모든 레포에 독립 설치. PAT + LLM API 키만 필요. (source: https://openhands.dev/blog/open-source-coding-agents-in-your-github-fixing-your-issues)

[FACT-5] **Software Agent SDK** (2025-11): Python SDK로 에이전트 임베드, Docker/Kubernetes 배포, 멀티 LLM 라우팅. (source: https://arxiv.org/abs/2511.03690)

[FACT-6] **Daytona 통합**: zero-setup 인프라, 수천 개 병렬 에이전트. (source: https://openhands.daytona.io/)

[FACT-7] **알려진 문제**: 장시간 실행 시 context window 포화 → CondensationAction 무한루프. 세션 비활성 타임아웃으로 야간 작업 중단 사례 있음. (source: https://github.com/OpenHands/OpenHands/issues/8630)

[FACT-8] **비용**: Cloud 무료 티어(MiniMax 모델), Self-hosted는 LLM API 비용만. (source: https://openhands.dev/)

[FACT-9] **Workspace 격리**: Docker per-task + `WORKSPACE_MOUNT_PATH` 환경변수로 프로젝트별 마운트. (source: OpenHands Docker 설정)

[FACT-10] **REST API**: `POST /api/conversations` + `conversation_trigger: "gui"` 로 에이전트 루프 자동 시작, trajectory 폴링으로 완료 감지. (source: 현재 프로젝트 실험 결과)

---

## Multi-Lens Analysis

### Domain Expert (Lens 1)

**Insight 1 — GitHub Action이 야간 자율 작업의 가장 안정적인 트리거 레이어** [GROUNDED]
GitHub Actions는 인프라 관리 없이 `schedule: cron`과 이슈 이벤트를 제공한다. `openhands-resolver.yml` 하나로 레포별 독립 설치 완결.
- Steel-man: 무료 티어 월 2,000분 제한, 다수 레포 동시 실행 시 큐잉 발생.

**Insight 2 — Context 포화가 야간 장시간 작업의 핵심 위험** [GROUNDED]
FACT-7이 직접 확인한 실제 이슈. `max_iterations` 파라미터가 유일한 방어 수단.
50% 완료 상태에서 루프가 멈추면 코드베이스 오염 가능.

**Insight 3 — WORKSPACE_MOUNT_PATH + Docker per-task가 유일하게 안전한 격리** [GROUNDED]
프로젝트 A 에이전트가 프로젝트 B 파일에 접근하는 것을 파일시스템 레벨에서 차단.

**Insight 4 — 모델 티어링이 비용 관리 핵심** [REASONED]
단순 태스크(lint/typo) → MiniMax 무료, 기능 구현 → Sonnet, 아키텍처 → Opus.
단, 저비용 모델 성공률 데이터는 공개 벤치마크에 없음.

**Insight 5 — Software Agent SDK가 장기 최적 아키텍처** [GROUNDED]
GitHub 플랫폼 종속 없이 태스크 큐, 실패 재시도, 비용 추적을 직접 구현 가능.
2025-11 공개로 API 안정성은 미검증.

### Self-Critique (Lens 2)

- GitHub Action "안정적" 주장 수정: 컨텍스트 포화 문제는 GitHub Action에도 동일 적용. 복잡 태스크 제한 필수.
- Dirty state 처리 누락: uncommitted changes가 남은 상태에서 다음 에이전트가 실행되면 오염 환경 시작. rollback 메커니즘 필수.
- 보안 위험: PAT는 전체 레포 접근 권한 노출. GitHub Apps 방식이 더 안전.
- 비용 vs 성공률 충돌: MiniMax 무료 모델의 실제 OpenHands 성공률 미검증.

### Synthesis (Lens 3)

핵심 원칙: **트리거 레이어 + 실행 레이어 + 격리 레이어 + 실패 처리 레이어** 4층 구조.

---

## Final Conclusion

## OpenHands 전역 자율 에이전트 — 실용 설정 가이드

### 전체 아키텍처

```
[트리거]              [실행]                [격리]
GitHub cron/label →  OpenHands Headless → Docker per-task
로컬 cron         →  REST API 폴링     → WORKSPACE_MOUNT_PATH
                          ↓
[실패 처리]           [비용 관리]
dirty state 감지  →  모델 티어 라우팅
git stash/rollback →  월별 예산 cap
Slack 알림         →  토큰 추적
```

---

### 레이어 1: 프로젝트별 설정 격리

각 프로젝트 루트에 `.openhands/config.toml`:

```toml
# /home/jayone/Project/AutoCode/.openhands/config.toml
[core]
workspace_base = "/home/jayone/Project/AutoCode"
max_iterations = 40          # 컨텍스트 포화 방어 — 핵심
max_budget_per_task = 2.0    # USD cap

[llm]
model = "claude-sonnet-4-5"

[sandbox]
# 해당 프로젝트 디렉토리만 마운트 — 격리 보장
volumes = {"/home/jayone/Project/AutoCode" = "/workspace:rw"}
```

글로벌 기본값 `~/.openhands/config.toml`:

```toml
[core]
max_iterations = 30

[llm]
model = "minimax/MiniMax-M2.5"  # 기본 저비용
```

---

### 레이어 2: 자동화 트리거

#### 옵션 A: GitHub Action (인프라 관리 불필요 — 권장)

```yaml
# .github/workflows/openhands-resolver.yml
name: OpenHands Nightly
on:
  schedule:
    - cron: '0 14 * * *'    # 23:00 KST
  issues:
    types: [labeled]

jobs:
  resolve:
    if: |
      github.event_name == 'schedule' ||
      (github.event_name == 'issues' &&
       github.event.label.name == 'fix-me')
    runs-on: ubuntu-latest
    timeout-minutes: 60      # 컨텍스트 포화 방어
    steps:
      - uses: all-hands-ai/openhands-resolver@v0.9
        with:
          llm-model: "claude-sonnet-4-5"
          max-iterations: "40"
        env:
          GITHUB_TOKEN: ${{ secrets.OPENHANDS_PAT }}
          LLM_API_KEY: ${{ secrets.ANTHROPIC_API_KEY }}
```

각 레포에 복사. Secrets에 `OPENHANDS_PAT`, `ANTHROPIC_API_KEY` 설정.

#### 옵션 B: 로컬 cron + Headless (완전 제어)

```bash
# ~/.openhands/run-nightly.sh
#!/bin/bash
set -euo pipefail

PROJECTS=("/home/jayone/Project/AutoCode" "/home/jayone/Project/AgentNode")
TASKS_FILE="$HOME/.openhands/tasks.json"

for PROJECT in "${PROJECTS[@]}"; do
    NAME=$(basename "$PROJECT")
    TASK=$(jq -r ".\"$NAME\"" "$TASKS_FILE" 2>/dev/null || echo "")
    [ -z "$TASK" ] && continue

    cd "$PROJECT"

    # Dirty state 감지 — 이전 실행 오염 방지
    if ! git diff --quiet || ! git diff --staged --quiet; then
        git stash push -m "openhands-pre-$(date +%Y%m%d-%H%M%S)"
        echo "[WARN] $NAME: dirty state stashed"
    fi

    # 작업 브랜치 생성
    BRANCH="openhands/nightly-$(date +%Y%m%d)"
    git checkout -b "$BRANCH" 2>/dev/null || git checkout "$BRANCH"

    # Headless 실행
    WORKSPACE_MOUNT_PATH="$PROJECT" \
    OPENHANDS_CONFIG="$PROJECT/.openhands/config.toml" \
        openhands --headless \
        --task "$TASK" \
        --max-iterations 40 \
        2>&1 | tee "/tmp/oh-log-$NAME.log"

    # 결과 처리
    if git diff --quiet; then
        echo "[NO-CHANGE] $NAME"
    else
        git add -A
        git commit -m "feat(openhands): nightly $(date +%Y%m%d)"
        gh pr create --title "OpenHands nightly: $NAME $(date +%Y%m%d)" \
                     --base main --head "$BRANCH"
    fi
done
```

crontab 등록:
```bash
# crontab -e
0 23 * * * /home/jayone/.openhands/run-nightly.sh >> /var/log/oh-nightly.log 2>&1
```

---

### 레이어 3: 실패 처리 — Dirty State Rollback

```bash
# 실패 시 rollback
on_failure() {
    local PROJECT="$1"
    cd "$PROJECT"
    git checkout -- .          # uncommitted 변경 폐기
    git clean -fd              # 추적 안 되는 파일 제거
    git checkout main
    git branch -D "openhands/nightly-$(date +%Y%m%d)" 2>/dev/null || true
    # Slack 알림
    curl -s -X POST "$SLACK_WEBHOOK" \
        -d "{\"text\": \"OpenHands FAILED: $(basename $PROJECT)\"}"
}
trap 'on_failure "$PROJECT"' ERR
```

---

### 레이어 4: 비용 관리

```json
// ~/.openhands/tasks.json — 프로젝트별 태스크 + 모델 티어 정의
{
    "AutoCode": {
        "task": "Review open issues labeled fix-me and implement fixes. Focus on test failures. Create separate commits per fix. Do not touch .env files.",
        "model": "claude-haiku-3-5",
        "max_iterations": 40
    },
    "AgentNode": {
        "task": "Check TODO comments added in the last 7 days. Implement only if confidence is HIGH. Skip architectural decisions.",
        "model": "claude-sonnet-4-5",
        "max_iterations": 30
    }
}
```

모델 티어 가이드:
| 태스크 유형 | 모델 | 비용 |
|------------|------|------|
| lint/format/typo | MiniMax M2.5 | 무료 |
| 버그 수정 | claude-haiku-3-5 | 저 |
| 기능 구현 | claude-sonnet-4-5 | 중 |
| 아키텍처 | claude-opus-4-5 | 고 |

---

### 접근법별 권고

| 시나리오 | 권장 방식 |
|----------|-----------|
| GitHub 레포 중심, 관리 최소화 | GitHub Action + openhands-resolver |
| 로컬 완전 제어, 비용 최소화 | Headless cron + dirty state 체크 |
| 수십~수백 프로젝트 병렬 | Daytona 통합 |
| 커스텀 오케스트레이션 필요 | Software Agent SDK |

---

### 핵심 주의사항

1. **`max_iterations=40` 필수**: 설정 안 하면 컨텍스트 포화로 무한루프
2. **Dirty state 체크 필수**: `git diff --quiet` 로 실행 전 상태 확인
3. **PAT 대신 GitHub Apps 권장**: PAT는 전체 레포 접근 권한 노출 위험
4. **작업 브랜치 격리**: 에이전트 작업은 반드시 feature branch에서, main 직접 수정 금지
5. **첫 배포는 `max_iterations=5`로 테스트**: dirty state 시나리오 직접 검증 후 확장

### Remaining Uncertainties

- MiniMax M2.5의 실제 OpenHands 태스크 성공률 (벤치마크 미공개)
- Software Agent SDK API 안정성 (2025-11 공개, 6개월 미만)
- `openhands --headless --output-json` 정확한 스키마 (공식 문서 미검증)

---

## Sources

- [OpenHands Headless Mode](https://docs.openhands.dev/openhands/usage/run-openhands/headless-mode)
- [OpenHands GitHub Action](https://docs.openhands.dev/openhands/usage/run-openhands/github-action)
- [OpenHands GitHub Action Marketplace](https://github.com/marketplace/actions/openhands-ai-action)
- [OpenHands Software Agent SDK (arXiv)](https://arxiv.org/abs/2511.03690)
- [CondensationAction 무한루프 이슈](https://github.com/OpenHands/OpenHands/issues/8630)
- [OpenHands Daytona 통합](https://openhands.daytona.io/)
- [OpenHands CLI](https://github.com/OpenHands/OpenHands-CLI)

## Related
- [[projects/LiveCode/research/20260326-omc-live-skill-critique|20260326-omc-live-skill-critique]]
- [[projects/LiveCode/research/20260323-openhands-docker-permission-solution|20260323-openhands-docker-permission-solution]]
