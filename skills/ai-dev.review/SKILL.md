---
name: ai-dev.review
description: 자동 검증 후 코드 리뷰를 수행하고 승인/변경요청을 결정합니다. "리뷰해줘", "코드 검토해줘" 요청 시 활성화. --full로 병렬 크로스체크.
---

# Skill: ai-dev.review

자동 검증 후 상세한 코드 리뷰를 수행합니다. `--full` 옵션으로 Codex/다른 LLM과 병렬 크로스체크할 수 있습니다.

**v4.0 신규**: 비즈니스 규칙 검증 추가 - 상태 변수 영향도, 요구사항 역추적, 유사 패턴 비교, 기능 충돌 분석

---

## 목적

- 자동 검증 (린트)
- 상세 코드 리뷰
- **비즈니스 규칙 검증** (신규)
- 승인/변경요청 판정

## 사용 시점

- `/ai-dev.review PK-XXXXX` - 리뷰 시작
- `/ai-dev.review PK-XXXXX --full` - 병렬 크로스체크 포함
- 보통 `/ai-dev.impl` 완료 후 실행

---

## 워크플로우

### Step 0: 사전 준비

#### 팀 규칙 로드

리뷰 시작 전 프로젝트 AGENTS.md를 읽어 팀 규칙을 적용합니다:

```bash
# kidsnote_ios 프로젝트
cat ~/Dev/Repo/kidsnote_ios/AGENTS.md
```

**AGENTS.md 핵심 규칙 (요약):**
- 아키텍처: Clean Architecture / 단방향 데이터 플로우
- 타입 명시: 변수/상수 초기화 시 필수
- String 연산: + 연산자 금지, 문자열 보간 사용
- guard문: guard 후 개행 필수
- @objc: 다음 라인에 코드 작성
- @Pulse: 같은 라인에 작성

**리뷰 예외 사항 (지적하지 않음):**
- switch문/computed property 한 줄 블럭
- 빈줄 추가/삭제
- filterEmpty 사용
- 삼항연산자 추천
- 주석/문서화 추가

#### spec.md 확인 (신규)

비즈니스 규칙 검증을 위해 spec.md 존재 여부 확인:

```bash
# spec.md 위치 확인
Glob: ".claude/contexts/work/kidsnote/docs/ai-dev/{TICKET_ID}*/spec.md"
```

- **spec.md 있음** → Step 2.3.2 요구사항 역추적 활성화
- **spec.md 없음** → Step 2.3.2 스킵 (경고 표시)

### Step 1: 자동 검증

#### 린트 검사

```bash
swiftlint lint --quiet
```

### Step 2: 코드 리뷰

#### CodeRabbit AI 리뷰

```bash
coderabbit review --plain -t all
```

**리뷰 기준** (AGENTS.md 참고):
- 아키텍처 준수
- 문서화 주석 존재 여부
- 메모리 릭 가능성 체크
- 보안 취약점

**이슈 분류**:
| 심각도 | 처리 |
|--------|------|
| 🔴 Critical | 필수 수정 |
| 🟠 High | 필수 수정 |
| 🟡 Medium | 리포트만 |
| 🟢 Low | 리포트만 |

#### Claude Code 심도 리뷰

**독립적으로** 변경된 파일을 읽고 상세 분석:

```bash
git diff --name-only HEAD~1
```

**분석 관점:**
1. **정확성 (Correctness)**: 로직 오류, 엣지 케이스
2. **보안 (Security)**: 인젝션, 접근 제어
3. **효율성 (Efficiency)**: 성능, 메모리
4. **유지보수성 (Maintainability)**: 가독성, 네이밍
5. **아키텍처**: AGENTS.md 규칙 준수

#### Codex MCP 크로스체크 (--full 옵션)

`--full` 옵션 사용 시 Codex MCP 추가 실행:

```
mcp__codex__codex(
  prompt: "다음 파일들의 코드 변경사항을 빠르게 스캔해주세요:

1. 보안 취약점 (Security vulnerabilities)
2. 성능 안티패턴 (Performance anti-patterns)
3. 코드 품질 이슈 (Code quality issues)

변경 파일:
{git diff --name-only HEAD~1 결과}

각 이슈를 Critical/High/Medium/Low로 분류해주세요.",
  cwd: "{프로젝트 경로}",
  approval-policy: "on-failure",
  sandbox: "read-only"
)
```

### Step 2.3: 비즈니스 규칙 검증 (신규)

