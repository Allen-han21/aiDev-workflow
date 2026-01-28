---
name: ai-dev
description: AI 협업 개발 스킬. TPL 분석 → Developer 구현 → 리뷰 → PR 생성. "개발해줘", "기능 구현", "버그 수정해줘", "ai-dev", "AI 협업" 요청 시 사용.
---

# Skill: ai-dev

AI와 협업하여 개발하는 통합 워크플로우입니다. 분석부터 PR 생성까지 전체 과정을 관리합니다.

**v5.0 신규**: Mega-skill 패턴 + 다단계 검증 + Sentinel 자동 관리

---

## 목적

- JIRA 티켓 기반 개발 자동화
- 일관된 워크플로우 제공
- 문서화 자동화 (analyze, spec, plan)
- **다단계 검증** (plan-check, code-check, work-check)
- Claude + Codex 크로스 체크를 통한 품질 향상
- **Sentinel 패턴으로 긴 워크플로우 지원**

## 사용 시점

- `/ai-dev PK-XXXXX` - 전체 워크플로우 시작
- `/ai-dev PK-XXXXX --auto` - 전체 자동화 (Mega-skill)
- `/ai-dev PK-XXXXX --figma https://...` - Figma 포함
- `/ai-dev help` - 사용 방법 표시

---

## Help (사용 방법)

`/ai-dev help` 실행 시 다음 내용을 표시합니다:

~~~markdown
## ai-dev v5.0 사용 방법

### 기본 명령어

```bash
# 전체 워크플로우 (단계별 확인)
/ai-dev PK-12345

# 전체 자동화 (Mega-skill)
/ai-dev PK-12345 --auto

# Figma 디자인 포함
/ai-dev PK-12345 --figma https://figma.com/design/xxx

# 빠른 개발 (검증 스킵)
/ai-dev PK-12345 --auto --skip-checks

# 특정 Phase부터 시작
/ai-dev PK-12345 --from impl

# 복잡한 문제 (최고 품질)
/ai-dev PK-12345 --no-codex --ultrathink
```

---

### 워크플로우 (9단계)

```
┌─────────────────────────────────────────────────────────────┐
│  Task 1: analyze     → JIRA + Figma + 코드 분석             │
│      ↓                                                      │
│  Task 2: spec        → Claude + Codex 크로스 체크           │
│      ↓                                                      │
│  Task 3: plan        → Codex MCP 계획 생성                  │
│      ↓                                                      │
│  Task 4: plan-check  → 5개 validators + devil's advocate ★  │
│      ↓                                                      │
│  Task 5: impl        → Task별 구현 + 로컬 커밋              │
│      ↓                                                      │
│  Task 6: code-check  → DRY/SOLID/Complexity 분석 ★          │
│      ↓                                                      │
│  Task 7: work-check  → 6개 bug checkers ★                   │
│      ↓                                                      │
│  Task 8: review      → 비즈니스 규칙 + 최종 판정            │
│      ↓                                                      │
│  Task 9: pr          → Push + GitHub PR 생성                │
└─────────────────────────────────────────────────────────────┘
```

---

### 개별 스킬 실행

```bash
/ai-dev.analyze PK-12345      # 분석
/ai-dev.spec PK-12345         # 스펙 정의
/ai-dev.plan PK-12345         # 구현 계획
/ai-dev.plan-check PK-12345   # 계획 검증 (5개 validators)
/ai-dev.impl PK-12345         # 코드 구현
/ai-dev.code-check PK-12345   # 품질 검사 (DRY/SOLID)
/ai-dev.work-check PK-12345   # 버그 검사 (6개 checkers)
/ai-dev.review PK-12345       # 리뷰 + 최종 판정
/ai-dev.pr PK-12345           # PR 생성
```

---

### Sentinel (세션 관리)

```bash
/ai-dev.sentinel save                    # 수동 저장
/ai-dev.sentinel list                    # 저장 목록
/ai-dev.sentinel restore {session-id}    # 복원
/ai-dev.sentinel cleanup --older-than 7d # 정리
```

