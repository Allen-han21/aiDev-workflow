---
name: ai-dev.code-check
description: 구현된 코드의 품질을 검증. DRY/SOLID/Complexity 분석. "품질 검사", "code check", "코드 체크" 요청 시 활성화.
---

# Skill: ai-dev.code-check

구현된 코드의 품질을 정적 분석 + 구조 분석으로 검증합니다. (review에서 분리된 품질 전용)

---

## 목적

- 코드 중복 (DRY 원칙) 검증
- 설계 원칙 (SOLID) 준수 확인
- 복잡도 분석 및 개선 제안
- 문서화 상태 확인

---

## ai-dev.review와의 차이

| 항목 | ai-dev.code-check | ai-dev.review |
|------|-------------------|---------------|
| **목적** | 코드 품질 검증 | 최종 승인 판정 |
| **검증 대상** | 구조/패턴/복잡도 | 기능 정확성/보안/비즈니스 규칙 |
| **실행 시점** | impl 직후 | code-check + work-check 후 |
| **출력** | 품질 리포트 + 개선 제안 | 승인/변경요청 판정 |

---

## 사용 시점

- `/ai-dev.code-check PK-XXXXX` - 품질 검사 시작
- `ai-dev.impl` 완료 후, `ai-dev.work-check` 실행 전
- 코드 리뷰 전 자체 점검

---

## 워크플로우

```
┌─────────────────────────────────────────────────────────────────┐
│                    ai-dev.code-check 워크플로우                   │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  [Step 1] 변경 파일 식별                                         │
│  git diff --name-only HEAD~N                                    │
│                                                                 │
│  [Step 2] 정적 분석 (자동)                                       │
│  ├── SwiftLint                                                  │
│  ├── Build 검증                                                 │
│  └── Architecture 위반 체크                                     │
│                                                                 │
│  [Step 3] 품질 분석 (병렬 3개)                                   │
│  ┌─────────────┬─────────────┬─────────────┐                   │
│  │ DRY Checker │ SOLID       │ Complexity  │                   │
│  │ 중복 코드   │ Checker     │ Analyzer    │                   │
│  │             │ 설계 원칙   │ 복잡도      │                   │
│  └──────┬──────┴──────┬──────┴──────┬──────┘                   │
│         └─────────────┼─────────────┘                           │
│                       ▼                                         │
│  [Step 4] 문서화 검증                                            │
│  문서화 주석 존재 여부                                           │
│                       ▼                                         │
│  [Step 5] 리포트 생성                                            │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

---

## 정적 분석 (Step 2)

### SwiftLint

```bash
swiftlint lint --quiet --reporter json
```

### Build 검증

```bash
xcodebuild build \
  -workspace KidsNote.xcworkspace \
  -scheme "kidsnote Development" \
  -destination "generic/platform=iOS Simulator" \
  -quiet
```

### Architecture 위반 체크

```bash
# UI → Repository 직접 호출 (위반)
Grep: "Repository\." --path Sources/Views/ --type swift

# Entity에서 UIKit import (위반)
Grep: "import UIKit|import SwiftUI" --path Sources/Entity/ --type swift

