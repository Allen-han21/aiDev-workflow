---
name: ai-dev.plan-check
description: plan.md를 5개 병렬 validators + devil's advocate로 검증. "계획 검증", "plan check", "플랜 체크" 요청 시 활성화.
---

# Skill: ai-dev.plan-check

spec.md와 plan.md를 5개 병렬 validators로 검증하고, devil's advocate가 findings를 도전합니다.

---

## 목적

- spec.md 요구사항이 plan.md에 모두 반영되었는지 검증
- AGENTS.md 컨벤션 및 아키텍처 패턴 준수 확인
- 기술적 실현 가능성 및 위험 평가
- False positive 감소 (devil's advocate)

---

## 사용 시점

- `/ai-dev.plan-check PK-XXXXX` - 계획 검증 시작
- `ai-dev.plan` 완료 후, `ai-dev.impl` 실행 전
- plan.md 작성 완료 후 검증

---

## 전제 조건

**plan mode에서 실행**

**필수 파일**:
- spec.md (요구사항)
- plan.md (검증 대상)

---

## 워크플로우

```
┌─────────────────────────────────────────────────────────────────┐
│                    ai-dev.plan-check 워크플로우                   │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  [Step 1] 문서 로드                                              │
│  spec.md + plan.md 읽기                                         │
│                                                                 │
│  [Step 2] 5개 Validators 병렬 실행                               │
│  ┌─────────┬─────────┬─────────┬─────────┬─────────┐           │
│  │Complete-│Pattern  │Feasibi- │Risk     │Scope    │           │
│  │ness     │Compli-  │lity     │Assessor │Discip-  │           │
│  │Checker  │ance     │Assessor │         │line     │           │
│  └────┬────┴────┬────┴────┬────┴────┬────┴────┬────┘           │
│       └─────────┴─────────┼─────────┴─────────┘                 │
│                           ▼                                     │
│  [Step 3] Findings 집계                                          │
│  P0/P1/P2/P3 심각도 분류                                         │
│                           ▼                                     │
│  [Step 4] Devil's Advocate                                      │
│  모든 findings 도전 → 확정/반박/신규 발견                         │
│                           ▼                                     │
│  [Step 5] 리포트 생성 + 판정                                     │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

---

## 5개 Validators

### 1. Completeness Checker (완전성 검증)

**역할**: spec.md 요구사항이 plan.md에 모두 반영되었는지 확인

**검증 항목**:
- spec.md의 각 요구사항이 plan.md Task에 매핑되는지
- 누락된 요구사항 목록 생성
- "70% Problem" 감지: 쉬운 부분만 상세하고 어려운 부분은 모호한지

**프롬프트 요약**:
```
spec.md의 각 요구사항을 plan.md Task와 매핑하세요.
누락된 요구사항을 P0/P1 심각도로 분류하세요.
모호한 단계 ("비즈니스 로직 구현", "에러 처리 추가" 등)를 식별하세요.
```

### 2. Pattern Compliance Checker (패턴 준수 검증)

**역할**: AGENTS.md 컨벤션 및 아키텍처 패턴 준수 확인

**검증 항목**:
- Clean Architecture 준수 (Entity → Repository → UseCase → UI)
- 코딩 컨벤션 (타입 명시, guard문 스타일 등)
- 파일 구조 규칙 (Feature 폴더 구조)

**프롬프트 요약**:
```
plan.md가 AGENTS.md 규칙을 준수하는지 확인하세요.
아키텍처 위반 (UI에서 Repository 직접 호출 등)을 식별하세요.
파일 생성 위치가 규칙에 맞는지 확인하세요.
```

### 3. Feasibility Assessor (실현 가능성 검증)

**역할**: 기술적으로 구현 가능한지 확인

**검증 항목**:
- 참조된 파일/함수가 실제로 존재하는지 (Glob/Grep)
- 의존성 충돌 여부
- API 호환성

**프롬프트 요약**:
```
plan.md에서 참조하는 파일이 실제로 존재하는지 Glob으로 확인하세요.
참조하는 함수/클래스가 존재하는지 Grep으로 확인하세요.
hallucination (존재하지 않는 것 참조)을 P0로 보고하세요.
```

### 4. Risk Assessor (위험 평가)

**역할**: 회귀 가능성, 영향 범위, 보안 위험 평가

**검증 항목**:
- 기존 기능 회귀 가능성
- 영향 범위 (다른 모듈에 미치는 영향)
- 보안 위험 (인증, 권한, 데이터 노출)
- 롤백 계획 존재 여부

**프롬프트 요약**:
```
plan.md 변경이 기존 기능에 미치는 영향을 분석하세요.
보안 관련 위험 (org_id 필터 누락 등)을 식별하세요.
롤백 불가능한 변경이 있는지 확인하세요.
```

### 5. Scope Discipline Checker (범위 제어)

**역할**: spec 범위 초과, gold-plating 감지

**검증 항목**:
- spec.md에 없는 추가 기능 포함 여부
- 불필요한 리팩토링 감지
- Over-engineering 징후

**프롬프트 요약**:
```
plan.md가 spec.md 범위를 초과하는지 확인하세요.
요청하지 않은 "개선"이나 리팩토링을 식별하세요.
과도한 추상화나 일반화를 감지하세요.
```

---

## Devil's Advocate Phase

모든 validator findings를 도전합니다.

**역할**: False positive 감소, 놓친 문제 발견

**도전 질문**:
1. "이 지적이 정말 유효한가?"
2. "이 맥락에서 예외가 될 수 있는가?"
3. "반박할 근거가 있는가?"
4. "validators가 놓친 문제는 없는가?"

**출력 상태**:
| 상태 | 의미 |
|------|------|
| CONFIRMED | 도전 후에도 유효 |
| DOWNGRADED | 심각도 하향 |
| DISMISSED | False positive로 판정 |
| NEW_DISCOVERY | 새로 발견된 문제 |

**프롬프트 요약**:
```
각 finding에 대해 반박을 시도하세요.
맥락을 고려하여 실제로 문제인지 판단하세요.
validators가 놓친 문제를 찾으세요.
CONFIRMED/DOWNGRADED/DISMISSED/NEW_DISCOVERY로 분류하세요.
```

---

## 심각도 분류 (P0-P3)

| Level | 의미 | 예시 | 조치 |
|-------|------|------|------|
| **P0** | 계획 실패 | Hallucinated 파일, 누락된 핵심 요구사항 | 필수 수정 |
| **P1** | 주요 위반 | 아키텍처 위반, 보안 위험 | 수정 권장 |
| **P2** | 개선 필요 | 경미한 패턴 편차, 누락된 edge case | 선택적 수정 |
| **P3** | 제안 | 스타일 선호, 최적화 제안 | 참고 |

**P0 필수 조건**: 증거 포함 (파일 존재 확인 결과 등)

---

## 실행 방법

### Step 1: 문서 로드

```
경로: ~/.claude/contexts/work/kidsnote/docs/ai-dev/{PK-xxxx}/
- spec.md
- plan.md
```

### Step 2: 5개 Validators 병렬 실행

**단일 메시지에서 5개 Task 동시 생성:**

```markdown
다음 5개 Task를 병렬로 실행합니다:

**Task 1: completeness-checker**
spec.md의 각 요구사항이 plan.md에 매핑되는지 확인.

**Task 2: pattern-compliance**
AGENTS.md 컨벤션 및 아키텍처 패턴 준수 확인.

**Task 3: feasibility-assessor**
참조된 파일/함수 존재 여부 확인 (Glob/Grep).

**Task 4: risk-assessor**
회귀 가능성, 보안 위험 평가.

**Task 5: scope-discipline**
범위 초과, gold-plating 감지.
```

### Step 3: Findings 집계

모든 validator 완료 후:
- P0/P1/P2/P3별 분류
- 중복 finding 병합
- 총 finding 수 집계

### Step 4: Devil's Advocate 실행

```markdown
다음 findings를 검토하고 도전합니다:

{findings_list}

각 finding에 대해:
1. 반박 시도
2. 맥락 고려
3. 상태 결정 (CONFIRMED/DOWNGRADED/DISMISSED)

추가로 놓친 문제가 있으면 NEW_DISCOVERY로 보고.
```

### Step 5: 리포트 생성

plan-check-report.md 생성 후 판정 표시.

---

## 출력 템플릿

```markdown
# {TICKET_ID} Plan Check Report

**검증일**: YYYY-MM-DD HH:MM
**검증 모드**: 5 Validators + Devil's Advocate

---

## 요약

| 심각도 | 원래 | Confirmed | Dismissed | 신규 |
|--------|------|-----------|-----------|------|
| P0     | N    | N         | N         | N    |
| P1     | N    | N         | N         | N    |
| P2     | N    | N         | N         | N    |
| P3     | N    | N         | N         | N    |

---

## Confirmed Issues (수정 필요)

### P0 Critical

**[PLAN-001] {이슈 제목}**
- **Validator**: {Validator 이름}
- **내용**: {설명}
- **증거**: {Glob/Grep 결과 등}
- **Devil's Advocate**: CONFIRMED - {유효한 이유}
- **권장 조치**: {수정 방법}

### P1 High
...

---

## Dismissed Issues (False Positive)

**[PLAN-010] {이슈 제목}**
- **원래 지적**: {Validator 지적}
- **반박 근거**: {왜 false positive인지}

---

## New Discoveries (Devil's Advocate 발견)

**[NEW-001] {이슈 제목}**
- **발견 경위**: {어떻게 발견}
- **심각도**: P{N}
- **영향**: {영향 범위}
- **권장 조치**: {수정 방법}

---

## 판정

| 조건 | 결과 |
|------|------|
| **Plan 승인** | ✅ 승인 / ⚠️ 조건부 승인 / ❌ 수정 필요 |
| P0 이슈 | N건 (0이어야 승인) |
| P1 이슈 | N건 (수정 권장) |

---

## 다음 단계

- ✅ 승인: `/ai-dev.impl PK-XXXXX` 진행 (구현 시작)
- ⚠️ 조건부 승인: P1 이슈 검토 후 진행 결정
- ❌ 수정 필요: plan.md 수정 후 `/ai-dev.plan-check` 재실행

---

*Validated by ai-dev.plan-check (5 validators + devil's advocate)*
```

---

## 파일 경로

```
~/.claude/contexts/work/kidsnote/docs/ai-dev/{PK-xxxx}/
├── analyze.md
├── spec.md
├── plan.md
└── plan-check-report.md  ← 생성
```

---

## 연계 스킬

| 스킬 | 용도 |
|------|------|
| `/ai-dev.plan` | 선행 (plan.md 생성) |
| `/ai-dev.impl` | 후속 (검증 통과 후 구현 시작) |

---

**Created:** 2026-01-28
**Version:** 1.0
