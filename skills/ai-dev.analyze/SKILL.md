---
name: ai-dev.analyze
description: 코드베이스 분석 + 엣지 케이스 식별 + 확인 사항 정리. JIRA 티켓을 입력받아 analyze.md 생성. "분석해줘", "analyze", "코드 분석" 요청 시 활성화.
---

# Skill: ai-dev.analyze

JIRA 티켓 정보(본문+댓글)와 Figma 디자인(자동 감지)을 기반으로 코드베이스를 분석합니다.

---

## 전제 조건

**plan mode에서 실행** - 이 스킬은 분석 전용이며 파일 수정을 하지 않습니다.

---

## 사용법

```bash
/ai-dev.analyze PK-XXXXX
```

---

## 워크플로우

### Step 1: JIRA 티켓 조회

```bash
/jira-get {TICKET_ID}
```

**수집 항목:**
- 제목 (Summary)
- 설명 (Description) - 전체 본문
- 담당자 (Assignee)
- 댓글 (Comments) - 기획/디자인 논의 내용
- 첨부파일 (Attachments) - Figma URL 감지
- Epic 링크 (있으면)

### Step 2: Figma 디자인 컨텍스트 추출

JIRA 본문/댓글에서 Figma URL 자동 감지:

```
# URL 패턴
figma.com/design/{file_key}/{file_name}?node-id={node_id}
figma.com/file/{file_key}/{file_name}?node-id={node_id}
```

**Figma URL 발견 시 figma-ocaml MCP 사용 (강화된 워크플로우):**

```
# 1. URL 파싱
mcp__figma-ocaml__figma_parse_url(url: "{figma_url}")

# 2. 화면 전체 목록 확인
mcp__figma-ocaml__figma_list_screens(
  file_key: "{file_key}",
  token: "{FIGMA_TOKEN}"
)

# 3. 구조 파악 (Outside-In 패턴)
mcp__figma-ocaml__figma_get_node_summary(
  file_key: "{file_key}",
  node_id: "{node_id}",
  token: "{FIGMA_TOKEN}"
)

# 4. 계층 시각화
mcp__figma-ocaml__figma_tree(
  file_key: "{file_key}",
  node_id: "{node_id}",
  token: "{FIGMA_TOKEN}"
)

# 5. Figma Variables 가져오기 (색상/간격/타이포 등)
mcp__figma-ocaml__figma_get_variables(
  file_key: "{file_key}",
  token: "{FIGMA_TOKEN}"
)

# 6. 디자인 토큰 추출
mcp__figma-ocaml__figma_export_tokens(
  file_key: "{file_key}",
  node_id: "{node_id}",
  token: "{FIGMA_TOKEN}"
)

# 7. 상세 노드 정보 (필요 시)
mcp__figma-ocaml__figma_get_node(
  file_key: "{file_key}",
  node_id: "{node_id}",
  token: "{FIGMA_TOKEN}",
  depth: 3
)
```

**Figma 분석 흐름 (Outside-In 패턴):**

```
┌─────────────────────────────────────────────────────────────┐
│  figma_parse_url        → URL에서 file_key, node_id 추출    │
│      ↓                                                      │
│  figma_list_screens     → 전체 화면 목록 파악               │
│      ↓                                                      │
│  figma_get_node_summary → 구조 요약 (Outside-In 시작)       │
│      ↓                                                      │
│  figma_tree             → 계층 구조 시각화                  │
│      ↓                                                      │
│  figma_get_variables    → Figma Variables (색상/간격)       │
│      ↓                                                      │
│  figma_export_tokens    → 디자인 토큰 추출                  │
│      ↓                                                      │
│  figma_get_node         → 상세 구현 시 참조                 │
└─────────────────────────────────────────────────────────────┘
```

**추출 항목:**
- 시나리오 흐름 (화면 간 네비게이션)
- 케이스별 화면 (정상/에러/빈 상태/로딩)
- as-is / to-be 비교 (있는 경우)
- 디자인 토큰 (색상, 폰트, 간격)
- Figma Variables (디자인 시스템 변수)
- 컴포넌트 계층 구조

