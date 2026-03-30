# [expert-research-v2] OpenHands Docker 권한 노이즈 제거
**Date**: 2026-03-23  **Skill**: expert-research-v2

## Original Question
OpenHands + Docker 환경에서 자율 에이전트 실행 시 sudo/권한 요청 노이즈 없이 완전 자율로 실행하는 방법.

## Web Facts
- [FACT-1] SANDBOX_USER_ID=$(id -u) 전달 시 생성 파일 소유권이 호스트 사용자로 귀속 (github.com/OpenHands/OpenHands/issues/1822)
- [FACT-2] docker-compose.yml SANDBOX_USER_ID=1000 설정이 "forces non-root inside sandboxes" (interconnectd.com)
- [FACT-3] rootless Docker 환경에서는 SANDBOX_USER_ID 제거 필요 — 이중 매핑 충돌
- [FACT-4] Docker userns-remap: daemon.json 설정으로 컨테이너 root → 호스트 비특권 사용자 매핑 (docs.docker.com)
- [FACT-5] --user $(id -u):$(id -g) 플래그로 컨테이너 실행 UID 지정 가능

## Final Conclusion

### TIER 1 (즉시 적용)
```yaml
environment:
  - SANDBOX_USER_ID=${UID:-1000}
```
```bash
export UID=$(id -u) && docker compose up
```

### TIER 2 (시스템 수준, 1회 설정)
```bash
sudo tee /etc/docker/daemon.json <<'EOF'
{"userns-remap": "jayone"}