> **배경**: PR #7360에서 CodeRabbit이 발견한 "추억보기 모드 충돌" 같은 비즈니스 규칙 위반을 감지하기 위해 추가된 단계

`--no-biz-rules` 옵션 사용 시 이 단계를 스킵합니다.

#### Step 2.3.1: 상태 변수 영향도 분석

**목적**: Bool 플래그 변경이 기존 로직에 미치는 영향 파악

**실행 조건**: 변경된 코드에 상태 변수(`is*`, `has*`, `should*`) 할당이 포함된 경우

**자동화 방법**:

```bash
# 1. 변경 파일에서 상태 변수 추출
git diff HEAD~1 | grep -E "^\+.*is[A-Z]|^\+.*has[A-Z]|^\+.*should[A-Z]"

# 2. 해당 변수의 전체 사용 패턴 분석 (할당점)
Grep: "{변수명}\s*=" --type swift --output_mode content

# 3. 조건 검사점 분석
Grep: "if.*{변수명}|guard.*{변수명}" --type swift --output_mode content
```

**분석 관점**:
- 해당 변수가 `true`/`false`일 때 각각 어떤 동작을 하는가?
- 새 코드가 기존 조건 분기를 우회하는가?
- 새 코드에서 해당 변수를 적절히 설정/검사하는가?

**출력 형식**:
```markdown
#### 상태 변수: {변수명}

**용도**: {비즈니스 의미}

**할당점 (N개)**:
| 파일 | 라인 | 조건 | 설정값 |
|------|-----|------|--------|

**검사점 (M개)**:
| 파일 | 라인 | 조건 | 동작 |
|------|-----|------|------|

**새 코드 검증**:
- [ ] 적절한 할당
- [ ] 적절한 검사
- [ ] 기존 규칙 준수

**위험 평가**: 🔴 높음 / 🟠 중간 / 🟢 낮음
```

#### Step 2.3.2: 요구사항 역추적 검증

**목적**: spec.md 요구사항이 모두 구현되었는지 확인

**실행 조건**: Step 0에서 spec.md가 발견된 경우

**자동화 방법**:
```bash
# spec.md 읽기
Read: .claude/contexts/work/kidsnote/docs/ai-dev/{TICKET_ID}*/spec.md
```

**검증 체크리스트**:
```markdown
### 요구사항 역추적

| # | 요구사항 | spec.md 섹션 | 구현 파일 | 상태 |
|---|---------|-------------|----------|------|
| 1 | {요구사항} | {섹션} | {파일} | ✅/❌ |

**누락된 요구사항**:
- ❌ {요구사항}: {구현 누락 이유}
```

#### Step 2.3.3: 유사 패턴 비교 분석

**목적**: 기존 유사 기능과의 패턴 일관성 확인

**실행 조건**: 새로운 함수/메서드 추가 또는 기존 함수 변형 시

**자동화 방법**:
```bash
# 1. 유사 함수명 패턴 검색 (예: schemeReportWrite → scheme*Report*)
Grep: "{유사 패턴}" --type swift --output_mode files_with_matches

# 2. 기존 구현 패턴 추출
Read: {기존 유사 파일}
```

**검증 항목**:
- 초기화 순서 일관성
- 상태 검사 로직 일관성
- 에러 핸들링 패턴 일관성

**출력 형식**:
```markdown
### 유사 패턴 비교

| 항목 | 기존 패턴 | 새 패턴 | 일관성 |
|------|----------|---------|--------|
| 상태 검사 | {패턴} | {패턴} | ✅/❌ |
| 에러 핸들링 | {패턴} | {패턴} | ✅/❌ |

**불일치 시 권장 수정**:
```diff
- 현재 코드
+ 패턴 일치 코드
```
```

#### Step 2.3.4: 기능 충돌 검증

**목적**: 새 기능이 기존 기능/모드와 충돌하는지 확인

**실행 조건**: 상태 변수 변경 또는 새로운 진입점(scheme, 버튼 등) 추가 시

**자동화 방법**:
```bash
# 1. 영향받는 모드/기능 식별
Grep: "Mode|State|Flag" --path {변경된 파일 디렉토리}

# 2. 모드별 조건 분기 확인
Grep: "if.*{모드변수}|guard.*{모드변수}" --type swift
```

**검증 시나리오 템플릿**:
```markdown
### 기능 충돌 분석

| 기존 기능/모드 | 충돌 가능성 | 영향 | 권장 조치 |
|---------------|------------|------|----------|
| {모드명} | 🔴/🟠/🟢 | {영향} | {조치} |

**충돌 시나리오**:
1. 전제조건: {모드} = {상태}
2. 사용자 액션: {액션}
3. 기대 결과: {기존 규칙}
4. 실제 결과: {새 코드 동작}
5. 충돌 여부: ✅/❌
```

