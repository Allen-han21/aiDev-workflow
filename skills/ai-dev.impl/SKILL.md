---
name: ai-dev.impl
description: plan.md의 Task 순서대로 코드를 구현합니다. Task별 로컬 커밋 + 테스트 + Xcode 실행. "구현해줘", "개발해줘", "코드 작성해줘" 요청 시 활성화.
---

# Skill: ai-dev.impl

plan.md의 Task 순서대로 코드를 구현합니다. **plan mode를 벗어나 Developer 역할로 전환**됩니다.

---

## 전제 조건

**plan mode 해제** - 이 스킬은 실제 코드 수정을 수행합니다.

**필수 선행**:
- plan.md 존재
- 사용자 구현 승인 완료 (ai-dev.plan에서)

---

## 사용법

```bash
/ai-dev.impl PK-XXXXX
```

---

## 워크플로우

### Step 1: plan.md 읽기

```
~/.claude/contexts/work/kidsnote/docs/ai-dev/{PK-xxxx-개발내용}/plan.md
```

계획이 없으면 안내:
```
plan.md가 없습니다.
먼저 계획을 수립하세요: /ai-dev.plan PK-XXXXX
```

### Step 2: Task 순차 실행

```
for each Task in plan.md:
    1. Task 상세 확인
    2. 의존성 Task 완료 여부 확인
    3. 코드 구현
    4. 빌드 검증
    5. 테스트 (코드 또는 [allen-test] 로그)
    6. 로컬 커밋 생성
    7. plan.md에 완료 표시
```

### Step 2.5: Apple 문서 참조 (새 API 사용 시)

처음 사용하는 API나 불확실한 API 사용법은 Apple 문서를 참조합니다.

**apple-docs MCP 사용:**
```
mcp__apple-docs__search_apple_docs(query: "{API명}")
mcp__apple-docs__get_apple_doc_content(url: "{문서 URL}")
```

**확인 항목:**
- 올바른 사용 패턴
- 필수 파라미터
- 반환 타입
- 에러 처리 방법
- availability 버전 (프로젝트 최소 지원 버전과 비교)

**샘플 코드 참조:**
```
mcp__apple-docs__search_sample_code(query: "{기능명}")
```

### Step 3: 코드 구현

