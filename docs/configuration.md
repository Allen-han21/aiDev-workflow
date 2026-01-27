# 설정 커스터마이징

AI-Dev 워크플로우를 프로젝트에 맞게 설정하는 방법입니다.

## 스킬 파일 수정

### 프로젝트 경로

`~/.claude/skills/ai-dev/SKILL.md`와 각 Phase 스킬에서 경로 수정:

```markdown
# 변경 전
~/Dev/Repo/my-ios-app

# 변경 후
~/Dev/Repo/your-actual-project-path
```

### JIRA 티켓 접두사

티켓 접두사 변경:

```markdown
# 변경 전
PROJ-XXXXX

# 변경 후
YOUR-XXXXX  # 예: TEAM-12345, APP-12345
```

### GitHub 저장소

GitHub URL 변경:

```markdown
# 변경 전
my-org/my-ios-app

# 변경 후
your-org/your-repo
```

## MCP 서버 설정

### Codex MCP

```json
{
  "mcpServers": {
    "codex": {
      "command": "codex-mcp",
      "args": ["--model", "gpt-4"]
    }
  }
}
```

### figma-ocaml MCP

```json
{
  "mcpServers": {
    "figma-ocaml": {
      "command": "figma-ocaml-mcp",
      "env": {
        "FIGMA_TOKEN": "figd_xxxxxxxxxxxx"
      }
    }
  }
}
```

### apple-docs MCP

```json
{
  "mcpServers": {
    "apple-docs": {
      "command": "apple-docs-mcp"
    }
  }
}
```

## 문서 저장 경로

기본 문서 저장 경로:
```
.claude/contexts/work/{project}/docs/ai-dev/{TICKET-description}/
├── analyze.md
├── spec.md
└── plan.md
```

경로 변경은 각 스킬의 SKILL.md에서 수정.

## 커밋 메시지 형식

기본 형식:
```
[PROJ-XXXXX] <Type>(<Scope>): <Subject>

<Body>
```

### Type 목록
- `feat`: 새 기능
- `fix`: 버그 수정
- `refactor`: 리팩토링
- `chore`: 설정 변경
- `docs`: 문서
- `test`: 테스트

### Scope 목록 (iOS 예시)
- `logic`: 비즈니스 로직
- `ui`: UI 관련
- `model`: 데이터 모델
- `networking`: 네트워크
- `build`: 빌드 설정
- `test`: 테스트

## 리뷰 설정

### CodeRabbit 통합

`ai-dev.review/SKILL.md`에서 CodeRabbit 설정 가능:
```bash
coderabbit review --plain -t all
```

### 린트 도구

iOS 프로젝트:
```bash
swiftlint lint --quiet
```

Android 프로젝트:
```bash
./gradlew lint
```

## 플랫폼별 설정

### iOS

- 빌드: `xcodebuild`
- 린트: `swiftlint`
- 테스트: `xcodebuild test`
- 시뮬레이터: `/xcode-run`

### Android

- 빌드: `./gradlew assembleDebug`
- 린트: `./gradlew lint`
- 테스트: `./gradlew test`
- 에뮬레이터: `adb`

## 크로스 체크 모드

### Codex 사용 (기본)
```bash
/ai-dev PROJ-123
```

### Claude만 사용
```bash
/ai-dev PROJ-123 --no-codex
```
- Codex 쿼터 절약
- Claude 멀티 관점 분석 활성화

### Extended Thinking
```bash
/ai-dev PROJ-123 --ultrathink
```
- 복잡한 문제에 권장
- `--no-codex`와 함께 사용 시 최고 품질

## 디버그 설정

### 테스트 로그 태그

기본: `[DEBUG]`

변경 시 `ai-dev.impl/SKILL.md` 수정:
```markdown
# 변경 전
[DEBUG]

# 변경 후
[YOUR-DEBUG-TAG]
```