**자동 저장 트리거:** Phase 전환, Task 완료, 대화 턴 > 20, "저장해줘"

---

### 옵션 정리

| 옵션 | 설명 |
|------|------|
| `--auto` | 전체 파이프라인 자동 실행 |
| `--figma URL` | Figma 디자인 포함 |
| `--from PHASE` | 특정 Phase부터 시작 |
| `--to PHASE` | 특정 Phase까지만 |
| `--skip-checks` | plan-check, code-check, work-check 스킵 |
| `--no-codex` | Codex MCP 비활성화 |
| `--ultrathink` | Extended thinking 활성화 |

---

### 검증 체커 (총 14개)

| Phase | 체커 | 역할 |
|-------|------|------|
| **plan-check** | completeness-checker | spec→plan 요구사항 누락 |
| | pattern-compliance | AGENTS.md 컨벤션 준수 |
| | feasibility-assessor | 기술적 실현 가능성 |
| | risk-assessor | 회귀/보안 위험 |
| | scope-discipline | gold-plating 감지 |
| | + devil's advocate | false positive 감소 |
| **code-check** | DRY Checker | 중복 코드 |
| | SOLID Checker | 설계 원칙 |
| | Complexity Analyzer | 복잡도 |
| **work-check** | Edge Case Hunter | 경계값 버그 |
| | Race Condition Detector | 동시성 버그 |
| | State Corruption Finder | 상태 오염 |
| | Memory Leak Hunter | 메모리 누수 |
| | Input Validation Checker | 입력 검증 |
| | Regression Detector | 회귀 버그 |

---

### 출력 파일

```
~/~/.claude/contexts/work/kidsnote/docs/ai-dev/{PK-xxxx}/
├── analyze.md              # Phase 0
├── spec.md                 # Phase 1
├── plan-check-report.md    # Phase 2.5 ★
├── plan.md                 # Phase 2
├── code-check-report.md    # Phase 3.5 ★
└── work-check-report.md    # Phase 3.8 ★
```
~~~

---

## 워크플로우 개요 (v5.0)

```
┌─────────────────────────────────────────────────────────────────────────┐
│                    ai-dev 워크플로우 v5.0 (Mega-skill)                   │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                         │
│  [입력] JIRA 티켓 번호 + Figma (선택)                                    │
│                                                                         │
│  ┌───────────────────────── TASK CHAIN ─────────────────────────┐      │
│  │                                                               │      │
│  │  Task 1: analyze [plan mode]                                 │      │
│  │  → JIRA 조회, Figma, 코드 분석 → analyze.md                   │      │
│  │      │                                                        │      │
│  │      ▼ [blockedBy: 1]                                        │      │
│  │  Task 2: spec [plan mode]                                    │      │
│  │  → Claude + Codex 크로스 체크 → spec.md                       │      │
│  │      │                                                        │      │
│  │      ▼ [blockedBy: 2]                                        │      │
│  │  Task 3: plan [plan mode]                                    │      │
│  │  → Codex MCP 계획 생성 + Claude 검증 → plan.md               │      │
│  │      │                                                        │      │
│  │      ▼ [blockedBy: 3]                                        │      │
│  │  Task 4: plan-check ★ [plan mode]                            │      │
│  │  → 5개 validators + devil's advocate → plan-check-report.md  │      │
│  │      │                                                        │      │
│  │      ▼ [blockedBy: 4] [plan mode 해제]                       │      │
│  │  Task 5: impl                                                 │      │
│  │  → Task별 구현 + 로컬 커밋 + 테스트                           │      │
│  │      │                                                        │      │
│  │      ▼ [blockedBy: 5]                                        │      │
│  │  Task 6: code-check ★ 신규                                   │      │
│  │  → DRY/SOLID/Complexity 분석 → code-check-report.md          │      │
│  │      │                                                        │      │
│  │      ▼ [blockedBy: 6]                                        │      │
│  │  Task 7: work-check ★ 신규                                   │      │
│  │  → 6개 병렬 bug checkers → work-check-report.md              │      │
│  │      │                                                        │      │
│  │      ▼ [blockedBy: 7]                                        │      │
│  │  Task 8: review                                               │      │
│  │  → 비즈니스 규칙 검증 + 최종 승인 판정                         │      │
│  │      │                                                        │      │
│  │      ▼ [blockedBy: 8] (승인 시)                              │      │
│  │  Task 9: pr                                                   │      │
│  │  → Push + GitHub PR 생성 → PR URL                            │      │
│  │                                                               │      │
│  └───────────────────────────────────────────────────────────────┘      │
│                                                                         │
│  [SENTINEL PATTERN]                                                     │
│  긴 대화 시 자동 저장 → 새 세션에서 복원 → 이어서 실행                   │
│                                                                         │
└─────────────────────────────────────────────────────────────────────────┘
```

