---
name: ai-dev.work-check
description: 10개 병렬 버그 체커로 구현된 코드의 버그를 탐색. "버그 검사", "work check", "워크 체크" 요청 시 활성화.
---

# Skill: ai-dev.work-check

10개 전문화된 버그 체커가 병렬로 구현된 코드를 검사합니다.

---

## 목적

- 엣지 케이스, 경계값 버그 탐지
- 동시성 및 상태 관련 버그 탐지
- 메모리 누수 및 리소스 관리 문제 탐지
- 입력 검증 및 보안 취약점 탐지
- 회귀 버그 가능성 평가

---

## ai-dev.review와의 차이

| 항목 | ai-dev.work-check | ai-dev.review |
|------|-------------------|---------------|
| **목적** | 버그 사전 탐지 | 최종 승인 판정 |
| **방식** | 10개 전문 체커 병렬 | 종합 리뷰 |
| **초점** | 기술적 버그 | 비즈니스 규칙 + 기술 |
| **출력** | 버그 리포트 + 재현 시나리오 | 승인/변경요청 |

---

## 사용 시점

- `/ai-dev.work-check PK-XXXXX` - 버그 검사 시작
- `ai-dev.code-check` 완료 후, `ai-dev.review` 실행 전
- 중요 기능 구현 후 자체 점검

---

## 워크플로우

```
┌─────────────────────────────────────────────────────────────────┐
│                    ai-dev.work-check 워크플로우                   │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  [Step 1] 문서 및 코드 로드                                      │
│  spec.md + plan.md + 변경된 코드                                │
│                                                                 │
│  [Step 2] 10개 Bug Checkers 병렬 실행                           │
│  ┌────────────┬────────────┬────────────┐                      │
│  │ Edge Case  │ Race       │ State      │                      │
│  │ Hunter     │ Condition  │ Corruption │                      │
│  │            │ Detector   │ Finder     │                      │
│  ├────────────┼────────────┼────────────┤                      │
│  │ Memory     │ Input      │ Regression │                      │
│  │ Leak       │ Validation │ Detector   │                      │
│  │ Hunter     │ Checker    │            │                      │
│  ├────────────┼────────────┼────────────┤                      │
│  │ Localiz-   │ Platform   │ UX         │  🆕 v1.1             │
│  │ ation      │ Compat-    │ Feedback   │                      │
│  │ Checker    │ ibility    │ Checker    │                      │
│  ├────────────┴────────────┴────────────┤                      │
│  │  Rx Race Condition Checker 🆕 v1.2   │                      │
│  └─────┬────────────────────────────────┘                      │
│        └────────────┼────────────┘                              │
│                     ▼                                           │
│  [Step 3] Bug Triage                                            │
│  심각도 분류 + 재현 시나리오 작성                                 │
│                     ▼                                           │
│  [Step 4] 리포트 생성                                            │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

---

## 10개 Bug Checkers

> **v1.1 추가**: Localization Checker, Platform Compatibility Checker, UX Feedback Checker
> (PR #7360, #7361 CodeRabbit/qazqaz1000 리뷰 피드백 반영)
>
> **v1.2 추가**: Rx Race Condition Checker (grepai trace 활용, RxSwift/ReactorKit 경쟁 조건 탐지)

### 1. Edge Case Hunter (엣지 케이스)

**역할**: 경계값 및 특수 입력 버그 탐지

**검증 항목**:
- nil/empty 입력 처리
- 경계값 (0, -1, MAX_INT, 빈 배열)
- 특수문자, 유니코드, 이모지
- 극단적 길이 (매우 짧거나 긴 문자열)

**프롬프트 요약**:
```
각 함수/메서드에 대해 엣지 케이스를 분석하세요:
- nil/empty 입력 시 어떻게 동작하나요?
- 경계값 (0, -1, MAX) 처리는 안전한가요?
- 빈 배열/딕셔너리에서 크래시가 발생하나요?
- 특수문자/이모지 입력 시 문제가 있나요?