### Step 3: iOS 코드베이스 분석

#### 3.1 LSP 기반 심볼 탐색 (1차)

Claude Code의 **swift-lsp 플러그인**이 활성화되어 있으므로,
Swift 파일을 Read할 때 LSP가 자동으로 타입 정보를 제공합니다.

**탐색 전략:**

1. **진입점 특정** - 키워드 기반 파일 검색
   ```bash
   Glob "**/*{키워드}*.swift"
   ```

2. **핵심 파일 Read** - LSP가 심볼/타입 정보 자동 추출
   ```
   # 예: StudentListViewController.swift 읽기
   → LSP가 의존하는 타입 정보 제공
   → Reactor, Service, Entity 타입 위치 자동 추적
   ```

3. **의존성 그래프 구축** - 참조 관계 기반
   ```
   Entity (Model)
       ↓
   Repository (Data)
       ↓
   Service/UseCase (Domain)
       ↓
   Reactor/ViewModel (Presentation)
       ↓
   ViewController/View (UI)
   ```

**LSP 활용 프롬프트 예시:**
```
"{ViewController}.swift 파일을 읽고,
이 클래스가 의존하는 타입들(Reactor, Service, Entity)의
정의 위치와 참조 관계를 분석해줘"
```

**수집 항목:**
- 핵심 타입 목록 (클래스/프로토콜/구조체)
- 각 타입의 정의 위치 (파일 경로)
- 타입 간 의존 관계 (호출/참조)
- 프로토콜 구현체 목록

#### 3.2 Explore 에이전트 (2차 - 패턴 탐색)

LSP로 특정된 영역 주변의 **패턴 및 컨벤션**을 탐색:

```
Task(subagent_type="Explore", prompt="
{티켓 제목}과 관련된 **유사 기능 구현 패턴**을 탐색합니다.

이미 특정된 핵심 파일:
- {LSP로 찾은 파일 목록}

찾아야 할 것:
1. 유사한 기능의 기존 구현 패턴
2. 해당 모듈에서 사용하는 공통 컴포넌트
3. 테스트 코드 패턴
4. API 호출 패턴

탐색 범위: 특정된 파일과 같은 Feature 디렉토리
탐색 깊이: medium
")
```

### Step 3.3: Apple 공식 문서 참조 (iOS 프로젝트)

코드베이스에서 사용되는 주요 API에 대해 Apple 문서를 참조합니다.

**apple-docs MCP 사용:**
```
mcp__apple-docs__search_apple_docs(query: "{API명}")
```

**확인 항목:**
- deprecated API 사용 여부
- availability 버전 (iOS 최소 지원 버전과 비교)
- 공식 권장 패턴
- 알려진 제약사항

**분석 결과 템플릿에 포함 (Step 6):**
```markdown
## 3.3. Apple 공식 문서 참조

### 사용 API 분석
| API | 상태 | iOS 버전 | 비고 |
|-----|------|----------|------|
| {API명} | ✅ 사용 가능 / ⚠️ deprecated | iOS {버전}+ | {비고} |

### 주의 사항
- {공식 문서에서 확인된 제약사항}
```

### Step 3.4: Rx 데이터 흐름 분석 (ReactorKit 프로젝트)

ReactorKit 기반 프로젝트에서 Action → Mutation → State 흐름을 분석합니다.

#### 3.4.1 grepai 그래프 검색으로 호출 관계 추출 (권장)

**grepai trace 명령어**:
```bash
# viewDidLoad에서 호출하는 모든 Action 추적
grepai trace callees "viewDidLoad" --json --depth 2

# 특정 Action의 호출 그래프 (Action → Mutation → State)
grepai trace graph "{ActionName}" --json --depth 3

# 같은 State 필드를 변경하는 코드 의미 검색
grepai search "{StateField} state mutation" --json --limit 10
```

