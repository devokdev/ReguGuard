# ReguGuard — System Architecture & Coursework Report

> Course: **CSE3101 Agentic AI, BML Munjal University**  
> Team: **Yash Yadav (230664), Kartavya Dev (230653), Nancy (230640)**  
> System: **ReguGuard (Multi-Agent Regulatory Impact Analysis)**  

---

## 1. Executive Summary & Purpose
ReguGuard is an autonomous multi-agent regulatory compliance analysis engine tailored for Indian Small & Medium Enterprises (SMEs) navigating GST and e-invoicing reforms. Given a new official notification or circular, the system:
1. Emits an execution **RunPlan** via a coordinator (`ManagerAgent`).
2. Fetches authoritative legal text via **FastMCP** tools (`RegulationMonitorAgent`).
3. Runs parallel clause-level diffing and enterprise financial retrieval (`ChangeDetectionAgent` $\parallel$ `SMEProfileAgent`).
4. Evaluates applicability via **ReAct** reasoning and version-aware vector retrieval (`ImpactAnalysisAgent`).
5. Invokes a **CrewAI Flow** over the Agent-to-Agent (**A2A**) protocol for reflection-based quote verification and action planning (`EvidenceVerificationCrew` $\rightarrow$ `ActionPlannerCrew`).
6. Enforces multi-layer deterministic **Guardrails** (input injection/toxicity, PII masking, tool allow-lists, output business rules).
7. Yields an auditable **`ImpactReport`** carrying the mandatory headline:  
   **"Potential regulatory impact detected — human review recommended"**.

---

## 2. Multi-Agent Topology & Communication Architecture

```
                       [ Incoming Regulation ]
                                  │
                                  ▼
                        [ Input Guardrail ]
                    (Injection & PII Masking)
                                  │
                                  ▼
                         [ Manager Agent ]
                        (Emits RunPlan)
                                  │
                                  ▼
                     [ Regulation Monitor Agent ]
                  (MCP: doc_fetcher, clause_parser)
                                  │
                  ┌───────────────┴───────────────┐
                  ▼                               ▼
       [ Change Detection Agent ]       [ SME Profile Agent ]
       (MCP: diff_tool, vector_search)  (MCP: sme_db, memory)
                  └───────────────┬───────────────┘
                                  │
                                  ▼
                     [ Impact Analysis Agent ]
                   (ReAct + Agentic RAG Vector DB)
                                  │
                                  ▼ [A2A Envelope]
                   [ CrewAI Flow A2A Server ]
                   ├── Verifier Agent
                   ├── Skeptic Agent (Reflection retry)
                   └── Action Planner (deadline_calc MCP)
                                  │
                                  ▼
                        [ Output Guardrail ]
                  (Substring Check & Schema Lock)
                                  │
                                  ▼
                     [ Validated ImpactReport ]
```

---

## 3. The 11 Professor Criteria & Verifiable Implementations

| # | Criterion | Technical Implementation | Code Reference | Proving Test |
|---|---|---|---|---|
| **1** | Blackboard Architecture | SQLite versioned `BlackboardStore` with read-tracking matrix | [`src/blackboard/store.py`](file:///c:/Users/karta/Desktop/projects/agentic_ai/src/blackboard/store.py) | `tests/test_blackboard.py` |
| **2** | $\ge 2$ Tools via MCP | 6 standalone tool servers (`doc_fetcher`, `diff_tool`, `clause_parser`, `vector_search`, `sme_db`, `deadline_calc`) + `blackboard_server` | [`src/mcp_servers/`](file:///c:/Users/karta/Desktop/projects/agentic_ai/src/mcp_servers/) | `tests/test_mcp_tools.py` |
| **3** | Structured Output via Pydantic | Validated `ImpactReport` with deterministic business rules | [`src/schemas.py`](file:///c:/Users/karta/Desktop/projects/agentic_ai/src/schemas.py) | `tests/test_schemas.py` |
| **4** | Agentic Patterns Compared | Parallel vs Sequential vs Hierarchical; ReAct vs CoT vs Single-shot | [`src/adk_app/topologies.py`](file:///c:/Users/karta/Desktop/projects/agentic_ai/src/adk_app/topologies.py) | `tests/test_step9_topologies.py` |
| **5** | Callbacks & Heatmaps | Granular `TraceEvent` spans across all agent lifecycles, models, and tools | [`src/observability/callbacks.py`](file:///c:/Users/karta/Desktop/projects/agentic_ai/src/observability/callbacks.py) | `tests/test_step4_adk.py` |
| **6** | A2A Cross-Framework | ADK calling CrewAI Flow via `CrewAIA2AServer` and Agent Cards | [`src/crew_app/flow.py`](file:///c:/Users/karta/Desktop/projects/agentic_ai/src/crew_app/flow.py) | `tests/test_step5_a2a.py` |
| **7** | Frameworks | Google ADK + CrewAI only | Pipeline & Flow implementations | Repo audit |
| **8** | Guardrails & Safety | 3-layer deterministic safety, PII redaction (GSTIN, PAN, Phone, Email) | [`src/guardrails/engine.py`](file:///c:/Users/karta/Desktop/projects/agentic_ai/src/guardrails/engine.py) | `tests/test_step7_guardrails.py` |
| **9** | Observability & Provenance | Trace IDs, Spans, DAG Provenance Graph, JSON/Markdown Audit Packs | [`src/observability/provenance.py`](file:///c:/Users/karta/Desktop/projects/agentic_ai/src/observability/provenance.py) | `tests/test_steps11_12.py` |
| **10** | End-to-End Evaluation | 48 labelled cases, 6 architecture configs (288 runs), boxplots & metrics | [`eval/run_benchmark.py`](file:///c:/Users/karta/Desktop/projects/agentic_ai/eval/run_benchmark.py) | `eval/run_benchmark.py` |
| **11** | Cloud Deployment | Production Docker container with Supervisord for Google Cloud Run | [`Dockerfile`](file:///c:/Users/karta/Desktop/projects/agentic_ai/Dockerfile), [`deploy/cloudrun.sh`](file:///c:/Users/karta/Desktop/projects/agentic_ai/deploy/cloudrun.sh) | Deployment audit |

