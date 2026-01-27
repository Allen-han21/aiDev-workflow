# ai-dev 스킬 시스템 종합 분석 보고서

> **요약**: 7개의 상호연결된 스킬이 JIRA 티켓 → 구현 → PR 생성의 전체 파이프라인을 자동화하는 AI 협업 개발 시스템

## 개요

ai-dev는 프로덕션급 AI 협업 개발 시스템입니다. 7개의 상호연결된 스킬이 JIRA 티켓 분석부터 코드 구현, PR 생성까지 전체 파이프라인을 자동화하는 메가 워크플로우입니다.

---

## 1. 전체 아키텍처 흐름

```
┌─────────────────────────────────────────────────────────────────┐
│                    ai-dev 통합 워크플로우                        │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  ENTRY: /ai-dev PK-XXXXX [--figma URL] [--from PHASE]           │
│         또는 /ai-dev.{analyze|spec|plan|impl|review|pr}         │
│                                                                 │
│  ════════ PLAN MODE (분석/설계 전용) ════════                    │
│                                                                 │
│  Phase 0: ai-dev.analyze                                        │
│  └─ JIRA 티켓 + Figma + 코드베이스 분석 → analyze.md            │
│                                                                 │
│  Phase 1: ai-dev.spec                                           │
│  └─ Claude + Codex 크로스 체크 → spec.md                        │
│                                                                 │
│  Phase 2: ai-dev.plan                                           │
│  └─ Codex + Claude 검증으로 구현 계획 → plan.md                 │
│                                                                 │
│  ════════ DEVELOPER MODE (코드 작성) ════════                    │
│                                                                 │
│  Phase 3: ai-dev.impl                                           │
│  └─ Task순 구현 → 로컬 커밋 → [allen-test] 로그 → Xcode 실행    │
│                                                                 │
│  Phase 4: ai-dev.review                                         │
│  └─ 린트 + CodeRabbit + Claude 심도 리뷰 → 승인/변경요청       │
│                                                                 │
│  Phase 5: ai-dev.pr                                             │
│  └─ Push + GitHub PR 생성 (표준 템플릿)                         │
│                                                                 │
│  OUTPUT: .claude/contexts/work/kidsnote/docs/ai-dev/{폴더}/     │
│          ├── analyze.md                                         │
│          ├── spec.md                                            │
│          ├── plan.md                                            │
│          └── [소스 코드 + 커밋]                                  │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

---

## 2. 각 스킬 상세 분석

### ai-dev (메인 오케스트레이션)

- **역할**: 전체 워크플로우 조율
- **트리거**: `/ai-dev PK-XXXXX` + 옵션들
- **옵션**:
  - `--figma URL`: Figma 디자인 분석 포함
  - `--from {phase}`: 특정 Phase부터 시작
  - `--to {phase}`: 특정 Phase까지만
  - `--no-codex`: Codex MCP 비활성화
  - `--ultrathink`: Extended thinking 활성화
- **의존성**: 없음 (시작점)
- **파일 저장**: `.claude/contexts/work/kidsnote/docs/ai-dev/{PK-XXXXX-제목}/`
- **핵심 메커니즘**: 각 Phase를 순차 호출하며 plan mode 전환 관리

---

### ai-dev.analyze (Phase 0)

- **역할**: 요구사항 + 코드 + 디자인 종합 분석
- **트리거**: `/ai-dev.analyze PK-XXXXX`
- **사전 조건**: plan mode (읽기 전용)
- **입력**: JIRA 티켓 번호
- **분석 프로세스**:
  1. **JIRA 조회**: `/jira-get` 호출 → 제목, 본문, 댓글, 첨부 수집
  2. **Figma 자동 감지**: URL 패턴 추출 → `figma_get_node_bundle` MCP 호출
  3. **iOS 코드 분석**:
     - LSP 기반 심볼 탐색 (타입 위치, 의존성)
     - Explore 에이전트로 유사 패턴 탐색
  4. **Apple 문서 참조**: `apple-docs__search_apple_docs` (deprecated API, availability)
  5. **Android 코드 참조** (선택): 동일 기능 PR 검색, 비즈니스 로직 비교
  6. **엣지 케이스 식별**: 빈 데이터, 네트워크 오류, 권한, 동시성 등
  7. **AskUserQuestion**: 확인 필요 사항 질문
- **출력**: `analyze.md` (7개 섹션)
  - 요구사항 요약 + 핵심 논의
  - Figma 디자인 분석
  - iOS 코드베이스 심볼 그래프
  - Android 코드 참조
  - 엣지 케이스
  - 기술적 제약
  - 확인 필요 사항

**핵심 특징**:
- LSP 활용: Swift 타입 정보 자동 제공
- 멀티플랫폼 참조: Android 구현 비교로 누락 방지
- Apple 호환성: 버전 체크

---

### ai-dev.spec (Phase 1)

- **역할**: 크로스 체크를 통한 스펙 확정
- **트리거**: `/ai-dev.spec PK-XXXXX`
- **사전 조건**: plan mode + `analyze.md` 필수
- **옵션**: `--no-codex`, `--ultrathink`
- **크로스 체크 메커니즘**:

**[기본] Claude + Codex MCP 병렬 분석:**
1. Claude (내부): 대화 맥락, 사용자 의도 기반 분석
2. Codex MCP: `mcp__codex__codex` 호출 → 코드 탐색 기반 분석
3. 상호 검토:
   - Claude → Codex 답변 검토 (동의/보완/다른관점)
   - Codex → Claude 검토 (`codex-reply`) (동의/보완/권장)
4. 종합:
   - 공통 합의 → `spec.md` 반영
   - 선택 필요 → AskUserQuestion

**[--no-codex] Claude 멀티 관점:**
- 아키텍처 분석가 (기존 아키텍처 일관성)
- 코드 품질 엔지니어 (테스트 가능성, 유지보수)
- 비즈니스 로직 검토자 (요구사항 충족, UX)
- 유사 구현 참조 (Grep)

- **출력**: `spec.md`
  - 개요 (기능/목표)
  - 상세 스펙 (화면/모델/규칙)
  - 엣지 케이스 처리
  - 기술 노트 (영향범위, 의존성)
  - 완료 조건
  - 크로스 체크 결과

**핵심 특징**:
- 3자 검증 (크로스 체크): Claude <-> Codex 상호 리뷰로 맹점 제거
- 멀티 관점 분석: 아키텍처, 품질, 비즈니스 모두 커버
- 사용자 선택 메커니즘: 의견 충돌 시 AskUserQuestion

---

### ai-dev.plan (Phase 2)

- **역할**: 확정된 스펙을 구현 계획으로 분해
- **트리거**: `/ai-dev.plan PK-XXXXX`
- **사전 조건**: plan mode + `spec.md` 필수
- **옵션**: `--no-codex`, `--ultrathink`

**[기본] Codex MCP + Claude 검증:**
1. `mcp__codex__codex` 호출 (prompt: "Swift + ReactorKit 기반 구현 계획", cwd: 프로젝트 경로, sandbox: "read-only")
2. Codex 답변: Task 분해, 파일 경로, 의존성, 복잡도, 코드 스니펫
3. Claude 검증: AGENTS.md 컨벤션 준수, 파일 경로 정확성, 의존성 순서, 누락 Task 확인

**[--no-codex] Claude 직접 계획:**
- `analyze.md` 심볼 의존성 그래프 활용
- AGENTS.md 읽기 (컨벤션 확인)
- Phase 구조로 Task 분해:
  - Phase 1: 데이터 계층 (Entity, Repository)
  - Phase 2: 비즈니스 로직 (UseCase, Service, Reactor)
  - Phase 3: UI 계층 (ViewController, Cell)
  - Phase 4: 통합 및 테스트

- **출력**: `plan.md`
  - 요약, Phase 구조, Task 상세 (파일, 작업 내용, 의존성, 복잡도, 예상 코드)
  - 실행 순서 (의존성 다이어그램)
  - 영향 파일 목록, 테스트 계획, 커밋 계획, 예상 복잡도

---

### ai-dev.impl (Phase 3)

- **역할**: `plan.md` 기반 실제 코드 구현
- **트리거**: `/ai-dev.impl PK-XXXXX`
- **사전 조건**: plan mode 해제 (Developer 역할) + `plan.md` 필수
- **옵션**: `--task N`, `--no-commit`, `--no-run`, `--auto`
- **구현 루프** (각 Task마다):
  1. Task 상세 확인
  2. 의존성 Task 완료 여부 확인
  3. Apple 문서 참조 (새 API 사용 시)
  4. 코드 구현: AGENTS.md 컨벤션 준수
  5. 빌드 검증: `xcodebuild build`
  6. 테스트: Unit Test + `[allen-test]` 로그 추가
  7. 로컬 커밋: `[PK-XXXXX] <Type>(<Scope>): <Subject>`
  8. `plan.md`에 완료 표시 + 커밋해시
  9. 다음 Task 확인 (수동/`--auto`)
- **모든 Task 완료 후**:
  1. Xcode + 시뮬레이터 실행 (osascript)
  2. `[allen-test]` 로그 확인
  3. 사용자 "테스트 완료" 입력 대기
  4. 로그 삭제 + 커밋

**핵심 특징**:
- Task 기반 순차 구현: 중단/재개 가능
- Apple 문서 통합: API 호환성 실시간 확인
- `[allen-test]` 로그: UI 테스트 자동화
- 커밋 그래눌러리티: 각 Task = 1개 커밋 (롤백 용이)

---

### ai-dev.review (Phase 4)

- **역할**: 자동 검증 + 심도 리뷰 + 판정
- **트리거**: `/ai-dev.review PK-XXXXX`
- **옵션**: `--quick`, `--full`
- **검증 단계**:
  1. **AGENTS.md 로드**: 팀 규칙
  2. **린트 검사**: `swiftlint lint --quiet`
  3. **CodeRabbit 리뷰**: `coderabbit review --plain -t all`
  4. **Claude 심도 리뷰**: Correctness, Security, Efficiency, Maintainability, Architecture
  5. **iOS DoD 체크리스트**: Swift 6 concurrency, 메모리 관리, SwiftUI 성능, 에러 처리
  6. **Apple API 호환성 검사**: deprecated 감지, availability 확인
  7. **이슈 분류**: Critical/High/Medium/Low
  8. **[--full] Codex MCP 크로스 체크**: 보안, 성능, 코드 품질 3자 검증
  9. **종합 판단**: CodeRabbit <-> Claude 비교, 충돌 시 Claude 우선

**판정 기준**:
- **승인**: Critical 0건 + High 0건 + 린트 통과
- **변경요청**: Critical 1+건 또는 High 다수

---

### ai-dev.pr (Phase 5)

- **역할**: Push + GitHub PR 생성
- **트리거**: `/ai-dev.pr [PK-XXXXX]`
- **옵션**: `--draft`, `--no-push`, `--amend`
- **프로세스**:
  1. Git 상태 분석 (병렬)
  2. JIRA 티켓 추출 (인자 → 브랜치명 → 커밋 메시지 폴백)
  3. 변경사항 분석 (신규/수정/삭제, Type 판단, UI 변경 여부)
  4. Push + PR 생성 (키즈노트 표준 템플릿)

**PR 템플릿 포함 내용**:
- JIRA Badge + 링크
- 작업 내용 (문제 현상/요구사항, 원인/배경)
- 변경 사항 (주요 파일, 세부 변경)
- 리뷰 노트 (복잡한 로직, 트레이드오프, 제한사항)
- 유닛 테스트
- 스크린샷 (UI 변경 시 자동 포함)

---

## 3. MCP/외부 도구 통합

| 도구 | 스킬 | 목적 |
|------|------|------|
| `jira-get` | analyze | JIRA 조회 |
| `figma_get_node_bundle` | analyze | Figma 디자인 추출 |
| `apple-docs__*` | analyze, impl, review | Apple API 호환성 |
| `mcp__codex__codex` | spec, plan, review | 코드 탐색 기반 분석 |
| `mcp__codex__codex-reply` | spec | Codex 추가 검토 |

### Git/CLI 도구

- `git` (상태, diff, log, add, commit, push)
- `gh` (PR 생성, 조회)
- `xcodebuild` (빌드 검증)
- `swiftlint` (린트)
- `coderabbit` (자동 리뷰)
- `osascript` (Xcode + 시뮬레이터 실행)

---

## 4. 핵심 메커니즘

### 크로스 체크 (spec 단계)

```
    Claude (맥락 기반)          Codex MCP (코드 탐색)
           ↓                           ↓
        분석 결과                   분석 결과
           ↓                           ↓
    Claude: Codex 검토     Codex: Claude 검토
           ↓                           ↓
           └─────────────┬─────────────┘
                         ↓
                 공통 합의 / 선택 필요
                         ↓
                  사용자 승인 → spec.md
