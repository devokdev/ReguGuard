"""
Acceptance Test for PRD §14 Step 6: ImpactReport & Minimal UI Execution
=======================================================================
Acceptance criteria:
- Complete end-to-end execution generates a valid ImpactReport.
- Fast, deterministic pipeline run passes all business rule validations.
"""

import pytest
from src.schemas import ImpactReport
from src.orchestrator import ReguGuardOrchestrator


def test_orchestrator_step_6():
    # CONCEPT: Step 6 Acceptance Test
    orchestrator = ReguGuardOrchestrator()
    report = orchestrator.run(
        case_id="CASE-STEP6-DEMO",
        doc_id="notif_10_2023",
        prior_doc_id="notif_13_2020",
        sme_id="SME-01"
    )

    assert isinstance(report, ImpactReport)
    assert report.case_id == "CASE-STEP6-DEMO"
    assert report.sme_id == "SME-01"
    assert "human review recommended" in report.headline
    assert len(report.evidence) >= 1
    assert report.verdict.verdict in ["impacted", "ambiguous", "not_impacted"]
    assert report.metrics.total_latency_s > 0.0