버그 발견 시 재현 시나리오를 작성하세요.
```

### 2. Race Condition Detector (동시성)

**역할**: 동시성 및 비동기 버그 탐지

**검증 항목**:
- 공유 상태 변수 동시 접근
- async/await 순서 의존성
- 여러 스레드 동시 접근 시나리오
- 데드락 가능 조건
- Main thread에서 UI 업데이트
- **[RxSwift/ReactorKit]** viewDidLoad Action 순서 vs 실행 순서
- **[RxSwift/ReactorKit]** 같은 State 필드를 변경하는 동시 Action
- **[RxSwift/ReactorKit]** 스케줄러 컨텍스트 (MainScheduler.instance vs asyncInstance)

**프롬프트 요약**:
```
동시성 관련 버그를 찾으세요:

[GCD/Swift Concurrency]
- 공유 상태에 여러 스레드가 접근하나요?
- async 작업의 순서가 보장되나요?
- UI 업데이트가 Main thread에서 이루어지나요?
- 데드락 가능성이 있나요?
- 특히 @MainActor, DispatchQueue, Task 사용을 확인하세요.

[RxSwift/ReactorKit] (grepai trace 활용 권장)
- viewDidLoad에서 여러 Action이 발생하나요?
  → bind 선언 순서 vs 실제 실행 순서 구분
  → 스케줄러 없는 bind는 동기적으로 순차 실행
  → observe(on: MainScheduler.asyncInstance)는 비동기 실행, 순서 미보장

- 같은 State 필드를 변경하는 여러 Action이 있나요?
  → Reactor.reduce에서 충돌 가능성 분석
  → Observable.merge 사용 시 실행 순서 미보장
  → Observable.concat 사용 시 순차 실행

- 스케줄러 컨텍스트 분석:
  → MainScheduler.instance: 동기적 Main thread
  → MainScheduler.asyncInstance: 비동기적 Main thread (순서 미보장)
  → observe(on:) 없는 경우: 이전 스케줄러 컨텍스트 유지

확정적 판단 기준:
✅ P0 확정: asyncInstance로 같은 State 동시 변경 확인됨
✅ P1 확정: merge 내 순서 의존 코드 발견
🟡 P2 주의: concat 내 비동기 API 호출 결과 의존
❌ 안전: concat으로 순차 처리, 단일 State 필드 변경
```

### 3. State Corruption Finder (상태 오염)

**역할**: 잘못된 상태 전이 및 불일치 탐지

**검증 항목**:
- 불가능한 상태 조합
- 잘못된 상태 전이 (A→C, A→B→C만 허용인데)
- 초기화 전 접근
- 클린업 누락으로 인한 잔여 상태

**프롬프트 요약**:
```
상태 관리 버그를 찾으세요:
- 불가능한 상태 조합이 발생할 수 있나요?
- 상태 전이가 올바른 순서로만 가능한가요?
- 초기화 전에 변수에 접근하는 경우가 있나요?
- 화면 이탈 시 상태가 제대로 정리되나요?

Reactor/ViewModel의 State 변경을 중점적으로 확인하세요.
```

### 4. Memory Leak Hunter (메모리 누수)

**역할**: 메모리 누수 및 리소스 관리 문제 탐지

**검증 항목**:
- [weak self] 누락된 closure
- delegate weak 참조 여부
- NotificationCenter observer 해제 누락
- Timer invalidate 누락
- 순환 참조 구조

**프롬프트 요약**:
```
메모리 누수 가능성을 찾으세요:
- closure에서 self 캡처 시 [weak self] 사용했나요?
- delegate가 weak으로 선언되었나요?
- NotificationCenter observer가 deinit에서 해제되나요?
- Timer가 invalidate 되나요?

