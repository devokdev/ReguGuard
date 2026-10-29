"""
ReguGuard ADK Agent Roster & Parallel Topology
==============================================
Implements:
- Manager Agent (Planning & Delegation)
- Regulation Monitor Agent (doc_fetcher, clause_parser)
- Change Detection Agent (diff_tool, vector_search)
- SME Profile Agent (sme_db, agent memory)
- Impact Analysis Agent (ReAct reasoning & agentic RAG)

Single Source of Truth: PRD §4, §4.1, §5.3, §14 Step 4
"""

from __future__ import annotations
import json
import time
from datetime import datetime, date
from typing import Dict, Any, List, Optional
from src.schemas import RunConfig, ClauseChange, SMEProfile, ImpactVerdict
from src.blackboard.store import BlackboardStore
from src.observability.callbacks import make_callbacks
from src.observability.llm_client import llm_client
from src.mcp_servers.doc_fetcher import fetch_regulation
from src.mcp_servers.clause_parser import split_clauses, extract_thresholds
from src.mcp_servers.diff_tool import diff_versions
from src.mcp_servers.sme_db import get_profile
from src.mcp_servers.vector_search import search


# CONCEPT: ADK Coordinator / Manager Agent (PRD §4.1)
class ManagerAgent:
    """Manager Coordinator that emits a RunPlan and delegates to sub-agents."""

    def __init__(self, blackboard: BlackboardStore):
        self.blackboard = blackboard
        self.callbacks = make_callbacks("Manager", framework="adk")

    def run(self, case_id: str, trace_id: str, doc_id: str, prior_doc_id: str, sme_id: str) -> Dict[str, Any]:
        t0 = time.time()
        span_id = self.callbacks.on_agent_start(trace_id, f"Case: {case_id} | Planning")

        # Emit RunPlan (PRD §3 Handout Topic: Planning)
        plan = {
            "plan_name": f"Regulatory Impact Run for {case_id}",
            "topology": "parallel",
            "stages": ["Monitor", "ChangeDetection||SMEProfile", "ImpactAnalysis", "A2A_EvidenceAction"],
            "doc_id": doc_id,
            "prior_doc_id": prior_doc_id,
            "sme_id": sme_id
        }
        self.blackboard.write(case_id, "plan", plan, "Manager", trace_id)
        self.blackboard.write(case_id, "status", "planned", "Manager", trace_id)

        latency_ms = (time.time() - t0) * 1000.0
        self.callbacks.on_agent_end(trace_id, span_id, latency_ms, payload_preview="RunPlan generated")
        return plan


# CONCEPT: ADK Regulation Monitor Agent (PRD §4.1)
class RegulationMonitorAgent:
    """Fetches regulation documents and parses clauses into shared state."""

    def __init__(self, blackboard: BlackboardStore):
        self.blackboard = blackboard
        self.callbacks = make_callbacks("RegulationMonitor", framework="adk")

    def run(self, case_id: str, trace_id: str, doc_id: str, prior_doc_id: str) -> Dict[str, Any]:
        t0 = time.time()
        span_id = self.callbacks.on_agent_start(trace_id, f"Fetching doc {doc_id}")

        # Tool 1: doc_fetcher
        t_tool = time.time()
        curr_doc = fetch_regulation(doc_id)
        prior_doc = fetch_regulation(prior_doc_id)
        self.callbacks.on_tool_call(trace_id, "doc_fetcher", (time.time() - t_tool) * 1000.0)

        # Tool 2: clause_parser
        t_parse = time.time()
        curr_clauses = split_clauses(curr_doc.get("content", ""))
        self.callbacks.on_tool_call(trace_id, "clause_parser", (time.time() - t_parse) * 1000.0)

        # Write to blackboard
        self.blackboard.write(case_id, "new_doc", curr_doc, "RegulationMonitor", trace_id)
        self.blackboard.write(case_id, "prior_doc", prior_doc, "RegulationMonitor", trace_id)
        self.blackboard.write(case_id, "clauses", curr_clauses, "RegulationMonitor", trace_id)

        latency_ms = (time.time() - t0) * 1000.0
        self.callbacks.on_agent_end(trace_id, span_id, latency_ms, payload_preview=f"Fetched {len(curr_clauses)} clauses")
        return {"status": "ok", "clauses_count": len(curr_clauses)}


