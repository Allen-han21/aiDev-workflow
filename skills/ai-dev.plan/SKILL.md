---
name: ai-dev.plan
description: 확정된 스펙 기반 구현 계획 수립. Codex MCP로 계획 생성 후 Claude 검증. "구현 계획 짜줘", "계획 세워줘", "설계해줘" 요청 시 활성화.
---

# Skill: ai-dev.plan

확정된 스펙(spec.md)을 기반으로 Codex에게 구현 계획을 질문하고 plan.md를 생성합니다.

---

## 전제 조건

**plan mode에서 실행**

**필수 선행**: spec.md 존재

---

## 사용법

```bash
/ai-dev.plan PROJ-XXXXX
```

---

## 옵션

| 옵션 | 설명 | 예시 |
|------|------|------|
| `--no-codex` | Codex MCP 계획 생성 비활성화 | Claude 직접 계획 수립 |
| `--ultrathink` | Extended thinking 활성화 | 복잡한 구현 계획 수립 시 |

### 옵션 조합 예시

```bash
# 기본 (Codex 사용)
/ai-dev.plan PROJ-12345

# Codex 쿼터 절약
/ai-dev.plan PROJ-12345 --no-codex

# 복잡한 문제 (ultrathink)
/ai-dev.plan PROJ-12345 --ultrathink

# 복잡한 문제 + Codex 쿼터 없음 (최고 품질)
/ai-dev.plan PROJ-12345 --no-codex --ultrathink

# 옵션 먼저도 가능
/ai-dev.plan --no-codex --ultrathink PROJ-12345
```

> **참고**: 옵션 위치는 자유롭습니다.

---

## 워크플로우

### Step 1: spec.md 읽기

```
.claude/contexts/work/my-project/docs/ai-dev/{PROJ-xxxx-개발내용}/spec.md
```

spec.md가 없으면 안내:
```
spec.md가 없습니다.
먼저 스펙을 확정하세요: /ai-dev.spec PROJ-XXXXX
```

### Step 2: 구현 계획 생성

#### 옵션 분기

| 옵션 | 실행 방식 |
|------|----------|
| 기본 (옵션 없음) | → Step 2-A: Codex MCP 계획 생성 |
| `--no-codex` | → Step 2-B: Claude 직접 계획 생성 |
| `--ultrathink` | → 선택된 방식에 ultrathink prefix 추가 |

---

### Step 2-A: Codex MCP 계획 질문 (기본)

#### `--ultrathink` 활성화 시 프롬프트 prefix

```
ultrathink해서 다음 스펙에 대한 구현 계획을 수립해줘.
모든 엣지 케이스, 의존성, 테스트 시나리오를 빠짐없이 고려해줘.
```

```
mcp__codex__codex(
  prompt: "다음 스펙을 구현하기 위한 상세 계획을 작성해주세요.

## 프로젝트 정보
- 언어: Swift
- 아키텍처: UIKit + ReactorKit (기존) / SwiftUI + ViewModel (신규)
- 의존성: RxSwift, SnapKit, Dependencies (pointfreeco)
- 코딩 컨벤션: AGENTS.md 참조

## 스펙
{spec.md 전체 내용}

## 요청 사항
1. Task를 세분화하여 체크박스 형식으로 작성
2. 각 Task별 영향 파일 목록 (전체 경로 포함)
3. 실행 순서와 의존성 (어떤 Task가 먼저 완료되어야 하는지)
4. 예상 복잡도 평가 (낮음/중간/높음)
5. 각 Task별 예상 코드 스니펫 (핵심 부분만)

## 출력 형식
Phase 구조로 분류:
- Phase 1: 데이터 레이어 (Entity, Repository)
- Phase 2: 비즈니스 로직 (UseCase, Reactor/ViewModel)
- Phase 3: UI 레이어 (View, Cell)
- Phase 4: 통합 및 테스트",
  cwd: "~/Dev/Repo/my-ios-app",
  approval-policy: "on-failure",
  sandbox: "read-only"
)
```

→ **Step 3-A로 이동**

---

### Step 2-B: Claude 직접 계획 생성 (`--no-codex`)

Codex 대신 Claude가 직접 구현 계획을 생성합니다.

#### `--ultrathink` 활성화 시 프롬프트 prefix