---

## 신규 검증 스킬 (v5.0)

### ai-dev.plan-check (plan 작성 후 검증)

**5개 병렬 validators + devil's advocate로 계획 검증**

| Validator | 역할 |
|-----------|------|
| completeness-checker | spec→plan 요구사항 누락 검증 |
| pattern-compliance | AGENTS.md 컨벤션 준수 |
| feasibility-assessor | 기술적 실현 가능성 |
| risk-assessor | 회귀/보안 위험 평가 |
| scope-discipline | gold-plating/스코프 초과 감지 |

**Devil's Advocate**: 모든 findings 도전 → false positive 감소

### ai-dev.code-check (Phase 3.5)

**품질 전용 검증 (review에서 분리)**

- DRY Checker (중복 코드)
- SOLID Checker (설계 원칙)
- Complexity Analyzer (복잡도)

### ai-dev.work-check (Phase 3.8)

**6개 병렬 bug checkers**

- Edge Case Hunter
- Race Condition Detector
- State Corruption Finder
- Memory Leak Hunter
- Input Validation Checker
- Regression Detector

---

## 문서 저장 경로

```
~/~/.claude/contexts/work/kidsnote/docs/ai-dev/{PK-xxxx-개발내용}/
├── analyze.md              # Phase 0 출력
├── spec.md                 # Phase 1 출력
├── plan-check-report.md    # Phase 2.5 출력 ★ 신규
├── plan.md                 # Phase 2 출력
├── code-check-report.md    # Phase 3.5 출력 ★ 신규
└── work-check-report.md    # Phase 3.8 출력 ★ 신규
```

---

## 옵션

| 옵션 | 설명 | 적용 |
|------|------|------|
| `--auto` | 전체 파이프라인 자동 실행 (Mega-skill) | 전체 |
| `--figma URL` | Figma 디자인 포함 | analyze |
| `--from PHASE` | 특정 Phase부터 시작 | 전체 |
| `--to PHASE` | 특정 Phase까지만 | 전체 |
| `--skip-checks` | plan-check, code-check, work-check 스킵 | 전체 |
| `--no-codex` | Codex MCP 비활성화 | spec, plan |
| `--ultrathink` | Extended thinking 활성화 | spec, plan |

### 사용 예시

```bash
# 전체 워크플로우 (기본 - 단계별 확인)
/ai-dev PK-12345

# Mega-skill 자동화 (확인 없이 전체 실행)
/ai-dev PK-12345 --auto

# 빠른 개발 (검증 스킵)
/ai-dev PK-12345 --auto --skip-checks

# Figma 포함
/ai-dev PK-12345 --figma https://figma.com/design/xxx

# 구현부터 시작 (이미 계획이 있을 때)
/ai-dev PK-12345 --from impl

# 복잡한 문제 (최고 품질)
/ai-dev PK-12345 --no-codex --ultrathink
```

---

## Sentinel 연동 (긴 워크플로우 지원)

긴 대화로 컨텍스트 임계치에 도달하면:

