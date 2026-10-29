"""
ReguGuard FastAPI Orchestration Backend
=======================================
Provides REST endpoints for running pipeline analyses, inspecting the blackboard,
retrieving trace waterfalls, and fetching registered tools & Agent Cards.

Single Source of Truth: PRD §9, §12
"""

from __future__ import annotations
from typing import Dict, Any, List, Optional
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from src.schemas import RunConfig, ImpactReport
from src.blackboard.store import BlackboardStore
from src.observability.trace_store import trace_store
from src.orchestrator import ReguGuardOrchestrator
from src.mcp_servers.sme_db import list_smes
from src.mcp_servers.doc_fetcher import list_new_documents
from src.api.stream import router as stream_router

app = FastAPI(
    title="ReguGuard API",
    description="Multi-Agent Regulatory Impact Analysis API",
    version="2.1"
)

app.include_router(stream_router)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

blackboard = BlackboardStore()
orchestrator = ReguGuardOrchestrator(blackboard)


class RunRequest(BaseModel):
    case_id: str
    doc_id: str
    prior_doc_id: str
    sme_id: str
    config: Optional[RunConfig] = None


@app.get("/health")
def health_check():
    return {"status": "ok", "system": "ReguGuard", "version": "2.1"}


@app.get("/api/smes")
def get_smes():
    return list_smes()


@app.get("/api/documents")
def get_documents():
    return list_new_documents()


@app.post("/api/run", response_model=ImpactReport)
def run_analysis(req: RunRequest):
    try:
        report = orchestrator.run(
            case_id=req.case_id,
            doc_id=req.doc_id,
            prior_doc_id=req.prior_doc_id,
            sme_id=req.sme_id,
            run_config=req.config
        )
        return report
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/blackboard/{case_id}")
def get_blackboard_snapshot(case_id: str):
    return blackboard.snapshot(case_id)


@app.get("/api/traces/{trace_id}")
def get_trace_spans(trace_id: str):
    return trace_store.get_trace_events(trace_id)


@app.get("/api/heatmaps/agent-metrics")
def get_agent_metrics():
    return trace_store.get_agent_metrics_matrix()


@app.get("/api/heatmaps/blackboard-access")
def get_blackboard_matrix():
    return blackboard.get_access_counts()

