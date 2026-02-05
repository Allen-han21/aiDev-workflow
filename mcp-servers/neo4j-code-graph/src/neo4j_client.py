"""Neo4j 클라이언트 - 코드 그래프 쿼리 및 분석"""

from neo4j import GraphDatabase
from typing import Optional
import json


class Neo4jClient:
    """Neo4j 코드 그래프 클라이언트"""

    def __init__(self, uri: str, user: str, password: str):
        self.driver = GraphDatabase.driver(uri, auth=(user, password))
        self._verify_connection()

    def _verify_connection(self):
        """연결 확인"""
        with self.driver.session() as session:
            session.run("RETURN 1").single()

    def close(self):
        """드라이버 종료"""
        self.driver.close()

    def run_query(self, cypher: str, params: dict = None) -> list[dict]:
        """Cypher 쿼리 실행"""
        with self.driver.session() as session:
            result = session.run(cypher, params or {})
            records = []
            for record in result:
                # Neo4j 레코드를 JSON 직렬화 가능한 dict로 변환
                record_dict = {}
                for key in record.keys():
                    value = record[key]
                    record_dict[key] = self._serialize_value(value)
                records.append(record_dict)
            return records

    def _serialize_value(self, value):
        """Neo4j 값을 JSON 직렬화 가능한 형태로 변환"""
        if value is None:
            return None
        if isinstance(value, (str, int, float, bool)):
            return value
        if isinstance(value, list):
            return [self._serialize_value(v) for v in value]
        if isinstance(value, dict):
            return {k: self._serialize_value(v) for k, v in value.items()}
        # Neo4j Node, Relationship 등
        if hasattr(value, '__dict__'):
            return str(value)
        return str(value)

    def find_impact(self, file_path: str, depth: int = 2) -> dict:
        """파일 변경 영향도 분석

        Args:
            file_path: 파일 경로 (Sources/ 이후 상대 경로)
            depth: 검색 깊이 (1-3)

        Returns:
            영향 분석 결과
        """
        # 파일 존재 확인 및 기본 정보
        file_query = """
        MATCH (target:CodeFile)
        WHERE target.path CONTAINS $path OR target.name CONTAINS $path
        RETURN target.name as name, target.path as path, target.module as module
        LIMIT 1
        """
        file_result = self.run_query(file_query, {"path": file_path})

        if not file_result:
            return {"error": f"File not found: {file_path}"}

        target_info = file_result[0]
        target_path = target_info["path"]

        # 유사한 파일 조회 (SIMILAR_TO 관계)
        similar_query = """
        MATCH (target:CodeFile {path: $path})-[r:SIMILAR_TO]-(similar:CodeFile)
        WHERE r.score > 0.8
        RETURN similar.name as name, similar.path as path,
               similar.module as module, r.score as score
        ORDER BY r.score DESC
        LIMIT 10
        """
        similar_result = self.run_query(similar_query, {"path": target_path})

        # 같은 모듈 파일 조회
        module_query = """
        MATCH (target:CodeFile {path: $path})
        MATCH (same_module:CodeFile)
        WHERE same_module.module = target.module AND same_module.path <> target.path
        RETURN same_module.name as name, same_module.path as path
        LIMIT 20
        """
        module_result = self.run_query(module_query, {"path": target_path})

        # 관련 커밋 조회 (있는 경우)
        commit_query = """
        MATCH (target:CodeFile {path: $path})<-[:MODIFIES]-(c:Commit)
        OPTIONAL MATCH (c)-[:RESOLVES]->(j:JiraIssue)
        RETURN c.hash as commit_hash, c.message as message,
               c.date as date, j.key as jira_key
        ORDER BY c.date DESC
        LIMIT 10
        """
        commit_result = self.run_query(commit_query, {"path": target_path})

        # 위험도 계산
        similar_count = len(similar_result)
        module_count = len(module_result)

        if similar_count > 5 or module_count > 15:
            risk_level = "HIGH"
        elif similar_count > 2 or module_count > 8:
            risk_level = "MEDIUM"
        else:
            risk_level = "LOW"

        return {
            "target": target_info,
            "similar_files": similar_result,
            "same_module_files": module_result[:10],  # 상위 10개만
            "related_commits": commit_result,
            "risk_level": risk_level,
            "stats": {
                "similar_count": similar_count,
                "module_file_count": module_count,
                "commit_count": len(commit_result)
            }
        }

    def trace_workflow(self, reactor_name: str, action_name: str = None) -> dict:
        """ReactorKit 워크플로우 추적

        Args:
            reactor_name: Reactor 클래스 이름
            action_name: 특정 Action 이름 (선택)

        Returns:
            워크플로우 분석 결과
        """
        # Reactor 확인 (Action 노드에서 reactor 속성으로 확인)
        reactor_check_query = """
        MATCH (a:Action {reactor: $reactor})
        RETURN count(a) as action_count
        """
        check_result = self.run_query(reactor_check_query, {"reactor": reactor_name})
        reactor_result = []  # 기본값

        if not check_result or check_result[0].get("action_count", 0) == 0:
            # Action 노드에 없으면 CodeFile에서도 찾아보기
            reactor_query = """
            MATCH (f:CodeFile)
            WHERE f.name CONTAINS $name AND f.name ENDS WITH 'Reactor.swift'
            RETURN f.name as name, f.path as path, f.module as module
            LIMIT 5
            """
            reactor_result = self.run_query(reactor_query, {"name": reactor_name})

            if not reactor_result:
                return {
                    "error": f"Reactor not found: {reactor_name}",
                    "suggestion": "Check if the reactor name is correct. Available reactors can be queried with: MATCH (a:Action) RETURN DISTINCT a.reactor LIMIT 20"
                }
        else:
            # Action 노드에서 찾은 경우 기본 정보 생성
            reactor_result = [{"name": f"{reactor_name}.swift", "path": f"(from Action nodes)", "module": "(inferred)"}]

        # Action/Mutation/State 노드 조회 (확장된 스키마가 있는 경우)
        workflow_query = """
        MATCH (a:Action {reactor: $reactor})
        OPTIONAL MATCH (a)-[:TRIGGERS]->(m:Mutation)
        OPTIONAL MATCH (m)-[:MODIFIES]->(s:StateField)
        RETURN a.name as action, m.name as mutation, s.name as state_field, s.type as state_type
        ORDER BY a.name
        """
        workflow_result = self.run_query(workflow_query, {"reactor": reactor_name})

        # 워크플로우가 없으면 파일 정보만 반환
        if not workflow_result or not workflow_result[0].get("action"):
            return {
                "reactor_files": reactor_result,
                "workflows": [],
                "race_condition_risks": [],
                "message": "Reactor workflow nodes not yet imported. Run code_structure importer first."
            }

        # Race condition 분석
        state_actions = {}
        for wf in workflow_result:
            if wf.get("state_field"):
                field = wf["state_field"]
                if field not in state_actions:
                    state_actions[field] = []
                if wf.get("action"):
                    state_actions[field].append(wf["action"])

        race_risks = []
        for field, actions in state_actions.items():
            unique_actions = list(set(actions))
            if len(unique_actions) > 1:
                race_risks.append({
                    "state_field": field,
                    "competing_actions": unique_actions,
                    "risk": "P1" if len(unique_actions) > 2 else "P2",
                    "reason": f"{len(unique_actions)} actions modify same state field"
                })

        return {
            "reactor_files": reactor_result,
            "workflows": workflow_result,
            "race_condition_risks": race_risks,
            "stats": {
                "action_count": len(set(wf.get("action") for wf in workflow_result if wf.get("action"))),
                "mutation_count": len(set(wf.get("mutation") for wf in workflow_result if wf.get("mutation"))),
                "state_field_count": len(set(wf.get("state_field") for wf in workflow_result if wf.get("state_field")))
            }
        }

    def get_graph_stats(self) -> dict:
        """그래프 통계 조회"""
        stats_query = """
        MATCH (n)
        WITH labels(n) as labels, count(n) as count
        UNWIND labels as label
        RETURN label, sum(count) as count
        ORDER BY count DESC
        """
        node_stats = self.run_query(stats_query)

        rel_query = """
        MATCH ()-[r]->()
        WITH type(r) as rel_type, count(r) as count
        RETURN rel_type, count
        ORDER BY count DESC
        """
        rel_stats = self.run_query(rel_query)

        return {
            "nodes": {stat["label"]: stat["count"] for stat in node_stats},
            "relationships": {stat["rel_type"]: stat["count"] for stat in rel_stats}
        }
