"""Swift 코드 구조 분석 및 Neo4j 임포트

ReactorKit Reactor 파일에서 Action, Mutation, State 추출하여:
- Action 노드 생성
- Mutation 노드 생성
- StateField 노드 생성
- TRIGGERS, MODIFIES 관계 생성
"""

import re
import os
from pathlib import Path
from neo4j import GraphDatabase
from typing import Optional


class SwiftCodeAnalyzer:
    """Swift 파일 정적 분석"""

    # 정규식 패턴
    CLASS_PATTERN = re.compile(
        r'(?:final\s+)?(?:class|struct)\s+(\w+)(?:\s*:\s*([^{]+))?'
    )
    ENUM_CASE_PATTERN = re.compile(r'case\s+(\w+)(?:\(.*?\))?')
    STATE_FIELD_PATTERN = re.compile(r'(?:var|let)\s+(\w+)\s*:\s*([^=\n]+?)(?:\s*=|$|\n)')

    def analyze_reactor(self, file_path: Path) -> dict:
        """Reactor 파일 분석

        Args:
            file_path: Reactor 파일 경로

        Returns:
            분석 결과 (actions, mutations, state_fields)
        """
        try:
            content = file_path.read_text(encoding='utf-8')
        except Exception as e:
            return {"error": str(e)}

        reactor_name = file_path.stem  # 예: LoginReactor

        result = {
            "file_path": str(file_path),
            "reactor_name": reactor_name,
            "actions": [],
            "mutations": [],
            "state_fields": []
        }

        # Action enum 추출
        action_block = self._extract_enum_block(content, "Action")
        if action_block:
            result["actions"] = self._extract_enum_cases(action_block)

        # Mutation enum 추출
        mutation_block = self._extract_enum_block(content, "Mutation")
        if mutation_block:
            result["mutations"] = self._extract_enum_cases(mutation_block)

        # State struct 추출
        state_block = self._extract_struct_block(content, "State")
        if state_block:
            result["state_fields"] = self._extract_state_fields(state_block)

        return result

    def _extract_enum_block(self, content: str, enum_name: str) -> Optional[str]:
        """enum 블록 추출"""
        pattern = rf'enum\s+{enum_name}\s*(?::\s*[^{{]+)?\s*\{{([^}}]+)\}}'
        match = re.search(pattern, content, re.DOTALL)
        return match.group(1) if match else None

    def _extract_struct_block(self, content: str, struct_name: str) -> Optional[str]:
        """struct 블록 추출"""
        pattern = rf'struct\s+{struct_name}\s*(?::\s*[^{{]+)?\s*\{{([^}}]+)\}}'
        match = re.search(pattern, content, re.DOTALL)
        return match.group(1) if match else None

    def _extract_enum_cases(self, block: str) -> list:
        """enum case 추출"""
        cases = []
        for match in self.ENUM_CASE_PATTERN.finditer(block):
            cases.append(match.group(1))
        return cases

    def _extract_state_fields(self, block: str) -> list:
        """State 필드 추출"""
        fields = []
        for match in self.STATE_FIELD_PATTERN.finditer(block):
            field_name = match.group(1).strip()
            field_type = match.group(2).strip()
            # 타입에서 불필요한 부분 제거
            field_type = re.sub(r'\s+', '', field_type)
            fields.append({
                "name": field_name,
                "type": field_type
            })
        return fields