retain cycle이 발생할 수 있는 구조를 식별하세요.
```

### 5. Input Validation Checker (입력 검증)

**역할**: 입력 검증 및 보안 취약점 탐지

**검증 항목**:
- 사용자 입력 검증 (타입, 범위, 길이)
- API 응답 타입 안전성
- JSON 디코딩 실패 처리
- SQL injection / XSS 가능성
- 민감 데이터 노출

**프롬프트 요약**:
```
입력 검증 문제를 찾으세요:
- 사용자 입력이 검증 없이 사용되나요?
- API 응답이 예상과 다를 때 크래시가 발생하나요?
- JSON 디코딩 실패 시 graceful하게 처리되나요?
- organization_id 필터링이 누락되었나요?
- 민감 데이터가 로그에 출력되나요?
```

### 6. Regression Detector (회귀 버그)

**역할**: 기존 기능에 미치는 영향 평가

**검증 항목**:
- 변경된 인터페이스의 호출자 영향
- 기존 테스트 커버리지
- 숨겨진 의존성
- 사이드 이펙트 전파

**프롬프트 요약**:
```
회귀 버그 가능성을 평가하세요:
- 변경한 함수/클래스를 다른 곳에서 사용하나요?
- 해당 기능에 대한 기존 테스트가 있나요?
- 변경이 다른 기능에 영향을 미치나요?
- 인터페이스 변경으로 컴파일 에러가 발생할 수 있나요?

Grep으로 변경된 함수/클래스 사용처를 모두 확인하세요.
```

### 7. Localization Checker (로컬라이징) 🆕

**역할**: 하드코딩된 문자열 및 로컬라이징 누락 탐지

**검증 항목**:
- UI에 노출되는 하드코딩 문자열
- NSLocalizedString 미사용
- Localized 구조체 미사용
- 다국어 지원 누락

**프롬프트 요약**:
```
로컬라이징 문제를 찾으세요:
- 사용자에게 보이는 문자열이 하드코딩되어 있나요?
- NSLocalizedString 또는 Localized 구조체를 사용했나요?
- 버튼 텍스트, 레이블, 알림 메시지가 로컬라이징되어 있나요?

AGENTS.md의 Localization 규칙:
- 문자열 하드코딩 금지
- Localized 구조체 내에 NSLocalizedString으로 정의
```

### 8. Platform Compatibility Checker (플랫폼 호환성) 🆕

**역할**: iOS 버전 및 iPad 멀티씬 호환성 검증

**검증 항목**:
- iOS 15+ API 사용 시 @available 체크
- UIApplication.shared.keyWindow (deprecated) 사용
- currentKeyWindow가 iPad 멀티윈도우에서 올바르게 동작하는지
- connectedScenes 순회 방식 vs first 사용
- Scene-based lifecycle 대응

**프롬프트 요약**:
```
플랫폼 호환성 문제를 찾으세요:
- deprecated API를 사용하고 있나요? (keyWindow 등)
- iPad 멀티윈도우/분할화면에서 문제가 발생할 수 있나요?
- connectedScenes.first 대신 compactMap으로 활성 씬을 찾나요?
- iOS 버전별 분기가 필요한 API를 무조건 호출하나요?

특히 UIApplication.shared.currentKeyWindow 사용처를 확인하세요.
```

### 9. UX Feedback Checker (사용자 피드백) 🆕

**역할**: 실패 시 사용자 피드백 방식 검증

**검증 항목**:
- API 실패 시 사용자에게 알림 여부
- 조용한 실패(silent failure) vs 명시적 에러 메시지
- 로딩 상태 표시 여부
- 네트워크 오류 시 재시도 옵션
- 딥링크/스킴 실패 시 fallback 동작

**프롬프트 요약**:
```
UX 피드백 문제를 찾으세요:
- API 호출 실패 시 사용자에게 어떤 피드백을 주나요?
- 조용히 실패하는 경우가 있나요? (의도적인지 확인 필요)
- 로딩 인디케이터가 표시되나요?
- 에러 발생 시 사용자가 무엇이 잘못됐는지 알 수 있나요?
- 딥링크 실패 시 적절한 fallback이 있나요?

