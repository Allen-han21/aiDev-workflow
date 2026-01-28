---
name: ai-dev.spec
description: 분석 결과 기반 스펙 확정. Claude와 Codex 크로스 체크 후 사용자 승인. "스펙 정의해줘", "스펙 작성해줘", "요구사항 분석해줘" 요청 시 활성화.
---

# Skill: ai-dev.spec

분석 결과(analyze.md)를 Claude와 Codex로 크로스 체크하여 스펙을 확정합니다.

---

## 전제 조건

**plan mode에서 실행**

**필수 선행**: analyze.md 존재

---

## 사용법

```bash
/ai-dev.spec PK-XXXXX
```

---

## 옵션

| 옵션 | 설명 | 예시 |
|------|------|------|
| `--no-codex` | Codex MCP 크로스 체크 비활성화 | Claude 멀티 관점 분석으로 대체 |
| `--ultrathink` | Extended thinking 활성화 | 복잡한 아키텍처/비즈니스 로직 분석 시 |

### 옵션 조합 예시

```bash
# 기본 (Codex 사용)
/ai-dev.spec PK-12345

# Codex 쿼터 절약
/ai-dev.spec PK-12345 --no-codex

# 복잡한 문제 (ultrathink)
/ai-dev.spec PK-12345 --ultrathink

# 복잡한 문제 + Codex 쿼터 없음 (최고 품질)
/ai-dev.spec PK-12345 --no-codex --ultrathink

# 옵션 먼저도 가능
/ai-dev.spec --no-codex --ultrathink PK-12345
```

> **참고**: 옵션 위치는 자유롭습니다.

---

## 워크플로우

### Step 1: analyze.md 읽기

```
~/.claude/contexts/work/kidsnote/docs/ai-dev/{PK-xxxx-개발내용}/analyze.md
```

analyze.md가 없으면 안내:
```
analyze.md가 없습니다.
먼저 분석을 실행하세요: /ai-dev.analyze PK-XXXXX
```

### Step 2: 모델 최적화 질문 생성

analyze.md 내용을 기반으로 구조화된 질문 생성:

```markdown
## 스펙 정의 요청

### 프로젝트 정보
- 프로젝트: kidsnote_ios
- 아키텍처: UIKit + ReactorKit (기존) / SwiftUI + ViewModel (신규)
- 의존성: RxSwift, SnapKit, Dependencies (pointfreeco)

### 요구사항 요약
{analyze.md 핵심 요약}

### 분석 파일 참조
경로: ~/.claude/contexts/work/kidsnote/docs/ai-dev/{폴더}/analyze.md

### 질문
1. 이 기능의 핵심 비즈니스 로직은 무엇인가?
2. 데이터 모델(Entity)은 어떻게 설계해야 하는가?
3. 예외 처리는 어떻게 해야 하는가?
4. 테스트 시나리오는 무엇인가?
```

### Step 3: 분석 실행

#### 옵션 분기

| 옵션 | 실행 방식 |
|------|----------|
| 기본 (옵션 없음) | → Step 3-A: Claude + Codex 병렬 |
| `--no-codex` | → Step 3-B: Claude 멀티 관점 분석 |
| `--ultrathink` | → 선택된 방식에 ultrathink prefix 추가 |

---

### Step 3-A: Claude + Codex 병렬 질문 (기본)

#### `--ultrathink` 활성화 시 프롬프트 prefix

```
ultrathink해서 다음 요구사항을 분석해줘.
아주 신중하게, 깊이 있게 분석하고 결론을 내려줘.
```

#### Claude (내부) 분석

현재 컨텍스트에서 직접 스펙 분석 수행:
- 대화 맥락 이해
- 사용자 의도 파악
- 아키텍처 일관성 고려

#### Codex MCP 호출

```
mcp__codex__codex(
  prompt: "{모델 최적화 질문}",
  cwd: "/Users/allen/Dev/Repo/kidsnote_ios",
  approval-policy: "on-failure",
  sandbox: "read-only"
)
```

**반환값 저장:**
- `threadId`: 후속 대화용
- `response`: Codex 분석 결과

→ **Step 4-A로 이동**

---

### Step 3-B: Claude 멀티 관점 분석 (`--no-codex`)

Codex 대신 Claude가 **세 가지 관점**에서 분석합니다.

#### `--ultrathink` 활성화 시 프롬프트 prefix

```
ultrathink해서 다음 요구사항을 분석해줘.
아주 신중하게, 깊이 있게 분석하고 결론을 내려줘.
```

#### 관점 1: 아키텍처 분석가

```
다음 요구사항을 아키텍처 관점에서 분석합니다:

{analyze.md 요약}

분석 항목:
1. 기존 아키텍처와의 일관성 (UIKit+ReactorKit / SwiftUI+ViewModel)
2. 계층 분리 적절성 (Data/Domain/Presentation)
3. 의존성 방향 검토 (DI 패턴 준수)
4. 영향 범위 예측
```

#### 관점 2: 코드 품질 엔지니어

