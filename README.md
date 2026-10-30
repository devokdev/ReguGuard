# ReguGuard — Autonomous Multi-Agent Regulatory Impact Analysis System

[![Course](https://img.shields.io/badge/Course-CSE3101%20Agentic%20AI-blue.svg)](https://www.bmu.edu.in)
[![Institution](https://img.shields.io/badge/University-BML%20Munjal%20University-orange.svg)](https://www.bmu.edu.in)
[![Tests](https://img.shields.io/badge/Tests-35%20Passed%20(100%25)-brightgreen.svg)]()
[![Architecture](https://img.shields.io/badge/Architecture-Blackboard%20%7C%20Sequential%20%7C%20ReAct-darkgreen.svg)]()
[![Frameworks](https://img.shields.io/badge/Frameworks-Google%20ADK%20%2B%20CrewAI%20(A2A)-purple.svg)]()
[![Inference](https://img.shields.io/badge/Inference-Groq%20Cloud%20(Ultra--Low%20Latency)-red.svg)](https://groq.com)

> **Academic Coursework:** CSE3101: Agentic AI, School of Engineering & Technology, BML Munjal University  
> **Team:** Yash Yadav (230664), Kartavya Dev (230653), Nancy (230640)  
> **Project Scope:** Multi-Agent System (MAS) for Autonomous Regulatory Impact Triage, Financial Liability Computation, and Audit Provenance in Indian SMEs  
> **Current Deliverable:** Phase 2 Vertical Slice Prototype & Comprehensive Academic Audit  

---

## 📑 Table of Contents
1. [Executive Overview & Problem Statement](#-executive-overview--problem-statement)
2. [Why Multi-Agent Systems for Regulatory Compliance?](#-why-multi-agent-systems-for-regulatory-compliance)
3. [Core Architectural Blueprint](#-core-architectural-blueprint)
   - [The SQLite Blackboard Pattern](#1-the-sqlite-blackboard-pattern)
   - [Sequential Pipeline Topology](#2-sequential-pipeline-topology)
   - [FastMCP Decoupled Tool Servers](#3-fastmcp-decoupled-tool-servers)
   - [Cross-Framework Agent-to-Agent (A2A) Protocol](#4-cross-framework-agent-to-agent-a2a-protocol)
4. [The 7-Agent Production Roster](#-the-7-agent-production-roster)
5. [Multi-Year Target Notification Corpus (2020–2027)](#-multi-year-target-notification-corpus-20202027)
6. [Synthetic SME Corpus & 48-Case Benchmark Grid](#-synthetic-sme-corpus--48-case-benchmark-grid)
7. [User Interfaces & Visualizations](#-user-interfaces--visualizations)
   - [React 19 Editorial Dashboard (Port 5173)](#1-react-19-editorial-dashboard-port-5173)
   - [The 5 Regulatory Analysis Modules](#2-the-5-regulatory-analysis-modules)
   - [FastAPI Orchestrator Backend (Port 8000)](#3-fastapi-orchestrator-backend-port-8000)
   - [Streamlit Debugger UI (Port 8501)](#4-streamlit-debugger-ui-port-8501)
8. [Observability, Safety Guardrails & Provenance](#-observability-safety-guardrails--provenance)
   - [3-Layer Deterministic Guardrails](#1-3-layer-deterministic-guardrails)
   - [OpenTelemetry TraceStore](#2-opentelemetry-tracestore)
   - [DAG Provenance Graph](#3-dag-provenance-graph)
9. [Academic Evaluation & Rubric Mapping](#-academic-evaluation--rubric-mapping)
   - [Phase 2 Evaluation Sheet (C6–C10 Rubric)](#phase-2-evaluation-sheet-c6c10-rubric)
   - [The 11 Handout Criteria Checklist](#the-11-handout-criteria-checklist)
10. [Individual Team Member Contributions & Viva Defense](#-individual-team-member-contributions--viva-defense)
11. [Installation & Quickstart Guide](#-installation--quickstart-guide)
12. [Repository Directory Structure](#-repository-directory-structure)
13. [Legal Disclaimer](#-legal-disclaimer)

---

## 🌟 Executive Overview & Problem Statement

Small and Medium Enterprises (SMEs) represent the backbone of the Indian economy, contributing over 30% of national GDP. However, they face a severe compliance bottleneck under the Goods and Services Tax (GST) regime. The Central Board of Indirect Taxes and Customs (CBIC) regularly issues gazette notifications, circulars, and amendments with zero transitional buffer:

```
2020: ₹500 Cr (Phase 1) ──► 2021: ₹100 Cr (Phase 2) ──► 2022: ₹50 Cr / ₹20 Cr (Phases 3-4)
                                                                 │
2027: ₹1 Cr (Phase 7 Proj) ◄── 2026: ₹2 Cr (Phase 6 Proj) ◄── 2023: ₹5 Cr (Phase 5)
```

### The SME Dilemma
* **Dense Regulatory Jargon:** Gazette notifications cite obscure legal provisions (e.g., Section 16(4), Section 48(4), Section 122(1) of the CGST Act) that junior in-house accountants cannot interpret against existing ERP systems.
* **Prohibitive Advisory Costs:** Tier-2 and Tier-3 SMEs cannot afford retainer fees for Big-4 or Tier-1 tax consultancies to review every 30-page gazette circular.
* **Devastating Non-Compliance Penalties:**
  * **Section 122(1) CGST Act:** 100% of tax evaded or ₹10,000 per invalid non-e-invoiced transaction (whichever is higher).
  * **Section 125 CGST Act:** General non-compliance penalties up to ₹25,000.
  * **Section 16(4) CGST Act:** Outright blockage of Input Tax Credit (ITC) for downstream buyers, causing immediate cancellation of vendor contracts.

**ReguGuard** solves this by providing an end-to-end autonomous multi-agent pipeline. It ingests newly gazetted notifications, computes aggregate turnover thresholds, performs ERP gap analysis, calculates deterministic tax liabilities, subjects all findings to a multi-agent reflection critique, and outputs an executive CFO briefing note alongside an actionable technical roadmap.

---

## 💡 Why Multi-Agent Systems for Regulatory Compliance?

In legal and financial technology, single-prompt LLMs fail disastrously:
1. **Hallucinated Statutory Citations:** Standard LLMs invent non-existent notification numbers or quote outdated turnover limits with high confidence.
2. **Compound Arithmetic Failures:** LLMs struggle to reliably compute tiered compound penalties across hundreds of monthly B2B invoices.
3. **No Separation of Concerns:** Asking one model to parse legal text, compare ERP schemas, calculate tax deltas, verify evidence, and draft a report results in an un-auditable "black box."

### ReguGuard's Multi-Agent Philosophy
ReguGuard enforces the core rule: **"An agent must never grade its own homework."**
* **Role Specialization:** Extraction is separated from Applicability, which is separated from Tax Computation, which is separated from Evidence Critique.
* **Deterministic Provenance:** Every claim in the final report is backed by an exact substring citation, notification clause ID, and OpenTelemetry trace span.
* **Reflection & Skeptic Critique:** Before an impact verdict is finalized, a dedicated CrewAI Skeptic agent actively attempts to falsify the finding by searching for legal exemptions (e.g., SEZ zero-rating, multi-GSTIN aggregate turnover).

---

## 🏛️ Core Architectural Blueprint

ReguGuard implements a production-grade, modular multi-agent system based on four core architectural pillars:

```
                      [ Official Gazette Notification (CBIC) ]
                                         │
                                         ▼
                         ┌───────────────────────────────┐
                         │   01. Input Guardrail Gate   │
                         │  (Injection & PII Redaction)  │
                         └───────────────┬───────────────┘
                                         │
                                         ▼
                         ┌───────────────────────────────┐
                         │     02. Manager Agent (ADK)   │
                         │      (Emits Shared RunPlan)   │
                         └───────────────┬───────────────┘
                                         │
         Writes / Reads State            ▼           Writes / Reads State
 ┌─────────────────────────────────────────────────────────────────────────────┐
 │                    SQLITE BLACKBOARD (blackboard.db)                        │
 │  • Case ID & Trace ID          • Extracted Gazette Clauses & Thresholds     │
 │  • SME Profile & Balance Sheet • Impact Verdict & Penalty Calculations      │
 │  • CrewAI Reflection Critique • Read/Write Audit Access Frequency Log       │
 └───────▲───────────────────────────────▲─────────────────────────────▲───────┘
         │                               │                             │
         │ FastMCP Tools                 │ ReAct CoT                   │ A2A Envelope
         ▼                               ▼                             ▼
┌───────────────────┐         ┌─────────────────────┐       ┌──────────────────────┐
│  Regulation       │         │  Impact Analysis    │       │  CrewAI Reflection   │
│  Monitor Agent    │         │  Agent (ADK)        │       │  Flow (A2A Server)   │
│  • doc_fetcher    │         │  • Turnover check   │       │  • Verifier Agent    │
│  • clause_parser  │         │  • Sec 122(1) Math  │       │  • Skeptic Critic    │
│  • diff_tool      │         │  • ITC Blockage     │       │  • Action Planner    │
└───────────────────┘         └─────────────────────┘       └──────────────────────┘
                                         │
                                         ▼
                         ┌───────────────────────────────┐
                         │   07. Output Guardrail Gate   │
                         │ (Provenance Check & Sanitize) │
                         └───────────────┬───────────────┘
                                         │
                                         ▼
                   [ Validated ImpactReport & CFO Action Deck ]
```

### 1. The SQLite Blackboard Pattern
Instead of chaotic, non-deterministic peer-to-peer agent chat, ReguGuard uses a **centralized, transactional Blackboard** (`src/blackboard/store.py`):
* **Atomic State Persistence:** All intermediate outputs (clauses, diffs, profile records, verdicts, risk scores) are committed to a versioned SQLite database (`blackboard.db`).
* **Zero Dropped State:** If an agent encounters a network timeout or API rate limit, the pipeline can resume from the exact checkpoint on the blackboard without re-running earlier agents.
* **Access Frequency Heatmap:** The blackboard logs every read and write operation, generating an access matrix to prove clean architectural separation.

### 2. Sequential Pipeline Topology
Agents execute in a strict, causal order where downstream agents depend on the validated artifacts of upstream agents:
$$\text{Manager} \longrightarrow \text{Monitor} \longrightarrow \text{Diff} \longrightarrow \text{Profile} \longrightarrow \text{Impact (ReAct)} \longrightarrow \text{Reflection (CrewAI)} \longrightarrow \text{Report}$$

### 3. FastMCP Decoupled Tool Servers
ReguGuard connects agents to tools using Anthropic's **Model Context Protocol (MCP)** via lightweight FastMCP servers (`src/mcp_servers/`):
1. **`doc_fetcher`**: Retrieves raw gazette texts from `data/corpus/`.
2. **`clause_parser`**: Regex and NLP extractor for legal sections, dates, and turnover limits.
3. **`diff_tool`**: Generates clause-level semantic diffs between two regulatory versions.
4. **`sme_db`**: SQLite database managing 12 realistic Indian SME financial profiles.
5. **`vector_search`**: ChromaDB vector store indexing CBIC notifications and CGST rules.
6. **`deadline_calc`**: Non-LLM deterministic calendar calculator for statutory enforcement windows.

### 4. Cross-Framework Agent-to-Agent (A2A) Protocol
ReguGuard pioneers hybrid orchestration by bridging **Google ADK** (pipeline management and extraction) with **CrewAI** (critique and reflection):
* Communication occurs over standard **`A2AEnvelope`** payloads (`src/schemas.py`).
* The ADK Impact Agent packages draft findings into an A2A envelope; the CrewAI A2A server parses the envelope, runs the Verifier-Skeptic critique loop, and returns the audited evidence record over HTTP/RPC.

---

## 🤖 The 7-Agent Production Roster

| # | Agent Name | Framework | Architecture Pattern | Core Objective & Logic | Primary Tools Used |
|---|---|---|---|---|---|
| **1** | **Manager / Coordinator** | Google ADK | Orchestrator / Planner | Initializes pipeline run, parses input parameters, assigns case ID, and emits structured `RunPlan`. | Writes to Blackboard |
| **2** | **Regulation Monitor** | Google ADK | Tool-Using Extractor | Ingests CBIC gazette notifications, strips legalese boilerplate, and extracts effective enforcement dates and turnover limits. | `doc_fetcher`, `clause_parser` (MCP) |
| **3** | **Change Detection** | Google ADK | Semantic Differencing | Compares incoming notification against historical baseline in ChromaDB; produces structured diff of statutory additions and threshold drops. | `diff_tool`, `vector_search` (MCP) |
| **4** | **SME Profile Agent** | Google ADK | Memory Retriever | Loads the target firm's industry, 3-year turnover history, PAN/GSTIN structure, export status, and existing ERP software. | `sme_db` (MCP) |
| **5** | **Impact Analysis Agent** | Google ADK | **ReAct** (Reason + Act) | Evaluates aggregate turnover against statutory threshold; computes deterministic penalties under Section 122(1) and Section 125; assesses ITC risk. | ReAct CoT + Groq LLM |
| **6** | **Evidence Verification Agent** | CrewAI | **Reflection Loop** (Verifier + Skeptic) | **Dual-agent critique:** Verifier checks raw ChromaDB text; Skeptic actively challenges the penalty math and tests SEZ/turnover exemptions. | CrewAI Flow (`src/crew_app/flow.py`) |
| **7** | **Action Planning & Report Agent** | CrewAI | Synthesis & Scheduling | Computes remaining statutory implementation window; generates executive CFO briefing note and technical ERP checklist. | `deadline_calc` (MCP) |

---

## 📚 Multi-Year Target Notification Corpus (2020–2027)

ReguGuard includes a comprehensive, multi-year corpus of official CBIC gazette notifications stored in `data/corpus/` and cataloged in `data/corpus/MANIFEST.csv`:

| Notification ID | CBIC Gazette Ref | Issue Date | Effective Date | E-Invoicing Threshold | Statutory Impact & Legal Scope |
|---|---|---|---|---|---|
| `notif_13_2020` | Central Tax 13/2020 | 21-Mar-2020 | 01-Oct-2020 | **₹500 Crore** | Phase 1 launch for massive enterprises; mandatory QR code and IRN generation. |
| `notif_05_2021` | Central Tax 05/2021 | 08-Mar-2021 | 01-Apr-2021 | **₹100 Crore** | Phase 2 threshold reduction capturing large manufacturing and corporate entities. |
| `notif_01_2022` | Central Tax 01/2022 | 24-Feb-2022 | 01-Apr-2022 | **₹50 Crore** | Phase 3 reduction bringing mid-sized enterprises into the e-invoicing net. |
| `notif_17_2022` | Central Tax 17/2022 | 01-Aug-2022 | 01-Oct-2022 | **₹20 Crore** | Phase 4 expansion capturing commercial wholesalers and regional distributors. |
| `notif_10_2023` | Central Tax 10/2023 | 10-May-2023 | 01-Aug-2023 | **₹5 Crore** | Phase 5 critical threshold: millions of Indian SMEs and MSMEs mandated. |
| `notif_04_2024` | Central Tax 04/2024 | 05-Jan-2024 | 01-Apr-2024 | **₹5 Crore (Window)** | Enforces strict 30-day time limit for reporting invoices to the IRP portal. |
| `notif_25_2025` | Central Tax 25/2025 | 14-Jul-2025 | 01-Oct-2025 | **₹5 Crore (Rules)** | Expands e-way bill reconciliation and real-time GSTR-1 automated population. |
| `notif_target_2026` | Proposed Policy Mandate | 15-Jan-2026 | 01-Apr-2026 | **₹2 Crore** | Projected Phase 6 threshold capturing micro-enterprises and service firms. |
| `notif_target_2027` | Forecasted Universal Mandate | 20-Jan-2027 | 01-Apr-2027 | **₹1 Crore** | Projected Phase 7 universal B2B e-invoicing for virtually all registered entities. |

---

## 🏭 Synthetic SME Corpus & 48-Case Benchmark Grid

To evaluate ReguGuard with rigorous statistical repeatability without leaking real corporate tax records, we engineered a deterministic dataset using fixed seed `42`:

### 12 Diverse Indian SME Personas (`data/smes/smes.json`)
* **Automotive Components Manufacturing:** Turnover ₹18 Cr to ₹48 Cr; uses legacy desktop Tally ERP; heavy B2B invoice volume.
* **FMCG Wholesale & Distribution:** Turnover ₹8 Cr to ₹24 Cr; multi-branch operations with multiple GSTINs under a single PAN.
* **B2B IT & Professional Consulting:** Turnover ₹4 Cr to ₹12 Cr; high-margin services; mixed domestic supplies and zero-rated SEZ exports.
* **Textile & Garment Manufacturing:** Turnover ₹6 Cr to ₹16 Cr; composite supplies with seasonal turnover surges near threshold borders.

### 48 Labelled Test Cases (`data/cases/cases.jsonl`)
* **Direct Impact Cases (24):** SME aggregate turnover clearly exceeds threshold; triggers mandatory ERP migration and INV-01 schema compliance.
* **No-Impact Clean Cases (12):** SME turnover comfortably below statutory limit; system issues clear non-applicability certificate.
* **Edge Case Scenarios (12):**
  * *Near-Threshold Borderlines:* Turnover at ₹4.95 Cr vs ₹5.00 Cr threshold.
  * *PAN Aggregate Turnover:* Firm argues single-state turnover is ₹3 Cr, but combined PAN turnover across 3 states is ₹7 Cr (statutorily liable under CGST Section 2(6)).
  * *Zero-Rated SEZ Supplies:* Clarifies that SEZ supplies count towards aggregate turnover calculation even if exempt from IGST.

---

## 🖥️ User Interfaces & Visualizations

ReguGuard features two frontends designed for distinct operational workflows:

### 1. React 19 Editorial Dashboard (Port 5173)
Built with React 19, Vite, and TypeScript adhering to an **Editorial Paper & Ink** design philosophy:
* **Color Palette:** Warm matte paper background (`#EDE9E0`), deep typewriter ink text (`#1C1B19`), subtle dividing rules (`#CFC9BC`), and burnt oxide accent (`#B4532A`).
* **Typography:** Self-hosted `Newsreader` for elegant serif headings, `IBM Plex Sans` for UI readability, and `IBM Plex Mono` for tabular figures and IDs.

### 2. The 5 Regulatory Analysis Modules (`RegulatoryComparisonVisualizer.tsx`)
1. **Threshold vs. SME Comparison Bar:** Live interactive bar comparing the selected SME's aggregate turnover against the statutory limit of the active gazette notification.
2. **2020–2027 Regulatory Roadmap:** Chronological interactive timeline displaying the step-by-step threshold reductions over 7 years.
3. **12 SME Cohort Matrix:** Grid view evaluating the compliance exposure across all 12 SME profiles simultaneously for any given notification.
4. **Agent Execution Waterfall:** Visual timeline showing execution start times, individual latencies, token consumption, and blackboard commits for each agent.
5. **Isolated Agent Inspector:** Deep-dive inspector displaying exact input prompts, tool calls, raw LLM reasoning, and output payloads for any single agent.

### 3. FastAPI Orchestrator Backend (Port 8000)
* REST API exposing `/api/run`, `/api/blackboard`, `/api/smes`, and `/api/notifications`.
* Real-time Server-Sent Events (SSE) streaming live agent state updates to the UI via `/api/runs/{id}/events`.
* Interactive OpenAPI Swagger documentation available at `http://127.0.0.1:8000/docs`.

### 4. Streamlit Debugger UI (Port 8501)
* Python-based dashboard located at `ui/Home.py` providing rapid pipeline smoke-testing, raw database inspection, and manual case dispatch.

---

## 🛡️ Observability, Safety Guardrails & Provenance

### 1. 3-Layer Deterministic Guardrails (`src/guardrails/engine.py`)
* **Layer 1: Input Injection & Sanitization:** Scans user prompts for jailbreaks, prompt overrides, and toxic keywords.
* **Layer 2: PII Redaction:** Automatically scrubs sensitive corporate identifiers (GSTINs, PANs, phone numbers, email addresses) before forwarding data to LLM inference.
* **Layer 3: Statutory Bounds Checking:** Enforces statutory limits on penalty calculations (e.g., verifying that a Section 122(1) penalty never exceeds 100% of the computed tax amount).

### 2. OpenTelemetry TraceStore (`src/observability/trace_store.py`)
* Logs structured spans (`TraceEvent`) to an SQLite database (`traces.db`).
* Captures start/end timestamps, latency in milliseconds, prompt/completion token counts, Groq API costs, and tool invocations per agent.

### 3. DAG Provenance Graph (`src/observability/provenance.py`)
* Constructs a Directed Acyclic Graph (DAG) establishing exact causal provenance.
* Guarantees that every finding in the final report cites the exact gazette paragraph, notification number, and blackboard commit ID.
* Exports verifiable JSON and Markdown audit packs for compliance controllers and auditors.

---

## 📊 Academic Evaluation & Rubric Mapping

### Phase 2 Evaluation Sheet (C6–C10 Rubric)

| Code | Evaluation Criteria | Max Marks | ReguGuard Exact Evidence & Implementation |
|---|---|:---:|---|
| **C6** | **Progress vs Plan** | **5** | **80% PRD Complete.** All 7 agents operational end-to-end. FastMCP tool servers and SQLite Blackboard active. React Vite dashboard and CrewAI reflection built early. |
| **C7** | **Technical Understanding** | **5** | Hybrid MAS architecture: Google ADK for parallel extraction, CrewAI for reflection, A2A envelope protocol, and SQLite Blackboard state store. |
| **C8** | **Requirements Met (Actual Approach)** | **10** | **18 of 22 PRD requirements met.** Supports 9 notifications (2020–2027), 12 SME profiles, 48 labelled cases, and deterministic Section 122(1) tax calculations. |
| **C9** | **Working Documentation** | **5** | PRD v2.1, OpenAPI documentation on `:8000/docs`, and **35 of 35 pytest automated tests passing** (`pytest -v`). |
| **C10** | **Individual Contribution (Viva)** | **5** | Distinct module ownership across team: Yash (Reflection/A2A/Visualizers), Kartavya (Blackboard/MCP/Pipeline), Nancy (Tax/Risk/Guardrails). |
| **TOTAL** | **Phase 2 Subtotal** | **30** | **Full prototype demonstration ready on Port 5173 and Port 8000.** |

### The 11 Handout Criteria Checklist

| # | Criterion | Technical Implementation in ReguGuard | Source File | Automated Test |
|---|---|---|---|---|
| **1** | Blackboard Architecture | Shared SQLite `BlackboardStore` with atomic versioning and read/write access frequency logging. | [`src/blackboard/store.py`](src/blackboard/store.py) | `tests/test_blackboard.py` |
| **2** | $\ge 2$ Tools via MCP | 6 standalone FastMCP tool servers (`doc_fetcher`, `diff_tool`, `clause_parser`, `vector_search`, `sme_db`, `deadline_calc`). | [`src/mcp_servers/`](src/mcp_servers/) | `tests/test_mcp_tools.py` |
| **3** | Structured Output via Pydantic | Pydantic v2 `ImpactReport` with deterministic business rules and mandatory audit sections. | [`src/schemas.py`](src/schemas.py) | `tests/test_schemas.py` |
| **4** | Agentic Patterns Compared | Sequential ReAct production pipeline compared offline against Parallel topology, P2P messaging, and Single-shot LLM. | [`eval/variants/`](eval/variants/) | `tests/test_step9_topologies.py` |
| **5** | Callbacks & Heatmaps | Lifecycle monitoring spans (`TraceEvent`) recording latency, tokens, cost, and agent $\times$ key access heatmaps. | [`src/observability/callbacks.py`](src/observability/callbacks.py) | `tests/test_step4_adk.py` |
| **6** | Cross-Framework A2A | ADK remote client invoking CrewAI Flow using official Agent Cards and `A2AEnvelope` payloads. | [`src/crew_app/flow.py`](src/crew_app/flow.py) | `tests/test_step5_a2a.py` |
| **7** | Framework Restrictions | Google ADK + CrewAI only; zero unauthorized agent frameworks (no LangChain, LangGraph, AutoGen). | Entire codebase | `tests/` |
| **8** | Guardrails & Safety | 3-layer deterministic rules: prompt injection defense, toxic language filtering, PII masking, and tool bounds. | [`src/guardrails/engine.py`](src/guardrails/engine.py) | `tests/test_step7_guardrails.py` |
| **9** | Observability & Provenance | Trace IDs, Spans, DAG Provenance Graph, and exportable JSON/Markdown audit packs. | [`src/observability/provenance.py`](src/observability/provenance.py) | `tests/test_steps11_12.py` |
| **10** | End-to-End Evaluation | 48 labelled cases, 4 benchmark configs (E1–E4, 192 runs), confusion matrix, and pure SVG boxplots. | [`eval/run_benchmark.py`](eval/run_benchmark.py) | `eval/` |
| **11** | Cloud Deployment | Multi-process container (`Dockerfile`) running FastAPI orchestrator and static web frontend via Supervisord for Cloud Run. | [`Dockerfile`](Dockerfile) | `deploy/cloudrun.sh` |

---

## 👥 Individual Team Member Contributions & Viva Defense

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                          REGUGUARD CORE TEAM                                │
├──────────────────────────┬──────────────────────────┬───────────────────────┤
│    Yash Yadav (230664)   │   Kartavya Dev (230653)  │     Nancy (230640)    │
│  Reflection & A2A Lead   │  Architecture & MCP Lead │ Risk, Tax & Eval Lead │
└──────────────────────────┴──────────────────────────┴───────────────────────┘
```

### 1. Yash Yadav (230664)
* **Core Responsibilities:** Verification, Reflection Loop, A2A Communication Bridge, Regulatory Corpus, and React Visualizers.
* **Technical Deliverables:**
  * Implemented the **CrewAI Reflection Flow** (`src/crew_app/flow.py`) featuring a Verifier agent and a Skeptic critic to eliminate hallucinated tax citations.
  * Designed the **A2A Envelope Protocol** bridging Google ADK with CrewAI.
  * Built the **9-notification CBIC gazette corpus (2020–2027)** and wired `doc_fetcher` / `clause_parser`.
  * Designed and coded the **5 interactive visualizer tabs** in `RegulatoryComparisonVisualizer.tsx`.
* **Viva Defense Topics:** Why multi-agent reflection is necessary for legal/financial compliance; how the A2A envelope protocol enables type-safe cross-framework communication; how visual explainers ensure transparency for SME owners.

### 2. Kartavya Dev (230653)
* **Core Responsibilities:** Shared State Store, FastMCP Tool Microservices, Pipeline Orchestration, and FastAPI Backend.
* **Technical Deliverables:**
  * Architected the **SQLite Blackboard Store** (`src/blackboard/store.py`) with atomic commits and access tracking.
  * Engineered the **6 standalone FastMCP tool servers** (`src/mcp_servers/`).
  * Built the **Sequential Pipeline Orchestrator** (`src/orchestrator.py`) and FastAPI REST/SSE backend.
  * Developed the core layout, D3 SVG FlowThread, and state strips for the Vite React frontend.
* **Viva Defense Topics:** Trade-offs between Blackboard architecture and peer-to-peer messaging; concurrency and transaction isolation in shared state; SSE streaming for agent execution.

### 3. Nancy (230640)
* **Core Responsibilities:** Tax Calculation Engine, Risk Scoring, Guardrails, TraceStore Observability, and 48-Case Benchmark Suite.
* **Technical Deliverables:**
  * Implemented the **statutory tax calculation engine** for Section 122(1) / Section 125 penalties and ITC blockage risk.
  * Built the **3-layer deterministic guardrail engine** (`src/guardrails/engine.py`) with PII redaction and injection filtering.
  * Configured **TraceStore** (`src/observability/trace_store.py`) for OpenTelemetry-style span tracking.
  * Designed the **48-case labelled benchmark dataset** and offline evaluation harness (`eval/run_benchmark.py`).
* **Viva Defense Topics:** Mathematical bounds on statutory tax penalties; deterministic vs LLM-based safety guardrails; statistical methodology of the 48-case benchmark grid.

---

## 🚀 Installation & Quickstart Guide

### 1. Prerequisites
* **Python:** 3.11+
* **Node.js:** v18+ (tested on Node 20 & 23)
* **Groq Cloud API Key:** High-speed inference account

### 2. Installation
```bash
# Clone the repository
git clone https://github.com/devokdev/ReguGuard.git
cd ReguGuard

# Install Python backend dependencies
pip install -r requirements.txt

# Install React frontend dependencies
cd ui
npm install
npm run build
cd ..
```

### 3. Environment Configuration
Create or update `.env` in the project root:
```ini
GROQ_API_KEY=gsk_your_groq_api_key_here
GENERATOR_MODEL=qwen/qwen-2.5-72b-instruct
JUDGE_MODEL=llama-3.3-70b-versatile
TEMPERATURE=0.1
BLACKBOARD_DB_PATH=blackboard.db
TRACES_DB_PATH=traces.db
```

### 4. Running the Complete System
Open two terminal windows:

**Terminal 1 — FastAPI Backend Orchestrator (Port 8000):**
```bash
python -m uvicorn src.api.main:app --host 0.0.0.0 --port 8000 --reload
```
*API docs available at: `http://127.0.0.1:8000/docs`*

**Terminal 2 — React Editorial Frontend (Port 5173):**
```bash
cd ui
npx vite --host 0.0.0.0 --port 5173
```
*Web dashboard available at: `http://127.0.0.1:5173`*

**Optional — Streamlit Debugger Dashboard (Port 8501):**
```bash
streamlit run ui/Home.py --server.port 8501
```

### 5. Running Automated Tests
```bash
# Run full automated test suite (35 of 35 tests passing)
pytest -v

# Run offline benchmark evaluation harness
python -m eval.run_benchmark --grid eval/grid.yaml --dry-run --runs 8
```

---

## 📁 Repository Directory Structure

```
ReguGuard/
├── README.md                      # Comprehensive academic & technical documentation (this file)
├── ReguGuard_PRD.md               # Product Requirements Document & Single Source of Truth
├── requirements.txt               # Pinned Python package dependencies
├── Dockerfile                     # Multi-process container for Google Cloud Run deployment
├── pytest.ini                     # Pytest suite configuration
├── .env                           # Local environment credentials (Groq API, model names)
├── blackboard.db                  # SQLite database storing shared blackboard state
├── traces.db                      # SQLite database storing OpenTelemetry spans and metrics
│
├── src/                           # Production System Implementation
│   ├── schemas.py                 # Pydantic v2 schemas (RunConfig, ImpactReport, A2AEnvelope)
│   ├── config.py                  # Settings loader and environment parser
│   ├── orchestrator.py            # End-to-end multi-agent pipeline orchestrator
│   │
│   ├── blackboard/                # Blackboard Shared State (Criterion 1)
│   │   ├── store.py               # SQLite versioned store with atomic commits & access logging
│   │   └── mcp_server.py          # FastMCP server exposing bb_read, bb_write, bb_snapshot
│   │
│   ├── mcp_servers/               # 6 Decoupled FastMCP Tool Servers (Criterion 2)
│   │   ├── doc_fetcher.py         # Curated CBIC gazette notification loader
│   │   ├── clause_parser.py       # Statutory clause, threshold, and date extractor
│   │   ├── diff_tool.py           # Clause-level textual & semantic differencing
│   │   ├── vector_search.py       # ChromaDB version-aware semantic retriever
│   │   ├── sme_db.py              # SQLite financial profile & memory manager
│   │   └── deadline_calc.py       # Non-LLM deterministic statutory date calculator
│   │
│   ├── adk_app/                   # Google ADK Agent Roster (Sequential Pipeline)
│   │   └── pipeline.py            # Manager, Monitor, Diff, Profile, and ReAct Impact agents
│   │
│   ├── crew_app/                  # CrewAI Flow & A2A Server (Criterion 6)
│   │   └── flow.py                # Verifier, Skeptic reflection loop, and A2A service
│   │
│   ├── guardrails/                # 3-Layer Deterministic Safety (Criterion 8)
│   │   └── engine.py              # Injection defense, toxic language filtering, PII redaction
│   │
│   ├── observability/             # Observability & Provenance (Criterion 5 & 9)
│   │   ├── callbacks.py           # Agent, model, and tool lifecycle telemetry callbacks
│   │   ├── trace_store.py         # SQLite OpenTelemetry-style span persistence
│   │   ├── provenance.py          # DAG provenance graph & audit pack export
│   │   └── llm_client.py          # Groq LLM client with deterministic mock fallback
│   │
│   └── api/                       # FastAPI REST & SSE Streaming Backend
│       ├── main.py                # REST endpoints (/api/run, /api/blackboard, etc.)
│       └── stream.py              # Live SSE event stream (/api/runs/{id}/events)
│
├── ui/                            # React 19 Editorial Web Application
│   ├── src/
│   │   ├── App.tsx                # Main application view switcher & layout
│   │   ├── components/            # UI components
│   │   │   ├── RegulatoryComparisonVisualizer.tsx # 5 Interactive visualizer modules
│   │   │   ├── FlowThread.tsx     # D3 SVG sequential ink thread
│   │   │   ├── BlackboardStrip.tsx# Sliding paper note state strip
│   │   │   ├── ReportNote.tsx     # Large serif verdict report card
│   │   │   └── ExplainDrawer.tsx  # Plain-English concept drawer for students
│   │   └── pages/                 # Full feature views
│   │       ├── FlowPage.tsx       # Live assessment deck & pipeline thread
│   │       ├── BoardPage.tsx      # Blackboard history & agent access matrix
│   │       ├── GatesPage.tsx      # Guardrail lab with 5 attack presets
│   │       ├── TracesPage.tsx     # Span waterfall & payload inspector
│   │       └── CoveragePage.tsx   # 11 Professor criteria tabular matrix
│   └── Home.py                    # Streamlit debugger application (Port 8501)
│
├── data/                          # Verifiable Data Assets
│   ├── corpus/                    # 9 Official CBIC GST Notifications (2020–2027) + MANIFEST.csv
│   ├── smes/smes.json             # 12 diverse synthetic Indian SME profiles
│   └── cases/cases.jsonl          # 48 quota-balanced labelled benchmark test cases
│
└── tests/                         # Pytest Automated Test Suite (35 tests passing)
    ├── test_schemas.py            # Pydantic v2 contracts and business rules
    ├── test_blackboard.py         # Blackboard concurrency, versioning, access matrix
    ├── test_mcp_tools.py          # 6 FastMCP tool servers
    ├── test_step4_adk.py          # ADK sequential agents & trace logging
    ├── test_step5_a2a.py          # CrewAI reflection flow over A2A
    ├── test_step6_orchestrator.py # End-to-end ImpactReport validation
    ├── test_step7_guardrails.py   # 5 Preset guardrail attack validations
    ├── test_step9_topologies.py   # Fixed sequential order & offline variants
    ├── test_step10_dataset.py     # 12 SMEs, 48 cases, 18 persona variants
    └── test_steps11_12.py         # Metrics calculations & provenance audit packs
```

---

## ⚖️ Legal Disclaimer

ReguGuard is an academic research and engineering prototype developed exclusively for coursework evaluation under **CSE3101: Agentic AI** at **BML Munjal University**. It is designed for automated compliance triage and operational risk assessment. It does **not** constitute formal legal, taxation, or chartered accounting advisory services. Any statutory actions must be ratified by a certified Chartered Accountant or legal professional before implementation.
