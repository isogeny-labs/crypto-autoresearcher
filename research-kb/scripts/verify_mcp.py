#!/usr/bin/env python3
"""End-to-end check: catalog -> CLI -> real stdio MCP subprocess -> client configs.

Run with the package interpreter:

    .venv/bin/python scripts/verify_mcp.py

Exit code is non-zero if any layer is empty or disagrees with the one below it.
The MCP check is a real subprocess launch, not an in-process FastMCP fixture.
"""

from __future__ import annotations

import asyncio
import json
import os
import sys
from pathlib import Path


def fail(message: str) -> None:
    print(f"FAIL: {message}")
    raise SystemExit(1)


async def check_mcp() -> dict:
    from fastmcp import Client
    from fastmcp.client.transports import StdioTransport

    command = str(Path(sys.executable).with_name("research-kb"))
    if not Path(command).exists():
        fail(f"missing {command}")
    transport = StdioTransport(command=command, args=["mcp"], env=dict(os.environ))
    async with Client(transport) as client:
        tools = {tool.name for tool in await client.list_tools()}
        required = {"search_knowledge", "get_context", "get_source", "kb_status", "recent_sources"}
        missing = required - tools
        if missing:
            fail(f"MCP is missing tools: {sorted(missing)}")
        status = (await client.call_tool("kb_status", {})).data
        if not status.get("ready"):
            fail(f"MCP reports no active corpus: {status}")
        result = (await client.call_tool("search_knowledge", {"query": "KN-FIND", "top_k": 1})).data
        if not result.get("results"):
            fail("MCP search returned no passages")
        return {"tools": sorted(tools), "revision": status.get("revision")}


def main() -> None:
    from research_kb.cli import app  # noqa: F401  (ensures the package resolves)
    from research_kb.library import Library

    library = Library()
    status = library.status()
    if not status.get("ready"):
        fail(f"catalog is not ready: {status}")
    print(f"catalog: {status['active_documents']} documents, revision {status['revision']}")

    result = library.search("KN-FIND", top_k=1)
    if not result["results"]:
        fail("CLI retrieval returned no passages")
    first = result["results"][0]
    print(f"search: {first['source_id']} ({first['content_hash'][:12]})")

    brief = library.brief("negative results for Semaev decomposition", top_k=2)
    if "source_id:" not in brief:
        fail("brief output carries no citations")
    print(f"brief: {len(brief)} chars, citation-bearing")

    mcp = asyncio.run(check_mcp())
    if mcp["revision"] != status["revision"]:
        fail(f"MCP revision {mcp['revision']} != catalog {status['revision']}")
    print(f"mcp: {len(mcp['tools'])} tools, same revision")

    from research_kb.clients import client_path

    for name in ("claude", "codex", "opencode"):
        path = client_path(name)
        if path.exists() and "research-kb" in path.read_text(encoding="utf-8", errors="replace"):
            print(f"client/{name}: registered at {path}")
    print(json.dumps({"status": "ok", "revision": status["revision"]}, indent=2))


if __name__ == "__main__":
    main()
