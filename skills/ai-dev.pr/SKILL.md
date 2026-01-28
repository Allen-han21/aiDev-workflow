---
name: ai-dev.pr
description: 리뷰 승인 후 로컬 커밋을 push하고 GitHub PR을 만듭니다. "PR 만들어줘", "풀리퀘 올려줘" 요청 시 활성화.
---

# Skill: ai-dev.pr

리뷰 승인 후 로컬 커밋을 push하고 **키즈노트 팀 PR 템플릿 형식**으로 GitHub PR을 생성합니다.

---

## 목적

- Git 상태 확인 및 변경사항 분석
- JIRA 티켓 자동 추출
- Conventional Commits 형식 커밋 생성
- 원격 브랜치 푸시
- 키즈노트 표준 템플릿으로 GitHub PR 생성

## 사용 시점

- `/ai-dev.pr PK-XXXXX` - PR 생성 시작
- `/ai-dev.pr` - JIRA 티켓 자동 추출
- 보통 `/ai-dev.review` 승인 후 실행

---

## 워크플로우

### Step 1: Git 상태 분석 (병렬 실행)

다음 명령어들을 병렬로 실행하여 현재 상태를 파악:

```bash
# 변경 파일 확인
git status

# Unstaged 변경 내용
git diff

# Staged 변경 내용
git diff --staged

# 현재 브랜치명 (JIRA 티켓 추출용)
git branch --show-current

# 커밋 히스토리 (main 또는 develop 기준)
git log main...HEAD --oneline

# 전체 변경 통계
git diff main...HEAD --stat

# 원격 브랜치 존재 여부
git ls-remote --heads origin $(git branch --show-current)
```

### Step 2: JIRA 티켓 추출

다음 순서로 JIRA 티켓 번호(PK-XXXXX) 찾기:
1. **인자로 전달된 값** 우선
2. **브랜치명**에서 추출 (예: `feature/PK-12345-description`)
3. **최신 커밋 메시지**에서 추출 (`git log -1 --pretty=%B`)
4. 없으면 생략 가능

### Step 3: 변경사항 분석

- 파일 변경 분류 (신규/수정/삭제)
- **변경 유형 판단**: feat/fix/refactor/docs
- **UI 변경 여부 확인** (View/ViewController/SwiftUI 파일)
- 커밋 메시지들 종합 분석

### Step 4: 변경 사항 스테이징

```bash
# 관련 파일만 스테이징 (민감 파일 제외)
git add Sources/
git add Tests/

# 또는 특정 파일
git add path/to/file1.swift path/to/file2.swift
```

**제외 파일:**
- `.env`, `credentials.json` 등 시크릿
- `*.xcuserstate` 등 Xcode 임시 파일

### Step 5: 커밋 생성

Conventional Commits 형식:

```bash
git commit -m "$(cat <<'EOF'
[PK-XXXXX] feat(scope): 변경 내용 요약

- 상세 변경 1
- 상세 변경 2
EOF
)"
```

**커밋 메시지 규칙:**
- Type: `feat`, `fix`, `remove`, `refactor`
- Scope: `logic`, `ui`, `model`, `networking`, `build`, `test`, `doc`
- Subject: 한국어, 마침표 없음, 명령문

### Step 6: Push

```bash
git push -u origin $(git branch --show-current)
```

### Step 7: PR 생성

키즈노트 표준 템플릿으로 PR 생성:

```bash
gh pr create \
  --title "[PK-XXXXX] {제목}" \
  --body "$(cat <<'EOF'
{PR 템플릿 내용}
EOF
)"
```

### Step 8: 결과 출력

PR URL 표시:

```
PR이 생성되었습니다.
https://github.com/kidsnote/kidsnote_ios/pull/XXXX

JIRA 티켓에 PR 링크를 추가하시겠습니까?
[Y] 추가  [N] 건너뛰기
```

---

## PR 템플릿 (키즈노트 표준)

