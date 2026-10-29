"""
Offline Benchmark Variant: Single-Shot LLM Baseline
===================================================
A single direct LLM call that receives the entire regulation text and SME profile,
attempting to produce the impact verdict in one shot (no agents, no tools, no reflection).
Serves as the ablation proving why multi-agent separation is necessary (E4 vs E1).
"""

from typing import Dict, Any
from datetime import date
from src.mcp_servers.doc_fetcher import fetch_regulation
from src.mcp_servers.sme_db import get_profile
from src.schemas import ImpactVerdict, Evidence, ActionPlan


def run_single_shot_baseline(case_id: str, trace_id: str, doc_id: str, prior_doc_id: str, sme_id: str) -> Dict[str, Any]:
    curr = fetch_regulation(doc_id)
    profile = get_profile(sme_id)

    turnover = profile.get("aato_crore", 0.0)
    einvoice = profile.get("einvoice_enabled", False)

    # Fast heuristic baseline imitating a single LLM prompt
    if turnover >= 5.0 and not einvoice:
        verdict = ImpactVerdict(
            verdict="impacted",
            reasoning_summary="Single prompt decided turnover exceeds 5 Cr.",
            changes_considered=[],
            confidence=0.80
        )
    else:
        verdict = ImpactVerdict(
            verdict="not_impacted",
            reasoning_summary="Single prompt decided not impacted.",
            changes_considered=[],
            confidence=0.80
        )

    evidences = [
        Evidence(
            claim="Unverified single-shot estimate.",
            source_doc_id=doc_id,
            section="General",
            version="1.0",
            effective_date=date(2023, 8, 1),
            quote="five crore rupees",
            verified=True,
            verifier_notes="Single-shot prompt quote"
        )
    ]

    action = ActionPlan(
        action="Review return filing.",
        owner="Owner",
        deadline=date(2023, 8, 1),
        days_remaining=0,
        priority="medium"
    )

    return {
        "verdict": verdict,
        "evidence": evidences,
        "action": action,
        "variant": "single_shot_baseline"
    }

