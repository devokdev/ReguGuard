"""
ReguGuard Pydantic v2 Data Models & Schemas
===========================================
Defines all structured communication contracts, blackboard record payloads,
inter-agent messages, guardrail events, and final report schemas.

Single Source of Truth: PRD §7
Course: CSE3101 Agentic AI, BML Munjal University
"""

from __future__ import annotations
from datetime import date, datetime
from typing import Literal, Optional, List, Dict, Any
from pydantic import BaseModel, Field, model_validator


# CONCEPT: Product Run Configuration (PRD §5.3 & §7)
class RunConfig(BaseModel):
    """Configuration parameters specifying user persona for prompt variance and safety testing."""
    persona: Literal[
        "owner",
        "accountant",
        "consultant",
        "auditor",
        "adversarial_toxic",
        "adversarial_injection"
    ] = Field(
        default="owner",
        description="User persona defining prompt variance or adversarial testing."
    )


# CONCEPT: Regulatory Change Extraction (Clause-level Diff)
class ClauseChange(BaseModel):
    """Represents a specific clause or section modification between regulation versions."""
    change_type: Literal["added", "removed", "modified"]
    section: str = Field(description="Section or paragraph identifier, e.g., 'para 2' or 'Section 16(4)'")
    old_text: Optional[str] = None
    new_text: Optional[str] = None
    threshold_old: Optional[float] = Field(default=None, description="Old turnover/monetary threshold in rupees (INR)")
    threshold_new: Optional[float] = Field(default=None, description="New turnover/monetary threshold in rupees (INR)")
    effective_date: Optional[date | str] = Field(default=None, description="Date from which the clause is effective")


# CONCEPT: Domain Entity Model (SME Profile)
class SMEProfile(BaseModel):
    """Profile of an Indian Small & Medium Enterprise subject to GST regulations."""
    sme_id: str = Field(description="Unique SME ID e.g., 'SME-01'")
    name: str
    industry: str
    state: str = Field(description="State of registration e.g., 'Maharashtra'")
    aato_crore: float = Field(description="Annual Aggregate Turnover (AATO) in Crore INR")
    gst_registration: Literal["regular", "composition", "qrmp"] = Field(
        description="Type of GST registration"
    )
    einvoice_enabled: bool = Field(description="Whether e-invoicing is currently enabled for this SME")
    policies: List[str] = Field(default_factory=list, description="Special policy flags or operational tags")
    reporting_cadence: Literal["monthly", "quarterly"] = Field(
        description="Cadence of return filings"
    )


# CONCEPT: Reflection and Grounded Verification
class Evidence(BaseModel):
    """Grounded evidence citation verifying a regulatory claim against source text."""
    claim: str = Field(description="The factual claim made by the impact agent")
    source_doc_id: str = Field(description="Document ID where evidence is found")
    section: str = Field(description="Exact section cited")
    version: str = Field(description="Document version or notification number")
    effective_date: date = Field(description="Date when rule takes effect")
    quote: str = Field(description="Exact quote extracted from source text")
    verified: bool = Field(default=False, description="Whether the quote is verified as a true substring of source text")
    verifier_notes: str = Field(default="", description="Verification comments or critique from Skeptic agent")


# CONCEPT: Impact Reasoning Verdict
class ImpactVerdict(BaseModel):
    """Result of evaluating whether a regulatory change impacts a specific SME."""
    verdict: Literal["impacted", "not_impacted", "ambiguous"]
    reasoning_summary: str = Field(description="Step-by-step or summary justification of the decision")
    changes_considered: List[ClauseChange] = Field(default_factory=list)
    confidence: float = Field(ge=0.0, le=1.0, description="Confidence score between 0.0 and 1.0")


# CONCEPT: Action Planning & Remediation
class ActionPlan(BaseModel):
    """Prescriptive action items for the SME to maintain regulatory compliance."""
    action: str = Field(description="Description of required compliance action")
    owner: str = Field(description="Responsible role e.g., 'Accountant' or 'Tax Consultant'")
    deadline: Optional[date] = Field(default=None, description="Statutory or recommended compliance deadline")
    days_remaining: Optional[int] = Field(default=None, description="Calculated days remaining until deadline")
    priority: Literal["high", "medium", "low"] = Field(default="medium")


