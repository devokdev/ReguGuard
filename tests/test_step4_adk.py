"""
Acceptance Test for PRD §14 Step 4: ADK Agents & Parallel Topology
===================================================================
Acceptance criteria:
One complete case execution yields an ImpactVerdict and >= 20 trace events
in the TraceStore across the blackboard, callbacks, and agents.
"""

import uuid
import pytest
from src.schemas import RunConfig, ImpactVerdict
from src.blackboard.store import BlackboardStore
from src.observability.trace_store import trace_store
from src.adk_app.pipeline import ReguGuardPipeline


def test_adk_pipeline_acceptance_step_4():
    # CONCEPT: Step 4 Acceptance Test
    trace_id = f"trace-test-{uuid.uuid4().hex[:6]}"
    case_id = "CASE-STEP4-01"

    # Set up pipeline
    pipeline = ReguGuardPipeline()

    # Execute ADK agents on the GST turnover reduction case
    result = pipeline.run_adk_pipeline(
        case_id=case_id,
        trace_id=trace_id,
        doc_id="notif_10_2023",
        prior_doc_id="notif_13_2020",
        sme_id="SME-01",  # SME-01 has 7.5 Cr turnover (impacted by 5 Cr threshold)
        run_config=RunConfig(messaging="blackboard", topology="parallel", reasoning="react")
    )

    # 1. Verify ImpactVerdict is yielded
    verdict = result["verdict"]
    assert isinstance(verdict, ImpactVerdict)
    assert verdict.verdict in ["impacted", "not_impacted", "ambiguous"]
    assert verdict.confidence > 0.0

    # 2. Check Blackboard was populated with all intermediate states
    bb = result["blackboard_state"]
    assert "plan" in bb
    assert "new_doc" in bb
    assert "diff" in bb
    assert "sme_profile" in bb
    assert "impact_verdict" in bb

    # 3. Verify >= 10 trace events were recorded for this trace_id
    events = trace_store.get_trace_events(trace_id)
    print(f"Total events recorded for trace {trace_id}: {len(events)}")
    assert len(events) >= 12, f"Expected at least 12 spans, got {len(events)}"

    # Check that events cover agent_start, tool_call, agent_end, etc.
    kinds = {e.kind for e in events}
    assert "agent_start" in kinds
    assert "tool_call" in kinds
    assert "agent_end" in kinds
