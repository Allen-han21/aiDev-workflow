"""Git 히스토리 Neo4j 임포트

Git 커밋 히스토리를 Neo4j에 임포트하여:
- Commit 노드 생성
- CodeFile과 MODIFIES 관계 연결
- JiraIssue와 RESOLVES 관계 연결
"""

import subprocess
import re
import os
from datetime import datetime
from neo4j import GraphDatabase
from typing import Optional


# JIRA 티켓 패턴
TICKET_PATTERN = re.compile(r'\[?(PK-\d+)\]?')
COMMIT_TYPE_PATTERN = re.compile(r'^(feat|fix|refactor|chore|docs|test|remove)\(')


class GitHistoryImporter:
    """Git 히스토리 Neo4j 임포터"""

    def __init__(self, uri: str, user: str, password: str, repo_path: str):
        self.driver = GraphDatabase.driver(uri, auth=(user, password))
        self.repo_path = repo_path
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
            # Commit 제약조건
            try:
                session.run("""
                    CREATE CONSTRAINT commit_hash IF NOT EXISTS
                    FOR (c:Commit) REQUIRE c.hash IS UNIQUE
                """)
            except Exception as e:
                print(f"Commit constraint: {e}")

            # JiraIssue 제약조건
            try:
                session.run("""
                    CREATE CONSTRAINT jira_key IF NOT EXISTS
                    FOR (j:JiraIssue) REQUIRE j.key IS UNIQUE
                """)
            except Exception as e:
                print(f"JiraIssue constraint: {e}")

            # 인덱스
            try:
                session.run("""
                    CREATE INDEX commit_date IF NOT EXISTS
                    FOR (c:Commit) ON (c.date)
                """)
            except Exception as e:
                print(f"Commit date index: {e}")

    def import_commits(self, since: str = "6 months ago", limit: int = 1000) -> dict:
        """Git 커밋 히스토리 임포트

        Args:
            since: 시작 시점 (예: "6 months ago", "2024-01-01")
            limit: 최대 커밋 수

        Returns:
            임포트 통계
        """
        print(f"Importing commits from {self.repo_path} (since: {since}, limit: {limit})")

        # Git log 가져오기
        cmd = [
            "git", "-C", self.repo_path, "log",
            f"--since={since}",
            "--format=%H|%an|%aI|%s",
            f"-{limit}"
        ]
        result = subprocess.run(cmd, capture_output=True, text=True)

        if result.returncode != 0:
            return {"error": result.stderr}

        commits = []
        for line in result.stdout.strip().split('\n'):
            if not line:
                continue
            parts = line.split('|', 3)
            if len(parts) < 4:
                continue

            hash_, author, date, message = parts
            ticket_match = TICKET_PATTERN.search(message)
            type_match = COMMIT_TYPE_PATTERN.search(message)

            commits.append({
                "hash": hash_,
                "author": author,
                "date": date,
                "message": message[:500],  # 메시지 길이 제한
                "ticket_id": ticket_match.group(1) if ticket_match else None,
                "type": type_match.group(1) if type_match else "other"
            })

        # Neo4j에 저장
        stats = self._save_commits(commits)
        stats["total_parsed"] = len(commits)

        return stats

    def _save_commits(self, commits: list) -> dict:
        """커밋 노드 저장"""
        stats = {"commits_created": 0, "jira_linked": 0, "errors": 0}

        with self.driver.session() as session:
            for commit in commits:
                try:
                    # Commit 노드 생성
                    session.run("""
                        MERGE (c:Commit {hash: $hash})
                        SET c.message = $message,
                            c.author = $author,
                            c.date = datetime($date),
                            c.ticket_id = $ticket_id,
                            c.type = $type
                    """, commit)
                    stats["commits_created"] += 1

                    # JIRA 이슈 연결
                    if commit["ticket_id"]:
                        session.run("""
                            MERGE (j:JiraIssue {key: $key})
                            WITH j
                            MATCH (c:Commit {hash: $hash})
                            MERGE (c)-[:RESOLVES]->(j)
                        """, {"key": commit["ticket_id"], "hash": commit["hash"]})
                        stats["jira_linked"] += 1

                except Exception as e:
                    stats["errors"] += 1
                    print(f"Error saving commit {commit['hash'][:8]}: {e}")

        return stats

    def import_commit_files(self, commit_hash: str) -> dict:
        """특정 커밋의 변경 파일 연결

        Args:
            commit_hash: 커밋 해시

        Returns:
            연결 통계
        """
        cmd = [
            "git", "-C", self.repo_path, "diff-tree",
            "--no-commit-id", "--name-status", "-r", commit_hash
        ]
        result = subprocess.run(cmd, capture_output=True, text=True)

        if result.returncode != 0:
            return {"error": result.stderr}

        stats = {"files_linked": 0, "files_skipped": 0}

        with self.driver.session() as session:
            for line in result.stdout.strip().split('\n'):
                if not line:
                    continue
                parts = line.split('\t')
                if len(parts) < 2:
                    continue

                status, file_path = parts[0], parts[-1]

                # Sources/ 내의 Swift 파일만
                if not file_path.startswith("Sources/") or not file_path.endswith(".swift"):
                    stats["files_skipped"] += 1
                    continue

                # CodeFile 경로는 Sources/ 이후만 저장되어 있음
                relative_path = file_path.replace("Sources/", "")

                result = session.run("""
                    MATCH (c:Commit {hash: $hash})
                    MATCH (f:CodeFile {path: $path})
                    MERGE (c)-[r:MODIFIES]->(f)
                    SET r.status = $status
                    RETURN count(*) as linked
                """, {"hash": commit_hash, "path": relative_path, "status": status})

                if result.single()["linked"] > 0:
                    stats["files_linked"] += 1
                else:
                    stats["files_skipped"] += 1

        return stats

    def import_all_commit_files(self, limit: int = 500) -> dict:
        """모든 커밋의 파일 연결

        Args:
            limit: 처리할 최대 커밋 수

        Returns:
            연결 통계
        """
        # Commit 노드에서 해시 조회
        with self.driver.session() as session:
            result = session.run("""
                MATCH (c:Commit)
                RETURN c.hash as hash
                ORDER BY c.date DESC
                LIMIT $limit
            """, {"limit": limit})
            commit_hashes = [r["hash"] for r in result]

        print(f"Linking files for {len(commit_hashes)} commits...")

        total_stats = {"commits_processed": 0, "files_linked": 0, "files_skipped": 0}

        for i, hash_ in enumerate(commit_hashes):
            if i % 50 == 0:
                print(f"  Progress: {i}/{len(commit_hashes)}")

            stats = self.import_commit_files(hash_)
            total_stats["commits_processed"] += 1
            total_stats["files_linked"] += stats.get("files_linked", 0)
            total_stats["files_skipped"] += stats.get("files_skipped", 0)

        return total_stats