```
ultrathink해서 다음 스펙에 대한 구현 계획을 수립해줘.
모든 엣지 케이스, 의존성, 테스트 시나리오를 빠짐없이 고려해줘.
```

#### 2-B.1 의존성 그래프 기반 탐색

**analyze.md의 심볼 의존성 그래프 활용:**

analyze.md에서 생성된 의존성 그래프를 기반으로 Task 순서를 자동 도출합니다.

```markdown
# analyze.md의 심볼 의존성 그래프 참조
## 3.1 심볼 의존성 그래프

StudentEntity (Model)
    │
    ├── StudentRepository (Data)
    │       └── StudentService (Domain)
    │               └── StudentListReactor (Presentation)
    │                       └── StudentListViewController (UI)
```

**의존성 순서 자동 도출:**
```
1. Entity 계층 (의존성 없음)
   → Task 1.1: Entity 정의/수정

2. Repository 계층 (Entity 의존)
   → Task 1.2: Repository 메서드 추가
   → 영향: Service, Reactor에 파급

3. Service/UseCase 계층 (Repository 의존)
   → Task 2.1: Service 로직 추가

4. Reactor/ViewModel 계층 (Service 의존)
   → Task 2.2: Reactor Action/State 추가
   → 참조 수 기반 영향 범위 검토

5. UI 계층 (Reactor 의존)
   → Task 3.1: ViewController/View 수정
```

**추가 탐색 (필요 시):**

```bash
# 1. 관련 파일 구조 파악
Glob: "Sources/Features/{Feature}/**/*.swift"

# 2. 유사 기능 구현 패턴 참조
Grep: "Reactor" --type swift --path "Sources/Features/"
Grep: "ViewModel" --type swift --path "Sources/Features/"

# 3. 핵심 파일 읽기
Read: 발견된 유사 패턴 파일 2-3개
```

#### 2-B.2 AGENTS.md 컨벤션 확인

```bash
Read: "~/Dev/Repo/my-ios-app/AGENTS.md"
```

코딩 컨벤션 추출:
- 파일 구조
- 네이밍 규칙
- 주석 형식
- 아키텍처 패턴

#### 2-B.3 구현 계획 수립

spec.md 기반으로 Phase/Task 분해:

```markdown
## 계획 수립 기준

1. **Task 분해 원칙**
   - 단일 책임 (한 Task = 한 가지 변경)
   - 독립 검증 가능 (각 Task 완료 후 빌드 가능)
   - 의존성 명시 (선행 Task 표시)

2. **Phase 구조**
   - Phase 1: 데이터 레이어 (Entity, Repository, DTO)
   - Phase 2: 비즈니스 로직 (UseCase, Service)
   - Phase 3: 프레젠테이션 (Reactor/ViewModel, View/ViewController)
   - Phase 4: 통합 및 테스트

3. **예상 코드 스니펫**
   - 각 Task별 핵심 코드 예시
   - 기존 패턴 참조하여 일관성 유지
```

→ **Step 3-B로 이동**

---

### Step 3-A: Claude 검증 (기본 모드)

Codex 답변을 Claude가 검증:

**검증 항목:**
- AGENTS.md 코딩 컨벤션 준수 여부
- 파일 경로 정확성 (실제 프로젝트 구조와 일치)
- 의존성 순서 타당성
- 누락된 Task 확인
- 예상 코드 스니펫 품질

**검증 결과 반영:**
- 오류 수정
- 누락 항목 추가
- 컨벤션 위반 사항 보정

→ **Step 4로 이동**

---

### Step 3-B: 자체 검증 체크리스트 (`--no-codex`)

Codex 검증 대신 Claude 자체 검증:

```markdown
## 자체 검증 항목

- [ ] AGENTS.md 코딩 컨벤션 준수
- [ ] 파일 경로가 실제 프로젝트 구조와 일치
- [ ] 의존성 순서가 논리적으로 타당
- [ ] 누락된 Task 없음
- [ ] 예상 코드 스니펫이 구체적
- [ ] 커밋 메시지 형식 준수
- [ ] 기존 유사 패턴 1개 이상 참조됨
```

→ **Step 4로 이동**

### Step 4: plan.md 생성

```
.claude/contexts/work/my-project/docs/ai-dev/{PROJ-xxxx-개발내용}/plan.md
```

### Step 5: 사용자 구현 승인

