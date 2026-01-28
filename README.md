# AI-Dev Workflow

> JIRA-based AI collaborative development workflow for Claude Code

Transform your development process with an AI-powered workflow that handles everything from analysis to PR creation.

## What's New in v5.0

- **Mega-skill Pattern**: `--auto` option for fully automated pipeline
- **Multi-stage Validation**: plan-check, code-check, work-check (14 validators)
- **Sentinel Pattern**: Auto-save/restore for long workflow sessions
- **9-Phase Workflow**: Extended from 6 phases with validation stages

## Features

- **9-Phase Workflow**: Analyze → Spec → Plan-Check → Plan → Implement → Code-Check → Work-Check → Review → PR
- **AI Cross-Check**: Claude + Codex MCP parallel verification
- **14 Validators**: 5 plan validators + 3 code quality + 6 bug checkers
- **Figma Integration**: Auto-extract design context via figma-ocaml MCP
- **Cross-Platform Reference**: iOS/Android codebase comparison
- **Documentation Automation**: Auto-generate analyze.md, spec.md, plan.md
- **Session Management**: Sentinel pattern for context preservation

## Quick Start

### 1. Install

```bash
git clone https://github.com/Allen-han21/aiDev-workflow.git
cd aiDev-workflow
./scripts/install.sh
```

### 2. Use

```bash
# Full workflow (step-by-step)
/ai-dev PROJ-12345

# Mega-skill automation (fully automated)
/ai-dev PROJ-12345 --auto

# Fast development (skip validation)
/ai-dev PROJ-12345 --auto --skip-checks

# With Figma design
/ai-dev PROJ-12345 --figma https://figma.com/design/xxx

# Show help
/ai-dev help

# Individual phases
/ai-dev.analyze PROJ-12345     # Phase 0: Analysis
/ai-dev.spec PROJ-12345        # Phase 1: Specification
/ai-dev.plan-check PROJ-12345  # Phase 2.5: Plan Validation
/ai-dev.plan PROJ-12345        # Phase 2: Planning
/ai-dev.impl PROJ-12345        # Phase 3: Implementation
/ai-dev.code-check PROJ-12345  # Phase 3.5: Code Quality
/ai-dev.work-check PROJ-12345  # Phase 3.8: Bug Detection
/ai-dev.review PROJ-12345      # Phase 4: Review
/ai-dev.pr PROJ-12345          # Phase 5: PR Creation
```

## Workflow Overview

