"""
ReguGuard Blackboard MCP Server
===============================
Exposes Blackboard operations (read, write, snapshot) via FastMCP
as required by PRD §6 (blackboard_server).

Tools:
- bb_read(case_id, keys, agent, trace_id)
- bb_write(case_id, key, value, agent, trace_id)
- bb_snapshot(case_id)
"""

from typing import Any, Dict, List, Optional
from mcp.server.fastmcp import FastMCP
from src.blackboard.store import BlackboardStore

# CONCEPT: MCP Tool Server (PRD §6)
mcp = FastMCP("blackboard_server")
store = BlackboardStore()


@mcp.tool()
def bb_read(
    case_id: str,
    keys: list[str] | None = None,
    agent: str = "mcp_client",
    trace_id: str | None = None
) -> dict:
    """Read latest values for keys from the shared blackboard for a given case."""
    return store.read(case_id=case_id, keys=keys, agent=agent, trace_id=trace_id)


@mcp.tool()
def bb_write(
    case_id: str,
    key: str,
    value: str,
    agent: str,
    trace_id: str | None = None
) -> dict:
    """Write or update a key on the shared blackboard for a given case."""
    entry = store.write(
        case_id=case_id,
        key=key,
        value=value,
        agent=agent,
        trace_id=trace_id
    )
    return {
        "status": "ok",
        "case_id": entry.case_id,
        "key": entry.key,
        "version": entry.version,
        "agent": entry.agent,
        "ts": entry.ts.isoformat()
    }


@mcp.tool()
def bb_snapshot(case_id: str) -> list:
    """Retrieve full audit trail snapshot of all entries written for a case."""
    return store.snapshot(case_id=case_id)


if __name__ == "__main__":
    mcp.run()
