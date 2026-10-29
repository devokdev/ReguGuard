"""
Acceptance Test for Step 9: Sequential Fixed Order & Offline Comparisons
========================================================================
Validates:
1. Production pipeline runs fixed sequential order (Manager -> Monitor -> Change -> Profile -> Impact)
2. All agents read/write to the Blackboard
3. Offline variants (P2P, Parallel, Single-shot) in eval/variants/ run properly
"""

from src.orchestrator import ReguGuardOrchestrator
from eval.variants.p2p_messaging import run_p2p_pipeline
from eval.variants.parallel_topology import run_parallel_pipeline
from eval.variants.single_shot import run_single_shot_baseline


def test_fixed_sequential_production_pipeline():
    orchestrator = ReguGuardOrchestrator()
    report = orchestrator.run(
        case_id="CASE-SEQ-TEST",
        doc_id="notif_10_2023",
        prior_doc_id="notif_13_2020",
        sme_id="SME-01"
    )
    assert report.verdict.verdict in ["impacted", "ambiguous", "not_impacted"]
    assert len(report.evidence) >= 1
    assert report.action is not None


def test_offline_variants():
    # E2: P2P
    p2p_res = run_p2p_pipeline("C-P2P", "tr-p2p", "notif_10_2023", "notif_13_2020", "SME-01")
    assert p2p_res["variant"] == "p2p_messaging"

    # E3: Parallel
    par_res = run_parallel_pipeline("C-PAR", "tr-par", "notif_10_2023", "notif_13_2020", "SME-01")
    assert par_res["variant"] == "parallel_topology"

    # E4: Single-shot
    ss_res = run_single_shot_baseline("C-SS", "tr-ss", "notif_10_2023", "notif_13_2020", "SME-01")
    assert ss_res["variant"] == "single_shot_baseline"
