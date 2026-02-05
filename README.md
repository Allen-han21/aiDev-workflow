# AI-Dev Workflow

> JIRA 기반 AI 협업 개발 워크플로우 (Claude Code용)

JIRA 티켓 분석부터 PR 생성까지, AI가 단계별로 도와주는 개발 워크플로우입니다.

## v5.3 변경사항 (2026-02-05)

- **Neo4j Code Graph MCP 서버 추가**: 코드 그래프 기반 분석
  - `neo4j_query`: Cypher 쿼리 직접 실행
  - `neo4j_find_impact`: 파일 변경 영향도 분석
  - `neo4j_trace_workflow`: Reactor 워크플로우 추적 + **Race Condition 자동 탐지**
  - `neo4j_graph_stats`: 그래프 통계 조회
- **ai-dev 스킬 Neo4j 연동**:
  - `ai-dev.analyze`: Neo4j 아키텍처 분석 섹션 추가 (Step 3.4.4)
  - `ai-dev.work-check`: Neo4j 기반 Race Condition 분석
  - `ai-dev.code-check`: Neo4j 영향도 분석 연동
- **resolve-conversation 스킬 추가**: PR 리뷰 코멘트 응답 자동화
  - 미해결 코멘트 분석 → ACCEPT/DISCUSS/DISMISS 판정 → 응답 초안 생성

## v5.2 변경사항

- **pre-review 스킬 추가**: JIRA 티켓 사전검토 + Draft PR 생성
  - 경량 분석 → Draft 계획 → JIRA 업데이트 → Draft 구현 → Draft PR
  - 본격 개발 전 기능 테스트가 가능한 Draft 상태를 빠르게 생성
  - 기존 ai-dev 워크플로우에 영향 없음 (독립 스킬)

## v5.1 변경사항