### Step 2.7: 리뷰 결과 종합

#### CodeRabbit 결과 확인 (필수)

종합 전에 **반드시** CodeRabbit 리뷰 결과가 있는지 확인:

```
CodeRabbit 리뷰 결과 확인:
- ✅ 결과 있음 → 종합 진행
- ❌ 결과 없음 → CodeRabbit 실행 후 종합
```

**결과 없으면 즉시 실행:**
```bash
coderabbit review --plain -t all
```

> **주의**: CodeRabbit 결과 없이 종합하지 마세요. 누락 시 크로스체크 품질이 저하됩니다.

#### 종합 판단

Claude가 CodeRabbit 결과와 자신의 리뷰를 비교하여 최종 판단:

**종합 판단 기준**:
1. **동의**: CodeRabbit과 Claude 모두 지적한 이슈
2. **반박**: CodeRabbit 지적이 오탐(false positive)인 경우 - 반박 이유와 근거 명시
3. **보강**: Claude만 발견한 이슈 (CodeRabbit이 놓친 것)
4. **종합**: 프로덕션 수준 최종 리뷰 제공

**--full 옵션 시 3자 크로스체크**:
| 동의 수준 | 판정 |
|----------|------|
| 3/3 동의 | 확정 이슈 |
| 2/3 동의 | 높은 가능성 |
| 1/3만 지적 | 검토 필요 |

**충돌 시**: Claude 판단 우선 (근거 명시)

### Step 2.5: iOS DoD 체크리스트

iOS 프로젝트인 경우 다음 항목을 필수 체크:

| 항목 | 체크 내용 |
|------|----------|
| Swift 6 concurrency | @MainActor, Sendable, Task 격리 준수 |
| 메모리 관리 | retain cycle, weak/unowned self 적절한 사용 |
| SwiftUI 성능 | 불필요한 body 재계산, @State/@StateObject 오용 |
| iOS 규칙 준수 | AGENTS.md 규칙 준수 여부 |
| 에러 처리 | try/catch 누락, 옵셔널 강제 언래핑 |
| **Apple API 호환성** | deprecated API, availability 버전 |

### Step 2.6: Apple API 호환성 체크

**apple-docs MCP 사용:**
변경된 코드에서 Apple API 사용 시 자동 체크:

```
mcp__apple-docs__search_apple_docs(query: "{사용된 API}")
```

**체크 항목:**
1. **deprecated API 사용**
   - deprecated 경고 발견 시 → 대안 API 제시
   - availability 체크 → 프로젝트 최소 지원 버전과 비교

2. **발견 시 리뷰 출력에 포함:**

```markdown
### 🟠 High: deprecated API 사용
**위치**: `{파일명}:{라인}`

**문제**: `{API명}`은 iOS {버전}부터 deprecated

**대안 API**: `{새 API명}` (iOS {버전}+)

**개선안**:
```diff
-oldAPI()
+newAPI()
```
```

**availability 불일치 시:**

```markdown
### 🔴 Critical: API 버전 불일치
**위치**: `{파일명}:{라인}`

**문제**: `{API명}`은 iOS {버전}+ 필요, 프로젝트 최소 버전 iOS {최소버전}

**해결안**:
1. `@available(iOS {버전}, *)` 래핑
2. 또는 대안 API 사용: `{대안 API명}`
```

### Step 3: 이슈 분류

발견된 이슈를 심각도로 분류:

| 심각도 | 설명 | 조치 |
|--------|------|------|
| 🔴 Critical | 필수 수정 (버그, 보안) | 머지 전 수정 필수 |
| 🟠 High | 강력 권장 | 머지 전 수정 권장 |
| 🟡 Medium | 권장 | 다음 버전에서 개선 |
| 🟢 Low | 참고 | 선택적 개선 |

### Step 4: 판정

**승인 조건:**
- 🔴 Critical 이슈 0건
- 🟠 High 이슈 0건 (또는 수용 가능한 사유)
- 린트 통과

**변경요청 조건:**
- 🔴 Critical 이슈 1건 이상
- 또는 🟠 High 이슈 다수

### Step 5: 결과 출력

리뷰 결과 보고서 생성 및 표시.

---

## 출력 템플릿