def main():
    """CLI 실행"""
    import argparse

    parser = argparse.ArgumentParser(description="Import Git history to Neo4j")
    parser.add_argument("--repo", default="/path/to/your/ios/project",
                        help="Repository path")
    parser.add_argument("--since", default="6 months ago",
                        help="Import commits since this date")
    parser.add_argument("--limit", type=int, default=1000,
                        help="Maximum number of commits")
    parser.add_argument("--uri", default="bolt://localhost:7687",
                        help="Neo4j URI")
    parser.add_argument("--user", default="neo4j", help="Neo4j user")
    parser.add_argument("--password", default="password", help="Neo4j password")
    parser.add_argument("--link-files", action="store_true",
                        help="Also link commits to CodeFile nodes")

    args = parser.parse_args()

    importer = GitHistoryImporter(args.uri, args.user, args.password, args.repo)

    try:
        print("Creating constraints...")
        importer.create_constraints()

        print("Importing commits...")
        stats = importer.import_commits(since=args.since, limit=args.limit)
        print(f"Commits imported: {stats}")

        if args.link_files:
            print("Linking files...")
            file_stats = importer.import_all_commit_files(limit=args.limit)
            print(f"Files linked: {file_stats}")

    finally:
        importer.close()


if __name__ == "__main__":
    main()