PM/기획과 협의가 필요한 UX 결정을 명시하세요.
```

### 10. Rx Race Condition Checker (Rx 경쟁 조건) 🆕

**역할**: RxSwift/ReactorKit 환경에서 타이밍 이슈 및 경쟁 조건 탐지

**검증 항목**:
- viewDidLoad Action 순서 vs 실행 순서 불일치
- 같은 State 필드를 변경하는 동시 Action
- 스케줄러 컨텍스트 누락/오용
- Observable.merge 내 순서 의존성
- 자식 Reactor로의 action.onNext 타이밍

**분석 도구** (grepai 활용 권장):
```bash
# 1. grepai trace로 호출 그래프 생성
grepai trace callees "viewDidLoad" --json --depth 2
grepai trace graph "{ActionName}" --json --depth 3

# 2. grepai search로 의미 기반 충돌 탐색
grepai search "multiple actions modify same state field" --json

# 3. Grep fallback (grepai 사용 불가 시)
Grep "rx\.viewDidLoad" {ViewController}.swift
Grep "Observable\.merge\|Observable\.concat" {Reactor}.swift
```

**프롬프트 요약**:
```
RxSwift/ReactorKit 경쟁 조건을 분석하세요:

[viewDidLoad 분석] - grepai trace callees 활용
1. rx.viewDidLoad에 bind된 모든 Action 나열
2. 각 bind의 스케줄러 확인 (없으면 "동기")
3. 실행 순서 예측:
   - 스케줄러 없음: bind 선언 순서대로 동기 실행
   - asyncInstance: 비동기 실행, 순서 미보장

[State 충돌 분석] - grepai trace graph 활용
1. Reactor.reduce에서 각 Mutation이 변경하는 State 필드 추출
2. 같은 필드를 변경하는 Mutation 쌍 식별
3. 해당 Mutation을 발생시키는 Action 추적
4. Action들이 동시에 호출될 수 있는지 확인

[확정적 버그 판단] - 그래프 분석 기반
- P0: asyncInstance로 같은 State 동시 변경 **그래프에서 확인됨**
- P1: merge 내 순서 의존 코드 **경로 추적으로 발견**
- P2: 스케줄러 명시 없이 비동기 API 결과로 UI 업데이트
```

**출력 형식**:
```markdown
### Rx Race Condition 분석 결과

#### viewDidLoad Action 흐름
[동기 실행]
1. .loadData (L436)

[비동기 실행 - 순서 미보장]
2. .loadExistTempFile (L474) - asyncInstance

#### State 충돌 위험
| State 필드 | Action A | Action B | 판정 |
|-----------|----------|----------|------|
| writingModel | .loadData | .setContent | 🟡 P2 |

#### 스케줄러 이슈
| 위치 | 문제 | 심각도 |
|------|------|--------|
| L674 | asyncInstance 후 State 의존 코드 | P1 |
```

**Neo4j 그래프 기반 확정적 판단** (선택적):

Neo4j MCP 서버 (`neo4j-code-graph`) 연결 시 더 정확한 분석이 가능합니다.

```bash
# Reactor 워크플로우 조회
mcp__neo4j-code-graph__neo4j_trace_workflow(reactor_name: "{Reactor명}")

# 결과 예시
{
  "reactor_files": [...],
  "workflows": [
    {"action": "login", "mutation": "setLoading", "state_field": "isLoading"},
    {"action": "autoLogin", "mutation": "setLoading", "state_field": "isLoading"}
  ],
  "race_condition_risks": [
    {"state_field": "isLoading", "competing_actions": ["login", "autoLogin"], "risk": "P1"}
  ]
}
```

**Neo4j 판정 기준**:
- `race_condition_risks` 반환 시 → **확정적 버그**로 판단
- grepai 분석과 일치 시 → 확신도 ↑
- 그래프 없으면 → 기존 grepai/Grep 분석만 사용

**Neo4j 출력 형식**:
```markdown
#### Rx Race Condition (Neo4j 확정)

✅ **그래프 분석 확정**: {State 필드}에 {N}개 Action 경쟁
- 경로 1: {action1} → {mutation1} → {state_field}
- 경로 2: {action2} → {mutation2} → {state_field}