```markdown
# {TICKET_ID} 코드 리뷰 결과

**리뷰일**: YYYY-MM-DD HH:MM
**티켓**: {TICKET_ID} - {제목}
**모드**: Claude Code (기본) / Claude + Codex MCP 병렬 (--full)

---

## 자동 검증

| 항목 | 결과 |
|------|------|
| 린트 | ✅ 통과 / ⚠️ 경고 N건 |
| CodeRabbit | Critical N, High N, Medium N |

---

## 🔍 리뷰 종합

### CodeRabbit 결과 검토
- ✅ 동의: N건 (Claude도 같은 이슈 발견)
- ❌ 반박: N건 (오탐, 반박 이유 명시)
- ➖ 수용: N건 (CodeRabbit만 발견, 유효한 지적)

### Claude 추가 발견
- ➕ N건 (CodeRabbit이 놓친 이슈)

---

## 🔍 비즈니스 규칙 검증

### 상태 변수 영향도
| 변수명 | 할당점 | 기존 규칙 | 새 코드 | 검증 결과 |
|--------|--------|----------|---------|-----------|
| {변수} | {N}개 | {규칙} | {상태} | ✅/❌ |

### 요구사항 역추적
| 요구사항 | spec.md | 구현 상태 | 검증 결과 |
|----------|---------|----------|-----------|
| {항목} | ✅ | ✅/❌ | ✅/❌ |

### 유사 패턴 비교
| 항목 | 기존 패턴 | 새 패턴 | 일관성 |
|------|----------|---------|--------|
| {항목} | {패턴} | {패턴} | ✅/❌ |

### 기능 충돌 분석
| 기존 기능/모드 | 충돌 가능성 | 영향 | 권장 조치 |
|---------------|------------|------|----------|
| {기능} | 높음/중간/낮음 | {영향} | {조치} |

---

## 코드 리뷰

### ✅ 좋은 점
- {긍정적 요소 1}
- {긍정적 요소 2}

### ⚠️ 개선 제안

#### 🔴 Critical (머지 전 필수)

**[1] 파일: `path/to/file.swift:42`**
- **문제**: {문제 설명}
- **영향**: {영향 범위}
- **개선안**:
```diff
- 삭제할 코드
+ 추가할 코드
```

#### 🟠 High

**[2] 파일: `path/to/file.swift:100`**
- **문제**: {문제 설명}
- **개선안**: {제안}

#### 🟡 Medium / 🟢 Low

(같은 형식)

---

## iOS DoD 체크리스트

| 항목 | 상태 | 비고 |
|------|------|------|
| Swift 6 concurrency | ✅/❌ | - |
| 메모리 관리 | ✅/❌ | - |
| SwiftUI 성능 | ✅/❌ | - |
| iOS 규칙 준수 | ✅/❌ | - |
| 에러 처리 | ✅/❌ | - |

---

## 📊 영향도 분석

### 변경된 주요 흐름
```
[기존 흐름]
   ↓
[새로운 흐름]
```

### 영향받는 컴포넌트
- ✅ {직접 영향}: {설명}
- ⚠️ {간접 영향}: {설명}
- ⬜ {영향 없음}: {설명}

---

## 판정

| 항목 | 결과 |
|------|------|
| **최종 판정** | ✅ 승인 / ❌ 변경요청 |
| Critical 이슈 | 0건 |
| High 이슈 | 0건 |
| 권장 수정 | N건 |

---

## 액션 아이템

### 필수 (Blocking)
1. [ ] {항목}

### 권장 (Non-blocking)
1. [ ] {항목}

---

*Reviewed by ai-dev.review*
```

---

## Codex MCP 통합 (--full 옵션)

`--full` 옵션 사용 시 Codex MCP와 병렬 실행됩니다:

| 관점 | Codex MCP | Claude |
|------|-----------|--------|
| 보안 취약점 | 패턴 매칭 스캔 | 로직 흐름 분석 |
| 성능 | 명백한 안티패턴 | 복잡도/메모리 분석 |
| 코드 스타일 | 린터 규칙 기반 | 팀 컨벤션 이해 |
| 아키텍처 | - | 설계 원칙 검토 |

**결과 충돌 시**: Claude 판단 우선

**MCP 호출 패턴:**
```
mcp__codex__codex(
  prompt: "{리뷰 요청}",
  cwd: "/Users/allen/Dev/Repo/kidsnote_ios",
  approval-policy: "on-failure",
  sandbox: "read-only"
)
```

---

## 옵션

