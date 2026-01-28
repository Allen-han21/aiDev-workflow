# AI-Dev Workflow

> JIRA 기반 AI 협업 개발 워크플로우 (Claude Code용)

JIRA 티켓 분석부터 PR 생성까지, AI가 단계별로 도와주는 개발 워크플로우입니다.

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
- **Figma 연동**: figma-ocaml MCP로 디자인 컨텍스트 자동 추출
- **크로스 플랫폼 참조**: iOS/Android 코드베이스 비교 분석
- **문서 자동 생성**: analyze.md, spec.md, plan.md 자동 생성
- **세션 관리**: Sentinel 패턴으로 컨텍스트 보존

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

## 문서

- [시작 가이드](docs/getting-started.md) - 설치 방법
- [워크플로우 상세](docs/workflow-overview.md) - 상세 워크플로우 설명
- [설정 가이드](docs/configuration.md) - 설정 방법
- [스킬 시스템 분석](docs/ai-dev-skill-analysis.md) - 스킬 시스템 상세 분석

## 라이선스

MIT License - 자세한 내용은 [LICENSE](LICENSE) 참조

---

**버전**: 5.1
**생성일**: 2026-01-23
**수정일**: 2026-01-29 (워크플로우 순서 수정 + Sentinel 구현 + README 한글화)
