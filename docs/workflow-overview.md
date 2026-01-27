# 워크플로우 개요

AI-Dev 워크플로우의 전체 흐름과 각 Phase별 상세 설명입니다.

## 전체 흐름

```
┌─────────────────────────────────────────────────────────────────┐
│                        ai-dev 워크플로우                          │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  [입력] JIRA 티켓 번호 + Figma (선택)                             │
│                                                                 │
│         ↓                                                       │
│  Phase 0: ai-dev.analyze [plan mode]                            │
│  → JIRA 조회 (본문+댓글), Figma(figma-ocaml), 코드 분석           │
│  → 출력: analyze.md                                              │
│                                                                 │
│         ↓                                                       │
│  Phase 1: ai-dev.spec [plan mode]                               │
│  → Claude + Codex 크로스 체크 → 스펙 확정                         │
│  → 출력: spec.md                                                 │
│                                                                 │
│         ↓                                                       │
│  Phase 2: ai-dev.plan [plan mode]                               │
│  → Codex MCP 계획 생성 → Claude 검증 → 사용자 구현 승인            │
│  → 출력: plan.md                                                 │
│                                                                 │
│         ↓ [plan mode 해제]                                       │
│  Phase 3: ai-dev.impl                                           │
│  → Task별 구현 + 로컬 커밋 + 테스트 + 빌드 검증                    │
│  → 출력: 소스 코드                                                │
│                                                                 │
│         ↓                                                       │
│  Phase 4: ai-dev.review                                         │
│  → 빌드/린트 검증, 코드 리뷰                                      │
│  → 출력: 승인/변경요청                                            │
│                                                                 │
│         ↓ (승인 시)                                              │
│  Phase 5: ai-dev.pr                                             │
│  → Push, GitHub PR 생성                                          │
│  → 출력: PR URL                                                  │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

## Phase별 상세

### Phase 0: ai-dev.analyze

**목적**: 요구사항 이해 및 코드베이스 분석

**수행 작업**:
1. JIRA 티켓 조회 (본문 + 댓글)
2. Figma URL 자동 감지 → 디자인 컨텍스트 추출
3. LSP 기반 심볼 탐색
4. Explore 에이전트로 패턴 탐색
5. 엣지 케이스 식별
6. 확인 사항 질문 (AskUserQuestion)

**출력**: `analyze.md`

### Phase 1: ai-dev.spec

**목적**: 스펙 확정 (Claude + Codex 크로스 체크)

**크로스 체크 흐름**:
```
1. 모델 최적화 질문 생성
2. 병렬 분석
   ├─ Claude: 대화 맥락 기반
   └─ Codex MCP: 코드 탐색 기반
3. 크로스 리뷰
   ├─ Claude → Codex 답변 검토
   └─ Codex → Claude 답변 검토
4. 종합
   ├─ 공통 합의 → spec.md 반영
   └─ 선택 필요 → AskUserQuestion
```

**출력**: `spec.md`

### Phase 2: ai-dev.plan

**목적**: 구현 계획 수립

**수행 작업**:
1. Codex MCP로 계획 초안 생성
2. Claude 검증 (컨벤션, 파일 경로, 의존성 순서)
3. Task 분해 (Phase → Task 구조)
4. 사용자 구현 승인

**Task 구조 예시**:
```
Phase 1: 데이터 레이어
├─ Task 1.1: Entity 정의
└─ Task 1.2: Repository 구현

Phase 2: 비즈니스 로직
├─ Task 2.1: UseCase 구현
└─ Task 2.2: Service 구현

Phase 3: 프레젠테이션
├─ Task 3.1: Reactor 구현
└─ Task 3.2: View 구현
```

**출력**: `plan.md`

### Phase 3: ai-dev.impl

**목적**: 코드 구현 (plan mode 해제)

**각 Task별 반복**:
```
for each Task in plan.md:
    1. Task 상세 확인
    2. 의존성 Task 완료 여부 확인
    3. 코드 구현
    4. 빌드 검증
    5. 테스트 ([DEBUG] 로그 또는 Unit Test)
    6. 로컬 커밋 생성
    7. plan.md에 완료 표시
```

**모든 Task 완료 후**:
1. 시뮬레이터 실행
2. 기능 테스트
3. [DEBUG] 로그 삭제

**출력**: 소스 코드 + 로컬 커밋

### Phase 4: ai-dev.review

**목적**: 코드 품질 검증

**자동 검증**:
- 빌드 검증
- 린트 검사 (swiftlint 등)
- CodeRabbit AI 리뷰 (선택)

**코드 리뷰 관점**:
1. 정확성 (Correctness)
2. 보안 (Security)
3. 효율성 (Efficiency)
4. 유지보수성 (Maintainability)
5. 아키텍처

**판정**:
- 승인: Critical/High 이슈 없음
- 변경요청: Critical/High 이슈 있음

### Phase 5: ai-dev.pr

**목적**: GitHub PR 생성

**수행 작업**:
1. Git 상태 확인
2. 최종 커밋 생성 (필요시)
3. Push
4. PR 생성 (gh CLI)

**PR 템플릿**:
```markdown
## Summary
- 변경 요약

## Test plan
- [ ] 빌드 확인
- [ ] 기능 테스트

## Related
- JIRA: PROJ-XXXXX
```

## 사용자 개입 포인트

| Phase | 시점 | 내용 |
|-------|------|------|
| analyze | 질문 | 엣지 케이스, 요구사항 확인 |
| spec | 크로스 체크 후 | 선택 사항 결정, 스펙 승인 |
| plan | 검증 후 | 계획 검토 및 구현 승인 |
| impl | 각 Task | 다음 Task 진행 여부 |
| impl | 완료 후 | 테스트 완료 확인 |
| review | 판정 후 | 변경요청 시 수정 |
| pr | 생성 전 | 최종 확인 |

## 옵션 상세

| 옵션 | 설명 | 사용 예시 |
|------|------|----------|
| `--figma URL` | Figma 디자인 포함 | `/ai-dev PROJ-123 --figma https://...` |
| `--from PHASE` | 특정 Phase부터 시작 | `/ai-dev PROJ-123 --from impl` |
| `--to PHASE` | 특정 Phase까지만 | `/ai-dev PROJ-123 --to plan` |
| `--no-codex` | Codex MCP 비활성화 | `/ai-dev PROJ-123 --no-codex` |
| `--ultrathink` | Extended thinking | `/ai-dev PROJ-123 --ultrathink` |
| `--full` | 병렬 크로스체크 | `/ai-dev.review PROJ-123 --full` |
| `--task N` | 특정 Task부터 | `/ai-dev.impl PROJ-123 --task 3` |
| `--auto` | 모든 Task 자동 | `/ai-dev.impl PROJ-123 --auto` |
| `--draft` | Draft PR | `/ai-dev.pr PROJ-123 --draft` |
