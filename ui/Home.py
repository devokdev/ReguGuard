"""
ReguGuard Streamlit Web Application
===================================
CSE3101 Agentic AI Coursework Showcase
Multipage UI with Concept Lens, Live Pipeline Graph, Blackboard Inspector, and Trace Explorer.

Single Source of Truth: PRD §3, §9
"""

import json
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

from src.schemas import RunConfig
from src.mcp_servers.sme_db import list_smes
from src.mcp_servers.doc_fetcher import list_new_documents
from src.orchestrator import ReguGuardOrchestrator
from src.blackboard.store import BlackboardStore
from src.observability.trace_store import trace_store

# Page Setup
st.set_page_config(
    page_title="ReguGuard — Regulatory Impact Multi-Agent AI",
    page_icon="🛡️",
    layout="wide"
)

# Initialize singletons in session state
if "blackboard" not in st.session_state:
    st.session_state.blackboard = BlackboardStore()
if "orchestrator" not in st.session_state:
    st.session_state.orchestrator = ReguGuardOrchestrator(st.session_state.blackboard)
if "last_report" not in st.session_state:
    st.session_state.last_report = None

# Top Branding Header
st.title("🛡️ ReguGuard — Regulatory Impact Analysis for SMEs")
st.caption("CSE3101 Agentic AI · BML Munjal University · Yash Yadav (230664), Kartavya Dev (230653), Nancy (230640)")

# Sidebar Navigation
page = st.sidebar.radio(
    "Navigation",
    [
        "Analyze Regulation",
        "Concept Map & Lens",
        "Blackboard Inspector",
        "Trace Explorer",
        "Guardrail Lab",
        "Coverage Matrix"
    ]
)

# -----------------------------------------------------------------------------
# PAGE 1: ANALYZE REGULATION
# -----------------------------------------------------------------------------
if page == "Analyze Regulation":
    st.markdown("### 📋 Run Multi-Agent Assessment")

    col_sme, col_doc, col_cfg = st.columns(3)
    smes = list_smes()
    docs = list_new_documents()

    with col_sme:
        sme_choice = st.selectbox(
            "Select SME Profile",
            options=[s["sme_id"] for s in smes],
            format_func=lambda x: f"{x}: {next((s['name'] for s in smes if s['sme_id'] == x), '')}"
        )
        selected_sme = next(s for s in smes if s["sme_id"] == sme_choice)
        st.info(f"**Turnover:** ₹{selected_sme['aato_crore']} Cr | **E-invoicing:** {selected_sme['einvoice_enabled']}")

    with col_doc:
        doc_choice = st.selectbox(
            "Select Target Notification",
            options=[d["doc_id"] for d in docs],
            format_func=lambda x: f"{x}: {next((d['title'] for d in docs if d['doc_id'] == x), '')}"
        )
        prior_doc_id = "notif_13_2020"

    with col_cfg:
        topology = st.selectbox("Topology", ["parallel", "sequential", "hierarchical"], index=0)
        messaging = st.selectbox("Messaging", ["blackboard", "p2p"], index=0)
        reasoning = st.selectbox("Reasoning", ["react", "cot", "single_shot"], index=0)

    # Concept Lens Chips
    st.markdown(
        """
        **Active Architecture Chips:** 
        `ParallelAgent (ADK)` · `Blackboard (SQLite/MCP)` · `ReAct (LLM)` · `Reflection (CrewAI)` · `A2A Cross-Framework`
        """
    )

    if st.button("🚀 Run ReguGuard Impact Pipeline", type="primary"):
        with st.spinner("Multi-agent system reasoning across ADK and CrewAI..."):
            case_id = f"CASE-{doc_choice}-{sme_choice}"
            cfg = RunConfig(messaging=messaging, topology=topology, reasoning=reasoning)
            report = st.session_state.orchestrator.run(
                case_id=case_id,
                doc_id=doc_choice,
                prior_doc_id=prior_doc_id,
                sme_id=sme_choice,
                run_config=cfg
            )
            st.session_state.last_report = report
            st.success("Analysis Complete!")

    # Display Report
    if st.session_state.last_report:
        rep = st.session_state.last_report
        st.divider()

        # Mandatory Headline & Disclaimer (PRD §7)
        st.warning(f"### ⚠️ {rep.headline}")
        st.caption(f"🛡️ Disclaimer: {rep.disclaimer}")

        m1, m2, m3, m4 = st.columns(4)
        m1.metric("Verdict", rep.verdict.verdict.upper())
        m2.metric("Confidence", f"{rep.verdict.confidence * 100:.1f}%")
        m3.metric("Latency", f"{rep.metrics.total_latency_s:.2f} s")
        m4.metric("Tokens In/Out", rep.metrics.total_tokens)

        st.markdown(f"**Reasoning Summary:** {rep.verdict.reasoning_summary}")

        # Grounded Evidence Table
        st.markdown("#### 📜 Grounded Evidence (Substring Verified)")
        if rep.evidence:
            ev_data = [
                {
                    "Section": e.section,
                    "Verified Substring Quote": e.quote,
                    "Source Doc": e.source_doc_id,
                    "Verified?": "✅ Pass" if e.verified else "❌ Fail",
                    "Verifier Notes": e.verifier_notes
                }
                for e in rep.evidence
            ]
            st.table(pd.DataFrame(ev_data))

        # Prescriptive Action Plan
        if rep.action:
            st.markdown("#### 📌 Prescriptive Action Plan")
            st.info(
                f"**Action:** {rep.action.action}\n\n"
                f"**Owner:** {rep.action.owner} | **Deadline:** {rep.action.deadline} | **Priority:** {rep.action.priority.upper()}"
            )

        # Download Report JSON
        st.download_button(
            "📥 Download Validated ImpactReport JSON",
            data=rep.model_dump_json(indent=2),
            file_name=f"{rep.case_id}_report.json",
            mime="application/json"
        )

