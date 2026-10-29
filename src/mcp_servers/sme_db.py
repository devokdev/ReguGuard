"""
ReguGuard MCP Server: sme_db
============================
Manages SME profiles from data/smes/smes.json and stores memory notes in SQLite.
Tools:
- get_profile(sme_id)
- list_smes()
- update_memory(sme_id, note)
"""

from __future__ import annotations
import json
import sqlite3
from pathlib import Path
from typing import Dict, List, Any, Optional
from mcp.server.fastmcp import FastMCP
from src.config import settings

mcp = FastMCP("sme_db")


def _get_db() -> sqlite3.Connection:
    conn = sqlite3.connect(str(settings.DB_PATH), check_same_thread=False)
    conn.row_factory = sqlite3.Row
    conn.execute("""
        CREATE TABLE IF NOT EXISTS sme_notes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            sme_id TEXT NOT NULL,
            note TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    conn.commit()
    return conn


def _load_smes_from_file() -> List[Dict[str, Any]]:
    path = Path(settings.SMES_FILE)
    if not path.exists():
        return []
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


@mcp.tool()
def list_smes() -> list:
    """Return list of all registered SMEs."""
    return _load_smes_from_file()


@mcp.tool()
def get_profile(sme_id: str) -> dict:
    """Retrieve detailed profile and memory notes for an SME by ID."""
    smes = _load_smes_from_file()
    matched = next((s for s in smes if s.get("sme_id") == sme_id), None)
    if not matched:
        return {"status": "error", "message": f"SME {sme_id} not found"}

    conn = _get_db()
    try:
        cur = conn.cursor()
        cur.execute("SELECT note, created_at FROM sme_notes WHERE sme_id = ? ORDER BY id DESC", (sme_id,))
        notes = [dict(r) for r in cur.fetchall()]
    finally:
        conn.close()

    res = dict(matched)
    res["notes"] = notes
    res["status"] = "ok"
    return res


@mcp.tool()
def update_memory(sme_id: str, note: str) -> dict:
    """Store an operational note or compliance memory for an SME."""
    conn = _get_db()
    try:
        cur = conn.cursor()
        cur.execute("INSERT INTO sme_notes (sme_id, note) VALUES (?, ?)", (sme_id, note))
        conn.commit()
    finally:
        conn.close()

    return {"status": "ok", "sme_id": sme_id, "note": note}


if __name__ == "__main__":
    mcp.run()