```
다음 요구사항을 코드 품질 관점에서 분석합니다:

{analyze.md 요약}

분석 항목:
1. AGENTS.md 코딩 컨벤션 준수 가능성
2. 테스트 가능성 (단위 테스트 작성 용이성)
3. 유지보수성 (변경 시 영향 최소화)
4. 코드 재사용성
```

#### 관점 3: 비즈니스 로직 검토자

```
다음 요구사항을 비즈니스 로직 관점에서 분석합니다:

{analyze.md 요약}

분석 항목:
1. 요구사항 충족 여부 (JIRA 티켓 내용)
2. 엣지 케이스 처리 완전성
3. 에러 핸들링 전략
4. UX 일관성
```

#### 추가 검증: 유사 구현 참조

기존 코드베이스에서 유사한 패턴 검색:
```bash
# 유사 기능 구현 찾기
Grep: "{기능 키워드}" --type swift
Read: 발견된 핵심 파일 1-2개
```

→ **Step 4-B로 이동**

---

### Step 4-A: 크로스 체크 (기본 모드)

#### 4.1 Claude에게 Codex 답변 전달

```
Codex의 스펙 분석 결과입니다:

{Codex 답변}

이 분석에 대해:
1. 동의하는 점
2. 보완이 필요한 점
3. 다른 관점에서의 제안
을 알려주세요.
```

#### 4.2 Codex에게 Claude 답변 전달

```
mcp__codex__codex-reply(
  threadId: "{이전 thread_id}",
  prompt: "다른 분석가의 의견입니다:

{Claude 답변}

이 의견에 대해:
1. 동의하는 점
2. 보완이 필요한 점
3. 최종 권장 사항
을 알려주세요."
)
```

→ **Step 5로 이동**

---

### Step 4-B: 셀프 크로스 체크 (`--no-codex`)

각 관점의 분석 결과를 교차 검증:

| 분류 | 조건 | 처리 |
|------|------|------|
| 전체 동의 | 세 관점 모두 동의 | → spec.md에 반영 |
| 부분 충돌 | 2개 이상 관점 충돌 | → AskUserQuestion으로 선택 요청 |
| 불확실 | 추가 정보 필요 | → AskUserQuestion으로 확인 |

→ **Step 5로 이동**

---

### Step 5: 종합

크로스 체크 결과를 종합:

**종합 스펙 초안:**

| 분류 | 내용 |
|------|------|
| 공통 합의 사항 | 양측 모두 동의한 내용 → spec.md에 반영 |
| 선택적 권장 사항 | 양측 의견이 다른 경우 → AskUserQuestion으로 사용자 선택 |
| 미결정 사항 | 추가 정보 필요 → AskUserQuestion으로 확인 |

### Step 6: 사용자 검증/승인

```
AskUserQuestion([
  {
    question: "스펙 초안이 생성되었습니다. 선택이 필요한 사항입니다.",
    header: "스펙 확정",
    options: [
      { label: "승인", description: "현재 스펙으로 진행" },
      { label: "수정 필요", description: "추가 조정 후 재검토" }
    ]
  },
  {
    question: "{선택 사항 1}: A안 vs B안",
    header: "{항목명}",
    options: [
      { label: "A안 (Claude 권장)", description: "{설명}" },
      { label: "B안 (Codex 권장)", description: "{설명}" }
    ]
  }
])
```

### Step 7: spec.md 생성

사용자 승인 후 저장:

```
~/.claude/contexts/work/kidsnote/docs/ai-dev/{PK-xxxx-개발내용}/spec.md
```

---

## 출력 템플릿

```markdown
# {TICKET_ID} 스펙

**확정일**: YYYY-MM-DD HH:MM
**티켓**: {TICKET_ID} - {제목}
**검증**: [기본] Claude + Codex 크로스 체크 완료
         [--no-codex] Claude 멀티 관점 분석 완료 (아키텍처/품질/비즈니스)
         [--ultrathink] Extended thinking 활성화

---

## 1. 개요

### 기능 설명
{한 줄 설명}

### 목표
- {목표 1}
- {목표 2}

---

## 2. 상세 스펙

### 2.1 화면/기능 설명

{상세 동작 설명}

**Figma**: {링크}

### 2.2 데이터 모델

```swift
/// [목적] {Entity} 데이터 표현
struct {Entity}Entity: Codable {
    let id: Int
    let name: String
    // ...
}
```

### 2.3 비즈니스 규칙

1. {규칙 1}
2. {규칙 2}

### 2.4 엣지 케이스 처리

| 케이스 | 조건 | 처리 방법 |
|--------|------|----------|
| 빈 데이터 | 결과 0건 | EmptyView 표시 |
| 네트워크 오류 | 타임아웃 | 재시도 버튼 |
| {기타} | {조건} | {처리} |

---

## 3. 기술 노트

### 3.1 영향 범위

| 파일 | 변경 내용 |
|------|----------|
| {file} | {설명} |

### 3.2 의존성

- **API**: {엔드포인트}
- **라이브러리**: {라이브러리명}

---

## 4. 완료 조건

- [ ] {기능 조건 1}
- [ ] {기능 조건 2}
- [ ] 단위 테스트 작성
- [ ] 코드 리뷰 완료

---

## 5. 크로스 체크 결과

### [기본 모드] Claude + Codex 분석 요약

#### Claude 분석 요약
{Claude 핵심 포인트}

#### Codex 분석 요약
{Codex 핵심 포인트}

### [`--no-codex` 모드] Claude 멀티 관점 분석 요약

#### 아키텍처 분석가 관점
{분석 요약}

#### 코드 품질 엔지니어 관점
{분석 요약}

#### 비즈니스 로직 검토자 관점
{분석 요약}

### 합의/선택 사항
- **합의**: {공통 사항}
- **선택 (사용자)**: {선택된 사항}

---

## 6. 참조

- **analyze.md**: 코드베이스 분석 결과
- **JIRA**: {티켓 URL}
- **Figma**: {Figma URL}

---

*Generated by ai-dev.spec*
*Mode: [기본] Claude + Codex cross-check / [--no-codex] Claude multi-perspective analysis*
```

