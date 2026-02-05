---
name: ai-dev.resolve-conversation
description: 내 PR의 미해결 리뷰 코멘트를 분석하고 반영(ACCEPT)/논의(DISCUSS)/반박(DISMISS) 판정 후 응답 초안을 생성합니다. "코멘트 처리", "리뷰 응답", "resolve", "코멘트 반박", "미해결 코멘트" 요청 시 활성화.
---

# Skill: ai-dev.resolve-conversation

내 PR에 달린 미해결 리뷰 코멘트를 분석하여 **반영/논의/반박** 판정 후 GitHub 응답 초안을 생성합니다.

---

## 목적

- 내 PR의 미해결 리뷰 코멘트 자동 수집 (coderabbitai 제외)
- 각 코멘트의 코드 컨텍스트 분석
- **ACCEPT** (반영) / **DISCUSS** (논의) / **DISMISS** (반박) 3단계 판정
- GitHub에 달 응답 초안 생성
- 선택적으로 자동 응답 게시 및 코드 수정

---

## 입력 (선행 조건)

| 항목 | 필수 | 설명 |
|------|------|------|
| GitHub 인증 | ✅ | `gh auth` 완료 |
| PR 번호 | ⭕ | 미지정 시 현재 브랜치 PR 자동 감지 |

---

## 사용 시점

- `/ai-dev.resolve-conversation` - 현재 브랜치 PR의 미해결 코멘트 처리
- `/ai-dev.resolve-conversation --pr 7890` - 특정 PR 지정
- `/ai-dev.resolve-conversation --all` - 내 모든 열린 PR 조회
- 다른 팀원으로부터 리뷰 코멘트를 받았을 때

---

## 워크플로우

```
┌─────────────────────────────────────────────────────────────────┐
│              ai-dev.resolve-conversation 워크플로우               │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  [Step 0] PR 미해결 코멘트 수집                                   │
│  gh api graphQL → reviewThreads (isResolved: false)            │
│  필터: coderabbitai 제외, 내 코멘트 제외                          │
│                                                                 │
│  [Step 1] 코멘트별 분석 (병렬)                                    │
│  ┌──────────────┬──────────────┬──────────────┐                │
│  │ Comment #1   │ Comment #2   │ Comment #N   │                │
│  │ • 파일 읽기   │ • 파일 읽기   │ • 파일 읽기   │                │
│  │ • 컨텍스트    │ • 컨텍스트    │ • 컨텍스트    │                │
│  │ • 타입 분류   │ • 타입 분류   │ • 타입 분류   │                │
│  └──────┬───────┴──────┬───────┴──────┬───────┘                │
│         └──────────────┼──────────────┘                        │
│                        ▼                                       │
│  [Step 2] 3단계 판정                                             │
│  ┌────────────┬────────────┬────────────┐                      │
│  │  ACCEPT    │  DISCUSS   │  DISMISS   │                      │
│  │ 타당, 수정  │ 추가 논의   │ 반박 가능   │                      │
│  └────────────┴────────────┴────────────┘                      │
│                        ▼                                       │
│  [Step 3] 응답 초안 생성                                         │
│  ACCEPT → 수정 방향 + diff                                       │
│  DISCUSS → 명확화 질문                                           │
│  DISMISS → 논리적 반박 이유                                       │
│                        ▼                                       │
│  [Step 4] 사용자 검토                                            │
│  AskUserQuestion으로 각 판정 확인                                │
│                        ▼                                       │
│  [Step 5 - 선택] 자동 처리                                       │
│  --auto-reply → 응답 게시                                        │
│  --auto-fix → 코드 수정 + 커밋                                   │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

---

## Step 0: PR 미해결 코멘트 수집

### GraphQL 쿼리

```bash
gh api graphql -f query='
query($owner: String!, $repo: String!, $pr: Int!) {
  repository(owner: $owner, name: $repo) {
    pullRequest(number: $pr) {
      number
      title
      url
      author { login }
      reviewThreads(first: 50) {
        nodes {
          isResolved
          comments(first: 10) {
            nodes {
              id
              author { login }
              body
              path
              line
              createdAt
            }
          }
        }
      }
    }
  }
}'
```

### 필터링 조건

```
미해결 스레드:
  - isResolved == false

제외 대상:
  - author.login == "coderabbitai"
  - author.login == {PR작성자} (본인 코멘트)
```

### 출력

```markdown
## Step 0: 미해결 코멘트 수집

**PR**: #{PR번호} - {PR 제목}
**미해결 코멘트**: N개 (coderabbitai 제외)