# -----------------------------------------------------------------------------
# PAGE 2: CONCEPT MAP & LENS (PRD §3)
# -----------------------------------------------------------------------------
elif page == "Concept Map & Lens":
    st.markdown("### 🎓 Agentic AI Course Concept Map (CSE3101 Handout Mapping)")
    st.markdown("Every component in ReguGuard demonstrates core concepts from the syllabus:")

    concepts = [
        {"Topic": "Intelligent Agents & Reasoning Layer", "Implementation": "ADK Agents & Groq/Llama LLM client", "File": "src/adk_app/pipeline.py"},
        {"Topic": "ReAct Reasoning", "Implementation": "Thought/Action/Observation pattern in Impact Agent", "File": "src/adk_app/pipeline.py"},
        {"Topic": "Reflection & Critique", "Implementation": "CrewAI Evidence Verifier + Skeptic retry loop", "File": "src/crew_app/flow.py"},
        {"Topic": "Tool Use / Function Calling", "Implementation": "6 FastMCP tool servers + blackboard server", "File": "src/mcp_servers/"},
        {"Topic": "Planning & Coordinator", "Implementation": "ManagerAgent RunPlan generation", "File": "src/adk_app/pipeline.py"},
        {"Topic": "Agentic RAG", "Implementation": "ChromaDB version-aware temporal retrieval", "File": "src/mcp_servers/vector_search.py"},
        {"Topic": "Multi-agent Topologies", "Implementation": "Parallel vs Sequential vs Hierarchical", "File": "src/adk_app/pipeline.py"},
        {"Topic": "Cross-framework A2A", "Implementation": "ADK remote invoking CrewAI over A2AEnvelope", "File": "src/crew_app/flow.py"},
        {"Topic": "Blackboard Shared State", "Implementation": "Versioned SQLite store with access logging", "File": "src/blackboard/store.py"},
        {"Topic": "Observability & Callbacks", "Implementation": "OpenTelemetry-style TraceEvents & heatmaps", "File": "src/observability/"},
        {"Topic": "Guardrails & Safety", "Implementation": "3-layer input, tool, output & PII masking", "File": "src/guardrails/"}
    ]
    st.dataframe(pd.DataFrame(concepts), use_container_width=True)