# Service에서 ViewController import (위반)
Grep: "ViewController" --path Sources/Services/ --type swift
```

---

## 품질 분석 (Step 3) - 병렬 5개

> **v1.1 추가**: Pattern Consistency Checker, Test Support Checker
> (PR #7360, #7361 qazqaz1000 ios-review 스킬 피드백 반영)

### 1. DRY Checker (중복 검증)

**역할**: 코드 중복 감지 및 공통화 제안

**검증 항목**:
- 10줄 이상 유사한 코드 블록
- 동일한 로직 패턴 반복
- 공통 유틸리티로 추출 가능한 코드

**프롬프트 요약**:
```
변경된 파일에서 중복 코드를 찾으세요.
10줄 이상 유사한 코드 블록을 식별하세요.
공통 함수/Extension 추출을 제안하세요.
```

**출력 형식**:
```markdown
| 파일 A | 파일 B | 유사도 | 라인 | 제안 |
|--------|--------|--------|------|------|
| {파일} | {파일} | 85%    | 15줄 | {공통 함수 추출} |
```

### 2. SOLID Checker (설계 원칙)

**역할**: SOLID 원칙 위반 감지

**검증 항목**:

| 원칙 | 위반 징후 |
|------|----------|
| **SRP** | 클래스가 여러 책임 (UI + 비즈니스 로직 + 데이터) |
| **OCP** | 확장 대신 수정 필요한 구조 (긴 if-else/switch) |
| **LSP** | 서브타입이 부모 계약 위반 |
| **ISP** | 사용하지 않는 프로토콜 메서드 강제 구현 |
| **DIP** | 구체 타입에 직접 의존 (추상화 없음) |

**프롬프트 요약**:
```
변경된 파일에서 SOLID 원칙 위반을 찾으세요.
각 원칙별로 위반 사례와 개선 방법을 제안하세요.
```

### 3. Complexity Analyzer (복잡도 분석)

**역할**: 코드 복잡도 측정 및 개선 제안

**검증 항목**:

| 항목 | 임계치 | 조치 |
|------|--------|------|
| Cyclomatic Complexity | > 10 | 함수 분해 권장 |
| 중첩 깊이 | > 4 | Early return 적용 |
| 함수 길이 | > 50줄 | 분리 권장 |
| 파라미터 개수 | > 5개 | 객체로 묶기 |
| 클래스 길이 | > 500줄 | 분리 권장 |

**프롬프트 요약**:
```
변경된 파일의 복잡도를 분석하세요.
임계치를 초과하는 함수/클래스를 식별하세요.
복잡도 감소를 위한 구체적 방법을 제안하세요.
```

### 4. Pattern Consistency Checker (패턴 일관성) 🆕

**역할**: 기존 코드와의 패턴 일관성 검증

**검증 항목**:
- 유사 기능의 기존 구현 패턴과 일치 여부
- 상태 변수 사용 패턴 (is*, has*, should*)
- 에러 처리 패턴 일관성
- 초기화 순서 일관성
- API 호출 패턴 일관성

**프롬프트 요약**:
```
기존 코드와의 패턴 일관성을 검증하세요:
- 유사한 기능이 이미 구현되어 있나요? 패턴이 일치하나요?
- 상태 변수 사용이 기존 코드와 일관적인가요?
- 에러 처리 방식이 동일한가요?
- 초기화 순서가 기존 패턴을 따르나요?

Grep으로 유사 함수명/패턴을 찾아 비교하세요.
[질문] 태그로 의도된 차이인지 확인 요청하세요.
```

**출력 형식**:
```markdown
| 새 코드 | 기존 패턴 | 일치 여부 | 비고 |
|---------|----------|----------|------|
| {함수} | {기존 함수} | ✅/⚠️ | {차이점} |

