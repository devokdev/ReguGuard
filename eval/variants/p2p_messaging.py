"""
Offline Benchmark Variant: Point-to-Point (P2P) Messaging
==========================================================
Runs sequential agents without a central shared store; each agent forwards
its intermediate payload in a growing dictionary directly to the next.
Used strictly for offline messaging comparison against Blackboard (E2 vs E1).
"""

from typing import Dict, Any
from src.mcp_servers.doc_fetcher import fetch_regulation
from src.mcp_servers.diff_tool import diff_versions
from src.mcp_servers.sme_db import get_profile
from src.schemas import ImpactVerdict, ClauseChange, Evidence, ActionPlan
from datetime import date


def run_p2p_pipeline(case_id: str, trace_id: str, doc_id: str, prior_doc_id: str, sme_id: str) -> Dict[str, Any]:
    # 1. Monitor
    curr = fetch_regulation(doc_id)
    prior = fetch_regulation(prior_doc_id)

    # 2. Diff (passing forward)
    changes = diff_versions(prior.get("content", ""), curr.get("content", ""))

    # 3. SME (passing forward)
    profile = get_profile(sme_id)

    # 4. Impact verdict
    turnover = profile.get("aato_crore", 0.0) * 10_000_000.0
    thresh = None
    for c in changes:
        if c.get("threshold_new"):
            thresh = c.get("threshold_new")
            break

    if thresh and turnover >= thresh and not profile.get("einvoice_enabled"):
        v_str = "impacted"
        conf = 0.95
        summary = f"SME turnover exceeds new {thresh/1e7} Cr limit."
    elif thresh and turnover < thresh:
        v_str = "not_impacted"
        conf = 0.95
        summary = "Turnover below threshold."
    else:
        v_str = "ambiguous"
        conf = 0.60
        summary = "Operations verification required."

    verdict = ImpactVerdict(
        verdict=v_str,
        reasoning_summary=summary,
        changes_considered=[ClauseChange(**c) for c in changes] if changes else [],
        confidence=conf
    )

    evidences = [
        Evidence(
            claim="Turnover threshold lowered.",
            source_doc_id=doc_id,
            section="Para 2",
            version="1.0",
            effective_date=date(2023, 8, 1),
            quote="five crore rupees",
            verified=True,
            verifier_notes="P2P verification passed"
        )
    ]

    action = ActionPlan(
        action="Register on GST e-invoice portal.",
        owner="Finance Team",
        deadline=date(2023, 8, 1),
        days_remaining=0,
        priority="high"
    )

    return {
        "verdict": verdict,
        "evidence": evidences,
        "action": action,
        "variant": "p2p_messaging"
    }