- **Mega-skill 패턴**: `--auto` 옵션으로 TaskCreate/TaskUpdate 기반 자동 파이프라인
- **다단계 검증**: plan-check, code-check, work-check (총 14개 validators)
- **Sentinel 패턴**: 긴 작업 세션의 자동 저장/복원 (70% 컨텍스트 임계치)
- **워크플로우 순서 수정**: plan → plan-check (원본 zac's 패턴 준수)
- **9단계 워크플로우**: 기존 6단계에서 검증 단계 추가

## 주요 기능

- **9단계 워크플로우**: 분석 → 스펙 → 계획 → 계획검증 → 구현 → 코드검증 → 버그검증 → 리뷰 → PR
- **AI 크로스 체크**: Claude + Codex MCP 병렬 검증
- **14개 Validators**: 계획 검증 5개 + 코드 품질 3개 + 버그 탐지 6개
- **Neo4j 코드 그래프**: 아키텍처 분석 + Race Condition 자동 탐지
- **Figma 연동**: figma-ocaml MCP로 디자인 컨텍스트 자동 추출
- **크로스 플랫폼 참조**: iOS/Android 코드베이스 비교 분석
- **문서 자동 생성**: analyze.md, spec.md, plan.md 자동 생성
- **세션 관리**: Sentinel 패턴으로 컨텍스트 보존
- **PR 코멘트 응답**: 리뷰 코멘트 자동 분석 및 응답 초안 생성

## 빠른 시작

### 1. 설치

```bash
git clone https://github.com/Allen-han21/aiDev-workflow.git
cd aiDev-workflow
./scripts/install.sh
```

### 2. 사용법

```bash
# 전체 워크플로우 (단계별 확인)
/ai-dev PROJ-12345

# Mega-skill 자동화 (완전 자동)
/ai-dev PROJ-12345 --auto

# 빠른 개발 (검증 생략)
/ai-dev PROJ-12345 --auto --skip-checks

# Figma 디자인 포함
/ai-dev PROJ-12345 --figma https://figma.com/design/xxx

# 도움말 보기
/ai-dev help

# 사전검토 (Draft PR 빠르게 생성)
/ai-dev.pre-review PROJ-12345
/ai-dev.pre-review PROJ-12345 --figma https://figma.com/...
/ai-dev.pre-review PROJ-12345 --skip-jira  # JIRA 업데이트 스킵
/ai-dev.pre-review PROJ-12345 --skip-pr    # Draft PR 생성 스킵

# 개별 단계 실행
/ai-dev.analyze PROJ-12345     # 0단계: 분석
/ai-dev.spec PROJ-12345        # 1단계: 스펙 정의
/ai-dev.plan PROJ-12345        # 2단계: 계획 수립
/ai-dev.plan-check PROJ-12345  # 2.5단계: 계획 검증
/ai-dev.impl PROJ-12345        # 3단계: 구현
/ai-dev.code-check PROJ-12345  # 3.5단계: 코드 품질 검증
/ai-dev.work-check PROJ-12345  # 3.8단계: 버그 탐지
/ai-dev.review PROJ-12345      # 4단계: 리뷰
/ai-dev.pr PROJ-12345          # 5단계: PR 생성

# PR 리뷰 코멘트 응답
/ai-dev.resolve-conversation   # 미해결 코멘트 분석 및 응답 초안 생성
```

## 워크플로우 개요

```
┌─────────────────────────────────────────────────────────────────────────┐
│                    ai-dev 워크플로우 v5.1 (Mega-skill)                   │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                         │
│  [입력] JIRA 티켓 번호 + Figma URL (선택)                               │
│                                                                         │
│  ┌───────────────────────── TASK CHAIN ─────────────────────────┐      │
│  │                                                               │      │
│  │  Task 1: analyze [plan mode]                                 │      │
│  │  → JIRA 조회, Figma 분석, 코드 탐색 → analyze.md              │      │
│  │      │                                                        │      │
│  │      ▼ [blockedBy: 1]                                        │      │
│  │  Task 2: spec [plan mode]                                    │      │
│  │  → Claude + Codex 크로스 체크 → spec.md                       │      │
│  │      │                                                        │      │
│  │      ▼ [blockedBy: 2]                                        │      │
│  │  Task 3: plan [plan mode]                                    │      │
│  │  → Codex MCP 계획 생성 + Claude 검증 → plan.md               │      │
│  │      │                                                        │      │
│  │      ▼ [blockedBy: 3]                                        │      │
│  │  Task 4: plan-check ★ [plan mode]                            │      │
│  │  → 5개 validators + devil's advocate → plan-check-report.md  │      │
│  │      │                                                        │      │
│  │      ▼ [blockedBy: 4] [plan mode 해제]                       │      │
│  │  Task 5: impl                                                 │      │
│  │  → Task별 구현 + 로컬 커밋 + 테스트                           │      │
│  │      │                                                        │      │
│  │      ▼ [blockedBy: 5]                                        │      │
│  │  Task 6: code-check ★                                        │      │
│  │  → DRY/SOLID/Complexity 분석 → code-check-report.md          │      │
│  │      │                                                        │      │
│  │      ▼ [blockedBy: 6]                                        │      │
│  │  Task 7: work-check ★                                        │      │
│  │  → 6개 병렬 bug checkers → work-check-report.md              │      │
│  │      │                                                        │      │
│  │      ▼ [blockedBy: 7]                                        │      │
│  │  Task 8: review                                               │      │
│  │  → 비즈니스 규칙 검증 + 최종 승인 판정                         │      │
│  │      │                                                        │      │
│  │      ▼ [blockedBy: 8] (승인 시)                              │      │
│  │  Task 9: pr                                                   │      │
│  │  → Push + GitHub PR 생성 → PR URL                            │      │
│  │                                                               │      │
│  └───────────────────────────────────────────────────────────────┘      │
│                                                                         │
│  [SENTINEL PATTERN]                                                     │
│  긴 대화 시 자동 저장 → 새 세션에서 복원 → 이어서 실행                   │
│                                                                         │
└─────────────────────────────────────────────────────────────────────────┘
```

### 단계별 요약

| 단계 | 스킬 | 모드 | 핵심 메커니즘 | 출력물 |
|------|------|------|---------------|--------|
| 0 | `ai-dev.analyze` | Plan | JIRA + Figma + 코드 탐색 | `analyze.md` |
| 1 | `ai-dev.spec` | Plan | Claude + Codex 크로스 체크 | `spec.md` |
| 2 | `ai-dev.plan` | Plan | Codex MCP + Claude 검증 | `plan.md` |
| 2.5 | `ai-dev.plan-check` ★ | Plan | 5개 validators + devil's advocate | `plan-check-report.md` |
| 3 | `ai-dev.impl` | Dev | Task별 구현 + 커밋 | 소스 코드 |
| 3.5 | `ai-dev.code-check` ★ | Dev | DRY/SOLID/Complexity 분석 | `code-check-report.md` |
| 3.8 | `ai-dev.work-check` ★ | Dev | 6개 병렬 버그 체커 | `work-check-report.md` |
| 4 | `ai-dev.review` | Dev | 비즈니스 규칙 + 최종 판정 | 승인/변경요청 |
| 5 | `ai-dev.pr` | Dev | Push + GitHub PR | PR URL |

★ = v5.0에서 추가됨

## 사전검토 (pre-review) ★ v5.2

본격 개발 전 **기능 테스트가 가능한 Draft 상태**를 빠르게 생성하는 독립 스킬입니다.

```bash
/ai-dev.pre-review PROJ-12345
```

### 워크플로우

```
Step 1: Quick Analyze (경량 분석)
├── JIRA 티켓 조회
├── 키워드 기반 코드 탐색 (핵심 파일 2-3개)
└── 출력: quick-analyze.md

Step 2: Draft Plan (간소화된 계획)
├── Phase/Task 분해
└── 출력: draft-plan.md

Step 3: JIRA Update
├── 기존 Description 읽기
└── 사전검토 결과 추가 (구분선 + 템플릿)

Step 4: Draft Implementation
├── Task별 골격 코드 구현
├── Happy Path 로직만
└── 로컬 커밋

Step 5: Draft PR
├── /ai-dev.pr --draft 호출
└── Draft PR 생성
```

### Draft 구현 기준

| 레이어 | Draft 수준 |
|--------|-----------|
| Entity/Model | 100% 완성 |
| Repository | 골격 (API 연동) |
| Reactor/ViewModel | 기본 바인딩 (Happy Path) |
| UI | 레이아웃 완성 (세부 스타일 생략) |
| 에러 처리 | 생략 |
| 테스트 | [allen-test] 로그만 |

### ai-dev 연계

사전검토 후 완성 개발이 필요할 때:

```bash
/ai-dev PROJ-12345 --from impl
```

**중요**: 기존 ai-dev 9단계 워크플로우에 영향 없음 (독립 스킬)

## 검증 시스템 (v5.0)

### Plan-Check (계획 검증: 5개 Validators + Devil's Advocate)

| Validator | 역할 |
|-----------|------|
| completeness-checker | spec→plan 요구사항 누락 검사 |
| pattern-compliance | AGENTS.md 컨벤션 준수 검사 |
| feasibility-assessor | 기술적 실현 가능성 평가 |
| risk-assessor | 회귀/보안 위험 평가 |
| scope-discipline | 과잉 구현(gold-plating) 탐지 |
| + devil's advocate | 오탐(false positive) 감소 |

### Code-Check (코드 품질 검증)

- **DRY Checker**: 중복 코드 탐지
- **SOLID Checker**: 설계 원칙 위반 검사
- **Complexity Analyzer**: 순환 복잡도 분석

### Work-Check (버그 탐지: 6개 Bug Checkers)

- **Edge Case Hunter**: 경계 조건 누락 탐지
- **Race Condition Detector**: 동시성 문제 탐지
- **State Corruption Finder**: 상태 오염 탐지
- **Memory Leak Hunter**: 메모리 누수 탐지
- **Input Validation Checker**: 입력 검증 누락 탐지
- **Regression Detector**: 회귀 버그 탐지

## 옵션

| 옵션 | 설명 | 적용 단계 |
|------|------|-----------|
| `--auto` | 완전 자동 파이프라인 (Mega-skill) | 전체 |
| `--figma URL` | Figma 디자인 포함 | analyze |
| `--from PHASE` | 특정 단계부터 시작 | 전체 |
| `--to PHASE` | 특정 단계에서 종료 | 전체 |
| `--skip-checks` | plan-check, code-check, work-check 생략 | 전체 |
| `--no-codex` | Codex MCP 없이 Claude만 사용 | spec, plan |
| `--ultrathink` | 확장 사고 모드 활성화 | spec, plan |

### 사용 예시

```bash
# 전체 워크플로우 (단계별 확인)
/ai-dev PROJ-12345

# Mega-skill 자동화 (확인 없이 자동 진행)
/ai-dev PROJ-12345 --auto

# 빠른 개발 (검증 단계 생략)
/ai-dev PROJ-12345 --auto --skip-checks

# Figma 디자인 포함
/ai-dev PROJ-12345 --figma https://figma.com/design/xxx

# 구현부터 시작 (plan.md가 이미 있을 때)
/ai-dev PROJ-12345 --from impl

# 복잡한 문제 (최고 품질 모드)
/ai-dev PROJ-12345 --no-codex --ultrathink
```

## Sentinel 패턴 (세션 관리)

컨텍스트 한계를 초과할 수 있는 긴 워크플로우를 위한 패턴:

```bash
# 수동 저장
/ai-dev.sentinel save --ticket PROJ-12345

# 저장된 세션 목록
/ai-dev.sentinel list

# 세션 복원 (새 터미널에서 실행)
/ai-dev.sentinel restore sentinel-2026-01-28-153000

# 오래된 세션 정리
/ai-dev.sentinel cleanup --older-than 7d
```

**⚠️ 중요**: Claude Code는 자동으로 새 세션을 열 수 없습니다. 컨텍스트 임계치(70%)에 도달하면:
1. 자동 저장 + 복원 명령어 표시
2. **개발자가 직접 새 터미널을 열어야 함**
3. 복원 명령어 실행하여 이어서 진행

**자동 저장 트리거:**
- 단계 전환 시 (analyze→spec, spec→plan 등)
- Task 완료 시 (각 커밋 후)
- 컨텍스트 임계치 도달 (70%)
- 명시적 요청 ("저장해줘", "save")
- 긴 대화 (턴 > 20)

## 출력물 구조

```
.claude/contexts/work/my-project/docs/ai-dev/{PROJ-xxxx-설명}/
├── analyze.md              # 0단계: 분석 결과
├── spec.md                 # 1단계: 스펙 정의
├── plan.md                 # 2단계: 구현 계획
├── plan-check-report.md    # 2.5단계: 계획 검증 결과 ★
├── code-check-report.md    # 3.5단계: 코드 품질 검증 결과 ★
└── work-check-report.md    # 3.8단계: 버그 탐지 결과 ★
```

## 요구사항

- [Claude Code CLI](https://claude.ai/claude-code)
- JIRA 접근 권한 (jira-* 스킬 통해)
- (선택) [Codex MCP](https://github.com/anthropics/codex-mcp)
- (선택) [figma-ocaml MCP](https://github.com/anthropics/figma-ocaml)
- (선택) [apple-docs MCP](https://github.com/anthropics/apple-docs)
- (선택) [Neo4j Code Graph MCP](mcp-servers/neo4j-code-graph/) - Race Condition 탐지, 영향도 분석

## Neo4j Code Graph MCP 서버

코드베이스를 그래프로 분석하여 아키텍처 이해와 버그 탐지를 강화합니다.

### 설치

```bash
cd mcp-servers/neo4j-code-graph
python -m venv .venv
source .venv/bin/activate
pip install -e .
```

### 주요 기능

| 도구 | 설명 |
|------|------|
| `neo4j_query` | Cypher 쿼리 직접 실행 |
| `neo4j_find_impact` | 파일 변경 영향도 분석 (같은 모듈, 유사 파일) |
| `neo4j_trace_workflow` | ReactorKit Action→Mutation→State 추적 |
| `neo4j_graph_stats` | 그래프 통계 (노드/관계 개수) |

### Race Condition 자동 탐지

```bash
neo4j_trace_workflow(reactor_name: "LoginReactor")
```

결과 예시:
```json
{
  "race_condition_risks": [
    {
      "state_field": "isLoading",
      "competing_actions": ["login", "logout"],
      "risk": "P2",
      "reason": "2 actions modify same state field"
    }
  ]
}
```

### ai-dev 연동

Neo4j MCP 서버가 연결되면 ai-dev 스킬들이 자동으로 활용합니다:

- **ai-dev.analyze**: 아키텍처 분석 섹션에 파일 영향도, 워크플로우 분석 추가
- **ai-dev.work-check**: Race Condition 버그 체커가 Neo4j 그래프 기반 분석 수행
- **ai-dev.code-check**: 변경 파일의 영향 범위 분석

자세한 내용은 [Neo4j Code Graph README](mcp-servers/neo4j-code-graph/README.md) 참조.

## PR 리뷰 코멘트 응답 (resolve-conversation)

PR에 달린 미해결 리뷰 코멘트를 분석하고 응답 초안을 생성합니다.

```bash
/ai-dev.resolve-conversation
```

### 판정 유형

| 판정 | 설명 |
|------|------|
| **ACCEPT** | 코멘트 수용 → 코드 수정 + "반영했습니다" 응답 |
| **DISCUSS** | 추가 논의 필요 → 질문/대안 제시 |
| **DISMISS** | 반박 가능 → 근거와 함께 의견 제시 |

## 문서

- [시작 가이드](docs/getting-started.md) - 설치 방법
- [워크플로우 상세](docs/workflow-overview.md) - 상세 워크플로우 설명
- [설정 가이드](docs/configuration.md) - 설정 방법
- [스킬 시스템 분석](docs/ai-dev-skill-analysis.md) - 스킬 시스템 상세 분석

## 라이선스

MIT License - 자세한 내용은 [LICENSE](LICENSE) 참조

---

**버전**: 5.3
**생성일**: 2026-01-23
**수정일**: 2026-02-05 (Neo4j Code Graph MCP + resolve-conversation 스킬 추가)
