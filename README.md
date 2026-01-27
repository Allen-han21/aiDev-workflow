# AI-Dev Workflow

> JIRA-based AI collaborative development workflow for Claude Code

Transform your development process with an AI-powered workflow that handles everything from analysis to PR creation.

## Features

- **6-Phase Workflow**: Analyze → Spec → Plan → Implement → Review → PR
- **AI Cross-Check**: Claude + Codex MCP parallel verification
- **Figma Integration**: Auto-extract design context via figma-ocaml MCP
- **Cross-Platform Reference**: iOS/Android codebase comparison
- **Documentation Automation**: Auto-generate analyze.md, spec.md, plan.md

## Quick Start

### 1. Install

```bash
git clone https://github.com/YOUR_USERNAME/aiDev-workflow.git
cd aiDev-workflow
./scripts/install.sh
```

### 2. Use

```bash
# Full workflow
/ai-dev PROJ-12345

# With Figma design
/ai-dev PROJ-12345 --figma https://figma.com/design/xxx

# Individual phases
/ai-dev.analyze PROJ-12345   # Phase 0: Analysis
/ai-dev.spec PROJ-12345      # Phase 1: Specification
/ai-dev.plan PROJ-12345      # Phase 2: Planning
/ai-dev.impl PROJ-12345      # Phase 3: Implementation
/ai-dev.review PROJ-12345    # Phase 4: Review
/ai-dev.pr PROJ-12345        # Phase 5: PR Creation
```

## Workflow Overview

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

### Phase별 핵심 역할

| Phase | 스킬 | Mode | 핵심 메커니즘 | 출력 |
|-------|------|------|--------------|------|
| 0 | `ai-dev.analyze` | Plan | JIRA + Figma + LSP 심볼 탐색 + Android 참조 | `analyze.md` |
| 1 | `ai-dev.spec` | Plan | Claude + Codex 크로스 체크 (3자 검증) | `spec.md` |
| 2 | `ai-dev.plan` | Plan | 의존성 그래프 기반 Task 분해 | `plan.md` |
| 3 | `ai-dev.impl` | Dev | Task별 구현 + 빌드 검증 + 로컬 커밋 | 소스 코드 |
| 4 | `ai-dev.review` | Dev | 린트 + CodeRabbit + Claude + Codex(--full) | 승인/변경요청 |
| 5 | `ai-dev.pr` | Dev | JIRA 자동 추출 + 표준 PR 템플릿 | PR URL |

### 의존성 체인

```
ai-dev.analyze → ai-dev.spec → ai-dev.plan → ai-dev.impl → ai-dev.review → ai-dev.pr
   (analyze.md)    (spec.md)     (plan.md)      (커밋들)       (판정)         (PR URL)
```

각 Phase는 이전 Phase의 출력에 의존하며, `--from` 옵션으로 중간부터 시작 가능합니다.

## Options

| Option | Description | Phases |
|--------|-------------|--------|
| `--figma URL` | Include Figma design | analyze |
| `--from PHASE` | Start from specific phase | all |
| `--to PHASE` | End at specific phase | all |
| `--no-codex` | Use Claude only (no Codex MCP) | spec, plan, review |
| `--ultrathink` | Enable extended thinking | spec, plan |
| `--full` | Parallel cross-check in review | review |
| `--task N` | Start from specific task | impl |
| `--auto` | Auto-proceed all tasks | impl |
| `--draft` | Create draft PR | pr |

## Requirements

- [Claude Code CLI](https://claude.ai/claude-code)
- JIRA access (via jira-* skills)
- (Optional) [Codex MCP](https://github.com/anthropics/codex-mcp)
- (Optional) [figma-ocaml MCP](https://github.com/anthropics/figma-ocaml)
- (Optional) [apple-docs MCP](https://github.com/anthropics/apple-docs)

## Documentation

- [Getting Started](docs/getting-started.md) - 시작 가이드
- [Workflow Overview](docs/workflow-overview.md) - 워크플로우 상세 설명
- [Configuration](docs/configuration.md) - 설정 방법
- [Skill System Analysis](docs/ai-dev-skill-analysis.md) - 7개 스킬 시스템 종합 분석 보고서

## License

MIT License - see [LICENSE](LICENSE) for details.

---

**Version**: 4.0
**Created**: 2026-01-23
**Updated**: 2026-01-28