```
구현 계획이 생성되었습니다.

[plan.md 핵심 내용 표시]

이 계획대로 구현을 시작하시겠습니까?
```

AskUserQuestion으로 확인:
```
AskUserQuestion([
  {
    question: "구현을 시작하시겠습니까?",
    header: "구현 승인",
    options: [
      { label: "구현 시작", description: "plan.md대로 코드 작성 시작" },
      { label: "계획 수정", description: "추가 조정 후 재검토" }
    ]
  }
])
```

---

## 출력 템플릿

```markdown
# {TICKET_ID} 구현 계획

**생성일**: YYYY-MM-DD HH:MM
**티켓**: {TICKET_ID} - {제목}
**생성자**: [기본] Codex MCP + Claude 검증
           [--no-codex] Claude 직접 계획 + 자체 검증
           [--ultrathink] Extended thinking 활성화

---

## 1. 요약

{2-3문장으로 구현 방향 요약}

---

## 2. Phase 구조

### Phase 1: 데이터 레이어
- [ ] Task 1.1: Entity 정의
- [ ] Task 1.2: Repository 구현

### Phase 2: 비즈니스 로직
- [ ] Task 2.1: UseCase/Service 구현
- [ ] Task 2.2: Reactor/ViewModel 구현

### Phase 3: UI 레이어
- [ ] Task 3.1: View/ViewController 구현
- [ ] Task 3.2: Cell/Component 구현

### Phase 4: 통합 및 테스트
- [ ] Task 4.1: 화면 연결
- [ ] Task 4.2: 테스트 작성

---

## 3. Task 상세

### Task 1.1: Entity 정의

**파일**: `Sources/Features/{Feature}/Models/{Entity}Entity.swift`

**작업 내용**:
- {Entity} 구조체 정의
- Codable 프로토콜 채택
- 필수 프로퍼티 정의

**예상 코드**:
```swift
/// [목적] {Entity} 데이터 표현
/// [기능] {설명}
struct {Entity}Entity: Codable {
    let id: Int
    let name: String
}
```

**예상 복잡도**: 낮음

---

### Task 1.2: Repository 구현

**파일**: `Sources/Repositories/{Feature}Repository.swift`

**작업 내용**:
- API 호출 메서드 구현
- 에러 핸들링

**의존성**: Task 1.1 완료 필요

**예상 복잡도**: 중간

---

(각 Task 상세...)

---

## 4. 실행 순서

```
Task 1.1 (Entity)
    ↓
Task 1.2 (Repository) ←── Task 1.1 의존
    ↓
Task 2.1 (Service)
    ↓
Task 2.2 (Reactor) ←── Task 1.2, Task 2.1 의존
    ↓
Task 3.1 (ViewController) ←── Task 2.2 의존
    ↓
Task 3.2 (Cell)
    ↓
Task 4.1 (통합)
    ↓
Task 4.2 (테스트)
```

---

## 5. 영향 파일 목록

| 파일 | 작업 | 복잡도 |
|------|------|--------|
| `Sources/Features/{Feature}/Models/{Entity}Entity.swift` | 신규 생성 | 낮음 |
| `Sources/Features/{Feature}/Views/{Feature}ViewController.swift` | 수정 | 중간 |
| ... | ... | ... |

---

## 6. 테스트 계획

각 Task별 테스트 방법:

| Task | 테스트 방법 | 비고 |
|------|------------|------|
| 1.1 | Unit Test | Entity Codable 테스트 |
| 2.2 | Unit Test | Reactor Action/State 테스트 |
| 3.1 | [DEBUG] 로그 | UI 동작 확인 |

---

## 7. 커밋 계획

| Task | 커밋 메시지 |
|------|------------|
| 1.1 | `[PROJ-XXXXX] feat(model): {Entity} Entity 추가` |
| 1.2 | `[PROJ-XXXXX] feat(networking): {Feature} Repository 구현` |
| 2.1 | `[PROJ-XXXXX] feat(logic): {Feature} Service 구현` |
| ... | ... |

---

## 8. 예상 복잡도

| 항목 | 평가 |
|------|------|
| 전체 복잡도 | 중간 |
| 신규 파일 수 | {N}개 |
| 수정 파일 수 | {M}개 |
| 총 Task 수 | {T}개 |

---

## 9. 주의사항

- {주의사항 1}
- {주의사항 2}

---

## 10. 참조

- **spec.md**: 확정된 스펙
- **analyze.md**: 코드베이스 분석

---

*Generated by ai-dev.plan*
*Mode: [기본] Codex MCP + Claude verification / [--no-codex] Claude direct planning*
```

