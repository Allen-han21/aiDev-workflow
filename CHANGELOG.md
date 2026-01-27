# Changelog

All notable changes to this project will be documented in this file.

## [4.0.0] - 2026-01-27

### Added
- Cross-check mechanism (Claude + Codex MCP parallel verification)
- Codex MCP integration for planning phase
- LSP-based symbol exploration in analyze phase
- Apple docs MCP integration for iOS API verification
- Android codebase cross-reference support

### Changed
- Unified workflow orchestrator (ai-dev)
- Improved task dependency tracking in plan phase
- Enhanced review phase with CodeRabbit integration

## [3.0.0] - 2026-01-15

### Added
- Extended thinking support (`--ultrathink` option)
- iOS DoD checklist in review phase
- Figma design token extraction

### Changed
- Refactored analyze phase for better code exploration
- Improved spec phase with multi-perspective analysis

## [2.0.0] - 2026-01-01

### Added
- Plan mode separation (Phase 0-2 in plan mode)
- Local commit generation per task
- Xcode simulator auto-launch

### Changed
- Separated implementation from planning
- Task-by-task progress tracking

## [1.0.0] - 2025-12-15

### Added
- Initial release
- Basic 6-phase workflow
- JIRA integration
- Figma integration via figma-ocaml MCP
