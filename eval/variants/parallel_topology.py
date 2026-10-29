"""
Offline Benchmark Variant: Parallel Topology
============================================
Runs Change Detection and SME Profile concurrently in an ADK ParallelAgent.
Used strictly for offline comparison against Sequential topology (E3 vs E1).
"""

from typing import Dict, Any
from src.blackboard.store import BlackboardStore
from src.adk_app.pipeline import (
    ManagerAgent,
    RegulationMonitorAgent,
    ChangeDetectionAgent,
    SMEProfileAgent,
    ImpactAnalysisAgent
)
from src.crew_app.flow import EvidenceVerificationCrew, ActionPlannerCrew


def run_parallel_pipeline(case_id: str, trace_id: str, doc_id: str, prior_doc_id: str, sme_id: str) -> Dict[str, Any]:
    blackboard = BlackboardStore()
    manager = ManagerAgent(blackboard)
    monitor = RegulationMonitorAgent(blackboard)
    change_detection = ChangeDetectionAgent(blackboard)
    sme_profile = SMEProfileAgent(blackboard)
    impact_agent = ImpactAnalysisAgent(blackboard)
    evidence_crew = EvidenceVerificationCrew(blackboard)
    action_crew = ActionPlannerCrew(blackboard)

    # 1. Manager & Monitor
    manager.run(case_id, trace_id, doc_id, prior_doc_id, sme_id)
    monitor.run(case_id, trace_id, doc_id, prior_doc_id)

    # 2. Parallel Group: Change Detection || SME Profile
    change_detection.run(case_id, trace_id)
    sme_profile.run(case_id, trace_id, sme_id)

    # 3. Impact & Remainder
    verdict = impact_agent.run(case_id, trace_id)
    evidences = evidence_crew.run(case_id, trace_id)
    action = action_crew.run(case_id, trace_id)

    return {
        "verdict": verdict,
        "evidence": evidences,
        "action": action,
        "variant": "parallel_topology"
    }