```

### 의존성 그래프 기반 Task 순서 (plan 단계)

```
analyze.md의 심볼 의존성 그래프:
    Entity (의존성 없음)
        ↓ (Task 1.1)
    Repository (Entity 의존)
        ↓ (Task 1.2)
    Service (Repository 의존)
        ↓ (Task 2.1)
    Reactor (Service 의존)
        ↓ (Task 2.2)
    ViewController (Reactor 의존)
        ↓ (Task 3.1)
```

### [allen-test] 로그 패턴 (impl 단계)

```swift
// 구현 중 추가
print("[allen-test] 검색어: \(keyword)")
print("[allen-test] 결과 개수: \(results.count)")

// 테스트 완료 후 삭제 → 자동 Grep + Edit로 제거
// 최종 로그 삭제 커밋: [PK-XXXXX] chore: 테스트 로그 삭제
```

### Apple API 호환성 실시간 체크 (impl + review)

- **impl 단계**: 새 API 사용 → apple-docs MCP 호출 → availability 확인
- **review 단계**: deprecated 감지 → Critical 이슈 → 대안 API 자동 제시

---

## 5. 고급 옵션 조합

```bash
# 기본 워크플로우 (Phase 0~5 모두)
/ai-dev PK-12345

# Figma 포함
/ai-dev PK-12345 --figma https://figma.com/design/...

