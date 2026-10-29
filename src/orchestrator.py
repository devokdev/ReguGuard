"""
ReguGuard End-to-End Orchestrator
=================================
Combines ADK Agents (Step 4) and CrewAI Flow via A2A (Step 5)
to construct the validated, grounded ImpactReport (PRD §7, §14 Step 6).
"""

from __future__ import annotations
import uuid
import time
from datetime import datetime
from typing import Dict, Any, Optional

from src.schemas import (
    RunConfig,
    ImpactReport,
    ImpactVerdict,
    Evidence,
    ActionPlan,
    RunMetrics,
    AgentMetrics,
    A2AEnvelope
)
from src.blackboard.store import BlackboardStore
from src.adk_app.pipeline import ReguGuardPipeline
from src.crew_app.flow import CrewAIA2AServer
from src.observability.trace_store import trace_store


class ReguGuardOrchestrator:
    """End-to-End Multi-Agent Orchestrator executing the complete vertical slice."""

    def __init__(self, blackboard: Optional[BlackboardStore] = None):
        self.blackboard = blackboard or BlackboardStore()
        self.adk_pipeline = ReguGuardPipeline(self.blackboard)
        self.a2a_server = CrewAIA2AServer(self.blackboard)

    def run(
        self,
        case_id: str,
        doc_id: str,
        prior_doc_id: str,
        sme_id: str,
        run_config: Optional[RunConfig] = None
    ) -> ImpactReport:
        t0 = time.time()
        trace_id = f"trace-{uuid.uuid4().hex[:8]}"
        config = run_config or RunConfig()

        # Step A: Run ADK Agents (Manager, Monitor, ChangeDetection || SMEProfile, ImpactAnalysis)
        adk_out = self.adk_pipeline.run_adk_pipeline(
            case_id=case_id,
            trace_id=trace_id,
            doc_id=doc_id,
            prior_doc_id=prior_doc_id,
            sme_id=sme_id,
            run_config=config
        )
        verdict: ImpactVerdict = adk_out["verdict"]

        # Step B: Call CrewAI Flow via A2A
        envelope = A2AEnvelope(
            case_id=case_id,
            trace_id=trace_id,
            blackboard_ref=f"blackboard://{case_id}",
            action_type="full_flow",
            payload={"sme_id": sme_id}
        )
        crew_resp = self.a2a_server.handle_envelope(envelope)

        evidence_items = [Evidence(**e) for e in crew_resp.get("evidence", [])]
        action_data = crew_resp.get("action")
        action_plan = ActionPlan(**action_data) if action_data else None

        # Step C: Collect RunMetrics from trace spans
        spans = trace_store.get_trace_events(trace_id)
        total_latency = (time.time() - t0)
        total_tokens = sum(s.tokens_in + s.tokens_out for s in spans)
        total_cost = sum(s.cost_usd for s in spans)

        metrics = RunMetrics(
            total_latency_s=round(total_latency, 3),
            total_tokens=total_tokens,
            total_cost_usd=round(total_cost, 6),
            per_agent={},
            retries=0,
            errors=0
        )

        # Step D: Construct and Validate Final ImpactReport (PRD §7)
        report = ImpactReport(
            case_id=case_id,
            trace_id=trace_id,
            sme_id=sme_id,
            generated_at=datetime.utcnow(),
            headline="Potential regulatory impact detected — human review recommended",
            verdict=verdict,
            evidence=evidence_items,
            action=action_plan,
            guardrail_flags=[],
            disclaimer="This note is for informational purposes and does not constitute formal legal or tax advice.",
            run_config=config,
            metrics=metrics
        )

        return report

