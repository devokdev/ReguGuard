"""
ReguGuard Blackboard Store (SQLite-backed)
=========================================
Implements the shared case record (Blackboard pattern) for all agents.
Every read and write is versioned, timestamped, attributed to an agent,
and logged for observability and heatmaps.

Single Source of Truth: PRD §5.3, §6, §8.1
"""

from __future__ import annotations
import json
import sqlite3
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field

from src.config import settings


# CONCEPT: Blackboard Shared State Record (PRD §5.3)
class BlackboardEntry(BaseModel):
    """A single versioned entry written to the blackboard."""
    case_id: str
    key: str
    value: Any
    agent: str
    version: int
    ts: datetime = Field(default_factory=datetime.utcnow)
    trace_id: Optional[str] = None


class BlackboardStore:
    """
    SQLite-backed versioned Blackboard store.
    Supports atomic writes, history snapshots, and read tracking for heatmaps.
    """

    def __init__(self, db_path: Optional[Path | str] = None):
        if db_path is None:
            self.db_path = Path(settings.DB_PATH)
        else:
            self.db_path = Path(db_path)

        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._init_db()

    def _get_connection(self) -> sqlite3.Connection:
        conn = sqlite3.connect(str(self.db_path), check_same_thread=False)
        conn.row_factory = sqlite3.Row
        return conn

    def _init_db(self) -> None:
        conn = self._get_connection()
        try:
            # Table storing current and historical values
            conn.execute("""
                CREATE TABLE IF NOT EXISTS blackboard_entries (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    case_id TEXT NOT NULL,
                    key TEXT NOT NULL,
                    value_json TEXT NOT NULL,
                    agent TEXT NOT NULL,
                    version INTEGER NOT NULL,
                    ts TEXT NOT NULL,
                    trace_id TEXT
                )
            """)
            conn.execute("""
                CREATE INDEX IF NOT EXISTS idx_bb_case_key ON blackboard_entries(case_id, key)
            """)

            # Table tracking read accesses for heatmaps (agent x key read matrix)
            conn.execute("""
                CREATE TABLE IF NOT EXISTS blackboard_reads (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    case_id TEXT NOT NULL,
                    key TEXT NOT NULL,
                    agent TEXT NOT NULL,
                    ts TEXT NOT NULL,
                    trace_id TEXT
                )
            """)
            conn.commit()
        finally:
            conn.close()

    # CONCEPT: Blackboard Write Operation
    def write(
        self,
        case_id: str,
        key: str,
        value: Any,
        agent: str,
        trace_id: Optional[str] = None
    ) -> BlackboardEntry:
        """
        Write a key-value pair to the blackboard for a given case_id.
        Automatically increments version number.
        """
        conn = self._get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT MAX(version) FROM blackboard_entries WHERE case_id = ? AND key = ?",
                (case_id, key)
            )
            row = cursor.fetchone()
            current_version = row[0] if (row and row[0] is not None) else 0
            new_version = current_version + 1

            ts = datetime.utcnow()
            value_json = json.dumps(value, default=str)

            cursor.execute(
                """
                INSERT INTO blackboard_entries (case_id, key, value_json, agent, version, ts, trace_id)
                VALUES (?, ?, ?, ?, ?, ?, ?)
                """,
                (case_id, key, value_json, agent, new_version, ts.isoformat(), trace_id)
            )
            conn.commit()

            return BlackboardEntry(
                case_id=case_id,
                key=key,
                value=value,
                agent=agent,
                version=new_version,
                ts=ts,
                trace_id=trace_id
            )
        finally:
            conn.close()

    # CONCEPT: Blackboard Read Operation (with access logging)
    def read(
        self,
        case_id: str,
        keys: Optional[List[str]] = None,
        agent: str = "unknown",
        trace_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Read the latest value for requested keys (or all keys if None) for a case_id.
        Logs read access for heatmap visualization.
        """
        conn = self._get_connection()
        try:
            cursor = conn.cursor()
            if keys:
                placeholders = ",".join("?" for _ in keys)
                query = f"""
                    SELECT b1.key, b1.value_json, b1.version, b1.agent, b1.ts
                    FROM blackboard_entries b1
                    INNER JOIN (
                        SELECT key, MAX(version) as max_v
                        FROM blackboard_entries
                        WHERE case_id = ? AND key IN ({placeholders})
                        GROUP BY key
                    ) b2 ON b1.key = b2.key AND b1.version = b2.max_v
                    WHERE b1.case_id = ?
                """
                params = [case_id] + list(keys) + [case_id]
                cursor.execute(query, params)
            else:
                query = """
                    SELECT b1.key, b1.value_json, b1.version, b1.agent, b1.ts
                    FROM blackboard_entries b1
                    INNER JOIN (
                        SELECT key, MAX(version) as max_v
                        FROM blackboard_entries
                        WHERE case_id = ?
                        GROUP BY key
                    ) b2 ON b1.key = b2.key AND b1.version = b2.max_v
                    WHERE b1.case_id = ?
                """
                cursor.execute(query, (case_id, case_id))

            rows = cursor.fetchall()
            result: Dict[str, Any] = {}
            ts_now = datetime.utcnow().isoformat()

            for r in rows:
                k = r["key"]
                result[k] = json.loads(r["value_json"])

                # Log read event
                cursor.execute(
                    """
                    INSERT INTO blackboard_reads (case_id, key, agent, ts, trace_id)
                    VALUES (?, ?, ?, ?, ?)
                    """,
                    (case_id, k, agent, ts_now, trace_id)
                )

            conn.commit()
            return result
        finally:
            conn.close()

    # CONCEPT: Blackboard Snapshot (Complete versioned audit trail)
    def snapshot(self, case_id: str) -> List[Dict[str, Any]]:
        """Retrieve the entire versioned change history for a case."""
        conn = self._get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute(
                """
                SELECT id, case_id, key, value_json, agent, version, ts, trace_id
                FROM blackboard_entries
                WHERE case_id = ?
                ORDER BY id ASC
                """,
                (case_id,)
            )
            rows = cursor.fetchall()
            return [
                {
                    "id": r["id"],
                    "case_id": r["case_id"],
                    "key": r["key"],
                    "value": json.loads(r["value_json"]),
                    "agent": r["agent"],
                    "version": r["version"],
                    "ts": r["ts"],
                    "trace_id": r["trace_id"]
                }
                for r in rows
            ]
        finally:
            conn.close()

    def get_access_counts(self) -> Dict[str, Dict[str, Dict[str, int]]]:
        """
        Returns read/write frequency matrix for heatmaps:
        {agent: {key: {'reads': N, 'writes': M}}}
        """
        conn = self._get_connection()
        try:
            cursor = conn.cursor()
            # Count writes
            cursor.execute("""
                SELECT agent, key, COUNT(*) as cnt
                FROM blackboard_entries
                GROUP BY agent, key
            """)
            writes = cursor.fetchall()

            # Count reads
            cursor.execute("""
                SELECT agent, key, COUNT(*) as cnt
                FROM blackboard_reads
                GROUP BY agent, key
            """)
            reads = cursor.fetchall()

            matrix: Dict[str, Dict[str, Dict[str, int]]] = {}

            for r in writes:
                agent = r["agent"]
                key = r["key"]
                matrix.setdefault(agent, {}).setdefault(key, {"reads": 0, "writes": 0})
                matrix[agent][key]["writes"] = r["cnt"]

            for r in reads:
                agent = r["agent"]
                key = r["key"]
                matrix.setdefault(agent, {}).setdefault(key, {"reads": 0, "writes": 0})
                matrix[agent][key]["reads"] = r["cnt"]

            return matrix
        finally:
            conn.close()
