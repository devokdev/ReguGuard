# ReguGuard — Viva Q&A & Practical Lab Exercises

> Course: **CSE3101 Agentic AI, BML Munjal University**  
> Team: **Yash Yadav (230664), Kartavya Dev (230653), Nancy (230640)**  
> Reference: PRD §15

---

## Module 1: `src/schemas.py` & System Data Contracts

### Viva Question 1: Why do we use Pydantic v2 schemas for all inter-agent messages instead of raw JSON dictionaries?
**Answer:**
Pydantic v2 enforces runtime schema validation, strict type-hinting, automatic type coercion, and immediate serialization/deserialization validation. In multi-agent architectures (ADK, CrewAI, MCP, A2A), agents produce unstructured or semi-structured LLM outputs. Forcing responses into validated Pydantic models ensures that any hallucinated or malformed output is caught immediately by the Output Guardrail before downstream agents or the UI consume it.

### Viva Question 2: How does the system prevent hallucinated claims from marking an SME as "impacted"?
**Answer:**
In `src/schemas.py`, `ImpactReport.validate_business_rules()` enforces a deterministic domain rule: if `verdict == "impacted"`, at least one evidence item must have `verified == True` (guaranteeing that the extracted quote is a verbatim substring of verified regulatory source text). If no evidence is verified, the system automatically downgrades the verdict to `"ambiguous"`, appends a guardrail flag, and caps confidence to $\le 0.5$.

### Viva Question 3: Explain the purpose of `TraceEvent` and why it includes OpenTelemetry-style fields.
**Answer:**
Criterion 5 and 9 require granular observability, auditability, and within-agent heatmaps. `TraceEvent` captures `trace_id`, `span_id`, `parent_span_id`, agent name, framework (`adk`, `crewai`, `mcp`, `system`), latency in milliseconds, input/output token counts, and cost in USD. This enables full provenance reconstruction and latency breakdown across all agents.

---

### Practical Lab Modification Exercise:
**Task:** Suppose the government introduces an exemption for SMEs registered under the "composition" scheme. How would you adjust the `ImpactReport` schema to flag composition scheme exemptions automatically?
**How to implement:**
1. Open [`src/schemas.py`](file:///c:/Users/karta/Desktop/projects/agentic_ai/src/schemas.py).
2. In `ImpactReport.validate_business_rules()`, inspect the SME profile or add a check: if `sme.gst_registration == "composition"` and the regulation only applies to regular taxpayers, modify the verdict to `"not_impacted"` or append a specialized note into `guardrail_flags`.
3. Run `pytest tests/test_schemas.py` to ensure validation still passes.

---

## Module 2: `src/blackboard/store.py` & Shared Blackboard Pattern

### Viva Question 1: What is the Blackboard architectural pattern and why is it mandatory in ReguGuard?
**Answer:**
The Blackboard architectural pattern centers on a shared, centralized knowledge repository (the blackboard) that autonomous, heterogeneous specialist agents (ADK agents, CrewAI flow, etc.) inspect, read from, and write to iteratively. In ReguGuard, it decouples multi-agent collaboration: the Regulation Monitor posts parsed clauses, Change Detection posts diffs, SME Profile loads company financials, Impact Analysis derives verdicts, and CrewAI posts verified quotes and action plans—all without brittle point-to-point hardcoded contracts.

### Viva Question 2: How does ReguGuard handle concurrent writes and audit trails on the Blackboard?
**Answer:**
`BlackboardStore` is backed by SQLite with transactional consistency. Every write computes `MAX(version) + 1` for the given `(case_id, key)` pair, storing historical versions alongside timestamps, agent names, and trace IDs. The `snapshot(case_id)` method provides a chronological provenance log of every change that transpired during a pipeline run.

### Practical Lab Modification Exercise:
**Task:** How would you restrict a specific agent (e.g. `sme_profile`) from writing to the `impact_verdict` key on the blackboard?
**How to implement:**
1. In `src/blackboard/store.py`, add a write permission rule inside `BlackboardStore.write()`:
   ```python
   RESTRICTED_KEYS = {"impact_verdict": ["adk_impact_agent"]}
   if key in RESTRICTED_KEYS and agent not in RESTRICTED_KEYS[key]:
       raise PermissionError(f"Agent {agent} is not authorized to write to {key}")
   ```
2. Run `pytest tests/test_blackboard.py`.

---

## Module 3: `src/mcp_servers/` & External Tools

### Viva Question 1: What is the Model Context Protocol (MCP) and why do we expose tools through it?
**Answer:**
MCP is an open standard that allows AI agents to securely discover, inspect schemas, and invoke external tools and data sources across process and machine boundaries. Exposing our 6 tools (e.g. `doc_fetcher`, `diff_tool`, `vector_search`) via FastMCP satisfies Course Criterion 2 and prevents tight coupling between the agent logic and underlying storage/parsing libraries.

### Viva Question 2: Why do we use a deterministic non-LLM calculator for statutory deadlines?
**Answer:**
LLMs are known to hallucinate dates and make arithmetic errors when computing elapsed days or calendar offsets. By delegating deadline computation to `deadline_calc`, we ensure 100% mathematical precision and reproducibility, which is crucial for legal and tax compliance.

### Practical Lab Modification Exercise:
**Task:** How would you add a new turnover threshold unit (e.g., "thousand crore") to `clause_parser`?
**How to implement:**
1. In `src/mcp_servers/clause_parser.py`, add `"thousand crore": 1000` to `word_to_num` or enhance the regex match.
2. Multiply by $10^7 \times 1000$ to get the correct rupee amount.
3. Verify by running `pytest tests/test_mcp_tools.py`.

---

## Module 4: Fixed Architecture Choices & Viva Defense

### Viva Question: Why did the team choose a Fixed Sequential Topology with Blackboard Messaging and ReAct Reasoning?
**Answer:**
1. **Why Blackboard Messaging?** In regulatory compliance, every legal assertion must be traceable to a source. The Blackboard serves as an immutable, versioned audit trail in SQLite where every agent's intermediate state (`clauses`, `diff`, `sme_profile`, `verdict`, `evidence`) is recorded with timestamps, agent signatures, and read/write access logs.
2. **Why Sequential Topology?** Regulatory analysis has strict causal dependencies: we cannot calculate a diff without first retrieving the document, we cannot evaluate applicability without knowing the SME's turnover, and we cannot formulate prescriptive deadlines without a grounded verdict. A deterministic sequential flow eliminates unpredictable coordinator loops, guarantees reproducible audit trails, and simplifies verification for viva evaluators.
3. **Why ReAct for the Impact Agent only?** Assessing statutory turnover thresholds requires dynamic querying of source clauses via tools and verifying facts before committing to a decision. ReAct provides an explicit Thought $\rightarrow$ Action (Agentic RAG vector search) $\rightarrow$ Observation trace that prevents hallucination, while other agents (Monitor, Change Detection, SME Profile) perform direct, tool-driven tasks.
4. **How are comparisons evaluated?** To satisfy the professor's criteria, alternative architectures (Point-to-Point messaging, Parallel topology, and Single-shot LLM baseline) are isolated in `eval/variants/` for offline benchmarking (E1–E4 grid), keeping the production product codebase clean, fast, and robust.

