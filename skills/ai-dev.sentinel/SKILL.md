---
name: ai-dev.sentinel
description: ai-dev 세션 상태를 저장하고 복원합니다. 컨텍스트 임계치 도달 시 자동 저장, "세션 저장", "세션 복원", "sentinel" 요청 시 활성화.
---

# Skill: ai-dev.sentinel

ai-dev 세션 상태를 sentinel 파일로 저장하고 복원합니다. 긴 워크플로우에서 컨텍스트 초과를 방지합니다.

---

## 목적

- 컨텍스트 임계치 도달 시 상태 자동 저장
- 새 세션에서 복원하여 이어서 실행
- Phase 전환/Task 완료 시 체크포인트 저장

---

## 명령어

### 저장 (Save)
```
/ai-dev.sentinel save [--ticket PK-XXXXX]
```
현재 세션 상태를 `~/.claude/sentinel/`에 저장

### 복원 (Restore)
```
/ai-dev.sentinel restore {session-id}
```
지정된 sentinel 파일에서 세션 복원

### 목록 (List)
```
/ai-dev.sentinel list [--ticket PK-XXXXX]
```
저장된 sentinel 파일 목록 표시

### 정리 (Cleanup)
```
/ai-dev.sentinel cleanup [--older-than 7d]
```
오래된 sentinel 파일 정리

---

## 실행 방법

### Save 프로세스 (실제 구현)

**명령어**: `/ai-dev.sentinel save [--ticket PK-XXXXX]`

```bash
## Step 1: 디렉토리 확인/생성
mkdir -p ~/.claude/sentinel

## Step 2: 현재 상태 수집

# 2.1 티켓 ID 추출 (대화에서 또는 --ticket 옵션)
TICKET_ID="PK-XXXXX"

# 2.2 TaskList로 현재 Task 상태 확인
TaskList() → completed_tasks, pending_tasks, current_task 추출

# 2.3 Git 상태 수집
git branch --show-current → branch
git log -1 --format="%h" → last_commit
git status --porcelain → uncommitted_changes

# 2.4 아티팩트 경로 확인
DOC_PATH="~/.claude/contexts/work/kidsnote/docs/ai-dev/{TICKET_ID}-*"
ls $DOC_PATH → analyze.md, spec.md, plan.md 존재 확인

## Step 3: JSON 파일 생성

TIMESTAMP=$(date +%Y-%m-%d-%H%M%S)
SESSION_ID="sentinel-${TIMESTAMP}"

# Write tool로 JSON 저장
Write(
  file_path: "~/.claude/sentinel/${SESSION_ID}.json",
  content: {JSON 구조}
)

## Step 4: 사용자에게 복원 명령어 안내
echo "복원: /ai-dev.sentinel restore ${SESSION_ID}"
```

### Restore 프로세스 (실제 구현)

**명령어**: `/ai-dev.sentinel restore {session-id}`

```bash
## Step 1: Sentinel 파일 읽기
Read("~/.claude/sentinel/{session-id}.json")

## Step 2: 필수 아티팩트 존재 확인
for artifact in [analyze.md, spec.md, plan.md]:
    if not exists(artifact):
        warn("⚠️ {artifact} 누락")

## Step 3: Git 상태 동기화
current_branch=$(git branch --show-current)
if current_branch != sentinel.git_state.branch:
    AskUserQuestion("브랜치 전환 필요: {branch}로 체크아웃?")
    if approved: git checkout {branch}

## Step 4: Task Chain 복원 (TaskCreate 사용)
for task in sentinel.task_state.completed_tasks:
    TaskCreate(subject: task.summary, ...)
    TaskUpdate(taskId: task.id, status: "completed")

TaskCreate(subject: sentinel.task_state.current_task.summary, ...)
TaskUpdate(taskId: current_task.id, status: "in_progress")

for task in sentinel.task_state.pending_tasks:
    TaskCreate(subject: task.summary, ...)
    # blockedBy 설정

## Step 5: 컨텍스트 요약 표시
echo "### 복원된 상태"
echo "현재 Phase: {current_phase}"
echo "현재 Task: {current_task}"
echo ""
echo "### 핵심 결정사항"
for decision in sentinel.context_summary.key_decisions:
    echo "- {decision}"
echo ""
echo "### 재개 지침"
echo sentinel.resume_instructions.summary
echo ""
echo "먼저 읽을 파일:"
for file in sentinel.resume_instructions.files_to_read_first:
    Read(file) # 컨텍스트에 로드

## Step 6: 재개 안내
echo "✅ 복원 완료. {current_task}부터 계속 진행합니다."
```

### List 프로세스 (실제 구현)

**명령어**: `/ai-dev.sentinel list [--ticket PK-XXXXX]`

