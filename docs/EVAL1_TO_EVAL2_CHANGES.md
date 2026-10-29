# ReguGuard — Evaluation 1 to Evaluation 2 Changes

Evaluation 1 = the submitted *ReguGuard Project Summary* (Phase 1). Evaluation 2 = Phase 2, driven by the professor's 11 minimum criteria and the Part-2 rubric. Each row is a single final choice.

| # | Area | Evaluation 1 said | Evaluation 2 decision (FINAL) | Why changed |
|---|---|---|---|---|
| D1 | Messaging architecture | Blackboard shared case record described; "Sequential / Hierarchical / Event-driven, Blackboard, P2P, MCP" listed as architectures to explore | **Blackboard only in production.** P2P is evaluated offline in `eval/variants/` for comparison. | Professor: Blackboard mandatory. Single clean product architecture. |
| D2 | Orchestration topology | "Event-driven hierarchy": Manager triggers all agents | **Sequential only in production.** Manager plans, then fixed sequential: Monitor -> Diff -> Profile -> Impact -> (A2A) CrewAI Flow. Parallel Change||Profile from Eval 1 figure was replaced by Sequential for traceability; evaluated offline in `eval/variants/`. | Strict causal dependencies in legal analysis, zero non-deterministic coordinator loops. |
| D3 | Frameworks | Not named | **ADK** for Manager, Monitor, Change Detection, SME Profile, Impact. **CrewAI** (as a Flow) for Evidence Verification and Action. Linked by **A2A**. | Professor: use both, cross-framework A2A. |
| D4 | A2A implementation | Not specified | **Official `a2a-sdk` wrapper** around the CrewAI Flow (not CrewAI's native A2A support). | One predictable path. |
| D5 | Impact reasoning | Unspecified | **ReAct for Impact Agent only.** Single-shot LLM baseline evaluated offline in `eval/variants/`. Self-consistency and CoT dropped. | Grounded tool use prevents hallucinations without token bloat. |
| D6 | LLM | "including local LLMs" (course aim) | **Cloud Gemini only** (Google AI Studio key) for generator and judge. **Local LLM / Ollama / Privacy Mode dropped.** Privacy is handled by PII masking before any LLM call. | Cloud Run cannot host a local model; single model path keeps costs and results comparable. |
| D7 | Regulation Monitor source | Watches official government sources via MCP | **Reads a curated offline corpus (`data/corpus/`) via the `doc_fetcher` MCP tool.** Live government fetching dropped. | Reliability and reproducibility for demo and benchmark. |
| D8 | Evaluation | 40+ labelled cases, LLM-as-judge | **48 labelled cases × 6 configs (288 runs) + persona suite**, deterministic metrics **plus** LLM-as-judge, and a **single-LLM baseline** config. | Professor: ~40 runs per variant, boxplots, dataset. |
| D9 | Observability | "Trace ID logging" | **Own SQLite `TraceStore` with OpenTelemetry-style span fields + dashboards** (trace explorer, 4 heatmaps, provenance graph). No external tracing backend. | Professor: callbacks, heatmaps, auditability. |
| D10 | Guardrails | Not in summary | **Rule-based** guardrails (regex/keyword + schema checks) at input, tool and output, with PII masking. No LLM-based classifier. | New professor criterion; deterministic and cheap. |
| D11 | Vector store / embeddings | Version-aware vector store | **ChromaDB with Gemini embeddings** (version-aware metadata). | Small deploy image; no local model. |
| D12 | UI | Not specified | **Streamlit (multipage) + FastAPI backend, Plotly charts, polling for live updates.** | Fast to build; supports Concept-Lens requirement. |
| D13 | Deployment | Not in summary | **One Cloud Run service, single container** running the app, CrewAI A2A server and MCP servers as separate processes (supervisord). MCP uses streamable HTTP everywhere. Benchmarks are run locally; result files are committed. | Professor: deploy on cloud. Simplest reliable setup. |
| D14 | Multimodal | Course topic, not in summary | **Out of scope.** | Time. |
| D15 | Phase-2 scope vs Eval-1 plan | Phase 2 = Monitor + Change Detection end-to-end + version-aware RAG for one domain | **Phase 2 target is a full vertical slice (all agents, blackboard, A2A, guardrails v1, trace UI).** This is a scope *increase*; the progress report must say so. | Rubric C8 scores "requirements met till now". |
| D16 | Unchanged | Domain = Indian SMEs, GST/e-invoicing; output labelled "human review recommended"; three user types; 7-agent roster | **Unchanged**, plus a Guardrail layer. | — |

