---
name: ai-dev.pr
description: 리뷰 승인 후 로컬 커밋을 push하고 GitHub PR을 만듭니다. "PR 만들어줘", "풀리퀘 올려줘" 요청 시 활성화.
---

# Skill: ai-dev.pr

리뷰 승인 후 로컬 커밋을 push하고 GitHub PR을 생성합니다.

---

## 목적

- Git 상태 확인
- Conventional Commits 형식 커밋 생성
- 원격 브랜치 푸시
- GitHub PR 생성

## 사용 시점

- `/ai-dev.pr PROJ-XXXXX` - PR 생성 시작
- 보통 `/ai-dev.review` 승인 후 실행

---

## 워크플로우

### Step 1: Git 상태 확인

```bash
# 현재 브랜치
git branch --show-current

# 변경 사항 확인
git status --porcelain

# 원격 브랜치 존재 여부
git ls-remote --heads origin $(git branch --show-current)
```

### Step 2: 변경 사항 스테이징

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

### Step 3: 커밋 생성

Conventional Commits 형식:

```bash
git commit -m "$(cat <<'EOF'
[PROJ-XXXXX] feat(scope): 변경 내용 요약

- 상세 변경 1
- 상세 변경 2
EOF
)"
```

**커밋 메시지 규칙 (AGENTS.md):**
- Type: `feat`, `fix`, `remove`, `refactor`
- Scope: `logic`, `ui`, `model`, `networking`, `build`, `test`, `doc`
- Subject: 한국어, 마침표 없음, 명령문

### Step 4: Push

```bash
git push -u origin $(git branch --show-current)
```

### Step 5: PR 생성

```bash
gh pr create \
  --title "[PROJ-XXXXX] {Type}: {제목}" \
  --body "$(cat <<'EOF'
## Summary
- {변경 요약 1}
- {변경 요약 2}

## Test plan
- [ ] 빌드 확인
- [ ] 기능 테스트
- [ ] 엣지 케이스 확인

## Related
- JIRA: PROJ-XXXXX
- Figma: {링크}
EOF
)"
```

### Step 6: 결과 출력

PR URL 표시:

```
PR이 생성되었습니다.
https://github.com/my-project/my-ios-app/pull/XXXX

JIRA 티켓에 PR 링크를 추가하시겠습니까?
[Y] 추가  [N] 건너뛰기
```

---

## PR 템플릿

```markdown
## Summary
- {변경 요약 1}
- {변경 요약 2}
- {변경 요약 3}

## Test plan
- [ ] 빌드 확인
- [ ] 기능 동작 테스트
- [ ] 엣지 케이스 확인
  - [ ] 빈 데이터
  - [ ] 네트워크 오류
- [ ] UI 확인 (Figma 대조)

## Screenshots
(필요 시 스크린샷 추가)

## Related
- JIRA: {PROJ-XXXXX}
- Figma: {링크}

## Checklist
- [ ] 코드 리뷰 완료
- [ ] 테스트 통과
- [ ] 린트 통과
```

---

## 옵션

| 옵션 | 설명 | 예시 |
|------|------|------|
| `--draft` | Draft PR 생성 | `/ai-dev.pr PROJ-12345 --draft` |
| `--no-push` | 커밋만 (push 안 함) | 로컬 확인용 |
| `--amend` | 기존 커밋 수정 | 사용자 명시적 요청 시만 |

---

## 예제

### 예제 1: 기본 PR 생성

```
User: /ai-dev.pr PROJ-32398

Claude: [ai-dev.pr 활성화]

Git 상태 확인 중...
브랜치: feature/ai-dev-test/PROJ-32398-test-codex
변경 파일: 5개

커밋 생성 중...
[PROJ-32398] feat(ui): 원생 검색 기능 추가

Push 중...
✅ origin/feature/ai-dev-test/PROJ-32398-test-codex

PR 생성 중...

---
PR #7350 생성됨
https://github.com/my-project/my-ios-app/pull/7350

제목: [PROJ-32398] feat(ui): 원생 검색 기능 추가
---

JIRA에 PR 링크를 추가하시겠습니까?
```

### 예제 2: Draft PR

```
User: /ai-dev.pr PROJ-32398 --draft

Claude: Draft PR로 생성합니다...

PR #7350 (Draft) 생성됨
https://github.com/my-project/my-ios-app/pull/7350
```

---

## 다음 단계

PR 생성 후:

```
ai-dev 워크플로우가 완료되었습니다.

생성된 산출물:
- ~/.claude/ai-dev/my-ios-app/PROJ-32398/
  - analysis.md
  - spec.md
  - plan.md
  - jira-description.md
- GitHub PR: #7350
- JIRA: PROJ-32398 (description 업데이트됨)

수고하셨습니다! 🎉
```

---

## 연계 스킬

| 스킬 | 용도 |
|------|------|
| `/ai-dev.review` | 선행 리뷰 승인 (권장) |
| `/jira-comment` | JIRA에 PR 링크 추가 |

---

**Created:** 2026-01-23
**Version:** 1.0
