"""Swift 파일 임포트 - CodeFile 노드 생성

Sources 디렉토리의 Swift 파일들을 CodeFile 노드로 임포트:
- 파일 경로, 이름, 모듈 정보
- Reactor와의 DEFINED_IN 관계
- 같은 디렉토리 파일들의 SAME_MODULE 관계
"""

import os
from pathlib import Path
from neo4j import GraphDatabase
from typing import Optional
import hashlib


class CodeFileImporter:
    """Swift 파일을 Neo4j CodeFile 노드로 임포트"""

    def __init__(self, uri: str, user: str, password: str, sources_path: str):
        self.driver = GraphDatabase.driver(uri, auth=(user, password))
        self.sources_path = Path(sources_path)
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
            try:
                session.run("""
                    CREATE CONSTRAINT code_file_unique IF NOT EXISTS
                    FOR (f:CodeFile) REQUIRE f.path IS UNIQUE
                """)
                print("CodeFile constraint created")
            except Exception as e:
                print(f"CodeFile constraint: {e}")

            try:
                session.run("""
                    CREATE INDEX code_file_name IF NOT EXISTS
                    FOR (f:CodeFile) ON (f.name)
                """)
                print("CodeFile name index created")
            except Exception as e:
                print(f"CodeFile name index: {e}")

            try:
                session.run("""
                    CREATE INDEX code_file_module IF NOT EXISTS
                    FOR (f:CodeFile) ON (f.module)
                """)
                print("CodeFile module index created")
            except Exception as e:
                print(f"CodeFile module index: {e}")

    def _extract_module(self, file_path: Path) -> str:
        """파일 경로에서 모듈 이름 추출

        Sources/Features/Album/Views/AlbumViewController.swift
        → Features/Album

        Sources/SwiftUI/Presentation/Views/Community/CommunityView.swift
        → SwiftUI/Presentation/Views/Community
        """
        relative = file_path.relative_to(self.sources_path)
        parts = relative.parts

        # 마지막 파일명 제외
        if len(parts) > 1:
            # Views, ViewControllers, Reactors 등은 모듈에 포함하지 않음
            module_parts = []
            for part in parts[:-1]:
                if part.lower() not in ('views', 'viewcontrollers', 'reactors',
                                        'models', 'cells', 'components'):
                    module_parts.append(part)
                else:
                    # 상위 폴더까지만 모듈로
                    break
            return '/'.join(module_parts) if module_parts else parts[0]
        return parts[0] if parts else "Root"

    def _get_file_type(self, file_path: Path) -> str:
        """파일 타입 추출"""
        name = file_path.stem

        if name.endswith('Reactor'):
            return 'Reactor'
        elif name.endswith('ViewController'):
            return 'ViewController'
        elif name.endswith('View') and not name.endswith('ViewController'):
            return 'View'
        elif name.endswith('Cell'):
            return 'Cell'
        elif name.endswith('Service'):
            return 'Service'
        elif name.endswith('Repository'):
            return 'Repository'
        elif name.endswith('UseCase'):
            return 'UseCase'
        elif name.endswith('Entity'):
            return 'Entity'
        elif name.endswith('Reducer'):
            return 'Reducer'
        elif name.endswith('Tests'):
            return 'Test'
        else:
            return 'Other'

    def import_files(self,
                     extensions: list[str] = None,
                     exclude_dirs: list[str] = None) -> dict:
        """Swift 파일 임포트

        Args:
            extensions: 임포트할 파일 확장자 (기본: ['.swift'])
            exclude_dirs: 제외할 디렉토리 (기본: ['Pods', 'DerivedData', ...])

        Returns:
            임포트 통계
        """
        if extensions is None:
            extensions = ['.swift']

        if exclude_dirs is None:
            exclude_dirs = [
                'Pods', 'DerivedData', '.build', 'Build',
                'Carthage', 'Tuist', 'ExternalLibraries',
                'Tests', 'UITests', 'Snapshots'
            ]

        stats = {
            "files_imported": 0,
            "by_type": {},
            "by_module": {},
            "errors": 0
        }

        # Swift 파일 수집
        swift_files = []
        for ext in extensions:
            swift_files.extend(self.sources_path.rglob(f"*{ext}"))

        # 제외 디렉토리 필터링
        filtered_files = []
        for f in swift_files:
            skip = False
            for exclude in exclude_dirs:
                if exclude in f.parts:
                    skip = True
                    break
            if not skip:
                filtered_files.append(f)

        print(f"Found {len(filtered_files)} Swift files (after filtering)")

        # 배치 처리
        batch_size = 100
        batch = []

        for file_path in filtered_files:
            try:
                relative_path = str(file_path.relative_to(self.sources_path))
                module = self._extract_module(file_path)
                file_type = self._get_file_type(file_path)

                batch.append({
                    "path": relative_path,
                    "name": file_path.name,
                    "stem": file_path.stem,
                    "module": module,
                    "type": file_type
                })

                # 통계 업데이트
                stats["by_type"][file_type] = stats["by_type"].get(file_type, 0) + 1
                stats["by_module"][module] = stats["by_module"].get(module, 0) + 1

                if len(batch) >= batch_size:
                    self._save_batch(batch)
                    stats["files_imported"] += len(batch)
                    print(f"Imported {stats['files_imported']} files...")
                    batch = []

            except Exception as e:
                stats["errors"] += 1
                print(f"Error processing {file_path}: {e}")

        # 남은 배치 처리
        if batch:
            self._save_batch(batch)
            stats["files_imported"] += len(batch)

        print(f"Total imported: {stats['files_imported']} files")
        return stats

    def _save_batch(self, batch: list[dict]):
        """배치 저장"""
        with self.driver.session() as session:
            session.run("""
                UNWIND $files as file
                MERGE (f:CodeFile {path: file.path})
                SET f.name = file.name,
                    f.stem = file.stem,
                    f.module = file.module,
                    f.type = file.type
            """, {"files": batch})

    def create_reactor_relationships(self) -> dict:
        """Reactor 노드와 CodeFile 연결 (DEFINED_IN)"""
        stats = {"relationships_created": 0}

        with self.driver.session() as session:
            # Action 노드의 reactor 속성과 CodeFile 연결
            result = session.run("""
                MATCH (a:Action)
                WITH DISTINCT a.reactor as reactor_name
                MATCH (f:CodeFile)
                WHERE f.stem = reactor_name OR f.name = reactor_name + '.swift'
                MERGE (a2:Action {reactor: reactor_name})-[:DEFINED_IN]->(f)
                RETURN count(*) as created
            """)

            # Reactor 이름과 CodeFile 매칭
            result = session.run("""
                MATCH (f:CodeFile)
                WHERE f.type = 'Reactor'
                MATCH (a:Action)
                WHERE a.reactor = f.stem
                MERGE (a)-[:DEFINED_IN]->(f)
                WITH f
                MATCH (m:Mutation)
                WHERE m.reactor = f.stem
                MERGE (m)-[:DEFINED_IN]->(f)
                WITH f
                MATCH (s:StateField)
                WHERE s.reactor = f.stem
                MERGE (s)-[:DEFINED_IN]->(f)
                RETURN count(DISTINCT f) as reactors_linked
            """)
            record = result.single()
            stats["relationships_created"] = record["reactors_linked"] if record else 0

        return stats

    def create_module_relationships(self) -> dict:
        """같은 모듈 파일들의 SAME_MODULE 관계 생성"""
        stats = {"relationships_created": 0}

        with self.driver.session() as session:
            # 먼저 작은 모듈만 선택 (100개 이하 파일)
            small_modules = session.run("""
                MATCH (f:CodeFile)
                WHERE f.module IS NOT NULL
                WITH f.module as module, count(f) as size
                WHERE size <= 50
                RETURN module
            """)
            modules = [r["module"] for r in small_modules]

            # 각 모듈별로 관계 생성
            for module in modules:
                result = session.run("""
                    MATCH (f1:CodeFile {module: $module}), (f2:CodeFile {module: $module})
                    WHERE f1.path < f2.path
                    MERGE (f1)-[:SAME_MODULE]->(f2)
                    RETURN count(*) as created
                """, {"module": module})
                record = result.single()
                stats["relationships_created"] += record["created"] if record else 0

        return stats