---

## 예제

### 예제 1: Codex 계획 + Claude 검증

```
User: /ai-dev.plan PROJ-32398

Claude: [ai-dev.plan 활성화]

spec.md 읽는 중...
경로: .claude/contexts/work/my-project/docs/ai-dev/PROJ-32398-원생관리-검색기능/spec.md

Codex MCP로 계획 생성 중...
[mcp__codex__codex 실행]

Codex 계획 결과:
- Phase 1: StudentSearchEntity 정의
- Phase 2: StudentListReactor 검색 Action 추가
- Phase 3: SearchBar UI 구현
- Phase 4: 테스트 작성

Claude 검증 중...
- 파일 경로 확인: ✅
- AGENTS.md 컨벤션: ✅ (주석 형식 보정 필요)
- 의존성 순서: ✅
- 누락 확인: SearchBar 디바운스 로직 Task 추가

[보정 완료]

plan.md 저장됨.
경로: .claude/contexts/work/my-project/docs/ai-dev/PROJ-32398-원생관리-검색기능/plan.md

---

# PROJ-32398 구현 계획

## 요약
원생 목록에 실시간 검색 기능을 추가합니다. SearchBar UI, 디바운스 필터링 로직, 빈 결과 처리를 구현합니다.

## Phase 구조

### Phase 1: 데이터 레이어
- [ ] Task 1.1: 검색 필터 확장 (StudentEntity)

### Phase 2: 비즈니스 로직
- [ ] Task 2.1: StudentListReactor 검색 Action/State 추가
- [ ] Task 2.2: 디바운스 로직 구현

### Phase 3: UI 레이어
- [ ] Task 3.1: StudentListViewController SearchBar 추가
- [ ] Task 3.2: 검색 결과 바인딩

### Phase 4: 테스트
- [ ] Task 4.1: 검색 로직 단위 테스트

---

[AskUserQuestion]
이 계획대로 구현을 시작하시겠습니까?
1. 구현 시작 - plan.md대로 코드 작성 시작
2. 계획 수정 - 추가 조정 후 재검토

User: 1

Claude: 구현 승인 완료.

다음 단계: /ai-dev.impl PROJ-32398
```

---

## 다음 단계

계획 확정 및 구현 승인 후:

```
구현 계획이 확정되었습니다.

plan mode를 해제하고 구현을 시작합니다.
→ /ai-dev.impl PROJ-32398
```

---

## 연계 스킬

| 스킬 | 용도 |
|------|------|
| `/ai-dev.spec` | 선행 스펙 확정 (필수) |
| `/ai-dev.impl` | 후속 구현 시작 |

---

## Codex 수준 품질 확보 (`--no-codex` 모드)

### Codex가 제공하던 가치와 대체 방법

| Codex 기능 | Claude 대체 방법 |
|-----------|------------------|
| 독립적 코드 탐색 | Claude에게 "관련 코드 찾아줘" 명시적 요청 |
| 크로스 체크 | 자체 검증 체크리스트로 대체 |
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
"Repository에 검색 메서드를 추가합니다"

# Good (구체적)
"Sources/Repositories/StudentRepository.swift에 검색 메서드 추가:

```swift
// Line 45 이후 추가
/// [기능] 학생 이름으로 검색
/// - Parameter keyword: 검색어
/// - Returns: 필터링된 학생 목록
func searchStudents(keyword: String) -> Single<[StudentEntity]> {
    return fetchAll()
        .map { students in
            students.filter { $0.name.contains(keyword) }
        }
}
```"
```

### 필수 검증 체크리스트

- [ ] 모든 파일 경로가 전체 경로로 명시됨
- [ ] 각 Task에 구체적 코드 스니펫 포함
- [ ] 의존성 순서가 명확히 표시됨
- [ ] 기존 유사 패턴 1개 이상 참조됨

---

**Created:** 2026-01-23
**Updated:** 2026-01-27
**Version:** 3.1 (의존성 그래프 기반 Task 분해 추가)
