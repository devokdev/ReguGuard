"""
Unit Tests for ReguGuard Schemas (PRD §7)
=========================================
Acceptance Test for Step 1:
Validates all Pydantic models, default values, serialization,
business rules, and boundary conditions.
"""

from datetime import date, datetime
import pytest
from pydantic import ValidationError

from src.schemas import (
    RunConfig,
    ClauseChange,
    SMEProfile,
    Evidence,
    ImpactVerdict,
    ActionPlan,
    AgentMetrics,
    RunMetrics,
    ImpactReport,
    TraceEvent,
    A2AEnvelope,
)


def test_run_config_persona_validation():
    # CONCEPT: Test persona configuration
    config = RunConfig()
    assert config.persona == "owner"

    custom = RunConfig(persona="auditor")
    assert custom.persona == "auditor"

    with pytest.raises(ValidationError):
        RunConfig(persona="invalid_persona")


def test_clause_change_creation():
    change = ClauseChange(
        change_type="modified",
        section="para 2",
        old_text="Turnover limit is 10 crore",
        new_text="Turnover limit is 5 crore",
        threshold_old=100000000.0,
        threshold_new=50000000.0,
        effective_date=date(2023, 8, 1)
    )
    assert change.section == "para 2"
    assert change.threshold_new == 50000000.0


def test_sme_profile_creation():
    sme = SMEProfile(
        sme_id="SME-01",
        name="Acme Steels Pvt Ltd",
        industry="Manufacturing",
        state="Maharashtra",
        aato_crore=7.5,
        gst_registration="regular",
        einvoice_enabled=False,
        policies=["b2b_sales"],
        reporting_cadence="monthly"
    )
    assert sme.aato_crore == 7.5
    assert not sme.einvoice_enabled


def test_evidence_verification():
    evidence = Evidence(
        claim="Threshold reduced to 5 crore",
        source_doc_id="notif_10_2023",
        section="para 2",
        version="v1.0",
        effective_date=date(2023, 8, 1),
        quote="registered person whose aggregate turnover exceeds five crore rupees",
        verified=True,
        verifier_notes="Matched source text exactly"
    )
    assert evidence.verified is True
    assert "five crore" in evidence.quote


def test_impact_verdict_confidence_bounds():
    verdict = ImpactVerdict(
        verdict="impacted",
        reasoning_summary="SME turnover is 7.5 Cr which exceeds new 5 Cr threshold.",
        confidence=0.95
    )
    assert verdict.confidence == 0.95

    with pytest.raises(ValidationError):
        ImpactVerdict(
            verdict="impacted",
            reasoning_summary="Bad confidence",
            confidence=1.5
        )


def test_impact_report_business_rule_downgrade():
    unverified_evidence = Evidence(
        claim="Threshold changed",
        source_doc_id="doc1",
        section="sec 1",
        version="1.0",
        effective_date=date(2023, 8, 1),
        quote="some text",
        verified=False
    )

    report = ImpactReport(
        case_id="C-001",
        trace_id="trace-123",
        sme_id="SME-01",
        verdict=ImpactVerdict(
            verdict="impacted",
            reasoning_summary="Looks impacted",
            confidence=0.90
        ),
        evidence=[unverified_evidence],
        run_config=RunConfig(),
        metrics=RunMetrics(
            total_latency_s=2.5,
            total_tokens=1500,
            total_cost_usd=0.001
        )
    )

    assert report.verdict.verdict == "ambiguous"
    assert report.verdict.confidence <= 0.5
    assert any("Downgraded" in flag for flag in report.guardrail_flags)
    assert "human review recommended" in report.headline


def test_impact_report_verified_evidence_preserves_impacted():
    verified_evidence = Evidence(
        claim="Threshold changed",
        source_doc_id="doc1",
        section="sec 1",
        version="1.0",
        effective_date=date(2023, 8, 1),
        quote="valid quote",
        verified=True
    )

    report = ImpactReport(
        case_id="C-002",
        trace_id="trace-124",
        sme_id="SME-01",
        verdict=ImpactVerdict(
            verdict="impacted",
            reasoning_summary="Verified impact",
            confidence=0.92
        ),
        evidence=[verified_evidence],
        run_config=RunConfig(),
        metrics=RunMetrics(
            total_latency_s=1.8,
            total_tokens=1200,
            total_cost_usd=0.0008
        )
    )

    assert report.verdict.verdict == "impacted"
    assert report.verdict.confidence == 0.92


def test_trace_event_schema():
    now = datetime.utcnow()
    event = TraceEvent(
        trace_id="trace-abc",
        span_id="span-1",
        agent="manager",
        framework="adk",
        kind="agent_start",
        ts_start=now,
        ts_end=now,
        latency_ms=12.5,
        tokens_in=100,
        tokens_out=20,
        cost_usd=0.00005,
        status="ok"
    )
    assert event.agent == "manager"
    assert event.framework == "adk"


def test_a2a_envelope_schema():
    envelope = A2AEnvelope(
        case_id="CASE-99",
        trace_id="TRACE-99",
        blackboard_ref="cases/CASE-99",
        action_type="verify_evidence",
        payload={"claim": "turnover lowered"}
    )
    assert envelope.action_type == "verify_evidence"
    assert envelope.payload["claim"] == "turnover lowered"
