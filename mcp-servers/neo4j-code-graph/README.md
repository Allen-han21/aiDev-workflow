# Neo4j Code Graph MCP Server

Claude Code에서 코드 그래프를 쿼리할 수 있는 MCP 서버입니다.

## 기능

- **코드 구조 분석**: ReactorKit Reactor의 Action → Mutation → State 흐름 추적
- **파일 영향도 분석**: 파일 변경 시 영향받는 관련 파일 탐지
- **Race Condition 탐지**: 같은 State 필드를 수정하는 여러 Action 자동 감지
- **Git 히스토리 연동**: 커밋과 JIRA 이슈 연결

## 설치

```bash
cd mcp-servers/neo4j-code-graph
python -m venv .venv
source .venv/bin/activate
pip install -e .
```

## 사용 가능한 도구

| 도구 | 설명 |
|------|------|
| `neo4j_query` | Cypher 쿼리 직접 실행 |
| `neo4j_find_impact` | 파일 변경 영향도 분석 |
| `neo4j_trace_workflow` | Reactor 워크플로우 추적 |
| `neo4j_graph_stats` | 그래프 통계 조회 |

## 환경 변수

| 변수 | 기본값 | 설명 |
|------|--------|------|
| `NEO4J_URI` | `bolt://localhost:7687` | Neo4j 연결 URI |
| `NEO4J_USER` | `neo4j` | Neo4j 사용자명 |
| `NEO4J_PASSWORD` | `password` | Neo4j 비밀번호 |

## Claude Code 설정

`~/.claude.json`에 추가:

```json
{
  "mcpServers": {
    "neo4j-code-graph": {
      "command": "python",
      "args": ["-m", "server"],
      "cwd": "~/.claude/mcp-servers/neo4j-code-graph/src",
      "env": {
        "PYTHONPATH": "~/.claude/mcp-servers/neo4j-code-graph/src",
        "NEO4J_URI": "bolt://localhost:7687",
        "NEO4J_USER": "neo4j",
        "NEO4J_PASSWORD": "your-password"
      }
    }
  }
}
```

## 데이터 임포트

### 1. Git 히스토리 임포트

```bash
cd src/importers
python git_history.py --repo /path/to/your/repo --since "6 months ago" --limit 500
```

### 2. 코드 구조 임포트 (ReactorKit)

```bash
python code_structure.py --sources /path/to/your/repo/Sources --create-relationships
```

### 3. 파일 노드 임포트

```bash
python code_files.py --sources /path/to/your/repo/Sources --create-relationships
```

## 사용 예시

### 파일 영향도 분석
```
neo4j_find_impact(file_path: "LoginViewController.swift")
```

결과:
- 같은 모듈 파일 목록
- 유사 파일 목록
- 관련 커밋 히스토리
- 위험도 (HIGH/MEDIUM/LOW)

### Reactor 워크플로우 추적
```
neo4j_trace_workflow(reactor_name: "LoginReactor")
```

결과:
- Action → Mutation → State 흐름
- Race Condition 위험 감지
- 통계 (Action/Mutation/State 개수)

### 직접 쿼리
```
neo4j_query(cypher: "MATCH (f:CodeFile) WHERE f.type = 'Reactor' RETURN f.name LIMIT 10")
```

## 그래프 스키마

### 노드

| 라벨 | 설명 |
|------|------|
| `CodeFile` | Swift 파일 |
| `Action` | ReactorKit Action |
| `Mutation` | ReactorKit Mutation |
| `StateField` | ReactorKit State 필드 |
| `Commit` | Git 커밋 |
| `JiraIssue` | JIRA 이슈 |

### 관계

| 관계 | 설명 |
|------|------|
| `TRIGGERS` | Action → Mutation |
| `MODIFIES` | Mutation → StateField |
| `DEFINED_IN` | Action/Mutation/StateField → CodeFile |
| `SAME_MODULE` | 같은 모듈의 CodeFile 간 |
| `RESOLVES` | Commit → JiraIssue |

## ai-dev 스킬 연동

이 MCP 서버는 ai-dev 워크플로우의 다음 스킬들과 연동됩니다:

- `ai-dev.analyze`: 코드베이스 분석 시 Neo4j 아키텍처 분석 섹션 추가
- `ai-dev.work-check`: 버그 검사 시 Race Condition 분석
- `ai-dev.code-check`: 코드 품질 검사 시 영향도 분석

## 라이선스

MIT License