| # | 리뷰어 | 파일 | 라인 | 생성일 |
|---|--------|------|------|--------|
| 1 | @{username} | {path} | {line} | {date} |
```

---

## Step 1: 코멘트별 분석

각 코멘트에 대해 병렬로 분석 수행:

### 1.1 코드 컨텍스트 로드

```bash
# 해당 파일의 라인 컨텍스트 읽기
Read({path}, offset: {line - 15}, limit: 30)
```

### 1.2 코멘트 타입 분류

| 타입 | 설명 | 예시 |
|------|------|------|
| BUG | 버그 지적 | "이 조건에서 크래시 발생" |
| STYLE | 코딩 스타일 | "네이밍 컨벤션", "포맷팅" |
| DESIGN | 설계 제안 | "이 로직은 분리하는게..." |
| QUESTION | 질문 | "왜 이렇게 구현했나요?" |
| SUGGESTION | 개선 제안 | "~하면 더 좋을 것 같습니다" |

### 1.3 코멘트 의도 분석

```markdown
### 코멘트 분석: #{번호}

**타입**: {BUG/STYLE/DESIGN/QUESTION/SUGGESTION}

**지적 내용**:
{무엇을 지적하는가}

**지적 이유**:
{왜 문제라고 생각하는가}

**제안 대안**:
{리뷰어가 제안하는 대안이 있는가}
```

---

## Step 2: 3단계 판정

### 판정 기준

| 판정 | 기준 | 액션 |
|------|------|------|
| **ACCEPT** | 타당한 지적, 수정 필요 | 코드 수정 방향 제시 |
| **DISCUSS** | 추가 논의 필요 | 명확화 질문 생성 |
| **DISMISS** | 반박 가능 | 논리적 반박 이유 작성 |

### 판정 플로우

```
1. 코멘트가 지적하는 문제가 실제로 존재하는가?
   ├─ 존재하지 않음 → DISMISS (사실 오류)
   └─ 존재 → 2단계

2. 지적된 문제가 수정이 필요한 수준인가?
   ├─ AGENTS.md 필수 규칙 위반 → ACCEPT
   ├─ 버그/크래시 가능성 → ACCEPT
   ├─ 트레이드오프 존재 → DISCUSS
   └─ 선호도/스타일 차이 → DISCUSS or DISMISS

3. 수정 시 득/실 분석
   ├─ 득 > 실 → ACCEPT
   ├─ 득 = 실 → DISCUSS (트레이드오프 설명)
   └─ 득 < 실 → DISMISS (이유 명시)
```

### 판정 예시

**ACCEPT 조건**:
- AGENTS.md 명시된 규칙 위반 (타입 명시, guard문 개행 등)
- 실제 버그 또는 크래시 가능성
- 성능 저하 명확

**DISCUSS 조건**:
- 의도가 불명확하여 추가 설명 필요
- 트레이드오프 존재 (예: 간결함 vs 명확함)
- 설계 방향 논의 필요

**DISMISS 조건**:
- 이미 처리된 이슈 (다른 곳에서 해결)
- 의도적 설계 선택 (문서화된 이유)
- 컨텍스트 오해 (리뷰어가 전체 맥락 미파악)

---

## Step 3: 응답 초안 생성

### ACCEPT 응답 템플릿

```markdown
좋은 지적 감사합니다! 수정하겠습니다.

**수정 방향**:
{수정 내용 요약}

**변경 코드**:
```diff
- 기존 코드
+ 수정 코드
```
```

### DISCUSS 응답 템플릿

```markdown
의견 감사합니다. 한 가지 확인하고 싶은 부분이 있습니다.

{질문 내용}

현재 이렇게 구현한 이유는 {이유}입니다.
{제안 방향}대로 변경하면 {트레이드오프}가 발생할 수 있어서 추가 논의가 필요할 것 같습니다.
```

### DISMISS 응답 템플릿

```markdown
검토해주셔서 감사합니다!

이 부분은 다음과 같은 이유로 현재 구현을 유지하려 합니다:

1. **{이유 1}**
   {상세 설명}

2. **{이유 2}** (있으면)
   {상세 설명}

{관련 코드나 문서 참조가 있으면 추가}

혹시 제가 놓친 부분이 있다면 말씀해주세요!
```

---

## Step 4: 사용자 검토

각 판정에 대해 사용자 확인:

```
AskUserQuestion([
  {
    question: "코멘트 #1에 대한 판정이 맞나요?",
    header: "[ACCEPT] 타입 명시 규칙 위반",
    options: [
      { label: "동의 - 수정 진행", description: "코멘트 반영 및 코드 수정" },
      { label: "DISCUSS로 변경", description: "추가 논의 필요" },
      { label: "DISMISS로 변경", description: "반박하고 싶음" }
    ],
    multiSelect: false
  }
])
```

---

## Step 5: 자동 처리 (선택)

### --auto-reply: 응답 게시

```bash
# GitHub PR 코멘트 답글 달기
gh api \
  repos/{owner}/{repo}/pulls/{pr}/comments/{comment_id}/replies \
  -f body='{응답 내용}'