| 옵션 | 설명 | 예시 |
|------|------|------|
| `--quick` | 빠른 리뷰 (Critical만, biz-rules 제외) | 긴급 수정 시 |
| `--full` | Codex/다른 LLM과 병렬 크로스체크 | 중요 변경 시 |
| `--biz-rules` | 비즈니스 규칙 검증 활성화 (기본값) | - |
| `--no-biz-rules` | 비즈니스 규칙 검증 비활성화 | 단순 수정 시 |
| `--deep` | 전체 검증 (biz-rules의 모든 하위 단계 실행) | 중요 기능 변경 |

### 옵션 조합 예시

```bash
# 기본 (비즈니스 규칙 검증 포함)
/ai-dev.review PK-32398

# 전체 검증 + Codex 크로스체크
/ai-dev.review PK-32398 --full --deep

# 빠른 리뷰 (긴급 핫픽스)
/ai-dev.review PK-32398 --quick

# 비즈니스 규칙 검증만 제외
/ai-dev.review PK-32398 --no-biz-rules
```

---

## 예제

### 예제 1: 기본 리뷰

```
User: /ai-dev.review PK-32398

Claude: [ai-dev.review 활성화]

자동 검증 중...
✅ 린트 통과
✅ CodeRabbit: Critical 0, High 0, Medium 2

코드 리뷰 중...
변경 파일: 5개

---
# PK-32398 코드 리뷰 결과

## 🔍 리뷰 종합

### CodeRabbit 결과 검토
- ✅ 동의: 1건 (디바운스 미적용)
- ❌ 반박: 1건 (불필요한 지적)
  - Medium: "변수명 개선" → 현재 네이밍이 AGENTS.md 규칙에 부합
- ➖ 수용: 0건

### Claude 추가 발견
- ➕ 0건

## ✅ 좋은 점
- 검색 로직이 깔끔하게 분리됨
- AGENTS.md 컨벤션 준수

## ⚠️ 개선 제안

### 🟡 Medium

**[1] StudentListReactor.swift:142**
- **문제**: 검색 디바운스 미적용
- **개선안**: `.debounce(.milliseconds(300), scheduler: MainScheduler.instance)` 추가

## 판정
**✅ 승인** (Critical/High 이슈 없음)
---

승인되었습니다. PR을 생성하시겠습니까?
→ /ai-dev.pr PK-32398
```

### 예제 2: 병렬 크로스체크 (--full)

```
User: /ai-dev.review PK-32398 --full

Claude: [ai-dev.review 활성화] (3자 크로스체크 모드)

## 자동 검증

| 항목 | 결과 |
|------|------|
| 린트 | ✅ 통과 |
| CodeRabbit | Critical 0, High 0, Medium 1 |

병렬 리뷰 시작:
1. Codex MCP: 빠른 스캔
   [mcp__codex__codex 실행]
2. Claude: 심도 분석 (진행 중)

---

## 🔍 리뷰 종합 (3자 크로스체크)

### CodeRabbit 결과 검토
- ✅ 동의: 1건 (검색 디바운스)
- ❌ 반박: 0건
- ➖ 수용: 0건

### Codex MCP 결과 검토
| 카테고리 | 발견 | 심각도 |
|---------|------|--------|
| 보안 | 이상 없음 | 🟢 |
| 성능 | 디바운스 제안 | 🟡 |

### 크로스체크 종합
| 동의 수준 | 이슈 | 판정 |
|----------|------|------|
| 3/3 동의 | 검색 디바운스 | 확정 이슈 |

### Claude 추가 발견
- ➕ 0건

### 📊 최종 이슈 목록
| 심각도 | 건수 | 조치 |
|--------|------|------|
| Critical | 0 | - |
| High | 0 | - |
| Medium | 1 | 리포트 |
| Low | 0 | - |

## 판정
**✅ 승인** (Critical/High 이슈 없음)
---

승인되었습니다. PR을 생성하시겠습니까?
→ /ai-dev.pr PK-32398
```

### 예제 3: 비즈니스 규칙 검증으로 충돌 발견