```
┌─────────────────────────────────────────────────────────────────────────┐
│                    ai-dev 워크플로우 v5.0 (Mega-skill)                   │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                         │
│  [입력] JIRA 티켓 번호 + Figma (선택)                                    │
│                                                                         │
│  ┌───────────────────────── TASK CHAIN ─────────────────────────┐      │
│  │                                                               │      │
│  │  Task 1: analyze [plan mode]                                 │      │
│  │  → JIRA 조회, Figma, 코드 분석 → analyze.md                   │      │
│  │      │                                                        │      │
│  │      ▼ [blockedBy: 1]                                        │      │
│  │  Task 2: spec [plan mode]                                    │      │
│  │  → Claude + Codex 크로스 체크 → spec.md                       │      │
│  │      │                                                        │      │
│  │      ▼ [blockedBy: 2]                                        │      │
│  │  Task 3: plan-check ★ [plan mode]                            │      │
│  │  → 5개 validators + devil's advocate → plan-check-report.md  │      │
│  │      │                                                        │      │
│  │      ▼ [blockedBy: 3]                                        │      │
│  │  Task 4: plan [plan mode]                                    │      │
│  │  → Codex MCP 계획 생성 + Claude 검증 → plan.md               │      │
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

### Phase Summary

| Phase | Skill | Mode | Key Mechanism | Output |
|-------|-------|------|---------------|--------|
| 0 | `ai-dev.analyze` | Plan | JIRA + Figma + Code exploration | `analyze.md` |
| 1 | `ai-dev.spec` | Plan | Claude + Codex cross-check | `spec.md` |
| 2.5 | `ai-dev.plan-check` ★ | Plan | 5 validators + devil's advocate | `plan-check-report.md` |
| 2 | `ai-dev.plan` | Plan | Codex MCP + Claude validation | `plan.md` |
| 3 | `ai-dev.impl` | Dev | Task-by-task implementation | Source code |
| 3.5 | `ai-dev.code-check` ★ | Dev | DRY/SOLID/Complexity analysis | `code-check-report.md` |
| 3.8 | `ai-dev.work-check` ★ | Dev | 6 parallel bug checkers | `work-check-report.md` |
| 4 | `ai-dev.review` | Dev | Business rules + final verdict | Approval/Changes |
| 5 | `ai-dev.pr` | Dev | Push + GitHub PR | PR URL |

★ = New in v5.0

## Validation System (v5.0)

### Plan-Check (5 Validators + Devil's Advocate)

| Validator | Role |
|-----------|------|
| completeness-checker | spec→plan requirement gaps |
| pattern-compliance | AGENTS.md convention adherence |
| feasibility-assessor | Technical feasibility |
| risk-assessor | Regression/security risks |
| scope-discipline | Gold-plating detection |
| + devil's advocate | False positive reduction |

### Code-Check (Quality Analysis)

- DRY Checker (duplicate code)
- SOLID Checker (design principles)
- Complexity Analyzer (cyclomatic complexity)

### Work-Check (6 Bug Checkers)

- Edge Case Hunter
- Race Condition Detector
- State Corruption Finder
- Memory Leak Hunter
- Input Validation Checker
- Regression Detector

## Options

| Option | Description | Phases |
|--------|-------------|--------|
| `--auto` | Fully automated pipeline (Mega-skill) | all |
| `--figma URL` | Include Figma design | analyze |
| `--from PHASE` | Start from specific phase | all |
| `--to PHASE` | End at specific phase | all |
| `--skip-checks` | Skip plan-check, code-check, work-check | all |
| `--no-codex` | Use Claude only (no Codex MCP) | spec, plan |
| `--ultrathink` | Enable extended thinking | spec, plan |

### Usage Examples

```bash
# Full workflow (step-by-step confirmation)
/ai-dev PROJ-12345

# Mega-skill automation (no confirmation)
/ai-dev PROJ-12345 --auto

# Fast development (skip validation)
/ai-dev PROJ-12345 --auto --skip-checks

# With Figma design
/ai-dev PROJ-12345 --figma https://figma.com/design/xxx

# Start from implementation (when plan exists)
/ai-dev PROJ-12345 --from impl

# Complex problem (highest quality)
/ai-dev PROJ-12345 --no-codex --ultrathink
```

## Sentinel Pattern (Session Management)

For long workflows that may exceed context limits:

```bash
# Manual save
/ai-dev.sentinel save

# List saved sessions
/ai-dev.sentinel list

# Restore session
/ai-dev.sentinel restore sentinel-2026-01-28-153000

# Cleanup old sessions
/ai-dev.sentinel cleanup --older-than 7d
```

**Auto-save Triggers:**
- Phase transitions (analyze→spec, spec→plan, etc.)
- Task completion (after each commit)
- Explicit request ("저장해줘", "save")
- Long conversations (turns > 20)

## Output Structure

```
.claude/contexts/work/my-project/docs/ai-dev/{PROJ-xxxx-description}/
├── analyze.md              # Phase 0
├── spec.md                 # Phase 1
├── plan-check-report.md    # Phase 2.5 ★
├── plan.md                 # Phase 2
├── code-check-report.md    # Phase 3.5 ★
└── work-check-report.md    # Phase 3.8 ★
```

## Requirements

- [Claude Code CLI](https://claude.ai/claude-code)
- JIRA access (via jira-* skills)
- (Optional) [Codex MCP](https://github.com/anthropics/codex-mcp)
- (Optional) [figma-ocaml MCP](https://github.com/anthropics/figma-ocaml)
- (Optional) [apple-docs MCP](https://github.com/anthropics/apple-docs)

## Documentation

- [Getting Started](docs/getting-started.md) - Installation guide
- [Workflow Overview](docs/workflow-overview.md) - Detailed workflow explanation
- [Configuration](docs/configuration.md) - Configuration guide
- [Skill System Analysis](docs/ai-dev-skill-analysis.md) - Comprehensive skill system analysis

## License

MIT License - see [LICENSE](LICENSE) for details.

---

**Version**: 5.0
**Created**: 2026-01-23
**Updated**: 2026-01-28 (Mega-skill + Multi-stage Validation + Sentinel)