```

### --auto-fix: 코드 수정

ACCEPT 판정된 항목에 대해:

```bash
# 1. 코드 수정 (Edit 도구 사용)
Edit({path}, old_string: "{기존}", new_string: "{수정}")

# 2. 커밋
git add {파일들}
git commit -m "[{TICKET_ID}] fix(review): {수정 내용 요약}"

# 3. Push
git push
```

---

## 출력 템플릿

```markdown
# PR #{PR번호} 리뷰 코멘트 분석

**분석일**: YYYY-MM-DD HH:MM
**PR**: #{PR번호} - {PR 제목}
**URL**: {PR URL}
**미해결 코멘트**: N개 (coderabbitai 제외)

---

## 요약

| 판정 | 개수 | 설명 |
|------|------|------|
| ACCEPT | N | 수정 필요 |
| DISCUSS | N | 추가 논의 |
| DISMISS | N | 반박 가능 |

---

## 코멘트 분석

### [ACCEPT] #1. {코멘트 요약}

**리뷰어**: @{username}
**파일**: `{path}:{line}`
**타입**: BUG / STYLE / DESIGN / QUESTION / SUGGESTION

**원본 코멘트**:
> {코멘트 원문}

**코드 컨텍스트**:
```swift
// {파일}:{라인}
{해당 코드 스니펫}
```

**분석**:
{왜 이 코멘트가 타당한지 분석}

**판정 근거**:
- {근거 1}
- {근거 2}

**수정 방향**:
```diff
- 기존 코드
+ 수정 코드
```

**응답 초안**:
```
{GitHub에 달 응답 초안}
```

---

### [DISCUSS] #2. {코멘트 요약}

**리뷰어**: @{username}
**파일**: `{path}:{line}`
**타입**: QUESTION

**원본 코멘트**:
> {코멘트 원문}

**분석**:
{추가 논의가 필요한 이유}

**판정 근거**:
- {트레이드오프 설명}

**응답 초안**:
```
{명확화 질문 응답}
```

---

### [DISMISS] #3. {코멘트 요약}

**리뷰어**: @{username}
**파일**: `{path}:{line}`
**타입**: STYLE

**원본 코멘트**:
> {코멘트 원문}

**분석**:
{왜 이 코멘트를 반박할 수 있는지 분석}

**판정 근거**:
- {반박 근거 1}
- {반박 근거 2}

**응답 초안**:
```
{정중하고 논리적인 반박 응답}
```

---

## 액션 아이템

### 수정 필요 (ACCEPT)
- [ ] #{코멘트ID}: {수정 내용 요약}

### 논의 필요 (DISCUSS)
- [ ] #{코멘트ID}: {논의 주제}

### 응답만 필요 (DISMISS)
- [ ] #{코멘트ID}: {응답 요약}

---

## 다음 단계

- ACCEPT 항목 코드 수정: `/codex-hotfix` 또는 수동 수정
- 응답 게시: `--auto-reply` 옵션 또는 GitHub에서 수동
- PR 업데이트: `/ai-dev.pr` 로 커밋 push

---

*Analyzed by ai-dev.resolve-conversation v1.0*
```

---

## 옵션

| 옵션 | 설명 | 예시 |
|------|------|------|
| `--pr {번호}` | PR 번호 지정 | `--pr 7890` |
| `--all` | 내 모든 열린 PR의 미해결 코멘트 조회 | |
| `--auto-reply` | 응답 자동 게시 (사용자 확인 후) | |
| `--auto-fix` | ACCEPT 항목 자동 수정 + 커밋 | |
| `--reviewer {이름}` | 특정 리뷰어 코멘트만 필터 | `--reviewer @senior-dev` |
| `--type {타입}` | 특정 타입만 필터 | `--type BUG,DESIGN` |

### 사용 예시

```bash
# 기본 사용 (현재 브랜치 PR)
/ai-dev.resolve-conversation

# PR 번호 지정
/ai-dev.resolve-conversation --pr 7890

# 모든 내 PR 조회
/ai-dev.resolve-conversation --all

# 응답만 자동 게시 (코드 수정 제외)
/ai-dev.resolve-conversation --pr 7890 --auto-reply

# 전체 자동화 (응답 + 코드 수정)
/ai-dev.resolve-conversation --pr 7890 --auto-reply --auto-fix

# 특정 리뷰어 코멘트만
/ai-dev.resolve-conversation --pr 7890 --reviewer @tech-lead

# 버그와 설계 관련 코멘트만
/ai-dev.resolve-conversation --pr 7890 --type BUG,DESIGN
```

---

## 예제

### 예제 1: 기본 사용

**User**:
```
/ai-dev.resolve-conversation
```

**Claude**:
```markdown
# PR #7361 리뷰 코멘트 분석