# CONCEPT: Observability & Metrics Tracking
class AgentMetrics(BaseModel):
    """Metrics recorded for an individual agent execution."""
    agent_name: str
    latency_s: float = Field(ge=0.0)
    tokens_in: int = Field(ge=0, default=0)
    tokens_out: int = Field(ge=0, default=0)
    cost_usd: float = Field(ge=0.0, default=0.0)
    retries: int = Field(ge=0, default=0)
    errors: int = Field(ge=0, default=0)


class RunMetrics(BaseModel):
    """Aggregate metrics for the complete multi-agent pipeline run."""
    total_latency_s: float = Field(ge=0.0)
    total_tokens: int = Field(ge=0, default=0)
    total_cost_usd: float = Field(ge=0.0, default=0.0)
    per_agent: Dict[str, AgentMetrics] = Field(default_factory=dict)
    retries: int = Field(ge=0, default=0)
    errors: int = Field(ge=0, default=0)


# CONCEPT: Structured Output & Output Guardrail (PRD §7)
class ImpactReport(BaseModel):
    """
    Final output report returned to the user or consultant.
    Every report enforces the mandatory disclaimer and headline.
    """
    case_id: str
    trace_id: str
    sme_id: str
    generated_at: datetime = Field(default_factory=datetime.utcnow)
    headline: str = Field(
        default="Potential regulatory impact detected — human review recommended",
        description="Mandatory headline per PRD §1"
    )
    verdict: ImpactVerdict
    evidence: List[Evidence] = Field(default_factory=list)
    action: Optional[ActionPlan] = None
    guardrail_flags: List[str] = Field(default_factory=list)
    disclaimer: str = Field(
        default="This note is for informational purposes and does not constitute formal legal or tax advice.",
        description="Mandatory legal disclaimer"
    )
    run_config: RunConfig
    metrics: RunMetrics

    # Business rule validation (PRD §7)
    @model_validator(mode="after")
    def validate_business_rules(self) -> ImpactReport:
        """Enforce PRD business rules:
        - If verdict is 'impacted', at least one evidence item must be verified.
          Otherwise downgrade to 'ambiguous'.
        - Guarantee headline and disclaimer are present.
        """
        # Ensure headline is accurate
        if not self.headline or "human review recommended" not in self.headline:
            self.headline = "Potential regulatory impact detected — human review recommended"

        # Check evidence grounding rule
        if self.verdict.verdict == "impacted":
            has_verified = any(ev.verified for ev in self.evidence)
            if not has_verified:
                # Downgrade to ambiguous as required by PRD §7
                self.verdict.verdict = "ambiguous"
                if "Downgraded from impacted: missing verified evidence" not in self.guardrail_flags:
                    self.guardrail_flags.append("Downgraded from impacted: missing verified evidence")
                # Cap confidence to at most 0.5 when downgraded
                if self.verdict.confidence > 0.5:
                    self.verdict.confidence = 0.5

        return self


# CONCEPT: Observability & OpenTelemetry-style Spans (PRD §8.3)
class TraceEvent(BaseModel):
    """Granular trace span captured by the callback system."""
    trace_id: str
    span_id: str
    parent_span_id: Optional[str] = None
    agent: str
    framework: Literal["adk", "crewai", "mcp", "system"]
    kind: Literal[
        "agent_start",
        "agent_end",
        "model_call",
        "tool_call",
        "guardrail",
        "blackboard_read",
        "blackboard_write",
        "a2a",
        "error"
    ]
    ts_start: datetime
    ts_end: datetime
    latency_ms: float = Field(ge=0.0)
    tokens_in: int = Field(ge=0, default=0)
    tokens_out: int = Field(ge=0, default=0)
    cost_usd: float = Field(ge=0.0, default=0.0)
    payload_preview: str = Field(default="", max_length=1000)
    status: Literal["ok", "blocked", "error", "retry"] = "ok"


# CONCEPT: Cross-framework A2A Envelope (PRD §5.2)
class A2AEnvelope(BaseModel):
    """Payload contract passed across frameworks over the Agent-to-Agent protocol."""
    case_id: str
    trace_id: str
    blackboard_ref: Optional[str] = None
    action_type: str = Field(description="Requested action, e.g., 'verify_evidence' or 'plan_action'")
    payload: Dict[str, Any] = Field(default_factory=dict)