**[질문]** {기존 함수}에서는 {패턴}을 사용하는데,
새 코드에서 {다른 패턴}을 사용한 것은 의도된 차이인가요?
```

**Neo4j 그래프 기반 자동 패턴 비교** (선택적):

Neo4j MCP 서버 (`neo4j-code-graph`) 연결 시 유사 코드를 자동으로 조회합니다.

```bash
# 유사도 85% 이상 파일 자동 조회
mcp__neo4j-code-graph__neo4j_query(cypher: "
  MATCH (target:CodeFile)-[r:SIMILAR_TO]-(similar:CodeFile)
  WHERE target.name CONTAINS '{변경된파일명}'
  AND r.score > 0.85
  RETURN similar.name, similar.module, r.score
  ORDER BY r.score DESC LIMIT 5
")
```

**Neo4j 출력 형식**:
```markdown
#### 유사 코드 자동 발견 (Neo4j)

| 유사 파일 | 모듈 | 유사도 | 비교 결과 |
|----------|------|--------|----------|
| {파일명} | {모듈} | 92% | 동일 패턴 확인 |
| {파일명} | {모듈} | 87% | ⚠️ 초기화 순서 다름 |
```

**Fallback**: Neo4j 연결 실패 시 기존 Grep 기반 유사 함수 검색만 수행

### 5. Test Support Checker (테스트 지원) 🆕

**역할**: 테스트 용이성 및 테스트 코드 존재 여부 검증

**검증 항목**:
- 테스트 가능한 구조인지 (의존성 주입, 프로토콜 사용)
- 관련 테스트 파일 존재 여부
- 테스트 케이스 추가 필요 여부
- URLSchemeTestView 등 개발/QA 지원 도구 업데이트 여부

**프롬프트 요약**:
```
테스트 지원을 검증하세요:
- 새 기능에 대한 테스트 파일이 있나요?
- 의존성 주입이 가능한 구조인가요?
- URLSchemeTestView 등 개발 도구에 테스트 케이스가 추가되었나요?
- Mock/Stub 생성이 용이한 구조인가요?

Glob으로 *Tests.swift, *Test.swift 파일을 확인하세요.
```

**출력 형식**:
```markdown
| 항목 | 상태 | 비고 |
|------|------|------|
| 테스트 파일 존재 | ✅/❌ | {파일명} |
| 테스트 케이스 추가 | ✅/❌ | {추가된 케이스} |
| 개발 도구 업데이트 | ✅/❌ | URLSchemeTestView 등 |
| DI 가능 구조 | ✅/⚠️ | {의존성 주입 상태} |
```

---

## 문서화 검증 (Step 4)

### 검증 항목

| 대상 | 필수 여부 | 형식 |
|------|----------|------|
| public/internal 메서드 | 필수 | `/// 문서화 주석` |
| 복잡한 로직 | 권장 | 인라인 주석 |
| 클래스/구조체 | 필수 | `/// [목적]`, `/// [기능]` |

### 검증 방법

```bash
# 문서화 주석 없는 public 함수
Grep: "public func|internal func" --type swift
# 결과에서 /// 주석 없는 항목 필터링
```

---

## 출력 템플릿

```markdown
# {TICKET_ID} Code Quality Report

**검증일**: YYYY-MM-DD HH:MM
**변경 파일**: N개
**총 라인**: N줄

---

## 정적 분석

| 항목 | 결과 | 상세 |
|------|------|------|
| SwiftLint | ✅ 경고 0개 | - |
| Build | ✅ 성공 | - |
| Architecture | ✅ 위반 0개 | - |

---

## 품질 분석

### DRY (중복 검증)

**상태**: ✅ 양호 / ⚠️ 개선 필요

| 파일 A | 파일 B | 유사도 | 라인 | 제안 |
|--------|--------|--------|------|------|
| {파일} | {파일} | 85%    | 15줄 | 공통 Extension 추출 |

**개선 제안**:
```swift
// Before (중복)
// File A
let formatted = formatter.string(from: date)

// File B
let formatted = formatter.string(from: date)

// After (공통화)
extension Date {
    var formatted: String {
        return DateFormatter.shared.string(from: self)
    }
}
```

### SOLID (설계 원칙)

**상태**: ✅ 양호 / ⚠️ 개선 필요

| 원칙 | 상태 | 위반 파일 | 설명 |
|------|------|----------|------|
| SRP | ✅ | - | - |
| OCP | ⚠️ | {파일} | 긴 switch문 |
| LSP | ✅ | - | - |
| ISP | ✅ | - | - |
| DIP | ⚠️ | {파일} | 구체 타입 직접 의존 |

**개선 제안**:
```swift
// Before (OCP 위반)
switch type {
case .typeA: ...
case .typeB: ...
case .typeC: ...  // 새 타입 추가 시 수정 필요
}

// After (OCP 준수)
protocol TypeHandler {
    func handle()
}
let handler = TypeHandlerFactory.make(type)
handler.handle()
```

### Complexity (복잡도)

**상태**: ✅ 양호 / ⚠️ 개선 필요

| 파일 | 함수명 | CC | 중첩 | 라인 | 제안 |
|------|--------|-----|------|------|------|
| {파일} | {함수} | 15 | 5 | 80 | 함수 분해 |

**개선 제안**:
- `processData()` → `validateInput()` + `transformData()` + `saveResult()`로 분리
- 중첩 깊이 감소: guard early return 적용

### Pattern Consistency (패턴 일관성) 🆕

**상태**: ✅ 양호 / ⚠️ 확인 필요

| 새 코드 | 기존 패턴 | 일치 | 비고 |
|---------|----------|------|------|
| {handleMomentsScheme} | {setMoments} | ⚠️ | 체험계정 처리 차이 |

**[질문]**: 기존 `setMoments`에서는 체험 계정 체크가 없는데,
새 `handleMomentsScheme`에서 체험 계정을 제외한 것은 의도된 차이인가요?

### Test Support (테스트 지원) 🆕

**상태**: ✅ 양호 / ⚠️ 개선 필요

| 항목 | 상태 | 비고 |
|------|------|------|
| 테스트 파일 존재 | ✅/❌ | {파일명} |
| 테스트 케이스 추가 | ✅/❌ | {추가된 케이스} |
| 개발 도구 업데이트 | ✅ | URLSchemeTestView |
| DI 가능 구조 | ✅/⚠️ | {상태} |

---

## 문서화

| 항목 | 상태 | 누락 |
|------|------|------|
| Public 메서드 | ✅ 완료 / ⚠️ N개 누락 | {목록} |
| 클래스/구조체 | ✅ 완료 / ⚠️ N개 누락 | {목록} |
| 복잡 로직 주석 | ✅ 완료 / ⚠️ N개 누락 | {목록} |

---

## 종합 판정

| 항목 | 결과 |
|------|------|
| **품질 등급** | A (우수) / B (양호) / C (개선 필요) / D (수정 필요) |
| 정적 분석 | ✅ 통과 |
| DRY | ✅/⚠️ |
| SOLID | ✅/⚠️ |
| Complexity | ✅/⚠️ |
| Pattern Consistency 🆕 | ✅/⚠️ |
| Test Support 🆕 | ✅/⚠️ |
| 문서화 | ✅/⚠️ |

**등급 기준**:
- A: 모든 항목 통과
- B: 경미한 개선 사항 1-2개
- C: 개선 필요 항목 3개 이상
- D: 정적 분석 실패 또는 심각한 위반

---

## 권장 조치

### 필수 (Blocking)
1. [ ] {정적 분석 오류 수정}

### 권장 (Non-blocking)
1. [ ] {중복 코드 공통화}
2. [ ] {복잡도 높은 함수 분해}

---

## 다음 단계

- ✅ A/B 등급: `/ai-dev.work-check` 진행
- ⚠️ C 등급: 권장 조치 검토 후 진행 결정
- ❌ D 등급: 필수 조치 완료 후 재검증

---

*Analyzed by ai-dev.code-check*
```

---

## 파일 경로

```
~/.claude/contexts/work/kidsnote/docs/ai-dev/{PK-xxxx}/
├── ...
└── code-check-report.md  ← 생성
```

---

## 연계 스킬

| 스킬 | 용도 |
|------|------|
| `/ai-dev.impl` | 선행 (코드 구현) |
| `/ai-dev.work-check` | 후속 (버그 검증) |

---

**Created:** 2026-01-28
**Updated:** 2026-01-29
**Version:** 1.1 (PR #7360, #7361 피드백 반영: Pattern Consistency, Test Support 체커 추가)
