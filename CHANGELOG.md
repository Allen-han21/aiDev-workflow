# 변경 이력

이 프로젝트의 주요 변경사항을 기록합니다.

## [5.2.0] - 2026-02-04

### 추가
- **ai-dev.pre-review 스킬** - JIRA 티켓 사전검토 + Draft PR 생성
  - 5단계 워크플로우: Quick Analyze → Draft Plan → JIRA Update → Draft Impl → Draft PR
  - JIRA Description에 사전검토 결과 자동 추가
  - ai-dev.pr --draft 옵션으로 Draft PR 생성
  - 기존 ai-dev 워크플로우에 영향 없음 (독립 스킬)

### 변경
- README.md에 pre-review 섹션 추가
- 버전 5.2로 업데이트

## [5.1.0] - 2026-01-29

### 추가
- **Mega-skill 패턴** - `--auto` 옵션으로 TaskCreate/TaskUpdate 기반 자동 파이프라인
- **Sentinel 패턴** - 긴 작업 세션의 자동 저장/복원 (70% 컨텍스트 임계치)

### 변경
- 워크플로우 순서 수정: plan → plan-check (원본 zac's 패턴 준수)
- README 한글화

## [5.0.0] - 2026-01-28

### 추가
- **plan-check 스킬** - 5개 validators + devil's advocate로 계획 검증
  - completeness-checker: spec→plan 요구사항 누락 검사
  - pattern-compliance: AGENTS.md 컨벤션 준수 검사
  - feasibility-assessor: 기술적 실현 가능성 평가
  - risk-assessor: 회귀/보안 위험 평가
  - scope-discipline: 과잉 구현(gold-plating) 탐지
- **code-check 스킬** - 코드 품질 검증
  - DRY Checker: 중복 코드 탐지
  - SOLID Checker: 설계 원칙 위반 검사
  - Complexity Analyzer: 순환 복잡도 분석
- **work-check 스킬** - 6개 병렬 버그 체커
  - Edge Case Hunter: 경계 조건 누락 탐지
  - Race Condition Detector: 동시성 문제 탐지
  - State Corruption Finder: 상태 오염 탐지
  - Memory Leak Hunter: 메모리 누수 탐지
  - Input Validation Checker: 입력 검증 누락 탐지
  - Regression Detector: 회귀 버그 탐지
- **9단계 워크플로우** - 기존 6단계에서 검증 단계 추가

### 변경
- 다단계 검증 시스템 도입 (총 14개 validators)

## [4.1.0] - 2026-01-28

### 추가
- **비즈니스 규칙 검증** - review 단계에서 비즈니스 로직 검증
  - 상태 변수 영향도 분석 (`is*`, `has*`, `should*` 패턴)
  - 요구사항 역추적 (spec.md 크로스 체크)
  - 유사 패턴 비교
  - 기능 충돌 탐지
- 리뷰 옵션: `--biz-rules`, `--no-biz-rules`, `--deep`
- CodeRabbit 결과 검증 단계 (합성 전 필수)

### 변경
- ai-dev.review를 v4.0으로 업데이트
- 비즈니스 규칙 섹션이 포함된 리뷰 출력 템플릿 개선

## [4.0.0] - 2026-01-27

### 추가
- **크로스 체크 메커니즘** - Claude + Codex MCP 병렬 검증
- **Codex MCP 연동** - 계획 단계에서 활용
- **LSP 기반 심볼 탐색** - 분석 단계에서 타입 정보 활용
- **Apple docs MCP 연동** - iOS API 검증
- **Android 코드베이스 크로스 참조** - 플랫폼 일관성 확보

### 변경
- 통합 워크플로우 오케스트레이터 (ai-dev)
- 계획 단계의 Task 의존성 추적 개선
- CodeRabbit 연동으로 리뷰 단계 강화

## [3.0.0] - 2026-01-15

### 추가
- **확장 사고 모드** - `--ultrathink` 옵션
- **iOS DoD 체크리스트** - 리뷰 단계에서 활용
- **Figma 디자인 토큰 추출**

### 변경
- 분석 단계 리팩토링 (코드 탐색 개선)
- 스펙 단계 개선 (다중 관점 분석)

## [2.0.0] - 2026-01-01

### 추가
- **Plan 모드 분리** - Phase 0-2는 plan 모드에서 실행
- **Task별 로컬 커밋 생성**
- **Xcode 시뮬레이터 자동 실행**

### 변경
- 구현과 계획 단계 분리
- Task별 진행 상황 추적

## [1.0.0] - 2025-12-15

### 추가
- 최초 릴리스
- 기본 6단계 워크플로우
- JIRA 연동
- figma-ocaml MCP를 통한 Figma 연동
