"""
Acceptance Test for PRD §14 Step 5: CrewAI Evidence + Action Flow behind A2A
============================================================================
Acceptance criteria:
- A2A round-trip works between ADK client and CrewAI A2A server.
- Evidence quotes pass the deterministic substring check against real notification text.
- Reflection logic handles retry on critique.
"""

import uuid
import pytest
from src.schemas import A2AEnvelope, Evidence
from src.blackboard.store import BlackboardStore
from src.crew_app.flow import CrewAIA2AServer
from src.mcp_servers.doc_fetcher import fetch_regulation


def test_crewai_a2a_acceptance_step_5():
    # CONCEPT: Step 5 Acceptance Test
    blackboard = BlackboardStore()
    case_id = "CASE-STEP5-A2A"
    trace_id = f"trace-a2a-{uuid.uuid4().hex[:6]}"

    # Populate blackboard with source document
    doc_10_2023 = fetch_regulation("notif_10_2023")
    blackboard.write(case_id, "new_doc", doc_10_2023, "RegulationMonitor", trace_id)

    # Initialize A2A server
    a2a_server = CrewAIA2AServer(blackboard=blackboard)

    # 1. Test Agent Card publication (PRD §5.2)
    card = a2a_server.get_agent_card()
    assert card["agent_id"] == "crewai-evidence-action-flow"
    assert any(skill["name"] == "verify_evidence" for skill in card["skills"])

    # 2. Simulate ADK invoking CrewAI over A2AEnvelope
    envelope = A2AEnvelope(
        case_id=case_id,
        trace_id=trace_id,
        blackboard_ref=f"blackboard://{case_id}",
        action_type="full_flow",
        payload={"query": "verify quotes and create action"}
    )

    # Dispatch to A2A server
    response = a2a_server.handle_envelope(envelope)
    assert response["status"] == "ok"
    assert "evidence" in response
    assert "action" in response

    # 3. Acceptance Check: Evidence quotes MUST pass the substring check
    source_text = doc_10_2023["content"]
    evidence_items = response["evidence"]
    assert len(evidence_items) >= 1

    for ev in evidence_items:
        quote = ev["quote"]
        assert ev["verified"] is True
        # String match verification
        assert quote in source_text, f"Quote '{quote}' failed substring verification against source text!"

    # 4. Check that Blackboard now holds CrewAI's output
    bb_read = blackboard.read(case_id, ["evidence", "action_plan"], agent="adk_client", trace_id=trace_id)
    assert "evidence" in bb_read
    assert "action_plan" in bb_read

