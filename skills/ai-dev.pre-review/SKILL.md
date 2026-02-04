---
name: ai-dev.pre-review
description: JIRA 티켓 사전검토 + Draft PR 생성. "사전검토", "pre-review", "draft PR 만들어줘", "검토해줘" 키워드로 트리거.
---

# ai-dev.pre-review (사전검토)

JIRA 티켓을 받아 **경량 분석 → Draft 계획 → JIRA 업데이트 → Draft 구현 → Draft PR**까지 빠르게 진행합니다.

**목적**: 본격 개발 전 기능 테스트가 가능한 Draft 상태를 빠르게 만들기

---

## 기존 ai-dev 워크플로우 영향

**영향 없음** - 독립 스킬로 구성

- 파일 위치: `~/.claude/skills/ai-dev.pre-review/SKILL.md` (독립 파일)
- 실행 방식: `/ai-dev.pre-review PROJ-XXXXX` (별도 명령어)
- ai-dev 메인 9단계 파이프라인은 **그대로 유지**
- ai-dev.analyze, ai-dev.spec 등과 **동일한 독립 구조**

---

## 사용법

```bash
/ai-dev.pre-review PROJ-XXXXX
/ai-dev.pre-review PROJ-XXXXX --figma https://figma.com/...
/ai-dev.pre-review PROJ-XXXXX --skip-jira
/ai-dev.pre-review PROJ-XXXXX --skip-pr
```

---

## 옵션

| 옵션 | 설명 | 기본값 |
|------|------|--------|
| `--figma URL` | Figma 디자인 URL 포함 | JIRA 첨부에서 자동 감지 |
| `--skip-jira` | JIRA 업데이트 스킵 | false |
| `--skip-pr` | Draft PR 생성 스킵 | false |

---

## 워크플로우

### Step 1: Quick Analyze (경량 분석)

JIRA 티켓 + 코드베이스 빠른 분석:

```bash
# JIRA 조회
~/.claude/scripts/jira/jira-cli get {TICKET_ID} --detailed

# 키워드 기반 코드 탐색
# - Grep으로 관련 키워드 검색
# - 핵심 파일 2-3개 Read
# - 기존 패턴 파악
```

**분석 항목:**
- 요구사항 핵심 내용
- 영향 받는 파일 목록
- 기존 유사 구현 패턴
- Figma URL (있는 경우)

**출력**: `~/.claude/contexts/work/{project}/docs/ai-dev/{PROJ-xxxx-개발내용}/quick-analyze.md`

### Step 2: Draft Plan (간소화된 계획)

Phase/Task 분해 (간소화):

```markdown
## Phase 1: 데이터 레이어
- [ ] Task 1.1: Entity 정의
- [ ] Task 1.2: Repository 골격

## Phase 2: 비즈니스 로직
- [ ] Task 2.1: UseCase/Service

## Phase 3: UI 레이어
- [ ] Task 3.1: Reactor/ViewModel
- [ ] Task 3.2: ViewController/View
```

**ai-dev.plan 대비 차이점:**
- Codex 크로스 체크 스킵
- 예상 코드 스니펫 간소화
- 테스트 계획 생략

**출력**: `~/.claude/contexts/work/{project}/docs/ai-dev/{PROJ-xxxx-개발내용}/draft-plan.md`

### Step 3: JIRA Update

JIRA Description에 사전검토 결과 추가:

```bash
# 기존 Description 조회
~/.claude/scripts/jira/jira-cli get {TICKET_ID} --field description

# 업데이트 (기존 내용 + 구분선 + 사전검토)
~/.claude/scripts/jira/jira-cli update {TICKET_ID} \
  --description "{기존 내용}

---
## 📋 사전검토 결과 (AI 분석)
{템플릿 내용}"
```

**주의**: 기존 Description 내용 반드시 보존

### Step 4: Draft Implementation

Draft 수준 구현:

```
for each Task in draft-plan.md:
    1. 코드 작성 (골격 수준)
    2. 빌드 검증 (xcodebuild)
    3. [debug] 로그 추가
    4. 로컬 커밋
```

**Draft 구현 기준:**

| 레이어 | Draft 수준 |
|--------|-----------|
| Entity/Model | 100% 완성 |
| Repository | 골격 (API 연동) |
| Reactor/ViewModel | 기본 바인딩 (Happy Path) |
| UI | 레이아웃 완성 (세부 스타일 생략) |
| 에러 처리 | 생략 |
| 테스트 | [debug] 로그만 |

### Step 5: Draft PR

**ai-dev.pr 스킬을 사용하여 Draft PR 생성:**

```bash
# ai-dev.pr 스킬 호출 (--draft 옵션 필수)
/ai-dev.pr {TICKET_ID} --draft
```

**중요**: 반드시 `--draft` 옵션을 사용하여 Draft 상태로 PR 생성

ai-dev.pr 스킬이 자동으로 처리하는 항목:
- 브랜치 생성/확인
- git push
- PR 생성 (Draft 모드)
- 프로젝트 표준 PR 템플릿 적용

**PR 제목 형식:**
```
[Draft] [PROJ-XXXXX] feat: {기능 설명}
```

---

## 산출물

### 문서 저장 경로

```
~/.claude/contexts/work/{project}/docs/ai-dev/{PROJ-xxxx-개발내용}/
├── quick-analyze.md    # Step 1 출력
└── draft-plan.md       # Step 2 출력
```

### quick-analyze.md 템플릿

