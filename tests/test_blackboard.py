"""
Unit Tests for Blackboard Store & MCP Server (PRD §14 Step 2 Acceptance Test)
=============================================================================
Acceptance criteria:
An ADK process and a CrewAI process (simulated concurrent writers/readers)
each read the other's writes accurately, verify versioning and read logs.
"""

import tempfile
from pathlib import Path
import pytest
from src.blackboard.store import BlackboardStore
from src.blackboard.mcp_server import bb_read, bb_write, bb_snapshot


@pytest.fixture
def temp_store():
    with tempfile.TemporaryDirectory() as tmpdir:
        db_path = Path(tmpdir) / "test_blackboard.db"
        yield BlackboardStore(db_path=db_path)


def test_blackboard_write_read_versioning(temp_store):
    # CONCEPT: Shared state blackboard write & read
    entry1 = temp_store.write(
        case_id="CASE-001",
        key="status",
        value="started",
        agent="manager",
        trace_id="tr-1"
    )
    assert entry1.version == 1

    entry2 = temp_store.write(
        case_id="CASE-001",
        key="status",
        value="in_progress",
        agent="change_detection",
        trace_id="tr-1"
    )
    assert entry2.version == 2

    # Read latest
    data = temp_store.read(case_id="CASE-001", keys=["status"], agent="adk_manager")
    assert data["status"] == "in_progress"


def test_cross_agent_read_writes(temp_store):
    # Acceptance Test: ADK process and CrewAI process read each other's writes
    # 1. ADK Agent (Impact Analysis) writes verdict to blackboard
    temp_store.write(
        case_id="CASE-GST-01",
        key="impact_verdict",
        value={"verdict": "impacted", "confidence": 0.95},
        agent="adk_impact_agent",
        trace_id="trace-gst"
    )

    # 2. CrewAI Agent (Evidence Verification) reads ADK's verdict
    read_by_crew = temp_store.read(
        case_id="CASE-GST-01",
        keys=["impact_verdict"],
        agent="crewai_evidence_agent",
        trace_id="trace-gst"
    )
    assert read_by_crew["impact_verdict"]["verdict"] == "impacted"

    # 3. CrewAI Agent writes verified evidence back to blackboard
    temp_store.write(
        case_id="CASE-GST-01",
        key="evidence",
        value=[{"section": "para 2", "verified": True, "quote": "exceeds five crore rupees"}],
        agent="crewai_evidence_agent",
        trace_id="trace-gst"
    )

    # 4. ADK Agent reads CrewAI's verified evidence
    read_by_adk = temp_store.read(
        case_id="CASE-GST-01",
        keys=["evidence"],
        agent="adk_manager",
        trace_id="trace-gst"
    )
    assert len(read_by_adk["evidence"]) == 1
    assert read_by_adk["evidence"][0]["verified"] is True


def test_blackboard_snapshot_and_access_counts(temp_store):
    # Test snapshot history
    temp_store.write("C-1", "doc", "v1.pdf", "monitor")
    temp_store.write("C-1", "doc", "v2.pdf", "monitor")
    temp_store.read("C-1", ["doc"], "change_detection")

    snapshot = temp_store.snapshot("C-1")
    assert len(snapshot) == 2
    assert snapshot[0]["value"] == "v1.pdf"
    assert snapshot[1]["value"] == "v2.pdf"

    matrix = temp_store.get_access_counts()
    assert matrix["monitor"]["doc"]["writes"] == 2
    assert matrix["change_detection"]["doc"]["reads"] == 1


def test_mcp_blackboard_tools():
    # Test MCP tool functions directly
    res_w = bb_write(
        case_id="MCP-01",
        key="sample_key",
        value="sample_value",
        agent="adk_agent"
    )
    assert res_w["status"] == "ok"

    res_r = bb_read(
        case_id="MCP-01",
        keys=["sample_key"],
        agent="crewai_agent"
    )
    assert res_r["sample_key"] == "sample_value"

    snap = bb_snapshot("MCP-01")
    assert len(snap) >= 1