# 부분 실행 (spec.md 이미 있을 때 plan부터)
/ai-dev PK-12345 --from plan

# spec까지만
/ai-dev PK-12345 --to spec

# Codex 쿼터 절약 (Claude만으로)
/ai-dev PK-12345 --no-codex

# 최고 품질 (Extended thinking)
/ai-dev PK-12345 --ultrathink

# 최고 품질 + 쿼터 절약
/ai-dev PK-12345 --no-codex --ultrathink

# 리뷰 3자 검증
/ai-dev.review PK-12345 --full
```

---

## 6. 문서 저장 구조

```
.claude/contexts/work/kidsnote/docs/ai-dev/
├── PK-32398-원생관리-검색기능/        ← {PK-XXXXX}-{제목-간단}
│   ├── analyze.md                   ← Phase 0 출력
│   ├── spec.md                      ← Phase 1 출력
│   ├── plan.md                      ← Phase 2 출력
│   └── [소스 코드 + 로컬 커밋들]      ← Phase 3 출력
├── PK-32399-새기능/
│   ├── analyze.md
│   ├── spec.md
│   └── plan.md
```

**폴더명 규칙**: 티켓번호 + 개발내용 (공백→하이픈, 특수문자 제거, 최대 30자)

---

## 7. 아키텍처 패턴 (AGENTS.md 준수)

| 계층 | 생성 | 의존성 |
|------|------|--------|
| Data | Repository | Entity |
| Domain | Service/UseCase | Repository |
| Presentation | Reactor/ViewModel | Service |
| UI | ViewController/View | Reactor |

**강제 규칙**: 타입 명시, String 연산 금지, guard 후 개행, 문서화 주석 (`///`)