def main():
    """CLI 실행"""
    import argparse

    parser = argparse.ArgumentParser(description="Import Swift files to Neo4j as CodeFile nodes")
    parser.add_argument("--sources", default="/path/to/your/ios/project/Sources",
                        help="Sources directory path")
    parser.add_argument("--uri", default="bolt://localhost:7687", help="Neo4j URI")
    parser.add_argument("--user", default="neo4j", help="Neo4j user")
    parser.add_argument("--password", default="password", help="Neo4j password")
    parser.add_argument("--create-relationships", action="store_true",
                        help="Also create DEFINED_IN and SAME_MODULE relationships")

    args = parser.parse_args()

    importer = CodeFileImporter(args.uri, args.user, args.password, args.sources)

    try:
        print("Creating constraints...")
        importer.create_constraints()

        print("\nImporting Swift files...")
        stats = importer.import_files()

        print(f"\n=== Import Stats ===")
        print(f"Total files: {stats['files_imported']}")
        print(f"Errors: {stats['errors']}")

        print(f"\nBy type:")
        for file_type, count in sorted(stats['by_type'].items(), key=lambda x: -x[1]):
            print(f"  {file_type}: {count}")

        print(f"\nTop modules:")
        sorted_modules = sorted(stats['by_module'].items(), key=lambda x: -x[1])[:15]
        for module, count in sorted_modules:
            print(f"  {module}: {count}")

        if args.create_relationships:
            print("\nCreating DEFINED_IN relationships (Reactor → CodeFile)...")
            reactor_stats = importer.create_reactor_relationships()
            print(f"  Linked: {reactor_stats['relationships_created']} reactors")

            print("\nCreating SAME_MODULE relationships...")
            module_stats = importer.create_module_relationships()
            print(f"  Created: {module_stats['relationships_created']} relationships")

    finally:
        importer.close()


if __name__ == "__main__":
    main()