1. **자동 저장**: 현재 상태를 sentinel 파일에 저장
2. **새 세션 스폰**: 복원 명령어 안내
3. **이어서 실행**: 중단된 Task부터 계속

### 자동 저장 트리거

| 트리거 | 조건 |
|--------|------|
| Phase 전환 | analyze→spec, spec→plan 등 |
| Task 완료 | 각 Task 커밋 후 |
| 명시적 요청 | "저장해줘", "세이브" |
| 긴 대화 | 대화 턴 > 20 |

### 복원

```bash
# 저장된 세션 목록
/ai-dev.sentinel list

# 세션 복원
/ai-dev.sentinel restore sentinel-2026-01-28-153000
```

---

## Phase별 상세

### Phase 0: ai-dev.analyze

**모드**: plan mode

**입력**: JIRA 티켓 번호, Figma URL (선택)

**프로세스**:
1. JIRA 티켓 조회 (본문 + 댓글)
2. Figma URL 자동 감지 → figma-ocaml MCP로 디자인 추출
3. Explore 에이전트로 iOS 코드베이스 탐색
4. Android 코드 참조
5. 엣지 케이스 식별
6. 확인 필요 사항 AskUserQuestion

**출력**: `analyze.md`

### Phase 1: ai-dev.spec

**모드**: plan mode

**입력**: analyze.md

**프로세스**:
1. 모델 최적화 질문 생성
2. Claude + Codex 병렬 분석
3. 크로스 체크 (상호 검토)
4. 종합 및 사용자 승인

**출력**: `spec.md`

### Phase 2: ai-dev.plan

**모드**: plan mode

**입력**: spec.md

**프로세스**:
1. Codex MCP로 계획 생성
2. Claude 검증 (AGENTS.md 준수)
3. 사용자 검토

**출력**: `plan.md`

### Phase 2.5: ai-dev.plan-check ★ (plan 검증)

**모드**: plan mode

**입력**: spec.md, plan.md

**프로세스**:
1. 5개 validators 병렬 실행
2. Findings 집계 (P0-P3)
3. Devil's advocate 도전
4. 리포트 생성 및 판정
5. P0 발견 시 plan.md 수정 후 재검증

**출력**: `plan-check-report.md`

### Phase 3: ai-dev.impl

**모드**: plan mode 해제

**입력**: plan.md

**프로세스**:
```
for each Task in plan.md:
    1. Task 상세 확인
    2. 의존성 Task 완료 확인
    3. 코드 구현
    4. 빌드 검증
    5. 테스트 (Unit Test 또는 [allen-test] 로그)
    6. 로컬 커밋
    7. plan.md 업데이트
```

**출력**: 소스 코드 + 로컬 커밋

### Phase 3.5: ai-dev.code-check ★ 신규

**입력**: 구현 완료된 코드

**프로세스**:
1. 정적 분석 (SwiftLint, Build)
2. 품질 분석 (DRY, SOLID, Complexity) - 병렬 3개
3. 문서화 검증
4. 리포트 생성

**출력**: `code-check-report.md`

### Phase 3.8: ai-dev.work-check ★ 신규

**입력**: 구현 완료된 코드 + spec.md

**프로세스**:
1. 6개 bug checkers 병렬 실행
2. Bug triage (심각도 분류)
3. 재현 시나리오 작성
4. 리포트 생성

**출력**: `work-check-report.md`

### Phase 4: ai-dev.review

**입력**: code-check-report.md, work-check-report.md, 변경된 코드

**프로세스**:
1. 자동 검증 (린트)
2. 비즈니스 규칙 검증
3. 최종 승인/변경요청 판정

**출력**: 리뷰 결과

### Phase 5: ai-dev.pr

**입력**: 승인된 코드

**프로세스**:
1. Push
2. GitHub PR 생성

**출력**: PR URL

---

## 예제: Mega-skill 자동화

