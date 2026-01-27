---
name: ai-dev
description: AI 협업 개발 스킬. TPL 분석 → Developer 구현 → 리뷰 → PR 생성. "개발해줘", "기능 구현", "버그 수정해줘", "ai-dev", "AI 협업" 요청 시 사용.
---

# Skill: ai-dev

AI와 협업하여 개발하는 통합 워크플로우입니다. 분석부터 PR 생성까지 전체 과정을 관리합니다.

---

## 목적

- JIRA 티켓 기반 개발 자동화
- 일관된 워크플로우 제공
- 문서화 자동화 (analyze, spec, plan)
- Claude + Codex 크로스 체크를 통한 품질 향상

## 사용 시점

- `/ai-dev PROJ-XXXXX` - 전체 워크플로우 시작
- `/ai-dev PROJ-XXXXX --figma https://...` - Figma 포함

---

## 워크플로우 개요

```
┌─────────────────────────────────────────────────────────────────┐
│                        ai-dev 워크플로우                          │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  [입력] JIRA 티켓 번호 + Figma (선택)                             │
│                                                                 │
│         ↓                                                       │
│  Phase 0: ai-dev.analyze [plan mode]                           │
│  → JIRA 조회 (본문+댓글), Figma(figma-ocaml), 코드 분석           │
│  → 출력: analyze.md                                             │
│                                                                 │
│         ↓                                                       │
│  Phase 1: ai-dev.spec [plan mode]                              │
│  → Claude + Codex 크로스 체크 → 스펙 확정                         │
│  → 출력: spec.md                                                │
│                                                                 │
│         ↓                                                       │
│  Phase 2: ai-dev.plan [plan mode]                              │
│  → Codex MCP 계획 생성 → Claude 검증 → 사용자 구현 승인            │
│  → 출력: plan.md                                                │
│                                                                 │
│         ↓ [plan mode 해제]                                      │
│  Phase 3: ai-dev.impl                                          │
│  → Task별 구현 + 로컬 커밋 + 테스트([DEBUG]) + Xcode 실행     │
│  → 출력: 소스 코드                                               │
│                                                                 │
│         ↓                                                       │
│  Phase 4: ai-dev.review                                        │
│  → 빌드/린트 검증, 코드 리뷰                                      │
│  → 출력: 승인/변경요청                                           │
│                                                                 │
│         ↓ (승인 시)                                             │
│  Phase 5: ai-dev.pr                                            │
│  → Push, GitHub PR 생성                                         │
│  → 출력: PR URL                                                 │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

---

## 문서 저장 경로

모든 문서는 프로젝트 내 중앙 저장소에 저장:

```
.claude/contexts/work/my-project/docs/ai-dev/{PROJ-xxxx-개발내용}/
├── analyze.md            # Phase 0 출력
├── spec.md               # Phase 1 출력
└── plan.md               # Phase 2 출력
```

**폴더명 생성 규칙:**
- 티켓 번호: JIRA 티켓 키 (예: PROJ-32398)
- 개발내용: JIRA 티켓 제목에서 추출
  - 공백 → 하이픈으로 변환
  - 특수문자 제거
  - 최대 30자
- 예: `PROJ-32398-원생관리-검색기능`

---

## Phase별 상세

### Phase 0: ai-dev.analyze

**모드**: plan mode (분석 전용, 파일 수정 안함)

**입력**: JIRA 티켓 번호, Figma URL (선택)

**프로세스**:
1. JIRA 티켓 조회 (본문 + 댓글)
2. Figma URL 자동 감지 → figma-ocaml MCP로 디자인 컨텍스트 추출
3. Explore 에이전트로 iOS 코드베이스 탐색
4. **Android 코드 참조** (`~/Dev/Repo/my-android-app`)
   - 비즈니스 로직 참조
   - API 패턴 확인
   - 엣지 케이스 처리 참고
   - 플랫폼 일관성 확인
5. 엣지 케이스 식별
6. 확인 필요 사항 AskUserQuestion

**출력**: `analyze.md`

### Phase 1: ai-dev.spec

**모드**: plan mode

**입력**: analyze.md

**프로세스**:
1. 모델 최적화 질문 생성
2. **Claude + Codex 병렬 분석**
   - Claude: 대화 맥락 기반 분석
   - Codex MCP: 코드 탐색 기반 분석
3. **크로스 체크**
   - Claude에게 Codex 답변 전달 → 비교/보완
   - Codex에게 Claude 답변 전달 (codex-reply) → 비교/보완
4. 종합: 공통 합의 → spec.md, 선택 필요 → AskUserQuestion
5. 사용자 승인

**출력**: `spec.md`

### Phase 2: ai-dev.plan

**모드**: plan mode

**입력**: spec.md

**프로세스**:
1. **Codex MCP로 계획 생성**
   ```
   mcp__codex__codex(
     prompt: "스펙 기반 구현 계획 작성",
     cwd: "~/Dev/Repo/my-ios-app",
     approval-policy: "on-failure",
     sandbox: "read-only"
   )
   ```
2. **Claude 검증**
   - AGENTS.md 코딩 컨벤션 준수 확인
   - 파일 경로 정확성 검증
   - 의존성 순서 타당성 검토
   - 누락 Task 확인
3. 보정 및 plan.md 생성
4. 사용자 구현 승인

**출력**: `plan.md`

### Phase 3: ai-dev.impl

**모드**: plan mode 해제 (Developer 역할)

**입력**: plan.md

**프로세스**:
```
for each Task in plan.md:
    1. Task 상세 확인
    2. 의존성 Task 완료 여부 확인
    3. 코드 구현 (AGENTS.md 컨벤션 준수)
    4. 빌드 검증 (xcodebuild)
    5. 테스트
       - 테스트 코드 가능 → Unit Test
       - UI 관련 → [DEBUG] 로그 추가
    6. 로컬 커밋 생성
       - 형식: [PROJ-XXXXX] <Type>(<Scope>): <Subject>
    7. plan.md에 완료 표시