**grepai 활용 워크플로우**:
```
[1단계: 호출 관계 파악]
grepai trace callees "viewDidLoad" --json
  ↓
  loadData, loadExistTempFile 등 발견
  ↓
[2단계: Action → State 영향 그래프]
grepai trace graph "{ActionName}" --depth 3 --json
  ↓
  Action → Mutation → State.field 경로 추출
  ↓
[3단계: 충돌 가능 Action 탐색]
grepai search "same state field mutation" --json
  ↓
  같은 필드 변경하는 Action 쌍 식별
```

#### 3.4.2 Grep 기반 분석 (fallback)

**Grep 명령어** (grepai 사용 불가 시):
```bash
Grep "rx\.viewDidLoad" {ViewController}.swift
Grep "\.bind\(to: reactor\.action\)" {ViewController}.swift
Grep "observe(on:.*Scheduler" {ViewController}.swift
Grep "Observable\.merge\|Observable\.concat" {Reactor}.swift
```

#### 3.4.3 분석 결과 템플릿

**분석 결과 템플릿에 포함 (Step 6):**
```markdown
## 3.4 Rx 데이터 흐름 분석

### viewDidLoad Action 순서
| 순서 | 라인 | Action | 스케줄러 | 실행 시점 |
|------|------|--------|----------|----------|
| 1 | L{라인} | .{Action명} | (없음) | 동기/즉시 |
| 2 | L{라인} | .{Action명} | asyncInstance | 비동기 |

### Action → State 영향 관계
| Action | 호출 경로 | 변경 State 필드 | 동시 호출 가능 Action | 위험도 |
|--------|----------|----------------|---------------------|--------|
| .{Action} | mutate→{...}→{Mutation} | {State.field} | .{OtherAction} | 🟡/❌ |

### 스케줄러 사용 현황
| 파일:라인 | 스케줄러 | 용도 |
|----------|----------|------|
| L{라인} | MainScheduler.instance | UI 업데이트 보장 |
| L{라인} | MainScheduler.asyncInstance | 비동기 실행 (순서 미보장 주의) |
```

#### 3.4.4 Neo4j 아키텍처 분석 (선택적)

Neo4j MCP 서버 (`neo4j-code-graph`) 연결 시 그래프 기반 분석을 수행합니다.

**사용 조건**: `mcp__neo4j-code-graph__neo4j_query` 도구가 사용 가능할 때

**분석 도구**:
```bash
# 1. 파일 영향도 분석
mcp__neo4j-code-graph__neo4j_find_impact(file_path: "{변경 예정 파일}")

# 2. Reactor 워크플로우 분석
mcp__neo4j-code-graph__neo4j_trace_workflow(reactor_name: "{Reactor명}")

# 3. 유사 코드 패턴 조회
mcp__neo4j-code-graph__neo4j_query(cypher: "
  MATCH (f:CodeFile)-[r:SIMILAR_TO]-(similar:CodeFile)
  WHERE f.name CONTAINS '{파일명}'
  RETURN similar.name, similar.module, r.score
  ORDER BY r.score DESC LIMIT 5
")
```

**출력 템플릿** (Step 6에 추가):
```markdown
### 3.4.4 Neo4j 아키텍처 분석

#### 파일 영향도
| 대상 파일 | 위험도 | 유사 파일 수 | 같은 모듈 파일 수 |
|-----------|--------|-------------|-----------------|
| {파일} | HIGH/MEDIUM/LOW | N | N |

#### Race Condition 위험 (그래프 기반)
| State 필드 | 경쟁 Action | 위험도 | 근거 |
|-----------|------------|--------|------|
| {필드} | {actions} | P1 확정 | Neo4j workflow 분석 |
```

**Fallback**: Neo4j 연결 실패 시 기존 grepai/Grep 분석만 수행 (영향 없음)

### Step 3.5: Android 코드 참조 (선택적)

동일 기능이 Android에 이미 구현되어 있다면 참조하여 비교/보완:

**Android 프로젝트 경로**: `~/Dev/Repo/kidsnote_android`

#### 3.5.1 Android PR 검색

**⚠️ 주의**: iOS와 Android는 별도 JIRA 티켓을 사용하므로 **내용 기반 검색** 필요

**검색 키워드 추출:**
1. JIRA 티켓 제목에서 핵심 키워드 추출
2. 기능명, 화면명 등으로 검색