# -----------------------------------------------------------------------------
# PAGE 3: BLACKBOARD INSPECTOR
# -----------------------------------------------------------------------------
elif page == "Blackboard Inspector":
    st.markdown("### 🗄️ Blackboard Shared State Inspector")
    case_input = st.text_input("Enter Case ID to inspect:", value="CASE-STEP5-A2A")
    if st.button("Inspect History"):
        snaps = st.session_state.blackboard.snapshot(case_input)
        if snaps:
            st.success(f"Retrieved {len(snaps)} versioned entries for {case_input}:")
            st.json(snaps)
        else:
            st.warning("No entries found for this Case ID.")

# -----------------------------------------------------------------------------
# PAGE 4: TRACE EXPLORER
# -----------------------------------------------------------------------------
elif page == "Trace Explorer":
    st.markdown("### 🔍 Trace Explorer & Heatmaps (Criterion 5 & 9)")
    matrix = trace_store.get_agent_metrics_matrix()
    if matrix:
        st.markdown("#### Agent Execution Latency & Metrics Heatmap")
        df_matrix = pd.DataFrame(matrix).T
        st.dataframe(df_matrix)

        fig = px.bar(
            df_matrix.reset_index(),
            x="index",
            y="avg_latency_ms",
            title="Average Latency per Agent (ms)",
            labels={"index": "Agent", "avg_latency_ms": "Latency (ms)"}
        )
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("No trace events recorded yet. Run an analysis from the Analyze tab!")

# -----------------------------------------------------------------------------
# PAGE 5: GUARDRAIL LAB
# -----------------------------------------------------------------------------
elif page == "Guardrail Lab":
    st.markdown("### 🛡️ Guardrail Lab (5 Attack Presets)")
    st.write("Demonstrates 3-layer deterministic guardrails and PII masking.")

# -----------------------------------------------------------------------------
# PAGE 6: COVERAGE MATRIX
# -----------------------------------------------------------------------------
elif page == "Coverage Matrix":
    st.markdown("### 📊 11 Professor Criteria Coverage Matrix")
    criteria_data = [
        {"Criterion #": 1, "Requirement": "Blackboard mandatory + compare messaging", "Status": "MET", "Evidence": "src/blackboard/store.py"},
        {"Criterion #": 2, "Requirement": ">=2 external tools via MCP", "Status": "MET", "Evidence": "6 servers in src/mcp_servers/"},
        {"Criterion #": 3, "Requirement": "Structured output via Pydantic", "Status": "MET", "Evidence": "src/schemas.py (ImpactReport)"},
        {"Criterion #": 4, "Requirement": "Agentic design patterns compared", "Status": "MET", "Evidence": "Parallel / ReAct in src/adk_app/"},
        {"Criterion #": 5, "Requirement": "Callback monitoring; heatmap per agent", "Status": "MET", "Evidence": "src/observability/callbacks.py"},
        {"Criterion #": 6, "Requirement": "A2A cross-framework (ADK <-> CrewAI)", "Status": "MET", "Evidence": "src/crew_app/flow.py"},
        {"Criterion #": 7, "Requirement": "CrewAI + ADK only", "Status": "MET", "Evidence": "ADK pipeline & CrewAI flow"},
        {"Criterion #": 8, "Requirement": "Guardrails, prompt variance/personas", "Status": "IN PROGRESS", "Evidence": "Step 7"},
        {"Criterion #": 9, "Requirement": "Observability, provenance", "Status": "MET", "Evidence": "src/observability/trace_store.py"},
        {"Criterion #": 10, "Requirement": "End-to-end evaluation, cost/time", "Status": "MET", "Evidence": "tests/ & RunMetrics"},
        {"Criterion #": 11, "Requirement": "Cloud deployment", "Status": "PREPARED", "Evidence": "Dockerfile & deploy script"}
    ]
    st.dataframe(pd.DataFrame(criteria_data), use_container_width=True)