| State 필드 | 경쟁 Action | 판정 | 근거 |
|-----------|------------|------|------|
| {필드} | {actions} | P1 확정 | Neo4j + grepai |
```

---

## 심각도 분류 (P0-P3)

| Level | 의미 | 예시 | 조치 |
|-------|------|------|------|
| **P0** | Critical | 크래시, 데이터 손실, 보안 취약점 | 필수 수정 |
| **P1** | High | 기능 오작동, 성능 저하 | 수정 권장 |
| **P2** | Medium | 엣지 케이스 미처리, 경미한 오류 | 선택적 수정 |
| **P3** | Low | 코드 스멜, 잠재적 문제 | 참고 |

---

## Bug Triage (Step 3)

모든 발견 집계 후:

1. **심각도 재평가**: 체커별 판단 검토
2. **중복 제거**: 같은 버그를 여러 체커가 발견한 경우
3. **재현 시나리오 작성**: P0/P1 버그에 대해 상세 시나리오
4. **수정 우선순위 결정**: 영향도 기반

---

## 출력 템플릿

```markdown
# {TICKET_ID} Bug Check Report

**검증일**: YYYY-MM-DD HH:MM
**검사자**: 6 Parallel Bug Checkers

---

## 요약

| Checker | 발견 | P0 | P1 | P2 | P3 |
|---------|------|----|----|----|----|
| Edge Case Hunter | N | N | N | N | N |
| Race Condition | N | N | N | N | N |
| State Corruption | N | N | N | N | N |
| Memory Leak | N | N | N | N | N |
| Input Validation | N | N | N | N | N |
| Regression | N | N | N | N | N |
| Localization 🆕 | N | N | N | N | N |
| Platform Compat 🆕 | N | N | N | N | N |
| UX Feedback 🆕 | N | N | N | N | N |
| Rx Race Condition 🆕 | N | N | N | N | N |
| **총계** | **N** | **N** | **N** | **N** | **N** |

---

## P0 Critical Bugs

### [BUG-001] {버그 제목}

**발견자**: {Checker 이름}
**파일**: `{파일}:{라인}`
**심각도**: P0 (Critical)

**설명**:
{버그 설명}

**재현 시나리오**:
```
전제조건: {조건}

1. {단계 1}
2. {단계 2}
3. {단계 3}

예상 결과: {예상}
실제 결과: {실제 - 크래시/오류}
```

**영향 범위**:
- {영향받는 기능/사용자}

**수정 제안**:
```diff
- 문제 코드
+ 수정 코드
```

---

## P1 High Priority Bugs

### [BUG-010] {버그 제목}
...

---

## P2 Medium Priority Bugs

### [BUG-020] {버그 제목}
...

---

## P3 Low Priority (참고)

| # | 버그 | Checker | 파일 |
|---|------|---------|------|
| BUG-030 | {버그} | {Checker} | {파일} |

---

## 판정

| 조건 | 결과 |
|------|------|
| **Work 승인** | ✅ 통과 / ❌ 수정 필요 |
| P0 버그 | N건 (0이어야 통과) |
| P1 버그 | N건 (수정 권장) |

---

## 권장 조치

### 필수 (Blocking)
1. [ ] [BUG-001] {P0 버그 수정}

### 권장 (Non-blocking)
1. [ ] [BUG-010] {P1 버그 수정}
2. [ ] [BUG-011] {P1 버그 수정}

---

## 다음 단계

- ✅ P0 없음: `/ai-dev.review` 진행
- ❌ P0 존재: 필수 조치 완료 후 재검증

---

*Checked by ai-dev.work-check (6 parallel bug checkers)*
```

---

## 파일 경로

```
~/.claude/contexts/work/kidsnote/docs/ai-dev/{PK-xxxx}/
├── ...
└── work-check-report.md  ← 생성
```

---

## 연계 스킬

| 스킬 | 용도 |
|------|------|
| `/ai-dev.code-check` | 선행 (품질 검증) |
| `/ai-dev.review` | 후속 (최종 승인) |

---

**Created:** 2026-01-28
**Updated:** 2026-01-29
**Version:** 1.1 (PR #7360, #7361 피드백 반영: Localization, Platform Compat, UX Feedback 체커 추가)