---

## 크로스 체크 메커니즘 상세

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

### 예제 1: 스펙 확정 + 크로스 체크

```
User: /ai-dev.spec PK-32398

Claude: [ai-dev.spec 활성화]

analyze.md 읽는 중...
경로: ~/.claude/contexts/work/kidsnote/docs/ai-dev/PK-32398-원생관리-검색기능/analyze.md

모델 최적화 질문 생성 중...

[병렬 분석 시작]

Claude 분석 중...
- 비즈니스 로직: 원생 이름/반 기준 실시간 필터링
- 데이터 모델: 기존 StudentEntity 활용
- 예외 처리: 빈 결과 시 EmptyView 표시

Codex MCP 호출 중...
[mcp__codex__codex 실행]

Codex 분석 결과:
- 비즈니스 로직: 디바운스 적용 검색
- 데이터 모델: SearchResult 래퍼 추가 제안
- 예외 처리: 토스트 메시지로 에러 표시

[크로스 체크]

Claude → Codex 검토:
- 동의: 디바운스 적용
- 보완: SearchResult 래퍼는 과도한 추상화, 기존 Entity 활용 권장
- 제안: 검색 히스토리 기능 고려

Codex → Claude 검토:
- 동의: 기존 Entity 활용 타당
- 보완: EmptyView보다 인라인 메시지가 UX상 좋음
- 권장: 디바운스 300ms 적용

[종합]
- 공통 합의: 디바운스 적용, 기존 Entity 활용
- 선택 필요: 에러 표시 방식 (EmptyView vs 인라인)

[AskUserQuestion]
빈 검색 결과 표시 방식을 선택해주세요:
1. EmptyView (Claude 권장) - 전체 화면 빈 상태
2. 인라인 메시지 (Codex 권장) - 목록 내 메시지

User: 2 선택

Claude: 스펙 확정 완료.

spec.md 저장됨.
경로: ~/.claude/contexts/work/kidsnote/docs/ai-dev/PK-32398-원생관리-검색기능/spec.md

다음 단계: /ai-dev.plan PK-32398
```

---

## 다음 단계

스펙 확정 후:

```
스펙이 확정되었습니다.

다음 단계로 구현 계획을 수립하시겠습니까?
→ /ai-dev.plan PK-32398
```

---

## 연계 스킬

| 스킬 | 용도 |
|------|------|
| `/ai-dev.analyze` | 선행 분석 (필수) |
| `/ai-dev.plan` | 후속 계획 수립 |

---

## Codex 수준 품질 확보 (`--no-codex` 모드)

### Codex가 제공하던 가치와 대체 방법

| Codex 기능 | Claude 대체 방법 |
|-----------|------------------|
| 독립적 코드 탐색 | Claude에게 "관련 코드 찾아줘" 명시적 요청 |
| 크로스 체크 | "세 가지 관점에서 분석해줘" 요청 |
| 구체적 패치 | "실제 코드 스니펫으로 보여줘" 명시 |

### 품질 보장 프롬프트 규칙

**`--no-codex` 모드 출력 기준:**

- ❌ 추상적 설명
- ✅ 구체적 코드 패치
- ✅ 파일 경로 전체 명시
- ✅ 실행 순서와 의존성 명시

**예시 (Bad vs Good):**

```
# Bad (추상적)
"ViewController에 검색 기능을 추가합니다"

# Good (구체적)
"Sources/Features/Student/StudentListViewController.swift의
setupUI() 메서드에 SearchBar 추가:

```swift
// Line 45 이후 추가
private lazy var searchBar: UISearchBar = {
    let bar = UISearchBar()
    bar.placeholder = "이름으로 검색"
    return bar
}()
```"
```

### 필수 검증 체크리스트

- [ ] 모든 파일 경로가 전체 경로로 명시됨
- [ ] 각 항목에 구체적 코드 스니펫 포함
- [ ] 의존성 순서가 명확히 표시됨
- [ ] 기존 유사 패턴 1개 이상 참조됨

---

**Created:** 2026-01-23
**Updated:** 2026-01-27
**Version:** 3.0 (--no-codex, --ultrathink 옵션 추가)