```markdown
# {TICKET_ID} Quick Analyze

**분석일**: YYYY-MM-DD HH:MM
**티켓**: {TICKET_ID} - {제목}

## 1. 요구사항 요약
{JIRA 내용 기반 핵심 요약}

## 2. 영향 파일
| 파일 | 역할 | 변경 예상 |
|------|------|----------|
| {파일 경로} | {역할} | 신규/수정 |

## 3. 기존 패턴 참조
{유사 기능 구현 패턴}

## 4. Figma (있는 경우)
- URL: {Figma URL}

## 5. 리스크/확인 필요
- {항목 1}
- {항목 2}
```

### draft-plan.md 템플릿

```markdown
# {TICKET_ID} Draft Plan

**생성일**: YYYY-MM-DD HH:MM

## Phase 1: 데이터 레이어
- [ ] Task 1.1: {설명}
  - 파일: {경로}
- [ ] Task 1.2: {설명}

## Phase 2: 비즈니스 로직
- [ ] Task 2.1: {설명}

## Phase 3: UI 레이어
- [ ] Task 3.1: {설명}
- [ ] Task 3.2: {설명}

## 예상 복잡도
{낮음/중간/높음}

## 의존성
- {외부 의존성}
```

### JIRA 업데이트 템플릿

```markdown
---
## 📋 사전검토 결과 (AI 분석)

**분석일**: YYYY-MM-DD
**분석자**: Claude Code (ai-dev.pre-review)

### 1. 요구사항 요약
- {핵심 기능 1}
- {핵심 기능 2}

### 2. 영향 파일
| 파일 | 변경 유형 |
|------|----------|
| {파일 경로} | 신규/수정 |

### 3. 구현 계획 (Draft)
- Phase 1: {데이터 레이어}
- Phase 2: {비즈니스 로직}
- Phase 3: {UI 레이어}

### 4. 확인 필요 사항
- [ ] {질문 1}
- [ ] {질문 2}

### 5. Draft PR
- **PR**: #{PR 번호} (Draft)
- **상태**: 기능 테스트 가능

*Generated by ai-dev.pre-review*
```

### Draft PR 본문 템플릿

```markdown
> ⚠️ **Draft PR** - 사전검토용 (기능 테스트 가능)

## 📋 Summary
{JIRA 요구사항 요약}

## 🔗 Related
- JIRA: [{TICKET_ID}](https://{your-domain}.atlassian.net/browse/{TICKET_ID})

## Draft 상태
- [x] UI 골격 완성
- [x] 기본 로직 (Happy Path)
- [ ] 엣지 케이스 처리
- [ ] 에러 핸들링
- [ ] Unit Test

## 테스트 방법
1. {테스트 단계 1}
2. {테스트 단계 2}

## 다음 단계
`/ai-dev {TICKET_ID} --from impl` 로 완성 개발 진행

---
🤖 Generated by ai-dev.pre-review
```

---

## ai-dev 연계

사전검토 후 완성 개발이 필요할 때:

```bash
# 사전검토 산출물 활용하여 완성 개발
/ai-dev PROJ-XXXXX --from impl

# 또는 처음부터 상세 분석
/ai-dev PROJ-XXXXX
```

**pre-review 출력물 → ai-dev 입력으로 활용:**
- `quick-analyze.md` → `analyze.md` 확장
- `draft-plan.md` → `plan.md` 확장

---

## 예제

### 예제 1: 기본 사전검토

```
User: /ai-dev.pre-review PROJ-32398

Claude: [ai-dev.pre-review 활성화]

===== Step 1: Quick Analyze =====
JIRA 조회 중... PROJ-32398: 원생 검색 기능 개선

코드베이스 탐색 중...
- StudentListViewController.swift 발견
- StudentSearchService.swift 발견

분석 완료!
quick-analyze.md 저장됨

===== Step 2: Draft Plan =====
Phase 구조 생성 중...
- Phase 1: 데이터 (1 Task)
- Phase 2: 로직 (2 Tasks)
- Phase 3: UI (2 Tasks)

draft-plan.md 저장됨

===== Step 3: JIRA Update =====
JIRA 본문 업데이트 중...
✅ PROJ-32398 Description 업데이트됨

===== Step 4: Draft Implementation =====
Task 1.1 시작: Entity 정의...
Task 2.1 시작: Service 골격...
Task 3.1 시작: Reactor 기본 구조...
Task 3.2 시작: UI 레이아웃...
✅ 5 Tasks 완료 (로컬 커밋 5개)

===== Step 5: Draft PR =====
/ai-dev.pr PROJ-32398 --draft 실행 중...
✅ PR #7350 생성됨 (Draft)

🎉 사전검토 완료!

결과:
- JIRA: PROJ-32398 업데이트됨
- Draft PR: #7350 (Draft)
- 상태: 기능 테스트 가능

다음 단계:
1. 시뮬레이터에서 기능 테스트
2. 피드백 수집
3. /ai-dev PROJ-32398 --from impl 로 완성
```

### 예제 2: JIRA 업데이트 스킵

```
User: /ai-dev.pre-review PROJ-32399 --skip-jira

Claude: [ai-dev.pre-review 활성화]
(Step 3 JIRA Update 스킵됨)
...
```

### 예제 3: Figma 포함

```
User: /ai-dev.pre-review PROJ-32400 --figma https://figma.com/file/xxx

Claude: [ai-dev.pre-review 활성화]

===== Step 1: Quick Analyze =====
Figma 디자인 분석 중...
- figma_get_node_summary 실행
- 화면 구조 파악

JIRA + Figma 분석 완료!
...
```

---

## 주의사항

- Draft PR은 **Ready for Review가 아님** (WIP 상태)
- JIRA 업데이트 시 **기존 내용 보존** 필수
- Draft 구현은 **프로덕션 품질이 아님**
- 사전검토 후 반드시 `/ai-dev`로 완성 개발 진행
- [debug] 로그는 완성 개발 시 제거

---

**Created:** 2025-02-04
**Version:** 1.0
