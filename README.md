# ReguGuard — Autonomous Multi-Agent Regulatory Impact Analysis System

[![Course](https://img.shields.io/badge/Course-CSE3101%20Agentic%20AI-blue.svg)](https://www.bmu.edu.in)
[![Institution](https://img.shields.io/badge/University-BML%20Munjal%20University-orange.svg)](https://www.bmu.edu.in)
[![Tests](https://img.shields.io/badge/Tests-35%20Passed%20(100%25)-brightgreen.svg)]()
[![Architecture](https://img.shields.io/badge/Architecture-Blackboard%20%7C%20Sequential%20%7C%20ReAct-darkgreen.svg)]()
[![Frameworks](https://img.shields.io/badge/Frameworks-Google%20ADK%20%2B%20CrewAI%20(A2A)-purple.svg)]()

> **Course:** CSE3101 Agentic AI, BML Munjal University  
> **Team:** Yash Yadav (230664), Kartavya Dev (230653), Nancy (230640)  
> **Evaluation:** Phase-2 Vertical Slice & Phase-3 Complete System Delivery  

---

## 🌟 Executive Overview
**ReguGuard** is an autonomous multi-agent regulatory compliance analysis engine tailored for Indian Small & Medium Enterprises (SMEs) navigating Goods and Services Tax (GST) and e-invoicing reforms. Given a newly gazetted notification or circular, ReguGuard:
1. Validates inputs through **multi-layer deterministic guardrails** and scrubs sensitive PII (GSTIN, PAN, Phone, Email).
2. Issues an explicit execution **RunPlan** via an ADK coordinator (`ManagerAgent`).
3. Fetches official legal texts via **FastMCP** tool servers (`RegulationMonitorAgent`).
4. Performs clause-level diffing to detect statutory turnover threshold changes (`ChangeDetectionAgent`).
5. Loads company operational financials and return schemes from SQLite (`SMEProfileAgent`).
6. Assesses SME applicability using **ReAct reasoning** with version-aware vector retrieval (`ImpactAnalysisAgent`).
7. Bridges to a **CrewAI Flow** over the official **Agent-to-Agent (A2A)** protocol for reflection-based quote verification and prescriptive action planning (`EvidenceVerificationCrew` $\rightarrow$ `ActionPlannerCrew`).
8. Produces an auditable, grounded **`ImpactReport`** carrying the mandatory regulatory headline:  
   **"Potential regulatory impact detected — human review recommended"** (not formal legal advice).

---

## 🏛️ System Architecture

Following the final architectural decisions, ReguGuard operates on a **single, unified production pipeline**:
- **Messaging Architecture:** **Blackboard Only** (SQLite versioned `BlackboardStore` exposed via MCP; all agents read and write).
- **Topology:** **Fixed Sequential Only** (Strict causal dependencies: Manager $\rightarrow$ Monitor $\rightarrow$ Diff $\rightarrow$ Profile $\rightarrow$ Impact $\rightarrow$ CrewAI Flow).
- **Reasoning:** **ReAct for the Impact Agent Only** (Thought $\rightarrow$ Action [Agentic RAG] $\rightarrow$ Observation $\rightarrow$ Verdict). Other agents are deterministic tool-using agents.
- **Offline Benchmark Variants:** Alternative patterns (P2P messaging, Parallel topology, and Single-shot LLM baseline) are isolated in `eval/variants/` for offline benchmarking against the 48-case grid.

```
                      [ Official Gazette Notification ]
                                      │
                                      ▼
                        [ 01 Gate: Input Guardrail ]
                    (Injection Filter & PII Redaction)
                                      │
                                      ▼
                       [ 02 Plan: ADK Manager Agent ]
                         (Writes RunPlan to Blackboard)
                                      │
                                      ▼
                   [ 03 Read: ADK Regulation Monitor Agent ]
                     (MCP: doc_fetcher, clause_parser)
                                      │
                                      ▼
                    [ 04 Diff: ADK Change Detection Agent ]
                         (MCP: diff_tool, difflib)
                                      │
                                      ▼
                     [ 05 Profile: ADK SME Profile Agent ]
                             (MCP: sme_db, memory)
                                      │
                                      ▼
                    [ 06 Judge: ADK Impact Analysis Agent ]
                   (ReAct Reasoning + Agentic RAG Vector DB)
                                      │
                                      ▼ [Agent-to-Agent (A2A) Protocol]
                      [ CrewAI Flow A2A Service ]
                      ├── Verifier Agent (Proposes citation quote)
                      ├── Skeptic Agent (Reflection retry loop via substring check)
                      └── Action Planner (MCP: deadline_calc)
                                      │
                                      ▼
                        [ 07 Gate: Output Guardrail ]
                    (Substring Verification & Disclaimer)
                                      │
                                      ▼
                        [ Validated ImpactReport Note ]
```

---

## 📋 The 11 Professor Criteria Checklist

| # | Criterion | Technical Implementation in ReguGuard | Code File | Verification Test |
|---|---|---|---|---|
| **1** | Blackboard Architecture | Shared SQLite `BlackboardStore` with atomic versioning and read/write access frequency logging. | [`src/blackboard/store.py`](src/blackboard/store.py) | `tests/test_blackboard.py` |
| **2** | $\ge 2$ Tools via MCP | 6 standalone FastMCP tool servers (`doc_fetcher`, `diff_tool`, `clause_parser`, `vector_search`, `sme_db`, `deadline_calc`) + `blackboard_server`. | [`src/mcp_servers/`](src/mcp_servers/) | `tests/test_mcp_tools.py` |
| **3** | Structured Output via Pydantic | Pydantic v2 `ImpactReport` with deterministic business rules (mandatory headline & unverified evidence downgrade). | [`src/schemas.py`](src/schemas.py) | `tests/test_schemas.py` |
| **4** | Agentic Patterns Compared | Sequential ReAct production pipeline compared offline against Parallel topology, P2P messaging, and Single-shot LLM. | [`eval/variants/`](eval/variants/) | `tests/test_step9_topologies.py` |
| **5** | Callbacks & Heatmaps | Lifecycle monitoring spans (`TraceEvent`) recording latency, tokens, cost, and agent $\times$ key access heatmaps. | [`src/observability/callbacks.py`](src/observability/callbacks.py) | `tests/test_step4_adk.py` |
| **6** | Cross-Framework A2A | ADK remote client invoking CrewAI Flow using official Agent Cards and `A2AEnvelope` payloads. | [`src/crew_app/flow.py`](src/crew_app/flow.py) | `tests/test_step5_a2a.py` |
| **7** | Framework Restrictions | Google ADK + CrewAI only; no unauthorized agent frameworks (no LangChain, LangGraph, AutoGen). | Full repo audit | `tests/` |
| **8** | Guardrails & Safety | 3-layer deterministic rules: prompt injection defense, toxic language filtering, PII masking (GSTIN/PAN/email), and tool bounds. | [`src/guardrails/engine.py`](src/guardrails/engine.py) | `tests/test_step7_guardrails.py` |
| **9** | Observability & Provenance | Trace IDs, Spans, DAG Provenance Graph, and exportable JSON/Markdown audit packs. | [`src/observability/provenance.py`](src/observability/provenance.py) | `tests/test_steps11_12.py` |
| **10** | End-to-End Evaluation | 48 labelled cases, 4 benchmark configs (E1–E4, 192 runs), confusion matrix, and pure SVG boxplots. | [`eval/run_benchmark.py`](eval/run_benchmark.py) | `eval/` |
| **11** | Cloud Deployment | Multi-process container (`Dockerfile`) running FastAPI orchestrator and static web frontend via Supervisord for Google Cloud Run. | [`Dockerfile`](Dockerfile) | `deploy/cloudrun.sh` |

---

## 🎨 Frontend Design System ("Matte Printed Paper, Editorial, Calm")

The UI is a hand-crafted, custom React 19 application built with Vite and TypeScript (no CSS frameworks, no component libraries, no Plotly/Recharts):
- **Editorial Paper Aesthetic:** Surface `#EDE9E0`, ink `#1C1B19`, rule `#CFC9BC`, accent oxide `#B4532A`. Single light theme with subtle 3.5% opacity paper texture.
- **Typography:** Self-hosted `Newsreader` (light serif headings), `IBM Plex Sans` (UI body), and `IBM Plex Mono` (code, IDs, tabular numbers).
- **The Flow Thread:** D3 SVG horizontal thread connecting stages with real-time Server-Sent Events (`/api/runs/{id}/events`).
- **Interactive Explain Drawer:** Plain-English, 3-sentence concept definitions for first-year students with direct source code links.
- **Pure SVG Visualizations:** Hand-calculated SVG boxplots and heatmaps rendering latency distributions across configurations.

---

## 👥 Individual Team Member Contribution & Viva Defense

| Student | Core Module & Role | Viva Defense Topics | Key Files |
|---|---|---|---|
| **Yash Yadav** (230664) | **Cross-Framework A2A & CrewAI Reflection Flow** | • A2A protocol bridging Google ADK and CrewAI.<br>• Verifier + Skeptic reflection loop enforcing verbatim substring quote checks.<br>• Prescriptive Action Planning and statutory deadline calculations. | [`src/crew_app/flow.py`](src/crew_app/flow.py)<br>[`tests/test_step5_a2a.py`](tests/test_step5_a2a.py) |
| **Kartavya Dev** (230653) | **Blackboard Shared State & FastMCP Tool Ecosystem** | • Versioned SQLite `BlackboardStore` with read/write access tracking for heatmaps.<br>• 6 FastMCP microservices (`diff_tool`, `doc_fetcher`, `sme_db`, `vector_search`).<br>• Sequential pipeline orchestration and SSE streaming backend. | [`src/blackboard/store.py`](src/blackboard/store.py)<br>[`src/mcp_servers/`](src/mcp_servers/)<br>[`src/orchestrator.py`](src/orchestrator.py) |
| **Nancy** (230640) | **Guardrails, Observability & Evaluation Benchmarks** | • 3-layer deterministic safety (prompt injection, toxic de-escalation, GSTIN/PAN PII redaction).<br>• OpenTelemetry-style `TraceEvent` spans and waterfall viewer.<br>• 48-case benchmark grid (E1–E4) and pure SVG distribution boxplots. | [`src/guardrails/engine.py`](src/guardrails/engine.py)<br>[`eval/run_benchmark.py`](eval/run_benchmark.py)<br>[`src/observability/trace_store.py`](src/observability/trace_store.py) |

---

## 🚀 Quickstart & Setup Guide

### 1. Prerequisites
- **Python:** 3.11+
- **Node.js:** v18+ (tested on Node 23)

### 2. Installation
```bash
# Clone the repository
git clone https://github.com/yash-yadav/reguguard.git
cd reguguard

# Install Python backend dependencies
pip install -r requirements.txt

# Install React frontend dependencies
cd ui
npm install
npm run build
cd ..
```

### 3. Environment Configuration
Copy `.env.example` to `.env` and set your Groq API key:
```ini
GROQ_API_KEY=gsk_your_groq_key_here
GENERATOR_MODEL=qwen/qwen3.8-27b
JUDGE_MODEL=qwen/qwen3.8-27b
```

### 4. Running the Application
Open two terminal windows:

**Terminal 1 (FastAPI Backend Orchestrator):**
```bash
python -m uvicorn src.api.main:app --host 0.0.0.0 --port 8000 --reload
```
*API documentation available at http://127.0.0.1:8000/docs*

**Terminal 2 (Vite React Web Frontend):**
```bash
cd ui
npx vite --host 127.0.0.1 --port 5173
```
*Open http://127.0.0.1:5173 in your browser to access the editorial web app.*

---

## 🧪 Testing & Evaluation Commands

### Run Full Automated Test Suite (35 Tests Passing):
```bash
pytest -v
```

### Run Offline Benchmark Suite (E1 Baseline vs E2 P2P vs E3 Parallel vs E4 Single-Shot):
```bash
python -m eval.run_benchmark --grid eval/grid.yaml --dry-run --runs 8
```

### Verify Zero Banned Architecture Terms in Product Code:
```bash
python -c "
import os, re
banned = ['hierarchical', 'self_consistency', 'hybrid', 'cot']
for base in ['src', 'ui/src']:
    for root, _, files in os.walk(base):
        for f in files:
            if f.endswith(('.py', '.ts', '.tsx')):
                with open(os.path.join(root, f), 'r', encoding='utf-8') as fp:
                    content = fp.read()
                    for b in banned:
                        assert not re.search(r'\b' + b + r'\b', content, re.IGNORECASE), f'Violation {b} in {f}'
print('All architecture checks passed: 0 banned terms.')
"
```

---

## 📁 Repository Directory Structure

```
reguguard/
├── README.md                      # Complete system documentation (this file)
├── ReguGuard_PRD.md               # Single source of truth product specification
├── requirements.txt               # Pinned Python package dependencies
├── Dockerfile                     # Multi-process container for Google Cloud Run
├── pytest.ini                     # Pytest workspace configuration
├── .env.example                   # Environment configuration template
│
├── src/                           # Production System Code (One architecture only)
│   ├── schemas.py                 # Pydantic v2 data models (RunConfig, ImpactReport, etc.)
│   ├── config.py                  # Settings loader & environment parsing
│   ├── orchestrator.py            # End-to-end sequential orchestrator
│   │
│   ├── blackboard/                # Blackboard Shared State (Criterion 1)
│   │   ├── store.py               # SQLite versioned store with read/write access logging
│   │   └── mcp_server.py          # FastMCP server exposing bb_read, bb_write, bb_snapshot
│   │
│   ├── mcp_servers/               # 6 Standalone Tool Servers (Criterion 2)
│   │   ├── doc_fetcher.py         # Curated gazette document loader
│   │   ├── clause_parser.py       # Section splitting & turnover/date extraction
│   │   ├── diff_tool.py           # Clause-level diffing between legal versions
│   │   ├── vector_search.py       # ChromaDB version-aware semantic retriever
│   │   ├── sme_db.py              # SQLite financial profile & memory manager
│   │   └── deadline_calc.py       # Non-LLM deterministic statutory date calculator
│   │
│   ├── adk_app/                   # Google ADK Agent Roster (Sequential Pipeline)
│   │   └── pipeline.py            # Manager, Monitor, Diff, Profile, ReAct Impact agents
│   │
│   ├── crew_app/                  # CrewAI Flow & A2A Server (Criterion 6)
│   │   └── flow.py                # Verifier, Skeptic reflection loop, and A2A service
│   │
│   ├── guardrails/                # 3-Layer Deterministic Guardrails (Criterion 8)
│   │   └── engine.py              # Injection defense, toxic filter, and PII masking
│   │
│   ├── observability/             # Observability & Provenance (Criterion 5 & 9)
│   │   ├── callbacks.py           # Agent, model, and tool lifecycle callbacks
│   │   ├── trace_store.py         # SQLite OpenTelemetry-style span persistence
│   │   ├── provenance.py          # DAG provenance graph & audit pack export
│   │   └── llm_client.py          # Groq LLM client with deterministic mock fallback
│   │
│   └── api/                       # FastAPI REST & SSE Streaming Backend
│       ├── main.py                # REST endpoints (/api/run, /api/blackboard, etc.)
│       └── stream.py              # Live SSE event stream (/api/runs/{id}/events)
│
├── ui/                            # Custom Editorial Web Frontend (Vite + React + TS)
│   ├── src/
│   │   ├── copy.ts                # Centralized editorial copy (max 3-word titles, 1-line plain definitions)
│   │   ├── App.tsx                # Multi-page view switcher
│   │   ├── components/            # Editorial UI components
│   │   │   ├── Header.tsx         # Slim text navigation bar
│   │   │   ├── Footer.tsx         # Coursework colophon & legal disclaimer
│   │   │   ├── FlowThread.tsx     # D3 SVG sequential ink thread
│   │   │   ├── BlackboardStrip.tsx# Sliding paper note state strip
│   │   │   ├── ReportNote.tsx     # Large serif verdict report card
│   │   │   └── ExplainDrawer.tsx  # Right-side plain-English concept drawer
│   │   ├── pages/                 # Full feature screens
│   │   │   ├── FlowPage.tsx       # Live assessment deck & pipeline thread
│   │   │   ├── BoardPage.tsx      # Blackboard history & agent access matrix
│   │   │   ├── GatesPage.tsx      # Guardrail lab with 5 attack presets
│   │   │   ├── TracesPage.tsx     # Span waterfall & payload inspector
│   │   │   ├── LabPage.tsx        # Pure SVG boxplot & benchmark comparisons
│   │   │   └── CoveragePage.tsx   # 11 Professor criteria tabular matrix
│   │   └── styles/                # Plain CSS design tokens (tokens.css, base.css)
│
├── eval/                          # Offline Benchmarks & Variant Studies (Criterion 4 & 10)
│   ├── grid.yaml                  # 4-config benchmark matrix (E1 to E4)
│   ├── run_benchmark.py           # Offline grid runner & dataset evaluator
│   ├── metrics.py                 # Deterministic precision, recall, F1, false alarm rate
│   ├── plots.py                   # Plotly/JSON distribution chart generators
│   └── variants/                  # Isolated comparison architectures (never imported in src/)
│       ├── p2p_messaging.py       # E2: Point-to-Point message forwarding
│       ├── parallel_topology.py   # E3: Concurrent Change Detection || SME Profile
│       └── single_shot.py         # E4: Single-LLM baseline ablation
│
├── data/                          # Verifiable Data Assets
│   ├── corpus/                    # Official CBIC GST & e-invoicing texts + MANIFEST.csv
│   ├── smes/smes.json             # 12 diverse synthetic Indian SME profiles
│   ├── cases/cases.jsonl          # 48 quota-balanced labelled test cases
│   ├── personas/                  # 6 personas x 3 variants = 18 prompt variants
│   └── eval/                      # Benchmark CSV runs, summaries, and audit packs
│
├── docs/                          # Coursework Submission & Viva Documentation
│   ├── MODULE_GUIDE.md            # 5-line module overviews & "how to modify" guide
│   ├── VIVA_QA.md                 # Viva questions, answers, and practical exercises
│   ├── ARCHITECTURE.md            # Architectural deep-dive & framework boundaries
│   ├── COVERAGE.md                # 11 Criteria status audit mapped to Rubric C8
│   ├── PROGRESS_REPORT.md         # Phase 2 vs Phase 3 progress vs plan breakdown
│   ├── EVAL1_TO_EVAL2_CHANGES.md  # Detailed decision audit log (D1 to D16)
│   └── DEVIATIONS.md              # Runtime library adaptations and deviations
│
└── tests/                         # Pytest Automated Test Suite (35 tests)
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
ReguGuard is an academic research project developed for course **CSE3101: Agentic AI** at **BML Munjal University**. It is designed for informational and compliance triage purposes only and does **not** constitute formal legal, financial, or tax advisory services. All outputs must be reviewed by a certified Chartered Accountant or legal professional before operational implementation.