```markdown
[![](https://badgen.net/badge/JIRA/PK-XXXXX/D55543)](https://kidsnote.atlassian.net/browse/PK-XXXXX)

## 작업 내용 :mag:

- **문제 현상** (버그인 경우) 또는 **요구사항** (기능인 경우)
> [실제 문제나 요구사항 설명]

- **원인** (버그인 경우) 또는 **배경** (기능인 경우)
> [근본 원인 또는 구현 배경]

## 변경 사항 :hammer_and_wrench:

[구체적인 파일별 변경 내역]

### 주요 파일
- `파일명.swift`: 변경 내용 설명
- `모델.swift`: 변경 내용 설명

### 세부 변경
- 변경사항 1
- 변경사항 2

## 리뷰 노트 :memo:

[리뷰어가 주목해야 할 핵심 포인트]
- 복잡한 로직 설명
- 트레이드오프 결정 사항
- 알려진 제한사항

## 유닛 테스트 :test_tube:

[테스트 추가/수정 내역]
- 추가한 테스트 케이스
- 테스트 커버리지 변화
- 수동 테스트 계획

(테스트 없으면 "해당 없음" 또는 "수동 테스트 예정" 명시)

## 스크린샷 :camera:

<!--
UI 변경이 있는 경우만 포함.
업로드 방법:
1. PR description 편집
2. 파일 드래그 앤 드롭
3. 생성된 URL로 placeholder 교체
-->

### 📱 이미지 (Before/After)

|**수정 전**|**수정 후**|
|----------|---------|
|<img width="400" src="https://github.com/user-attachments/assets/UPLOAD-BEFORE.png">|<img width="400" src="https://github.com/user-attachments/assets/UPLOAD-AFTER.png">|

### 📹 동영상 (Before/After)

|**수정 전**|**수정 후**|
|----------|---------|
|<video src="https://github.com/user-attachments/assets/UPLOAD-BEFORE.mp4">|<video src="https://github.com/user-attachments/assets/UPLOAD-AFTER.mp4">|

(UI 변경 없으면 스크린샷 섹션 전체 삭제)
```

---

## 변경 유형별 템플릿 조정

| 유형 | 조정 사항 |
|------|----------|
| **버그 수정** | "문제 현상" + "원인" 강조 |
| **새 기능** | "요구사항" + "구현 배경" 강조 |
| **리팩토링** | Before/After 비교 강조 |
| **문서화** | 간소화 (스크린샷 섹션 제외) |

---

## UI 변경 감지

다음 파일이 변경되면 스크린샷 섹션 포함:
- `*View.swift`, `*ViewController.swift`
- `*.swiftui` 관련 파일
- `*.xib`, `*.storyboard`

변경 없으면 스크린샷 섹션 전체 삭제.

---

## 옵션

| 옵션 | 설명 | 예시 |
|------|------|------|
| `--draft` | Draft PR 생성 | `/ai-dev.pr PK-12345 --draft` |
| `--no-push` | 커밋만 (push 안 함) | 로컬 확인용 |
| `--amend` | 기존 커밋 수정 | 사용자 명시적 요청 시만 |

---

## 예제

### 예제 1: 기본 PR 생성

```
User: /ai-dev.pr PK-32398

Claude: [ai-dev.pr 활성화]

Git 상태 확인 중...
브랜치: feature/ai-dev-test/PK-32398-test-codex
변경 파일: 5개
변경 유형: feat (새 기능)
UI 변경: 감지됨 (SearchView.swift)

커밋 생성 중...
[PK-32398] feat(ui): 원생 검색 기능 추가

Push 중...
✅ origin/feature/ai-dev-test/PK-32398-test-codex

PR 생성 중...

---
PR #7350 생성됨
https://github.com/kidsnote/kidsnote_ios/pull/7350

제목: [PK-32398]  원생 검색 기능 추가
스크린샷 업로드가 필요합니다 (UI 변경 감지됨)
---

JIRA에 PR 링크를 추가하시겠습니까?
```

### 예제 2: Draft PR

```
User: /ai-dev.pr PK-32398 --draft

Claude: Draft PR로 생성합니다...

PR #7350 (Draft) 생성됨
https://github.com/kidsnote/kidsnote_ios/pull/7350
```

### 예제 3: JIRA 자동 추출

```
User: /ai-dev.pr

Claude: [ai-dev.pr 활성화]

브랜치명에서 JIRA 티켓 추출: PK-32398
(브랜치: feature/PK-32398-search-feature)

계속 진행하시겠습니까?
```

---

## 전체 커밋 히스토리 분석

**중요**: 최신 커밋만이 아닌 **base 브랜치 분기점부터 전체** 검토
- 여러 커밋의 맥락을 종합하여 하나의 스토리로 구성
- PR 제목과 내용에 전체 변경사항 반영

---

## PR 제목 작성

Conventional Commits 형식:
- `feat: 다크모드 토글 추가`
- `fix: Enrollment 디코딩 오류 수정`
- `refactor: NetworkManager 모듈화`

JIRA 티켓 포함:
- `[PK-12345] feat: 다크모드 토글 추가`

---

## 다음 단계

PR 생성 후:

```
ai-dev 워크플로우가 완료되었습니다.

생성된 산출물:
- ~/.claude/ai-dev/kidsnote_ios/PK-32398/
  - analysis.md
  - spec.md
  - plan.md
  - jira-description.md
- GitHub PR: #7350
- JIRA: PK-32398 (description 업데이트됨)

수고하셨습니다!
```

---

## 연계 스킬

| 스킬 | 용도 |
|------|------|
| `/ai-dev.review` | 선행 리뷰 승인 (권장) |
| `/jira-comment` | JIRA에 PR 링크 추가 |

---

**Updated:** 2026-01-27
**Version:** 2.0 (create-pr 통합)