```

**모든 Task 완료 후**:
1. Xcode + 시뮬레이터 실행 (osascript)
2. [DEBUG] 로그로 기능 확인
3. 사용자 "테스트 완료" 후 로그 삭제

**출력**: 소스 코드 + 로컬 커밋들

### Phase 4: ai-dev.review

**입력**: 변경된 코드

**프로세스**:
1. 빌드/린트/테스트 검증
2. 코드 리뷰
3. 승인/변경요청 판정

**출력**: 리뷰 결과

### Phase 5: ai-dev.pr

**입력**: 승인된 코드

**프로세스**:
1. Push
2. GitHub PR 생성 (gh CLI)

**출력**: PR URL

---

## 옵션

| 옵션 | 설명 | 적용 Phase |
|------|------|-----------|
| `--figma URL` | Figma 디자인 포함 | analyze |
| `--from PHASE` | 특정 Phase부터 시작 | 전체 |
| `--to PHASE` | 특정 Phase까지만 | 전체 |
| `--no-codex` | Codex MCP 비활성화 (Claude만 사용) | spec, plan, review |
| `--ultrathink` | Extended thinking 활성화 | spec, plan |

### 사용 예시

```bash
# 전체 워크플로우
/ai-dev PROJ-12345

# Figma 포함
/ai-dev PROJ-12345 --figma https://figma.com/design/xxx

# 분석부터 계획까지만
/ai-dev PROJ-12345 --to plan

# 구현부터 시작 (이미 계획이 있을 때)
/ai-dev PROJ-12345 --from impl

# Codex 쿼터 절약 (Claude만 사용)
/ai-dev PROJ-12345 --no-codex

# 복잡한 문제 (Codex + ultrathink)
/ai-dev PROJ-12345 --ultrathink

# 복잡한 문제 + Codex 쿼터 없음 (최고 품질)
/ai-dev PROJ-12345 --no-codex --ultrathink

# 옵션 먼저도 가능
/ai-dev --no-codex --ultrathink PROJ-12345
```

> **참고**: 옵션 위치는 자유롭습니다. 티켓 번호 앞/뒤 모두 인식됩니다.

---

## 사용자 개입 포인트

| Phase | 개입 시점 | 내용 |
|-------|----------|------|
| analyze | 질문 | 엣지 케이스, 요구사항 확인 |
| spec | 크로스 체크 후 | 선택 사항 결정, 스펙 승인 |
| plan | 검증 후 | 계획 검토 및 구현 승인 |
| impl | 각 Task | 다음 Task 진행 여부 (--auto 가능) |
| impl | 완료 후 | 테스트 완료 확인 |
| review | 판정 후 | 변경요청 시 수정 |
| pr | 생성 전 | 최종 확인 |

---

## 크로스 체크 메커니즘 (spec Phase)

```
┌─────────────────────────────────────────────────────────────────┐
│                    크로스 체크 흐름                              │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  [1] analyze.md → 모델 최적화 질문 생성                          │
│                                                                 │
│  [2] 병렬 분석                                                   │
│      ┌──────────────────┐    ┌──────────────────┐              │
│      │ Claude (내부)     │    │ Codex MCP        │              │
│      │ - 대화 맥락       │    │ - 코드 탐색      │              │
│      │ - 사용자 의도     │    │ - 패턴 매칭      │              │
│      └────────┬─────────┘    └────────┬─────────┘              │
│               ↓                       ↓                        │
│           Claude 답변             Codex 답변                    │
│                                                                 │
│  [3] 크로스 리뷰                                                 │
│      ┌──────────────────────────────────────────────┐          │
│      │ Claude → Codex 검토                           │          │
│      │ "Codex 분석에 대해 동의/보완/다른관점"         │          │
│      │                                              │          │
│      │ Codex → Claude 검토 (codex-reply)            │          │
│      │ "Claude 분석에 대해 동의/보완/권장사항"        │          │
│      └──────────────────────────────────────────────┘          │
│                                                                 │
│  [4] 종합                                                       │
│      ✅ 공통 합의 → spec.md 반영                                │
│      ⚖️ 선택 필요 → AskUserQuestion                             │
│      ❓ 미결정 → 추가 확인                                       │
│                                                                 │
│  [5] 사용자 승인 → spec.md 생성                                 │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

