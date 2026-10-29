# ReguGuard — Phase-2 11 Criteria Coverage Matrix

> Course: **CSE3101 Agentic AI, BML Munjal University**  
> Team: **Yash Yadav (230664), Kartavya Dev (230653), Nancy (230640)**  
> Reference: PRD §2, §14 (Step 8), §15

---

| # | Criterion | PRD Req | Implementation Status | Primary Code Evidence | Verification Test |
|---|-----------|---------|-----------------------|-----------------------|-------------------|
| **1** | Blackboard Architecture | Shared state mandatory + comparison | **MET** | [`src/blackboard/store.py`](file:///c:/Users/karta/Desktop/projects/agentic_ai/src/blackboard/store.py) | `tests/test_blackboard.py` |
| **2** | External Tools via MCP | $\ge 2$ tools via MCP | **MET** (6 servers built) | [`src/mcp_servers/`](file:///c:/Users/karta/Desktop/projects/agentic_ai/src/mcp_servers/) | `tests/test_mcp_tools.py` |
| **3** | Structured Output via Pydantic | Pydantic v2 data models | **MET** | [`src/schemas.py`](file:///c:/Users/karta/Desktop/projects/agentic_ai/src/schemas.py) | `tests/test_schemas.py` |
| **4** | Agentic Design Patterns | ReAct, Reflection, Parallel topology | **MET** | [`src/adk_app/pipeline.py`](file:///c:/Users/karta/Desktop/projects/agentic_ai/src/adk_app/pipeline.py), [`src/crew_app/flow.py`](file:///c:/Users/karta/Desktop/projects/agentic_ai/src/crew_app/flow.py) | `tests/test_step4_adk.py` |
| **5** | Callbacks & Heatmaps | Lifecycle monitoring spans & heatmaps | **MET** | [`src/observability/callbacks.py`](file:///c:/Users/karta/Desktop/projects/agentic_ai/src/observability/callbacks.py), [`src/observability/trace_store.py`](file:///c:/Users/karta/Desktop/projects/agentic_ai/src/observability/trace_store.py) | `tests/test_step4_adk.py` |
| **6** | A2A Protocol | Cross-framework communication | **MET** (ADK $\leftrightarrow$ CrewAI) | [`src/crew_app/flow.py`](file:///c:/Users/karta/Desktop/projects/agentic_ai/src/crew_app/flow.py) (`CrewAIA2AServer`) | `tests/test_step5_a2a.py` |
| **7** | Framework Restriction | CrewAI + Google ADK only | **MET** | Clean framework split behind standard adapters | Full repo audit |
| **8** | Guardrails & Safety | 3-layer guardrails & PII masking | **MET** | [`src/guardrails/engine.py`](file:///c:/Users/karta/Desktop/projects/agentic_ai/src/guardrails/engine.py) | `tests/test_step7_guardrails.py` |
| **9** | Observability & Provenance | Trace IDs, Spans, Provenance links | **MET** | [`src/observability/trace_store.py`](file:///c:/Users/karta/Desktop/projects/agentic_ai/src/observability/trace_store.py) | `tests/test_step4_adk.py` |
| **10** | End-to-End Evaluation | Reproducible pipeline with metrics | **MET** | [`src/orchestrator.py`](file:///c:/Users/karta/Desktop/projects/agentic_ai/src/orchestrator.py) | `tests/test_step6_orchestrator.py` |
| **11** | Cloud Deployment | Google Cloud Run containerization | **PREPARED** | `Dockerfile`, `deploy/cloudrun.sh` | Build audit |

---

### Phase-2 Vertical Slice Verification Summary:
- **Total Tests Passing:** 27 unit & acceptance tests across all 8 P0 steps.
- **Accepted Vertical Slice:** An end-to-end multi-agent pipeline spanning Manager planning, Regulation fetching, clause-level diffing, SME profile loading, ReAct impact analysis, cross-framework A2A invocation to CrewAI's reflection verification flow, deterministic deadline computation, rule-based guardrails, and final Pydantic `ImpactReport` generation.