```
User: /ai-dev PK-32398 --auto

Claude: [ai-dev 활성화 - Mega-skill 모드]

Task Chain 생성됨 (9개 Task):
  1. analyze [pending]
  2. spec [blocked by 1]
  3. plan [blocked by 2]
  4. plan-check [blocked by 3]
  5. impl [blocked by 4]
  6. code-check [blocked by 5]
  7. work-check [blocked by 6]
  8. review [blocked by 7]
  9. pr [blocked by 8]

===== Task 1: analyze 시작 =====
JIRA 조회 중... PK-32398: 원생 검색 기능
[분석 진행]
✅ Task 1 완료 - analyze.md 저장됨

===== Task 2: spec 시작 =====
Claude + Codex 병렬 분석 중...
✅ Task 2 완료 - spec.md 저장됨

===== Task 3: plan 시작 =====
Codex MCP로 계획 생성 중...
✅ Task 3 완료 - plan.md 저장됨

===== Task 4: plan-check 시작 =====
5개 validators 병렬 실행 중...
  - completeness-checker ✅
  - pattern-compliance ✅
  - feasibility-assessor ✅
  - risk-assessor ✅
  - scope-discipline ✅
Devil's advocate 실행 중...
✅ Task 4 완료 - plan-check-report.md 저장됨

===== Task 5: impl 시작 =====
[Task별 구현 진행]
...

⚠️ 컨텍스트 70% 도달 - Sentinel 자동 저장
Session ID: sentinel-2026-01-28-153000

복원 명령어:
/ai-dev.sentinel restore sentinel-2026-01-28-153000
```

---

## 개별 Phase 실행

```bash
/ai-dev.analyze PK-12345     # Phase 0
/ai-dev.spec PK-12345        # Phase 1
/ai-dev.plan PK-12345        # Phase 2
/ai-dev.plan-check PK-12345  # Phase 2.5 ★ (plan 검증)
/ai-dev.impl PK-12345        # Phase 3
/ai-dev.code-check PK-12345  # Phase 3.5 ★ 신규
/ai-dev.work-check PK-12345  # Phase 3.8 ★ 신규
/ai-dev.review PK-12345      # Phase 4
/ai-dev.pr PK-12345          # Phase 5
```

---

## 연계 스킬

| 스킬 | 용도 |
|------|------|
| `/ai-dev.sentinel` | 세션 저장/복원 |
| `/jira-get` | JIRA 티켓 조회 |
| `/figma-design-spec` | Figma 디자인 분석 |
| `/codex-hotfix` | 리뷰 이슈 빠른 수정 |

---

## 주의사항

- Phase 0~4는 plan mode (분석/설계 전용)
- Phase 5부터 plan mode 해제 (코드 수정 가능)
- 각 Phase는 이전 Phase 출력에 의존
- `--auto` 모드에서도 Critical 이슈 발견 시 중단
- Sentinel 자동 저장으로 긴 워크플로우 지원

---

## 실행 방법 (Mega-skill 구현)

### --auto 모드: TaskCreate로 Task Chain 생성

`/ai-dev PK-XXXXX --auto` 실행 시 다음과 같이 Task Chain을 생성합니다:

```
## Step 1: Task Chain 생성 (단일 메시지에서 9개 Task 생성)

TaskCreate({
  subject: "1. analyze - JIRA/Figma/코드 분석",
  description: "JIRA 티켓 조회, Figma 디자인 추출, 코드베이스 탐색",
  activeForm: "코드베이스 분석 중"
})
→ task_id: "1"

TaskCreate({
  subject: "2. spec - 스펙 확정",
  description: "Claude + Codex 크로스 체크로 스펙 확정",
  activeForm: "스펙 정의 중"
})
→ task_id: "2"
TaskUpdate({ taskId: "2", addBlockedBy: ["1"] })

TaskCreate({
  subject: "3. plan - 구현 계획 수립",
  description: "Codex MCP로 계획 생성 + Claude 검증",
  activeForm: "구현 계획 수립 중"
})
→ task_id: "3"
TaskUpdate({ taskId: "3", addBlockedBy: ["2"] })

TaskCreate({
  subject: "4. plan-check - 계획 검증",
  description: "5개 validators + devil's advocate로 계획 검증",
  activeForm: "계획 검증 중"
})
→ task_id: "4"
TaskUpdate({ taskId: "4", addBlockedBy: ["3"] })

TaskCreate({
  subject: "5. impl - 코드 구현",
  description: "plan.md 기반 Task별 구현 + 로컬 커밋",
  activeForm: "코드 구현 중"
})
→ task_id: "5"
TaskUpdate({ taskId: "5", addBlockedBy: ["4"] })

TaskCreate({
  subject: "6. code-check - 품질 검사",
  description: "DRY/SOLID/Complexity 분석",
  activeForm: "품질 검사 중"
})
→ task_id: "6"
TaskUpdate({ taskId: "6", addBlockedBy: ["5"] })

TaskCreate({
  subject: "7. work-check - 버그 검사",
  description: "6개 병렬 bug checkers 실행",
  activeForm: "버그 검사 중"
})
→ task_id: "7"
TaskUpdate({ taskId: "7", addBlockedBy: ["6"] })

TaskCreate({
  subject: "8. review - 코드 리뷰",
  description: "비즈니스 규칙 검증 + 최종 승인 판정",
  activeForm: "코드 리뷰 중"
})
→ task_id: "8"
TaskUpdate({ taskId: "8", addBlockedBy: ["7"] })

TaskCreate({
  subject: "9. pr - PR 생성",
  description: "Push + GitHub PR 생성",
  activeForm: "PR 생성 중"
})
→ task_id: "9"
TaskUpdate({ taskId: "9", addBlockedBy: ["8"] })
```

### Step 2: Task 순차 실행

```
TaskList() → 실행 가능한 Task 확인 (blockedBy가 비어있거나 완료된 Task)

for each unblocked task:
    TaskUpdate({ taskId, status: "in_progress" })

    # 해당 스킬 실행
    switch task.subject:
        case "analyze": /ai-dev.analyze 실행
        case "spec": /ai-dev.spec 실행
        case "plan": /ai-dev.plan 실행
        case "plan-check": /ai-dev.plan-check 실행
        case "impl": /ai-dev.impl 실행
        case "code-check": /ai-dev.code-check 실행
        case "work-check": /ai-dev.work-check 실행
        case "review": /ai-dev.review 실행
        case "pr": /ai-dev.pr 실행

    TaskUpdate({ taskId, status: "completed" })

    # Sentinel 체크포인트 저장
    /ai-dev.sentinel save --ticket {TICKET_ID}
```

### Step 3: Sentinel 자동 저장 트리거

각 Task 완료 시 자동으로 상태를 저장합니다:

```
if task.status == "completed":
    sentinel_save({
        ticket_id: TICKET_ID,
        current_phase: task.subject,
        completed_tasks: TaskList().filter(t => t.status == "completed"),
        pending_tasks: TaskList().filter(t => t.status == "pending")
    })
```

### Step 4: 컨텍스트 임계치 도달 시

대화가 길어져 컨텍스트 70%에 도달하면:

```
1. 현재 상태 자동 저장 (/ai-dev.sentinel save)
2. 사용자에게 안내:

   ⚠️ 컨텍스트 임계치 도달

   Session ID: sentinel-{timestamp}
   현재 진행: Task {N} ({phase})

   👉 새 터미널을 열고 다음 명령어를 실행하세요:
   $ claude
   > /ai-dev.sentinel restore {session-id}
```

**⚠️ 중요**: Claude Code는 자체적으로 새 세션을 spawn할 수 없습니다.
개발자가 직접 새 터미널을 열고 복원 명령어를 실행해야 합니다.

---

**Created:** 2026-01-23
**Updated:** 2026-01-28
**Version:** 5.1 (Mega-skill 실행 방법 + Task Chain 구현 추가)