---

## 예제

### 예제 1: 전체 워크플로우

```
User: /ai-dev PROJ-32398

Claude: [ai-dev 활성화]

===== Phase 0: 분석 =====
JIRA 조회 중... PROJ-32398: 원생 검색 기능
본문 + 댓글 수집 완료

Figma URL 감지됨:
https://figma.com/design/xxx?node-id=123:456
figma-ocaml MCP로 디자인 컨텍스트 추출 중...

코드 분석 중...
[Explore 에이전트 실행]

엣지 케이스:
- 빈 검색어
- 결과 없음
- 네트워크 오류

확인이 필요합니다:
[AskUserQuestion: 검색 디바운스 시간은?]

User: 300ms

Claude: 분석 완료. analyze.md 저장됨.

===== Phase 1: 스펙 확정 =====
Claude + Codex 병렬 분석 중...

[크로스 체크 결과]
- 공통 합의: 디바운스 적용, 기존 Entity 활용
- 선택 필요: 빈 결과 표시 방식

[AskUserQuestion: EmptyView vs 인라인 메시지?]

User: 인라인 메시지

Claude: 스펙 확정. spec.md 저장됨.

===== Phase 2: 계획 수립 =====
Codex MCP로 계획 생성 중...
Claude 검증 중...

Task 분해:
- Task 1.1: Entity 정의
- Task 2.1: Reactor 검색 Action 추가
- Task 2.2: 디바운스 로직 구현
- Task 3.1: SearchBar UI 추가

구현을 시작하시겠습니까?

User: 구현 시작

Claude: plan.md 저장됨. plan mode 해제.

===== Phase 3: 구현 =====
Task 1.1 시작...
[코드 작성]
[빌드 검증] ✅
[로컬 커밋] abc1234

✅ Task 1.1 완료
다음 Task로 진행하시겠습니까?

User: Y

... (각 Task 반복) ...

모든 Task 완료.
Xcode 시뮬레이터 실행 중...

[테스트 안내]
1. 시뮬레이터에서 원생 검색 기능 확인
2. Xcode Console에서 [DEBUG] 검색
3. 정상 동작 확인 후 "테스트 완료"라고 해주세요

User: 테스트 완료

Claude: [DEBUG] 로그 삭제 완료.

===== Phase 4: 리뷰 =====
빌드 검증... ✅
린트 검사... ✅
코드 리뷰 중...

✅ 승인 (Critical 이슈 없음)

===== Phase 5: PR 생성 =====
Push 중...
PR 생성 중...

PR #7350 생성됨
https://github.com/my-project/my-ios-app/pull/7350

워크플로우 완료!
```

---

## 개별 Phase 실행

전체 워크플로우 대신 개별 Phase만 실행 가능:

```bash
/ai-dev.analyze PROJ-12345   # Phase 0만
/ai-dev.spec PROJ-12345      # Phase 1만
/ai-dev.plan PROJ-12345      # Phase 2만
/ai-dev.impl PROJ-12345      # Phase 3만
/ai-dev.review PROJ-12345    # Phase 4만
/ai-dev.pr PROJ-12345        # Phase 5만
```

---

## 연계 스킬

| 스킬 | 용도 |
|------|------|
| `/jira-get` | JIRA 티켓 조회 |
| `/jira-update` | JIRA 티켓 업데이트 |
| `/figma-design-spec` | Figma 디자인 분석 (대안) |
| `/codex-hotfix` | 리뷰 이슈 빠른 수정 |

---

## 주의사항

- Phase 0~2는 plan mode에서 실행 (분석/설계 전용)
- Phase 3부터 plan mode 해제 (코드 수정 가능)
- 각 Phase는 이전 Phase 출력에 의존
- `--from` 옵션 사용 시 필요한 파일이 있어야 함
- 로컬 커밋은 Phase 3 (impl)에서 Task별 생성
- Push/PR은 Phase 5 (pr)에서만 수행

---

**Created:** 2026-01-23
**Updated:** 2026-01-27
**Version:** 4.0 (크로스 체크 + Codex MCP 통합)
