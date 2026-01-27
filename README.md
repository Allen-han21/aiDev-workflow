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
┌─────────────────────────────────────────────────────────────┐
│                    AI-Dev Workflow                          │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  [Input] JIRA Ticket + Figma (optional)                     │
│                                                             │
│         ↓                                                   │
│  Phase 0: ai-dev.analyze [plan mode]                        │
│  → JIRA query, Figma extraction, codebase analysis          │
│  → Output: analyze.md                                       │
│                                                             │
│         ↓                                                   │
│  Phase 1: ai-dev.spec [plan mode]                           │
│  → Claude + Codex cross-check → spec confirmation           │
│  → Output: spec.md                                          │
│                                                             │
│         ↓                                                   │
│  Phase 2: ai-dev.plan [plan mode]                           │
│  → Codex MCP planning → Claude verification                 │
│  → Output: plan.md                                          │
│                                                             │
│         ↓ [exit plan mode]                                  │
│  Phase 3: ai-dev.impl                                       │
│  → Task-by-task implementation + local commits              │
│  → Output: source code                                      │
│                                                             │
│         ↓                                                   │
│  Phase 4: ai-dev.review                                     │
│  → Build/lint verification, code review                     │
│  → Output: approval/change request                          │
│                                                             │
│         ↓ (on approval)                                     │
│  Phase 5: ai-dev.pr                                         │
│  → Push, GitHub PR creation                                 │
│  → Output: PR URL                                           │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

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

- [Getting Started](docs/getting-started.md) (Korean)
- [Workflow Overview](docs/workflow-overview.md) (Korean)
- [Configuration](docs/configuration.md) (Korean)

## License

MIT License - see [LICENSE](LICENSE) for details.

---

**Version**: 4.0
**Created**: 2026-01-23
**Updated**: 2026-01-27