class CodeStructureImporter:
    """코드 구조 Neo4j 임포터"""

    def __init__(self, uri: str, user: str, password: str, sources_path: str):
        self.driver = GraphDatabase.driver(uri, auth=(user, password))
        self.sources_path = Path(sources_path)
        self.analyzer = SwiftCodeAnalyzer()
        self._verify_connection()

    def _verify_connection(self):
        """연결 확인"""
        with self.driver.session() as session:
            session.run("RETURN 1").single()

    def close(self):
        """드라이버 종료"""
        self.driver.close()

    def create_constraints(self):
        """제약조건 생성"""
        with self.driver.session() as session:
            # Action 제약조건
            try:
                session.run("""
                    CREATE CONSTRAINT action_unique IF NOT EXISTS
                    FOR (a:Action) REQUIRE (a.name, a.reactor) IS UNIQUE
                """)
            except Exception as e:
                print(f"Action constraint: {e}")

            # Mutation 제약조건
            try:
                session.run("""
                    CREATE CONSTRAINT mutation_unique IF NOT EXISTS
                    FOR (m:Mutation) REQUIRE (m.name, m.reactor) IS UNIQUE
                """)
            except Exception as e:
                print(f"Mutation constraint: {e}")

            # StateField 제약조건
            try:
                session.run("""
                    CREATE CONSTRAINT state_field_unique IF NOT EXISTS
                    FOR (s:StateField) REQUIRE (s.name, s.reactor) IS UNIQUE
                """)
            except Exception as e:
                print(f"StateField constraint: {e}")

    def import_reactors(self) -> dict:
        """모든 Reactor 파일 분석 및 임포트

        Returns:
            임포트 통계
        """
        reactor_files = list(self.sources_path.rglob("*Reactor.swift"))
        print(f"Found {len(reactor_files)} Reactor files")

        stats = {
            "reactors_processed": 0,
            "actions_created": 0,
            "mutations_created": 0,
            "state_fields_created": 0,
            "errors": 0
        }

        for file_path in reactor_files:
            result = self.analyzer.analyze_reactor(file_path)

            if "error" in result:
                stats["errors"] += 1
                print(f"Error analyzing {file_path.name}: {result['error']}")
                continue

            # 빈 Reactor 스킵
            if not result["actions"] and not result["mutations"]:
                continue

            reactor_name = result["reactor_name"]
            node_stats = self._save_reactor_structure(reactor_name, result)

            stats["reactors_processed"] += 1
            stats["actions_created"] += node_stats["actions"]
            stats["mutations_created"] += node_stats["mutations"]
            stats["state_fields_created"] += node_stats["state_fields"]

        return stats

    def _save_reactor_structure(self, reactor_name: str, data: dict) -> dict:
        """Reactor 구조 저장"""
        stats = {"actions": 0, "mutations": 0, "state_fields": 0}

        with self.driver.session() as session:
            # Action 노드 생성
            for action in data["actions"]:
                session.run("""
                    MERGE (a:Action {name: $name, reactor: $reactor})
                """, {"name": action, "reactor": reactor_name})
                stats["actions"] += 1

            # Mutation 노드 생성
            for mutation in data["mutations"]:
                session.run("""
                    MERGE (m:Mutation {name: $name, reactor: $reactor})
                """, {"name": mutation, "reactor": reactor_name})
                stats["mutations"] += 1

            # StateField 노드 생성
            for field in data["state_fields"]:
                session.run("""
                    MERGE (s:StateField {name: $name, reactor: $reactor})
                    SET s.type = $type
                """, {
                    "name": field["name"],
                    "reactor": reactor_name,
                    "type": field["type"]
                })
                stats["state_fields"] += 1

        return stats

    def analyze_action_mutation_mapping(self, reactor_name: str) -> dict:
        """Action → Mutation 매핑 분석 (mutate 함수 분석)

        Args:
            reactor_name: Reactor 이름

        Returns:
            매핑 정보
        """
        reactor_files = list(self.sources_path.rglob(f"{reactor_name}.swift"))

        if not reactor_files:
            return {"error": f"Reactor not found: {reactor_name}"}

        file_path = reactor_files[0]
        content = file_path.read_text(encoding='utf-8')

        # mutate 함수에서 Action → Mutation 매핑 추출 (간략 버전)
        # 실제 분석은 더 복잡한 파싱이 필요
        mappings = []

        # case .actionName: 패턴 찾기
        action_cases = re.findall(
            r'case\s+\.(\w+).*?(?:return|concat|merge).*?\.(\w+)',
            content, re.DOTALL
        )

        for action, mutation in action_cases:
            mappings.append({
                "action": action,
                "mutation": mutation
            })

        return {
            "reactor": reactor_name,
            "mappings": mappings
        }

    def create_triggers_relationships(self) -> dict:
        """TRIGGERS 관계 생성 (Action → Mutation)

        Note: 이 함수는 간단한 휴리스틱 기반입니다.
        정확한 분석을 위해서는 AST 파싱이 필요합니다.
        """
        stats = {"relationships_created": 0}

        # 같은 Reactor 내의 Action과 Mutation 연결 (이름 기반 휴리스틱)
        with self.driver.session() as session:
            # 예: setLoading Action → setLoading Mutation
            result = session.run("""
                MATCH (a:Action), (m:Mutation)
                WHERE a.reactor = m.reactor
                AND (
                    a.name = m.name
                    OR lower(a.name) CONTAINS lower(m.name)
                    OR lower(m.name) CONTAINS lower(a.name)
                )
                MERGE (a)-[r:TRIGGERS]->(m)
                RETURN count(r) as created
            """)
            stats["relationships_created"] += result.single()["created"]

        return stats

    def create_modifies_relationships(self) -> dict:
        """MODIFIES 관계 생성 (Mutation → StateField)

        Note: 이름 기반 휴리스틱입니다.
        """
        stats = {"relationships_created": 0}

        with self.driver.session() as session:
            # 예: setLoading Mutation → isLoading StateField
            result = session.run("""
                MATCH (m:Mutation), (s:StateField)
                WHERE m.reactor = s.reactor
                AND (
                    lower(m.name) CONTAINS lower(s.name)
                    OR lower(s.name) CONTAINS lower(replace(m.name, 'set', ''))
                )
                MERGE (m)-[r:MODIFIES]->(s)
                RETURN count(r) as created
            """)
            stats["relationships_created"] += result.single()["created"]

        return stats


def main():
    """CLI 실행"""
    import argparse

    parser = argparse.ArgumentParser(description="Import Swift code structure to Neo4j")
    parser.add_argument("--sources", default="/path/to/your/ios/project/Sources",
                        help="Sources directory path")
    parser.add_argument("--uri", default="bolt://localhost:7687",
                        help="Neo4j URI")
    parser.add_argument("--user", default="neo4j", help="Neo4j user")
    parser.add_argument("--password", default="password", help="Neo4j password")
    parser.add_argument("--create-relationships", action="store_true",
                        help="Also create TRIGGERS and MODIFIES relationships")

    args = parser.parse_args()

    importer = CodeStructureImporter(args.uri, args.user, args.password, args.sources)

    try:
        print("Creating constraints...")
        importer.create_constraints()

        print("Importing Reactor structures...")
        stats = importer.import_reactors()
        print(f"Import stats: {stats}")

        if args.create_relationships:
            print("Creating TRIGGERS relationships...")
            triggers_stats = importer.create_triggers_relationships()
            print(f"TRIGGERS: {triggers_stats}")

            print("Creating MODIFIES relationships...")
            modifies_stats = importer.create_modifies_relationships()
            print(f"MODIFIES: {modifies_stats}")

    finally:
        importer.close()


if __name__ == "__main__":
    main()