**분석일**: 2026-01-29 14:30
**PR**: #7361 - [PK-32445] 학부모 대상 추억보기 스킴(moments) 추가
**미해결 코멘트**: 1개

---

## 요약

| 판정 | 개수 |
|------|------|
| DISCUSS | 1 |

---

## 코멘트 분석

### [DISCUSS] #1. 체험 계정 처리 의도

**리뷰어**: @qazqaz1000
**파일**: `MainCoordinator.swift:123`
**타입**: QUESTION

**원본 코멘트**:
> [질문] 체험 계정 처리 의도 확인
> 기존 `setMoments` 함수에서는 `isTrialMode` 체크가 없는데, 새로운 `handleMomentsScheme`에서는 체험 계정을 제외하고 있습니다.
> 이는 의도된 차이인가요?

**코드 컨텍스트**:
```swift
// MainCoordinator.swift:120-130
func handleMomentsScheme(_ params: [String: String]) {
    guard !UserManager.shared.isTrialMode else { return }  // 체험 계정 제외
    // ...
}
```

**분석**:
리뷰어가 기존 함수와 새 함수의 일관성에 대해 질문하고 있습니다.
실제로 `isTrialMode` 체크는 CRM 마케팅 대상에서 체험 계정을 제외하려는 의도적 설계입니다.

**판정 근거**:
- 의도된 설계이지만 리뷰어에게 설명이 필요
- 기존 함수와의 차이점 명확화 필요

**응답 초안**:
```
좋은 질문 감사합니다!

네, 의도된 차이입니다. `handleMomentsScheme`은 CRM 마케팅 딥링크 용도로,
체험 계정 사용자는 마케팅 대상에서 제외하려는 기획 의도가 있습니다.

기존 `setMoments`, `reportMemories`, `albumMemories`는 앱 내부 네비게이션 용도라
체험 계정도 접근 가능하게 되어 있습니다.

혼동을 줄이기 위해 주석을 추가하겠습니다!
```

---

## 다음 단계

판정을 검토하시겠습니까?
```

**Claude (AskUserQuestion)**:
```
코멘트 #1에 대한 판정이 맞나요?
- [DISCUSS] 동의 - 응답 달기 (추천)
- ACCEPT로 변경 - 코드 수정 필요
- DISMISS로 변경 - 더 강하게 반박
```

### 예제 2: 모든 PR 조회

**User**:
```
/ai-dev.resolve-conversation --all
```

**Claude**:
```markdown
# 내 PR 미해결 코멘트 요약

**조회일**: 2026-01-29 14:30
**열린 PR**: 7개
**미해결 코멘트 있는 PR**: 3개

---

## PR별 요약

| PR | 제목 | 미해결 | 리뷰어 |
|----|------|--------|--------|
| #7361 | [PK-32445] 학부모 대상 추억보기 스킴 | 1 | @qazqaz1000 |
| #7360 | [PK-32581] 알림장 작성 스킴 추가 | 2 | @qazqaz1000 |
| #7353 | App Store Connect 릴리스 노트 | 0 | - |

---

## 전체 미해결 코멘트: 3개

### PR #7361
1. [DISCUSS] 체험 계정 처리 의도 - @qazqaz1000

### PR #7360
1. [DISCUSS] API 호출 실패 시 에러 처리 - @qazqaz1000
2. [DISCUSS] 메인 스레드 호출 확인 - @qazqaz1000

---

어떤 PR부터 처리하시겠습니까?
```

---

## 연계 스킬

| 스킬 | 용도 | 순서 |
|------|------|------|
| `/ai-dev.review --peer` | 다른 사람 PR에 코멘트 작성 | 선행 (리뷰어 입장) |
| `/ai-dev.resolve-conversation` | 내 PR 코멘트 처리 | **본 스킬** |
| `/codex-hotfix` | ACCEPT 항목 빠른 수정 | 후속 |
| `/ai-dev.pr` | 수정 후 PR 업데이트 | 후속 |

---

## 톤 & 매너 가이드

### 응답 작성 시 주의사항

1. **정중함 유지**: 리뷰어의 시간과 노력에 감사 표현
2. **논리적 근거**: 반박 시 명확한 이유 제시
3. **개방적 태도**: "혹시 제가 놓친 부분이 있다면" 등 추가 피드백 환영
4. **간결함**: 장황한 설명보다 핵심 위주

### 피해야 할 표현

- ❌ "그건 틀렸습니다" → ✅ "다른 관점에서 보면..."
- ❌ "이미 알고 있습니다" → ✅ "의도적인 설계입니다. 그 이유는..."
- ❌ 무응답/무시 → ✅ 모든 코멘트에 응답

---

**Created**: 2026-01-29
**Updated**: 2026-01-29
**Version**: 1.0
