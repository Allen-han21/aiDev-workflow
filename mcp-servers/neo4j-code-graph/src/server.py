#!/usr/bin/env python3
"""
Neo4j Code Graph MCP Server
Claude Code에서 코드 그래프 쿼리 실행

도구:
- neo4j_query: Cypher 쿼리 직접 실행
- neo4j_find_impact: 파일 변경 영향도 분석
- neo4j_trace_workflow: Reactor 워크플로우 추적
- neo4j_graph_stats: 그래프 통계 조회
"""

import os
import json
import asyncio
from typing import Any

from mcp.server import Server
from mcp.types import Tool, TextContent

# 상대 임포트 대신 직접 임포트
import sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from neo4j_client import Neo4jClient

# 서버 인스턴스
server = Server("neo4j-code-graph")

# Neo4j 클라이언트 (lazy initialization)
_neo4j: Neo4jClient | None = None


def get_neo4j() -> Neo4jClient:
    """Neo4j 클라이언트 가져오기 (lazy init)"""
    global _neo4j
    if _neo4j is None:
        _neo4j = Neo4jClient(
            uri=os.environ.get("NEO4J_URI", "bolt://localhost:7687"),
            user=os.environ.get("NEO4J_USER", "neo4j"),
            password=os.environ.get("NEO4J_PASSWORD", "password")
        )
    return _neo4j


@server.list_tools()
async def list_tools() -> list[Tool]:
    """사용 가능한 도구 목록"""
    return [
        Tool(
            name="neo4j_query",
            description="Execute Cypher query on code graph. Returns query results as JSON.",
            inputSchema={
                "type": "object",
                "properties": {
                    "cypher": {
                        "type": "string",
                        "description": "Cypher query to execute"
                    },
                    "params": {
                        "type": "object",
                        "description": "Query parameters (optional)",
                        "additionalProperties": True
                    }
                },
                "required": ["cypher"]
            }
        ),
        Tool(
            name="neo4j_find_impact",
            description="Find impact of changing a file. Returns similar files, same-module files, and related commits.",
            inputSchema={
                "type": "object",
                "properties": {
                    "file_path": {
                        "type": "string",
                        "description": "File path or name to analyze (e.g., 'LoginViewController.swift')"
                    },
                    "depth": {
                        "type": "integer",
                        "default": 2,
                        "description": "Search depth (1-3)"
                    }
                },
                "required": ["file_path"]
            }
        ),
        Tool(
            name="neo4j_trace_workflow",
            description="Trace ReactorKit Action -> Mutation -> State workflow. Identifies potential race conditions.",
            inputSchema={
                "type": "object",
                "properties": {
                    "reactor_name": {
                        "type": "string",
                        "description": "Reactor class name (e.g., 'LoginReactor')"
                    },
                    "action_name": {
                        "type": "string",
                        "description": "Specific action to trace (optional)"
                    }
                },
                "required": ["reactor_name"]
            }
        ),
        Tool(
            name="neo4j_graph_stats",
            description="Get statistics about the code graph (node counts, relationship counts).",
            inputSchema={
                "type": "object",
                "properties": {},
                "required": []
            }
        )
    ]


@server.call_tool()
async def call_tool(name: str, arguments: dict) -> list[TextContent]:
    """도구 호출 처리"""
    try:
        client = get_neo4j()

        if name == "neo4j_query":
            result = client.run_query(
                arguments["cypher"],
                arguments.get("params", {})
            )
            return [TextContent(
                type="text",
                text=json.dumps(result, indent=2, ensure_ascii=False)
            )]

        elif name == "neo4j_find_impact":
            result = client.find_impact(
                arguments["file_path"],
                arguments.get("depth", 2)
            )
            return [TextContent(
                type="text",
                text=json.dumps(result, indent=2, ensure_ascii=False)
            )]

        elif name == "neo4j_trace_workflow":
            result = client.trace_workflow(
                arguments["reactor_name"],
                arguments.get("action_name")
            )
            return [TextContent(
                type="text",
                text=json.dumps(result, indent=2, ensure_ascii=False)
            )]

        elif name == "neo4j_graph_stats":
            result = client.get_graph_stats()
            return [TextContent(
                type="text",
                text=json.dumps(result, indent=2, ensure_ascii=False)
            )]

        else:
            return [TextContent(
                type="text",
                text=f"Unknown tool: {name}"
            )]

    except Exception as e:
        return [TextContent(
            type="text",
            text=json.dumps({
                "error": str(e),
                "tool": name,
                "suggestion": "Check Neo4j connection and query syntax"
            }, ensure_ascii=False)
        )]


def main():
    """MCP 서버 실행"""
    from mcp.server.stdio import stdio_server

    async def run():
        async with stdio_server() as (read_stream, write_stream):
            await server.run(
                read_stream,
                write_stream,
                server.create_initialization_options()
            )

    asyncio.run(run())


if __name__ == "__main__":
    main()
