# 시작하기

AI-Dev 워크플로우 설치 및 설정 가이드입니다.

## 사전 요구사항

### 필수
- [Claude Code CLI](https://claude.ai/claude-code) 설치
- JIRA 접근 권한 (jira-* 스킬 필요)
- GitHub CLI (`gh`) 설치

### 선택
- Codex MCP - 크로스 체크 및 계획 생성
- figma-ocaml MCP - Figma 디자인 추출
- apple-docs MCP - Apple API 문서 참조

## 설치

### 방법 1: 자동 설치 (권장)

```bash
git clone https://github.com/YOUR_USERNAME/aiDev-workflow.git
cd aiDev-workflow
./scripts/install.sh
```

### 방법 2: 수동 설치

```bash
# 1. 저장소 클론
git clone https://github.com/YOUR_USERNAME/aiDev-workflow.git
cd aiDev-workflow

# 2. 스킬 파일 복사
cp -r skills/* ~/.claude/skills/

# 3. 설정 파일 생성 (선택)
cp config/config.example.yaml ~/.claude/skills/ai-dev/config.yaml
```

## 설정

### 프로젝트별 경로 설정

스킬 파일 내 경로를 프로젝트에 맞게 수정:

```bash
# 예: iOS 프로젝트 경로 설정
vi ~/.claude/skills/ai-dev/SKILL.md
# ~/Dev/Repo/my-ios-app → 실제 프로젝트 경로로 변경
```

### JIRA 설정

JIRA 스킬이 설치되어 있어야 합니다:
- `/jira-get` - 티켓 조회
- `/jira-update` - 티켓 업데이트

### MCP 서버 설정 (선택)

`~/.claude/mcp.json`에 MCP 서버 추가:

```json
{
  "mcpServers": {
    "codex": {
      "command": "codex-mcp"
    },
    "figma-ocaml": {
      "command": "figma-ocaml-mcp",
      "env": {
        "FIGMA_TOKEN": "your-figma-token"
      }
    },
    "apple-docs": {
      "command": "apple-docs-mcp"
    }
  }
}
```

## 첫 실행

```bash
# Claude Code 시작
claude

# 워크플로우 실행
/ai-dev PROJ-12345
```

## 문제 해결

### JIRA 티켓을 찾을 수 없음

- JIRA 접근 권한 확인
- 티켓 번호 형식 확인 (PROJ-12345)

### Codex MCP 연결 실패

- `--no-codex` 옵션으로 Claude만 사용
- MCP 서버 설정 확인

### Figma 디자인 추출 실패

- FIGMA_TOKEN 환경변수 확인
- Figma 파일 접근 권한 확인

## 다음 단계

- [워크플로우 개요](workflow-overview.md) - 전체 흐름 이해
- [설정 커스터마이징](configuration.md) - 프로젝트에 맞게 설정