# CONCEPT: ADK Change Detection Agent (PRD §4.1)
class ChangeDetectionAgent:
    """Computes clause-level diff between prior and current regulation versions."""

    def __init__(self, blackboard: BlackboardStore):
        self.blackboard = blackboard
        self.callbacks = make_callbacks("ChangeDetection", framework="adk")

    def run(self, case_id: str, trace_id: str) -> List[Dict[str, Any]]:
        t0 = time.time()
        span_id = self.callbacks.on_agent_start(trace_id, "Computing regulatory diff")

        docs = self.blackboard.read(case_id, ["new_doc", "prior_doc"], "ChangeDetection", trace_id)
        old_text = docs.get("prior_doc", {}).get("content", "")
        new_text = docs.get("new_doc", {}).get("content", "")

        t_diff = time.time()
        changes = diff_versions(old_text, new_text)
        self.callbacks.on_tool_call(trace_id, "diff_tool", (time.time() - t_diff) * 1000.0)

        self.blackboard.write(case_id, "diff", changes, "ChangeDetection", trace_id)

        latency_ms = (time.time() - t0) * 1000.0
        self.callbacks.on_agent_end(trace_id, span_id, latency_ms, payload_preview=f"Found {len(changes)} changes")
        return changes


# CONCEPT: ADK SME Profile Agent (PRD §4.1)
class SMEProfileAgent:
    """Retrieves SME parameters and memory from SME database."""

    def __init__(self, blackboard: BlackboardStore):
        self.blackboard = blackboard
        self.callbacks = make_callbacks("SMEProfile", framework="adk")

    def run(self, case_id: str, trace_id: str, sme_id: str) -> Dict[str, Any]:
        t0 = time.time()
        span_id = self.callbacks.on_agent_start(trace_id, f"Loading profile for {sme_id}")

        t_sme = time.time()
        profile_data = get_profile(sme_id)
        self.callbacks.on_tool_call(trace_id, "sme_db", (time.time() - t_sme) * 1000.0)

        self.blackboard.write(case_id, "sme_profile", profile_data, "SMEProfile", trace_id)

        latency_ms = (time.time() - t0) * 1000.0
        self.callbacks.on_agent_end(trace_id, span_id, latency_ms, payload_preview=f"SME: {profile_data.get('name')}")
        return profile_data