**AGENTS.md 컨벤션 준수:**
- 들여쓰기: 탭 대신 스페이스
- 타입 명시: 변수/상수 초기화 시
- 주석: 문서화 주석 필수 (/// 형식)
- 네이밍: PascalCase (클래스), camelCase (변수/함수)

**구현 순서:**
1. 필요한 파일 읽기
2. 코드 작성 (Edit/Write)
3. 관련 파일 수정 (import 추가 등)

### Step 4: 빌드 검증

```bash
xcodebuild build \
  -workspace KidsNote.xcworkspace \
  -scheme "kidsnote Development" \
  -destination "generic/platform=iOS Simulator" \
  -quiet
```

빌드 실패 시:
- 에러 분석
- 수정 후 재시도
- 연속 3회 실패 시 사용자에게 알림

### Step 5: 테스트

**테스트 코드 작성 가능한 경우:**

```swift
func test_{기능}_{시나리오}() {
    // Given
    // When
    // Then
}
```

**테스트 코드 작성이 어려운 경우 (UI 관련 등):**

`[allen-test]` 로그 추가:

```swift
print("[allen-test] 검색어 입력: \(keyword)")
print("[allen-test] 검색 결과 개수: \(results.count)")
```

테스트 방법 문서화:
```markdown
### 테스트 방법
1. {화면}으로 이동
2. {액션} 수행
3. Xcode Console에서 `[allen-test]`로 필터링
4. {예상 결과} 확인
```

### Step 6: 로컬 커밋 생성

**각 Task 완료 후 커밋:**

```bash
git add {관련 파일들}
git commit -m "$(cat <<'EOF'
[PK-XXXXX] feat(scope): Task 설명

- 상세 내용 1
- 상세 내용 2
EOF
)"
```

**커밋 메시지 형식 (AGENTS.md 준수):**
```
[PK-XXXXX] <Type>(<Scope>): <Subject>

<Body>
```

| Type | 설명 |
|------|------|
| feat | 새로운 기능 |
| fix | 버그 수정 |
| refactor | 리팩토링 |

### Step 7: plan.md 업데이트

완료된 Task 체크:

```markdown
- [x] Task 1.1: Entity 정의 ✅ (2026-01-27)
- [ ] Task 1.2: Repository 구현
```

### Step 8: 다음 Task 확인

```
Task 1.1 완료되었습니다.
커밋: abc1234

다음 Task로 진행하시겠습니까?
→ Task 1.2: Repository 구현

[Y] 계속  [N] 중단
```

`--auto` 옵션 사용 시 자동 진행.

### Step 9: 모든 Task 완료 후

**1. Xcode + 시뮬레이터 실행:**

```bash
osascript <<'EOF'
tell application "Xcode" to activate
delay 0.5
tell application "System Events"
    tell process "Xcode"
        click menu item "Run" of menu "Product" of menu bar 1
    end tell
end tell
EOF
```

**2. 전체 기능 테스트:**
- 시뮬레이터에서 기능 확인
- Console에서 `[allen-test]` 로그 확인

### Step 9.5: Figma 시각적 검증 (UI Task인 경우)

Figma 디자인이 있는 UI 구현 Task 완료 후 시각적 검증을 수행합니다.

**검증 조건:**
- analyze.md에 Figma URL이 있는 경우
- UI 관련 Task를 구현한 경우

**figma-ocaml MCP로 검증:**

```
# 1. 상세 디자인 가져오기
mcp__figma-ocaml__figma_get_node(
  file_key: "{file_key}",
  node_id: "{node_id}",
  token: "{FIGMA_TOKEN}",
  depth: 5
)

# 2. 시각적 검증 (SSIM 95%+ 목표)
mcp__figma-ocaml__figma_verify_visual(
  file_key: "{file_key}",
  node_id: "{node_id}",
  token: "{FIGMA_TOKEN}",
  screenshot_path: "{구현 스크린샷 경로}",
  target_ssim: 0.95,
  max_iterations: 3
)

# 3. 반복 검증이 필요한 경우
mcp__figma-ocaml__figma_fidelity_loop(
  file_key: "{file_key}",
  node_id: "{node_id}",
  token: "{FIGMA_TOKEN}",
  screenshot_path: "{구현 스크린샷 경로}"
)
```

**Figma 검증 흐름:**

```
┌─────────────────────────────────────────────────────────────┐
│  UI Task 구현 완료                                          │
│      ↓                                                      │
│  시뮬레이터 스크린샷 캡처                                    │
│      ↓                                                      │
│  figma_get_node         → Figma 디자인 가져오기             │
│      ↓                                                      │
│  figma_verify_visual    → SSIM 비교 (95%+ 목표)            │
│      ↓                                                      │
│  ✅ 통과 (95%+) → 다음 단계                                 │
│  ❌ 미달 → figma_fidelity_loop로 반복 수정                  │
└─────────────────────────────────────────────────────────────┘
```

**검증 결과 출력:**

```markdown
### Figma 시각적 검증 결과

| 화면 | SSIM | 상태 |
|------|------|------|
| {화면명} | 97.2% | ✅ 통과 |
| {화면명} | 93.1% | ⚠️ 미달 (수정 필요) |

**미달 항목 수정 사항:**
- 색상: #1F8CF8 → rgb(32,141,249)로 변환
- 간격: padding 12px → 16px로 수정
```

**3. 테스트 로그 삭제:**

테스트 완료 후 `[allen-test]` 로그 제거:

```swift
// 삭제 대상
print("[allen-test] 검색어 입력: \(keyword)")  // 삭제
print("[allen-test] 검색 결과 개수: \(results.count)")  // 삭제
```

**4. 로그 삭제 커밋:**

```bash
git add -u
git commit -m "[PK-XXXXX] chore: 테스트 로그 삭제"
```

---

## 출력 형식

**각 Task 완료 시:**
```
✅ Task 1.1 완료: Entity 정의
   파일: Sources/Features/StudentSearch/Models/StudentSearchEntity.swift
   테스트: Unit Test 추가됨
   커밋: abc1234

다음 Task로 진행합니다...
```

**모든 Task 완료 시:**
```
🎉 모든 Task가 완료되었습니다.

구현 결과:
- 생성된 파일: 5개
- 수정된 파일: 3개
- 커밋 수: 8개

Xcode에서 시뮬레이터를 실행합니다...

[테스트 안내]
1. 시뮬레이터에서 기능 확인
2. Xcode Console에서 [allen-test] 검색
3. 정상 동작 확인 후 "테스트 완료"라고 해주세요

테스트 완료 후 [allen-test] 로그를 삭제합니다.

다음 단계: /ai-dev.review PK-XXXXX
```

---

## 파일 생성 위치

| 타입 | 경로 |
|------|------|
| ViewController | `Sources/Features/{Feature}/Views/` |
| Reactor | `Sources/Features/{Feature}/Reactors/` |
| Entity | `Sources/Features/{Feature}/Models/` |
| Service | `Sources/Services/` |
| Repository | `Sources/Repositories/` |
| UseCase | `Sources/UseCases/` |

---

## 코드 템플릿

### Entity

```swift
/// [목적] {Entity} 데이터를 표현합니다.
/// [기능] {설명}
struct {Feature}Entity: Codable {
    let id: Int
    let name: String
    // ...
}
```

### Reactor

```swift
import ReactorKit
import RxSwift

/// [목적] {Feature} 화면의 상태 관리
/// [기능] {설명}
final class {Feature}Reactor: Reactor {
    enum Action {
        case load
    }

    enum Mutation {
        case setLoading(Bool)
        case setData([Entity])
    }

    struct State {
        var isLoading: Bool = false
        var data: [Entity] = []
    }

    let initialState: State = State()

    func mutate(action: Action) -> Observable<Mutation> {
        // ...
    }

    func reduce(state: State, mutation: Mutation) -> State {
        var newState: State = state
        // ...
        return newState
    }
}
```

---

## 옵션

| 옵션 | 설명 | 예시 |
|------|------|------|
| `--task N` | 특정 Task부터 시작 | `/ai-dev.impl PK-12345 --task 2.1` |
| `--no-commit` | 커밋 생성 생략 | 개발 중 반복 작업 시 |
| `--no-run` | Xcode 실행 생략 | 빌드만 확인 시 |
| `--auto` | 모든 Task 자동 진행 | 확인 없이 연속 실행 |

---

## 예제

### 예제 1: 순차 구현

```
User: /ai-dev.impl PK-32398

Claude: [ai-dev.impl 활성화]

plan.md 읽는 중...
경로: ~/.claude/contexts/work/kidsnote/docs/ai-dev/PK-32398-원생관리-검색기능/plan.md

6개 Task 확인됨

---

Task 1.1 시작: Entity 정의
파일: Sources/Features/StudentList/Models/StudentSearchEntity.swift

[Write 도구 실행]

빌드 검증 중...
✅ 빌드 성공

테스트 추가 중...
[allen-test] 로그 추가

로컬 커밋 생성...
커밋: abc1234

✅ Task 1.1 완료

다음 Task로 진행하시겠습니까?
→ Task 1.2: Repository 구현

User: Y

Claude: Task 1.2 시작: Repository 구현
...
```

### 예제 2: 모든 Task 완료

```
...

✅ Task 4.2 완료: 테스트 작성

---

🎉 모든 Task가 완료되었습니다.

구현 결과:
- 생성된 파일: 5개
- 수정된 파일: 3개
- 커밋 수: 6개

Xcode에서 시뮬레이터를 실행합니다...
[osascript 실행]

[테스트 안내]
1. 시뮬레이터에서 원생 검색 기능 확인
2. Xcode Console에서 [allen-test] 검색
3. 검색어 입력 시 로그 출력 확인

정상 동작 확인 후 "테스트 완료"라고 해주세요.

User: 테스트 완료

Claude: [allen-test] 로그 삭제 중...
3개 파일에서 5개 로그 삭제

커밋 생성...
[PK-32398] chore: 테스트 로그 삭제

✅ 구현 완료

다음 단계: /ai-dev.review PK-32398
```

---

## 진행 상황 추적

plan.md에 진행 상황 기록:

```markdown
## 진행 현황

| Task | 상태 | 완료일 | 커밋 |
|------|------|--------|------|
| 1.1 | ✅ 완료 | 2026-01-27 | abc1234 |
| 1.2 | 🔄 진행중 | - | - |
| 2.1 | ⏳ 대기 | - | - |
```

---

## 다음 단계

모든 Task 완료 후:

```
구현이 완료되었습니다.

다음 단계로 코드 리뷰를 진행하시겠습니까?
→ /ai-dev.review PK-32398
```

---

## 연계 스킬

| 스킬 | 용도 |
|------|------|
| `/ai-dev.plan` | 선행 계획 수립 (필수) |
| `/ai-dev.review` | 후속 코드 리뷰 |

---

**Created:** 2026-01-23
**Updated:** 2026-01-27
**Version:** 2.0