```bash
## Step 1: Sentinel 파일 목록 조회
Glob("~/.claude/sentinel/sentinel-*.json")

## Step 2: 각 파일 파싱하여 요약 표시
for file in sentinel_files:
    Read(file)
    parse JSON
    extract: session_id, ticket_id, current_phase, current_task, timestamp

## Step 3: 테이블 형식으로 출력
| Session ID | Ticket | Phase | Task | 저장 시점 |
|------------|--------|-------|------|----------|
| sentinel-... | PK-... | impl | Task 2.3 | 3시간 전 |
```

### Cleanup 프로세스 (실제 구현)

**명령어**: `/ai-dev.sentinel cleanup [--older-than 7d]`

```bash
## Step 1: 오래된 파일 찾기
find ~/.claude/sentinel -name "sentinel-*.json" -mtime +7

## Step 2: 사용자 확인
AskUserQuestion("{N}개 파일 삭제?")

## Step 3: 삭제
if approved:
    rm {files}
```

---

## Sentinel 파일 구조

```json
{
  "version": "1.0",
  "session_id": "sentinel-2026-01-28-153000",
  "ticket_id": "PK-32398",
  "timestamp": "2026-01-28T15:30:00Z",

  "workflow_state": {
    "current_phase": "impl",
    "current_task_id": "Task 2.3",
    "phase_progress": {
      "analyze": "completed",
      "spec": "completed",
      "plan_check": "completed",
      "plan": "completed",
      "impl": "in_progress",
      "code_check": "pending",
      "work_check": "pending",
      "review": "pending",
      "pr": "pending"
    }
  },

  "task_state": {
    "completed_tasks": [
      {"id": "Task 1.1", "commit": "abc1234", "summary": "Entity 정의"},
      {"id": "Task 1.2", "commit": "def5678", "summary": "Repository 구현"}
    ],
    "current_task": {
      "id": "Task 2.3",
      "status": "in_progress",
      "progress": "SearchBar 레이아웃 완료, 바인딩 작업 중",
      "modified_files": [
        "Sources/Features/StudentList/Views/StudentListViewController.swift"
      ],
      "last_action": "SearchBar addSubview 및 constraints 추가"
    },
    "pending_tasks": [
      {"id": "Task 2.4", "summary": "검색 결과 표시"},
      {"id": "Task 3.1", "summary": "UI 통합 테스트"}
    ]
  },

  "artifacts": {
    "analyze_md": "~/.claude/contexts/work/kidsnote/docs/ai-dev/PK-32398-원생검색/analyze.md",
    "spec_md": "~/.claude/contexts/work/kidsnote/docs/ai-dev/PK-32398-원생검색/spec.md",
    "plan_md": "~/.claude/contexts/work/kidsnote/docs/ai-dev/PK-32398-원생검색/plan.md",
    "plan_check_report": "~/.claude/contexts/work/kidsnote/docs/ai-dev/PK-32398-원생검색/plan-check-report.md"
  },

  "git_state": {
    "branch": "feature/PK-32398-student-search",
    "base_branch": "develop",
    "last_commit": "jkl3456",
    "commit_message": "[PK-32398] feat(reactor): 검색 debounce 로직 추가",
    "uncommitted_changes": [
      "Sources/Features/StudentList/Views/StudentListViewController.swift"
    ]
  },

  "context_summary": {
    "key_decisions": [
      "SearchBar는 UISearchBar 대신 커스텀 뷰 사용 (디자인 일관성)",
      "Debounce 시간 300ms (사용자 확인됨)",
      "빈 결과는 인라인 메시지로 표시"
    ],
    "important_patterns": [
      "StudentListReactor에 searchQuery 액션 추가",
      "기존 filterStudents 메서드 활용"
    ],
    "caveats": [
      "isTimeLineMode 체크 필요 (추억보기 모드 충돌 방지)"
    ]
  },

  "resume_instructions": {
    "summary": "Task 2.3 'SearchBar 바인딩' 작업 중. 레이아웃 완료, RxSwift 바인딩 구현 필요.",
    "next_steps": [
      "1. searchBar.rx.text를 reactor.action에 바인딩",
      "2. debounce(300ms) 적용",
      "3. 빌드 테스트 후 커밋"
    ],
    "files_to_read_first": [
      "Sources/Features/StudentList/Views/StudentListViewController.swift",
      "Sources/Features/StudentList/Reactors/StudentListReactor.swift"
    ]
  }
}
```

---

## 자동 저장 트리거

다음 조건 중 하나라도 충족 시 자동 저장 권장:

| 트리거 | 조건 | 동작 |
|--------|------|------|
| **Phase 전환** | analyze→spec, spec→plan 등 | 자동 저장 |
| **Task 완료** | 각 Task 커밋 후 | 체크포인트 저장 |
| **명시적 요청** | "저장해줘", "세이브" | 즉시 저장 |
| **긴 대화** | 대화 턴 > 20 | 저장 권장 알림 |

---

## 출력 템플릿

### Save 출력

```markdown
## Sentinel 저장 완료

**Session ID**: sentinel-2026-01-28-153000
**Ticket**: PK-32398

### 현재 상태
- **Phase**: impl (3/8)
- **Task**: Task 2.3 (SearchBar 바인딩)
- **완료된 Task**: 4개
- **남은 Task**: 5개

### Git 상태
- **Branch**: feature/PK-32398-student-search
- **Last Commit**: jkl3456
- **Uncommitted**: 1개 파일

### 복원 명령어
```
/ai-dev.sentinel restore sentinel-2026-01-28-153000
```

저장 경로: `~/.claude/sentinel/sentinel-2026-01-28-153000.json`
```

### Restore 출력

```markdown
## Sentinel 복원

**Session ID**: sentinel-2026-01-28-153000
**Ticket**: PK-32398
**저장 시점**: 2026-01-28 15:30:00

---

### 복원된 상태

**현재 Phase**: impl
**현재 Task**: Task 2.3 (SearchBar 바인딩)

### 컨텍스트 요약

**핵심 결정사항**:
- SearchBar는 UISearchBar 대신 커스텀 뷰 사용
- Debounce 시간 300ms
- 빈 결과는 인라인 메시지

**주의사항**:
- isTimeLineMode 체크 필요

---

### 재개 지침

**현재 작업**: Task 2.3 'SearchBar 바인딩'
- 레이아웃 완료
- RxSwift 바인딩 구현 필요

**다음 단계**:
1. searchBar.rx.text를 reactor.action에 바인딩
2. debounce(300ms) 적용
3. 빌드 테스트 후 커밋

**먼저 읽을 파일**:
- StudentListViewController.swift
- StudentListReactor.swift

---

복원이 완료되었습니다. Task 2.3부터 계속 진행합니다.
```

### List 출력

```markdown
## Sentinel 파일 목록

| Session ID | Ticket | Phase | Task | 저장 시점 |
|------------|--------|-------|------|----------|
| sentinel-2026-01-28-153000 | PK-32398 | impl | Task 2.3 | 3시간 전 |
| sentinel-2026-01-27-102000 | PK-32398 | spec | - | 1일 전 |
| sentinel-2026-01-26-090000 | PK-32100 | pr | Task 4.1 | 2일 전 |

**복원**: `/ai-dev.sentinel restore {session-id}`
**정리**: `/ai-dev.sentinel cleanup --older-than 7d`
```

---

## 파일 경로

```
~/.claude/sentinel/
├── sentinel-2026-01-28-153000.json
├── sentinel-2026-01-27-102000.json
└── ...
```

---

## 연계 스킬

| 스킬 | 용도 |
|------|------|
| `/ai-dev` | 메인 워크플로우 (Sentinel 자동 연동) |
| `/ai-dev.impl` | Task 완료 시 체크포인트 저장 |

---

## 핵심 원리 (Reddit uhgrippa 패턴)

> "store state in an sentinel file then pick back up with a spawned subagent until all planned tasks in the execution loop are completed"

**Sentinel 패턴의 핵심:**
1. 컨텍스트 임계치 도달 시 상태를 파일에 저장
2. 새 세션에서 파일을 읽어 상태 복원
3. Task Chain이 모두 완료될 때까지 반복

**⚠️ 중요: 새 세션은 개발자가 직접 열어야 합니다**

Claude Code는 자체적으로 새 세션을 spawn할 수 없습니다.
컨텍스트 임계치 도달 시:
1. 자동으로 상태 저장 + 복원 명령어 안내
2. **개발자가 직접 새 터미널/세션 열기**
3. 복원 명령어 실행하여 이어서 진행

```
[세션 1 - 컨텍스트 임계치 도달]
⚠️ Sentinel 저장 완료
👉 새 세션에서 실행: /ai-dev.sentinel restore sentinel-xxx

[개발자가 직접 새 터미널 열기]

[세션 2]
$ claude
> /ai-dev.sentinel restore sentinel-xxx
→ 상태 복원 → 이어서 진행
```

**ai-dev과의 연동:**
- ai-dev --auto 실행 시 각 Task 완료마다 자동 저장
- 컨텍스트 70% 도달 시 자동 저장 + 복원 안내
- **개발자가 새 세션 열고** `/ai-dev.sentinel restore`로 이어서 진행

---

**Created:** 2026-01-28
**Updated:** 2026-01-28
**Version:** 2.0 (실제 동작하는 구현 추가)
