"""
ReguGuard Trace Store (SQLite-backed)
=====================================
Stores OpenTelemetry-style spans and trace events across all agents.
Enables Trace Explorer, waterfall visualizations, heatmaps, and audit trails.

Single Source of Truth: PRD §8.1, §8.3, Criterion 5 & 9
"""

from __future__ import annotations
import json
import sqlite3
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any, Optional
from src.schemas import TraceEvent
from src.config import settings


# CONCEPT: Observability & OpenTelemetry-style Trace Storage (PRD §8.3)
class TraceStore:
    def __init__(self, db_path: Optional[Path | str] = None):
        if db_path is None:
            self.db_path = Path(settings.TRACE_DB_PATH)
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
            conn.execute("""
                CREATE TABLE IF NOT EXISTS trace_events (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    trace_id TEXT NOT NULL,
                    span_id TEXT NOT NULL,
                    parent_span_id TEXT,
                    agent TEXT NOT NULL,
                    framework TEXT NOT NULL,
                    kind TEXT NOT NULL,
                    ts_start TEXT NOT NULL,
                    ts_end TEXT NOT NULL,
                    latency_ms REAL NOT NULL,
                    tokens_in INTEGER NOT NULL,
                    tokens_out INTEGER NOT NULL,
                    cost_usd REAL NOT NULL,
                    payload_preview TEXT,
                    status TEXT NOT NULL
                )
            """)
            conn.execute("""
                CREATE INDEX IF NOT EXISTS idx_traces_tid ON trace_events(trace_id)
            """)
            conn.commit()
        finally:
            conn.close()

    def log_event(self, event: TraceEvent) -> None:
        """Persist a single TraceEvent span into SQLite."""
        conn = self._get_connection()
        try:
            conn.execute(
                """
                INSERT INTO trace_events (
                    trace_id, span_id, parent_span_id, agent, framework, kind,
                    ts_start, ts_end, latency_ms, tokens_in, tokens_out, cost_usd,
                    payload_preview, status
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    event.trace_id,
                    event.span_id,
                    event.parent_span_id,
                    event.agent,
                    event.framework,
                    event.kind,
                    event.ts_start.isoformat(),
                    event.ts_end.isoformat(),
                    event.latency_ms,
                    event.tokens_in,
                    event.tokens_out,
                    event.cost_usd,
                    event.payload_preview[:1000],
                    event.status
                )
            )
            conn.commit()
        finally:
            conn.close()

    def get_trace_events(self, trace_id: str) -> List[TraceEvent]:
        """Fetch all spans for a specific trace in chronological order."""
        conn = self._get_connection()
        try:
            cur = conn.cursor()
            cur.execute(
                """
                SELECT trace_id, span_id, parent_span_id, agent, framework, kind,
                       ts_start, ts_end, latency_ms, tokens_in, tokens_out, cost_usd,
                       payload_preview, status
                FROM trace_events
                WHERE trace_id = ?
                ORDER BY id ASC
                """,
                (trace_id,)
            )
            rows = cur.fetchall()
            return [
                TraceEvent(
                    trace_id=r["trace_id"],
                    span_id=r["span_id"],
                    parent_span_id=r["parent_span_id"],
                    agent=r["agent"],
                    framework=r["framework"],
                    kind=r["kind"],
                    ts_start=datetime.fromisoformat(r["ts_start"]),
                    ts_end=datetime.fromisoformat(r["ts_end"]),
                    latency_ms=r["latency_ms"],
                    tokens_in=r["tokens_in"],
                    tokens_out=r["tokens_out"],
                    cost_usd=r["cost_usd"],
                    payload_preview=r["payload_preview"],
                    status=r["status"]
                )
                for r in rows
            ]
        finally:
            conn.close()

    def get_agent_metrics_matrix(self) -> Dict[str, Dict[str, float]]:
        """
        Calculates aggregate statistics per agent for Plotly heatmaps (Criterion 5):
        latency, tokens, cost, errors.
        """
        conn = self._get_connection()
        try:
            cur = conn.cursor()
            cur.execute("""
                SELECT agent,
                       AVG(latency_ms) as avg_latency,
                       SUM(tokens_in + tokens_out) as total_tokens,
                       SUM(cost_usd) as total_cost,
                       SUM(CASE WHEN status = 'error' THEN 1 ELSE 0 END) as errors,
                       SUM(CASE WHEN kind = 'guardrail' THEN 1 ELSE 0 END) as guardrails
                FROM trace_events
                GROUP BY agent
            """)
            rows = cur.fetchall()
            return {
                r["agent"]: {
                    "avg_latency_ms": r["avg_latency"] or 0.0,
                    "total_tokens": r["total_tokens"] or 0,
                    "total_cost_usd": r["total_cost"] or 0.0,
                    "errors": r["errors"] or 0,
                    "guardrail_hits": r["guardrails"] or 0
                }
                for r in rows
            }
        finally:
            conn.close()


trace_store = TraceStore()

