"""
ReguGuard Observability Callbacks
=================================
Attaches lifecycle monitoring callbacks to agents.
Captures start/end events, model invocations, tool calls, and guardrail checks.

Single Source of Truth: PRD §8.1, Criterion 5
"""

from __future__ import annotations
import uuid
import time
from datetime import datetime
from typing import Callable, Optional, Dict, Any
from src.schemas import TraceEvent
from src.observability.trace_store import trace_store


# CONCEPT: ADK & Agent Lifecycle Callbacks (PRD §8.1)
class AgentCallbackHandler:
    """Manages span creation and logging for an individual agent."""

    def __init__(self, agent_name: str, framework: str = "adk"):
        self.agent_name = agent_name
        self.framework = framework

    def on_agent_start(self, trace_id: str, payload_preview: str = "") -> str:
        """Invoked when an agent starts reasoning."""
        span_id = str(uuid.uuid4())[:8]
        now = datetime.utcnow()
        event = TraceEvent(
            trace_id=trace_id,
            span_id=span_id,
            parent_span_id=None,
            agent=self.agent_name,
            framework=self.framework,
            kind="agent_start",
            ts_start=now,
            ts_end=now,
            latency_ms=0.0,
            tokens_in=0,
            tokens_out=0,
            cost_usd=0.0,
            payload_preview=payload_preview,
            status="ok"
        )
        trace_store.log_event(event)
        return span_id

    def on_agent_end(
        self,
        trace_id: str,
        span_id: str,
        latency_ms: float,
        tokens_in: int = 0,
        tokens_out: int = 0,
        cost_usd: float = 0.0,
        payload_preview: str = "",
        status: str = "ok"
    ) -> None:
        """Invoked when an agent finishes execution."""
        now = datetime.utcnow()
        event = TraceEvent(
            trace_id=trace_id,
            span_id=span_id,
            parent_span_id=None,
            agent=self.agent_name,
            framework=self.framework,
            kind="agent_end",
            ts_start=now,
            ts_end=now,
            latency_ms=latency_ms,
            tokens_in=tokens_in,
            tokens_out=tokens_out,
            cost_usd=cost_usd,
            payload_preview=payload_preview,
            status=status
        )
        trace_store.log_event(event)

    def on_tool_call(
        self,
        trace_id: str,
        tool_name: str,
        latency_ms: float,
        payload_preview: str = "",
        status: str = "ok"
    ) -> None:
        """Invoked when an external tool is called."""
        span_id = str(uuid.uuid4())[:8]
        now = datetime.utcnow()
        event = TraceEvent(
            trace_id=trace_id,
            span_id=span_id,
            parent_span_id=None,
            agent=self.agent_name,
            framework="mcp",
            kind="tool_call",
            ts_start=now,
            ts_end=now,
            latency_ms=latency_ms,
            tokens_in=0,
            tokens_out=0,
            cost_usd=0.0,
            payload_preview=f"Tool: {tool_name} | {payload_preview}",
            status=status
        )
        trace_store.log_event(event)

    def on_model_call(
        self,
        trace_id: str,
        model_name: str,
        latency_ms: float,
        tokens_in: int,
        tokens_out: int,
        cost_usd: float = 0.0,
        payload_preview: str = ""
    ) -> None:
        """Invoked when an LLM inference call completes."""
        span_id = str(uuid.uuid4())[:8]
        now = datetime.utcnow()
        event = TraceEvent(
            trace_id=trace_id,
            span_id=span_id,
            parent_span_id=None,
            agent=self.agent_name,
            framework=self.framework,
            kind="model_call",
            ts_start=now,
            ts_end=now,
            latency_ms=latency_ms,
            tokens_in=tokens_in,
            tokens_out=tokens_out,
            cost_usd=cost_usd,
            payload_preview=f"Model: {model_name} | {payload_preview}",
            status="ok"
        )
        trace_store.log_event(event)


def make_callbacks(agent_name: str, framework: str = "adk") -> AgentCallbackHandler:
    """Factory creating callback handler per agent as specified in PRD §8.1."""
    return AgentCallbackHandler(agent_name=agent_name, framework=framework)