```bash
# 1. 내용 기반 검색 (권장)
gh pr list --repo kidsnote/kidsnote_android --search "원생 검색" --state all
gh pr list --repo kidsnote/kidsnote_android --search "student search" --state all

# 2. 날짜 범위로 최근 PR 확인 (기능명 모호할 때)
gh pr list --repo kidsnote/kidsnote_android --state merged --limit 50

# 3. PR 상세 조회
gh pr view {PR_NUMBER} --repo kidsnote/kidsnote_android

# 4. PR 변경 파일 목록
gh pr diff {PR_NUMBER} --repo kidsnote/kidsnote_android --name-only

# 5. PR diff 내용 확인
gh pr diff {PR_NUMBER} --repo kidsnote/kidsnote_android
```

**검색 전략:**
| 순서 | 방법 | 예시 |
|------|------|------|
| 1 | 기능 키워드 | "원생 검색", "student search" |
| 2 | 화면명 | "StudentList", "원생 목록" |
| 3 | API 엔드포인트 | "students/search" |
| 4 | Epic 연결 | 같은 Epic의 Android 티켓 확인 |

**PR에서 확인할 항목:**
- PR 제목/설명: 구현 방향 및 주요 변경 사항
- 변경 파일 목록: 영향 범위 파악
- 코드 diff: 실제 구현 로직 확인
- 리뷰 코멘트: 논의된 이슈 및 결정 사항

#### 3.5.2 Android 코드베이스 탐색

PR이 없거나 추가 탐색이 필요한 경우:

```
Task(subagent_type="Explore", prompt="
~/Dev/Repo/kidsnote_android 에서 {티켓 제목}과 관련된 코드를 탐색합니다.

찾아야 할 것:
1. 관련 Activity/Fragment 파일
2. 관련 ViewModel 파일
3. 관련 Repository/UseCase 파일
4. API 호출 패턴
5. 엣지 케이스 처리 로직

탐색 깊이: medium
")
```

**Android 참조 목적:**

| 항목 | 설명 |
|------|------|
| 비즈니스 로직 | 이미 구현된 로직 참조하여 누락 방지 |
| API 패턴 | 엔드포인트, 파라미터, 응답 처리 확인 |
| 엣지 케이스 | Android에서 처리한 예외 상황 참고 |
| 플랫폼 일관성 | iOS/Android 동작 일관성 유지 |
| PR 리뷰 | 코드 리뷰에서 논의된 이슈 참고 |

**참조 결과 활용:**
- Android PR 있음 → PR 내용 및 리뷰 코멘트 참고
- Android 구현 있음 → iOS 구현 시 참고 사항으로 기록
- Android 구현 없음 → iOS 선행 개발로 표시
- 차이점 발견 시 → 확인 필요 사항에 추가

### Step 4: 엣지 케이스 분석

코드 분석 결과를 바탕으로 엣지 케이스 식별:

**분석 관점:**
- 빈 데이터 처리
- 네트워크 오류 상황
- 권한/인증 실패
- 동시성 이슈
- 메모리/성능 제약
- 하위 호환성

### Step 5: 확인 필요 사항 정리

기획/디자인에 확인이 필요한 사항을 AskUserQuestion으로 질문:

```
AskUserQuestion([
  {
    question: "빈 목록일 때 어떤 UI를 표시할까요?",
    header: "빈 상태 UI",
    options: [
      { label: "기존 EmptyView 사용", description: "앱 전역 빈 상태 컴포넌트" },
      { label: "커스텀 메시지", description: "이 화면 전용 빈 상태 디자인" }
    ]
  }
])
```

### Step 6: analyze.md 생성

분석 결과를 저장:

```bash
# 저장 경로
~/.claude/contexts/work/kidsnote/docs/ai-dev/{PK-xxxx-개발내용}/analyze.md
```

**폴더명 생성 규칙:**
- 티켓 번호: JIRA 티켓 키 (예: PK-32398)
- 개발내용: JIRA 티켓 제목에서 추출
  - 공백 → 하이픈으로 변환
  - 특수문자 제거
  - 최대 30자
