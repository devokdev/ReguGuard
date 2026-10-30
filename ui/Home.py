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

        # ---------------------------------------------------------------------
        # NEW: REGULATORY IMPACT & NOTIFICATION COMPARISON VISUALIZATIONS
        # ---------------------------------------------------------------------
        st.divider()
        st.markdown("### 📊 Regulatory Threshold & Notification Comparison Analytics")
        st.caption("Visualizing current SME financials versus Gazette Notification changes (2020–2026 Target).")

        viz_col1, viz_col2 = st.columns(2)

        sme_turnover = selected_sme["aato_crore"]
        prior_threshold = 10.0
        new_threshold = 2.0 if doc_choice == "notif_synthetic_01" else 5.0

        with viz_col1:
            st.markdown("##### 1. Statutory Threshold vs SME Turnover (Crores INR)")
            fig_thresh = go.Figure()
            fig_thresh.add_trace(go.Bar(
                x=["Prior Law (17/2022)", "Target Law (" + doc_choice + ")", selected_sme["name"]],
                y=[prior_threshold, new_threshold, sme_turnover],
                marker_color=["#8C857B", "#B4532A", "#2B4C3F" if sme_turnover > new_threshold else "#4E6B3A"],
                text=[f"₹{prior_threshold} Cr", f"₹{new_threshold} Cr", f"₹{sme_turnover} Cr"],
                textposition="auto"
            ))
            fig_thresh.add_hline(
                y=new_threshold,
                line_dash="dash",
                line_color="#B4532A",
                annotation_text=f"New Legal Ceiling: ₹{new_threshold} Cr",
                annotation_position="top right"
            )
            fig_thresh.update_layout(
                paper_bgcolor="#EDE9E0",
                plot_bgcolor="#E4DFD3",
                margin=dict(l=20, r=20, t=30, b=20),
                height=320,
                yaxis_title="Turnover (₹ Crores)",
                font=dict(family="sans-serif", size=12)
            )
            st.plotly_chart(fig_thresh, use_container_width=True)

        with viz_col2:
            st.markdown("##### 2. 2020–2026 Gazette E-Invoicing Roadmap")
            timeline_years = ["2020 (Oct)", "2021 (Apr)", "2022 (Apr)", "2022 (Oct)", "2023 (Aug)", "2026 (Oct)"]
            timeline_limits = [500, 50, 20, 10, 5, 2]
            fig_time = go.Figure()
            fig_time.add_trace(go.Scatter(
                x=timeline_years,
                y=timeline_limits,
                mode="lines+markers+text",
                name="Statutory Limit",
                line=dict(color="#B4532A", width=3),
                marker=dict(size=10, color="#1C1B19"),
                text=[f"₹{l} Cr" for l in timeline_limits],
                textposition="top right"
            ))
            fig_time.add_hline(
                y=sme_turnover,
                line_dash="dot",
                line_color="#2B4C3F",
                annotation_text=f"{selected_sme['name']} (₹{sme_turnover} Cr)",
                annotation_position="bottom left"
            )
            fig_time.update_layout(
                paper_bgcolor="#EDE9E0",
                plot_bgcolor="#E4DFD3",
                margin=dict(l=20, r=20, t=30, b=20),
                height=320,
                yaxis_type="log",
                yaxis_title="Turnover Limit (Log Scale Cr)",
                font=dict(family="sans-serif", size=12)
            )
            st.plotly_chart(fig_time, use_container_width=True)

        # 12 SME Cohort Impact Matrix
        st.markdown("##### 3. All 12 SME Cohort Impact Comparison (Before vs After Law Change)")
        cohort_df = pd.DataFrame(smes)
        cohort_df["Old Rule Status (10 Cr)"] = cohort_df["aato_crore"].apply(
            lambda x: "Mandated" if x > 10.0 else "Exempt"
        )
        cohort_df["New Law Status (" + str(new_threshold) + " Cr)"] = cohort_df.apply(
            lambda r: "Exempt" if r["gst_registration"] == "composition" or r["aato_crore"] <= new_threshold else "MANDATED",
            axis=1
        )
        cohort_df["Delta Status"] = cohort_df.apply(
            lambda r: "🚨 Newly Impacted" if (r["Old Rule Status (10 Cr)"] == "Exempt" and r["New Law Status (" + str(new_threshold) + " Cr)"] == "MANDATED")
            else ("⚠️ Already Mandated" if r["Old Rule Status (10 Cr)"] == "Mandated" else "✅ Remained Exempt"),
            axis=1
        )

        st.dataframe(
            cohort_df[["sme_id", "name", "industry", "state", "aato_crore", "Old Rule Status (10 Cr)", "New Law Status (" + str(new_threshold) + " Cr)", "Delta Status"]],
            use_container_width=True
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