---

## 8. 위험 관리

- **Codex MCP**: `approval-policy: "on-failure"`, `sandbox: "read-only"` (파일 수정 없음)
- **Git 안정성**: 로컬 커밋만 생성 (push는 review 후), 각 Task = 1 커밋
- **Apple API 호환성**: 모든 API 사용 시 자동 호환성 체크

---

## 9. 의존성 체인

```
ai-dev.analyze
    ↓ (analyze.md 생성)
ai-dev.spec
    ↓ (spec.md 생성)
ai-dev.plan
    ↓ (plan.md 생성)
ai-dev.impl ← Task 기반 (각 Task = 1 커밋)
    ↓
ai-dev.review
    ↓
ai-dev.pr
```

- **선형 의존성**: 각 Phase는 이전 Phase 출력에 의존
- **`--from` 옵션**: 의존성 건너뛰기 (이미 파일 존재 시)
- **Task 기반 격자화**: impl 단계에서 재개/중단 가능

---

## 10. 시너지 요약

```
Phase 0: 정보 수집 (JIRA + Figma + 코드 + Android)
    ↓ (analyze.md)
Phase 1: 관점 통합 (Claude + Codex 크로스 체크)
    ↓ (spec.md)
Phase 2: 구현 가능성 검증 (의존성 자동 순서)
    ↓ (plan.md)
Phase 3: 코드 품질 보장 (Apple 호환성 + [allen-test])
    ↓ (커밋들)
Phase 4: 다층 검증 (린트 + CodeRabbit + Claude + Codex)
    ↓ (판정)
Phase 5: 표준화 (키즈노트 PR 템플릿)
    ↓ (PR URL)
```

각 Phase가 이전 Phase의 결과물을 재가공/고도화하며, 정보 손실 없이 누적됩니다.

---

**마지막 업데이트**: 2026-01-28