```
User: /ai-dev.review PK-32581

Claude: [ai-dev.review 활성화]

자동 검증 중...
✅ 린트 통과
✅ CodeRabbit: Critical 0, High 0, Medium 0

spec.md 확인 중...
✅ 발견: .claude/contexts/work/kidsnote/docs/ai-dev/PK-32581-알림장작성스킴/spec.md

비즈니스 규칙 검증 중...

---
# PK-32581 코드 리뷰 결과

## 🔍 비즈니스 규칙 검증

### 상태 변수 영향도

#### 상태 변수: isTimeLineMode

**용도**: 추억보기 모드 (읽기 전용 상태)

**할당점 (9개)**:
| 파일 | 조건 | 설정값 |
|------|------|--------|
| MainCoordinator.swift:664 | schemeMemoriesAlbum | false |
| MainCoordinator.swift:699 | schemeReport | false |
| MainCoordinator.swift:870 | schemeMoments | true |
| ... | ... | ... |

**검사점 (4개)**:
| 파일 | 조건 | 동작 |
|------|------|------|
| ReportTableViewController.m:1886 | touchWrite | 차단 알림 표시 |
| ReportArchiveViewController.swift:380 | checkWriteReportEnable | 작성 차단 |

**새 코드 검증**:
- [x] 적절한 할당: schemeReportWrite에서 false 설정
- [ ] **적절한 검사: ❌ 추억보기 모드 상태 체크 누락!**

**위험 평가**: 🔴 높음

### 유사 패턴 비교

| 항목 | schemeReport (기존) | schemeReportWrite (신규) | 일관성 |
|------|-------------------|------------------------|--------|
| isTimeLineMode 체크 | ✅ 있음 | ❌ 없음 | ❌ |
| 에러 핸들링 | ✅ | ✅ | ✅ |

### 기능 충돌 분석

| 기존 기능/모드 | 충돌 가능성 | 영향 | 권장 조치 |
|---------------|------------|------|----------|
| 추억보기 모드 | 🔴 높음 | 작성 화면 진입 가능 | isTimeLineMode 체크 추가 |

**충돌 시나리오**:
1. 전제조건: isTimeLineMode = true (추억보기 중)
2. 사용자 액션: kidsnote://report/write 스킴 호출
3. 기대 결과: 목록으로 fallback (작성 차단)
4. 실제 결과: 작성 화면 진입됨
5. 충돌 여부: ❌ 규칙 위반

---

## ⚠️ 개선 제안

### 🔴 Critical (머지 전 필수)

**[1] 파일: `MainCoordinator.swift:700`**
- **문제**: schemeReportWrite에서 추억보기 모드 체크 누락
- **영향**: 추억보기 모드에서 의도치 않게 작성 화면 진입 가능
- **개선안**:
```diff
case .schemeReportWrite:
+   if UserInfo.shared().isTimeLineMode {
+       showReport(data: nil)  // 목록으로 fallback
+       return
+   }
    UserInfo.shared().isTimeLineMode = false
    let schemeData: [String: Any] = ["openWrite": "true"]
    showReport(data: schemeData)
```

---

## 판정
**❌ 변경요청** (Critical 이슈 1건)

---

Critical 이슈를 수정한 후 다시 리뷰해주세요.
수정 후: /ai-dev.review PK-32581
```

---

## 다음 단계

### 리뷰 완료 후 GitHub 코멘트

리뷰가 완료되면 사용자에게 GitHub 리뷰 코멘트 남길지 질문:

```
리뷰가 완료되었습니다.

GitHub에 리뷰를 남기시겠습니까?
1. ✅ 승인 (Approve)
2. 💬 코멘트만 (Comment)
3. ❌ 변경요청 (Request Changes)
4. 🚫 남기지 않음
```

**GitHub 리뷰 코멘트 명령어:**
```bash
# 승인
gh pr review {PR_NUMBER} --approve --body "LGTM! ✅"

# 코멘트만
gh pr review {PR_NUMBER} --comment --body "{리뷰 요약}"

# 변경요청
gh pr review {PR_NUMBER} --request-changes --body "{개선 사항}"
```

### 승인 시

```
리뷰가 승인되었습니다.

다음 단계로 PR을 생성하시겠습니까?
→ /ai-dev.pr PK-32398
```

### 변경요청 시

```
❌ 변경요청

Critical 이슈를 수정한 후 다시 리뷰해주세요.
수정 후: /ai-dev.review PK-32398
```

---

## 연계 스킬

| 스킬 | 용도 |
|------|------|
| `/ai-dev.impl` | 선행 구현 (필수) |
| `/ai-dev.pr` | 후속 PR 생성 |
| `/codex-hotfix` | 발견된 이슈 빠른 수정 |

---

**Created:** 2026-01-23
**Updated:** 2026-01-28
**Version:** 4.0 (비즈니스 규칙 검증 추가 - 상태 변수 영향도, 요구사항 역추적, 유사 패턴 비교, 기능 충돌 분석)