- 예: `PK-32398-원생관리-검색기능`

---

## 출력 템플릿

```markdown
# {TICKET_ID} 분석 결과

**분석일**: YYYY-MM-DD HH:MM
**티켓**: {TICKET_ID} - {제목}
**담당자**: {Assignee}

---

## 1. 요구사항 요약

### 티켓 본문
{Description 요약}

### 핵심 논의 (댓글)
- {날짜} {작성자}: {핵심 내용}
- ...

---

## 2. Figma 디자인 분석

### 화면 목록
| 화면명 | 설명 | Node ID |
|--------|------|---------|
| {화면1} | {설명} | {node_id} |

### 시나리오 흐름
1. {진입 조건}
2. {액션}
3. {결과}

### 케이스별 화면
| 케이스 | 화면 | 설명 |
|--------|------|------|
| 정상 | {화면} | {설명} |
| 빈 상태 | {화면} | {설명} |
| 에러 | {화면} | {설명} |
| 로딩 | {화면} | {설명} |

### as-is / to-be (있는 경우)
| 항목 | 현재 | 변경 |
|------|------|------|
| {항목} | {as-is} | {to-be} |

---

## 3. iOS 코드베이스 분석

### 3.1 심볼 의존성 그래프

#### 핵심 타입 계층
```
{TargetEntity} (Model)
    │
    ├── {Repository} (Data)
    │       └── {Service} (Domain)
    │               └── {Reactor} (Presentation)
    │                       └── {ViewController} (UI)
    │
    └── {NewEntity} (Model) ← 신규 생성 필요 시
```

#### 타입별 참조 현황
| 타입 | 정의 위치 | 참조 수 | 변경 영향도 |
|------|----------|--------|-----------|
| {Entity} | `Sources/Models/...` | N | 높음/중간/낮음 |
| {Reactor} | `Sources/Features/.../Reactors/...` | N | 높음/중간/낮음 |
| {Service} | `Sources/Services/...` | N | 높음/중간/낮음 |

#### 프로토콜 구현 현황
| 프로토콜 | 구현체 | 파일 위치 |
|----------|--------|----------|
| {Protocol}Protocol | {Implementation} | `path/to/file.swift` |

### 3.2 관련 파일
| 파일 | 역할 | 변경 예상 |
|------|------|----------|
| `path/to/file.swift` | {역할} | 높음/중간/낮음 |

### 3.3 기존 패턴
- {패턴}: {설명}

### 3.4 의존성
- **API**: {엔드포인트}
- **라이브러리**: {라이브러리명}

---

## 3.5. Android 코드 참조

### Android PR 정보
| 항목 | 내용 |
|------|------|
| 검색 키워드 | {사용한 검색어} |
| PR 번호 | #{PR_NUMBER} (없으면 "없음") |
| Android 티켓 | {PA-XXXXX} (iOS 티켓과 다름) |
| PR 제목 | {PR 제목} |
| PR 상태 | merged / open / closed |
| PR URL | https://github.com/kidsnote/kidsnote_android/pull/{NUMBER} |

### PR 주요 내용 (PR이 있는 경우)
- **구현 방향**: {PR 설명에서 추출}
- **주요 변경**: {핵심 변경 사항}
- **리뷰 포인트**: {코드 리뷰에서 논의된 주요 이슈}

### Android 구현 현황
| 상태 | 설명 |
|------|------|
| ✅ 구현됨 / ❌ 미구현 / 🔄 부분 구현 | {상태 설명} |

### 참조 파일 (Android에 구현된 경우)
| 파일 | 역할 | iOS 참고 사항 |
|------|------|--------------|
| `path/to/File.kt` | {역할} | {iOS 구현 시 참고할 점} |

### 비즈니스 로직 비교
| 항목 | Android | iOS 적용 |
|------|---------|----------|
| {로직 1} | {Android 구현} | {iOS에 적용할 방식} |
| {로직 2} | {Android 구현} | {iOS에 적용할 방식} |

### API 패턴
- **엔드포인트**: {Android에서 사용하는 API}
- **요청 파라미터**: {파라미터 목록}
- **응답 처리**: {응답 처리 방식}

### Android 엣지 케이스 처리
| 케이스 | Android 처리 | iOS 적용 여부 |
|--------|-------------|--------------|
| {케이스} | {처리 방식} | ✅/❌ |

### 플랫폼 일관성 확인
- [ ] {일관성 체크 항목 1}
- [ ] {일관성 체크 항목 2}

---

## 4. 엣지 케이스

| 케이스 | 조건 | 현재 처리 | 권장 처리 |
|--------|------|----------|----------|
| 빈 데이터 | {조건} | {현재} | {권장} |
| 네트워크 오류 | {조건} | {현재} | {권장} |
| {기타} | {조건} | {현재} | {권장} |

---

## 5. 기술적 제약

- {제약 1}
- {제약 2}

---

## 6. 확인 필요 사항

- [ ] {질문 1} → 답변: {사용자 답변}
- [ ] {질문 2} → 답변: {사용자 답변}

---

## 7. 원본 참조

- **JIRA**: {티켓 URL}
- **Figma**: {Figma URL}

---

*Generated by ai-dev.analyze*
```