# CONCEPT: ADK Impact Analysis Agent with ReAct & Agentic RAG (PRD §4.1, §5.3)
class ImpactAnalysisAgent:
    """
    Evaluates regulatory changes against SME parameters using the ReAct pattern:
    Thought -> Action (vector_search tool) -> Observation -> Verdict.
    """

    def __init__(self, blackboard: BlackboardStore):
        self.blackboard = blackboard
        self.callbacks = make_callbacks("ImpactAnalysis", framework="adk")

    def run(
        self,
        case_id: str,
        trace_id: str
    ) -> ImpactVerdict:
        t0 = time.time()
        span_id = self.callbacks.on_agent_start(trace_id, "Evaluating impact using ReAct reasoning")

        # Read Blackboard inputs
        bb_data = self.blackboard.read(
            case_id,
            ["diff", "sme_profile", "new_doc"],
            "ImpactAnalysis",
            trace_id
        )
        diff_list = bb_data.get("diff", [])
        sme = bb_data.get("sme_profile", {})

        sme_turnover_cr = sme.get("aato_crore", 0.0)
        sme_turnover_rs = sme_turnover_cr * 10_000_000.0
        einvoice_status = sme.get("einvoice_enabled", False)

        # ReAct Step 1: Tool Call (Agentic RAG vector search)
        t_rag = time.time()
        rag_hits = search(query="turnover limit threshold e-invoice", k=2)
        self.callbacks.on_tool_call(trace_id, "vector_search", (time.time() - t_rag) * 1000.0)

        # ReAct Step 2: Thought & Reasoning Prompt
        prompt = f"""
        Role: Regulatory Impact Expert for Indian GST.
        Method: ReAct (Thought -> Action -> Observation -> Verdict).

        Thought: Compare SME turnover with the newly lowered threshold in the regulation diff.
        Observation from tools:
        - SME: {sme.get('name')} | Turnover: {sme_turnover_cr} Cr | E-inv Enabled: {einvoice_status}
        - Regulation Changes: {json.dumps(diff_list)}
        - Retrieved Clauses: {json.dumps(rag_hits)}

        Determine:
        1. verdict: impacted | not_impacted | ambiguous
        2. confidence: float between 0.0 and 1.0
        3. reasoning_summary: concise factual justification.
        """

        llm_resp = llm_client.generate(
            prompt=prompt,
            system_instruction="You are ReguGuard Impact Analysis Agent using ReAct reasoning. Respond in strict JSON.",
            response_format="json"
        )
        self.callbacks.on_model_call(
            trace_id,
            model_name=llm_resp["model"],
            latency_ms=llm_resp["latency_ms"],
            tokens_in=llm_resp["tokens_in"],
            tokens_out=llm_resp["tokens_out"],
            payload_preview="ReAct impact verdict generated"
        )

        try:
            parsed = json.loads(llm_resp["content"])
            verdict_str = parsed.get("verdict", "ambiguous")
            confidence = float(parsed.get("confidence", 0.85))
            summary = parsed.get("reasoning_summary", "Threshold change analyzed.")
        except Exception:
            threshold_new = None
            for c in diff_list:
                if c.get("threshold_new"):
                    threshold_new = c.get("threshold_new")
                    break

            if threshold_new and sme_turnover_rs >= threshold_new and not einvoice_status:
                verdict_str = "impacted"
                confidence = 0.95
                summary = f"SME AATO of {sme_turnover_cr} Cr exceeds the new statutory limit of {threshold_new/1e7} Cr."
            elif threshold_new and sme_turnover_rs < threshold_new:
                verdict_str = "not_impacted"
                confidence = 0.95
                summary = f"SME AATO of {sme_turnover_cr} Cr is below the threshold of {threshold_new/1e7} Cr."
            else:
                verdict_str = "ambiguous"
                confidence = 0.60
                summary = "Requires human verification of SME operations."

        verdict = ImpactVerdict(
            verdict=verdict_str,
            reasoning_summary=summary,
            changes_considered=[ClauseChange(**c) for c in diff_list] if diff_list else [],
            confidence=min(max(confidence, 0.0), 1.0)
        )

        # Write verdict to blackboard
        self.blackboard.write(case_id, "impact_verdict", verdict.model_dump(), "ImpactAnalysis", trace_id)

        latency_ms = (time.time() - t0) * 1000.0
        self.callbacks.on_agent_end(trace_id, span_id, latency_ms, payload_preview=f"Verdict: {verdict.verdict}")
        return verdict


# CONCEPT: Fixed Sequential Multi-Agent Topology (PRD §5.3 - Final Choice)
class ReguGuardPipeline:
    """
    Fixed Sequential Pipeline:
    Manager (RunPlan) -> Regulation Monitor -> Change Detection -> SME Profile -> Impact Analysis (ReAct)
    """

    def __init__(self, blackboard: Optional[BlackboardStore] = None):
        self.blackboard = blackboard or BlackboardStore()
        self.manager = ManagerAgent(self.blackboard)
        self.monitor = RegulationMonitorAgent(self.blackboard)
        self.change_detection = ChangeDetectionAgent(self.blackboard)
        self.sme_profile = SMEProfileAgent(self.blackboard)
        self.impact_agent = ImpactAnalysisAgent(self.blackboard)

    def run_adk_pipeline(
        self,
        case_id: str,
        trace_id: str,
        doc_id: str,
        prior_doc_id: str,
        sme_id: str,
        run_config: Optional[RunConfig] = None
    ) -> Dict[str, Any]:
        """Runs the fixed sequential ADK agent group in exact order."""
        # 1. Manager Planning
        self.manager.run(case_id, trace_id, doc_id, prior_doc_id, sme_id)

        # 2. Regulation Monitor
        self.monitor.run(case_id, trace_id, doc_id, prior_doc_id)

        # 3. Change Detection
        self.change_detection.run(case_id, trace_id)

        # 4. SME Profile
        self.sme_profile.run(case_id, trace_id, sme_id)

        # 5. Impact Analysis (ReAct)
        verdict = self.impact_agent.run(case_id, trace_id)

        return {
            "case_id": case_id,
            "trace_id": trace_id,
            "verdict": verdict,
            "blackboard_state": self.blackboard.read(case_id, agent="pipeline_observer", trace_id=trace_id)
        }