---

## 예제

### 예제 1: 기본 분석

```
User: /ai-dev.analyze PK-32398

Claude: [ai-dev.analyze 활성화]

JIRA 티켓 조회 중...
PK-32398: 원생관리 검색 기능

본문 + 댓글 수집 완료.
- 댓글 3개: 기획자/디자이너 논의 내용 포함

Figma URL 감지됨:
https://figma.com/design/xxx?node-id=123:456

figma-ocaml MCP로 디자인 컨텍스트 추출 중...
- 화면 5개 발견
- 케이스별 화면: 정상/빈 상태/에러

iOS 코드베이스 분석 중...
[Explore 에이전트 실행]

관련 파일:
- StudentListViewController.swift
- StudentListReactor.swift
- StudentService.swift

Android PR 검색 중...
키워드: "원생 검색", "student search"
[gh pr list --repo kidsnote/kidsnote_android --search "원생 검색" --state all]

Android PR 발견: #1234
[gh pr view 1234 --repo kidsnote/kidsnote_android]

PR 정보:
- 제목: [PA-5678] feat(student): 원생 검색 기능 추가  ← Android 티켓 번호는 다름
- 상태: merged
- 변경 파일: 8개

PR 주요 내용:
- 검색 디바운스 300ms 적용
- 빈 결과 시 인라인 메시지 표시
- 리뷰 코멘트: "특수문자 입력 시 예외 처리 필요" → 반영됨

Android 코드베이스 탐색 중...
[Explore 에이전트 - ~/Dev/Repo/kidsnote_android]

참조 파일:
- StudentListFragment.kt
- StudentListViewModel.kt
- StudentRepository.kt

비교 결과:
- 검색 디바운스: Android 300ms 적용됨 → iOS도 동일 적용 권장
- 빈 결과 처리: Android 인라인 메시지 사용
- API: /api/v2/students/search 동일
- 특수문자 처리: Android에서 이슈 발견 후 수정됨 → iOS도 동일 적용

엣지 케이스 확인 중...
- 검색어가 없을 때
- 검색 결과가 없을 때
- 네트워크 오류 시

확인 필요 사항:
[AskUserQuestion]
1. 검색 디바운스 시간은?
2. 빈 검색 결과 UI는?

분석 완료. analyze.md 저장됨.
경로: ~/.claude/contexts/work/kidsnote/docs/ai-dev/PK-32398-원생관리-검색기능/analyze.md
```

---

## 다음 단계

분석 완료 후:

```
분석이 완료되었습니다.

다음 단계로 스펙을 확정하시겠습니까?
→ /ai-dev.spec PK-32398
```

---

## 연계 스킬

| 스킬 | 용도 |
|------|------|
| `/ai-dev.spec` | 분석 결과로 스펙 확정 |
| `/jira-get` | JIRA 티켓 상세 조회 |

---

**Created:** 2026-01-23
**Updated:** 2026-01-27
**Version:** 3.0 (LSP 기반 심볼 탐색 통합)
